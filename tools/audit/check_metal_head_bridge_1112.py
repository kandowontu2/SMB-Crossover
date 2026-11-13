"""Qualify the Metal deferred head bridge in memory; write zero artifacts."""
from collections import Counter
from itertools import product
import argparse
import json
import check_metal_flower_1112 as Flower
import compose_metal_head_bridge_1112 as Compose
M = Flower.M


def inject(cpu, native, kind):
    """Check the real ISR and the continuation of a split C-bank write."""
    model = cpu.memory
    shadow = M.get(model, 'CurrentBankC')
    transient = (bytes(model[cpu.pc - 3:cpu.pc + 3]) == bytes.fromhex('8da17d8d1651')
                 and model.rawtags[2] != shadow and cpu.a == shadow)
    if kind != 'lagNMI' or not transient:
        return Flower.Host.Async.inject(cpu, native, kind)

    async_test = Flower.Host.Async
    expected = M.fork(model)
    expected_cpu = native(memory=expected, pc=cpu.pc)
    registers = (cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp, cpu.pc)
    for field in ('a', 'x', 'y', 'p', 'sp'):
        setattr(expected_cpu, field, getattr(cpu, field))
    native.step(expected_cpu)
    skipped = M.get(model, 'NmiSkipped')
    writes = len(model.ram_writes)
    lag, regular = async_test.lag_branch(model)
    assert M.get(model, 'NmiDisable') == 255
    cpu.nmi()
    low, hits = 255, 0
    for _ in range(80000):
        low = min(low, cpu.sp)
        if (cpu.sp, cpu.pc) == registers[-2:]:
            break
        assert cpu.pc != regular and model[cpu.pc] != 0
        hits += cpu.pc == lag
        native.step(cpu)
    else:
        raise AssertionError('Lag NMI continuation bound')
    assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp, cpu.pc) == registers
    assert hits == 1 and M.get(model, 'NmiSkipped') == (skipped + 1) & 255
    assert model.rawtags[2] == shadow and len(model.ram_writes) == writes
    native.step(cpu)
    assert async_test.state(model) == async_test.state(expected)
    assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp, cpu.pc) == (
        expected_cpu.a, expected_cpu.x, expected_cpu.y, expected_cpu.p & 0xef, expected_cpu.sp, expected_cpu.pc)
    return low


def call(model, entry, bank, *, a=85, x=7, y=91, p=0x61, limit=500000):
    model[0x16a], model[0x16c], model[0x16d] = a, entry & 255, entry >> 8
    cpu = M.NesMPU(memory=model, pc=M.address(model.bundle, 'FarCallCommon'))
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = bank, x, y, p, 224
    cpu.stPushWord(0x5ffe)
    minimum = cpu.sp
    for _ in range(limit):
        if cpu.pc == 0x5fff: break
        assert model[cpu.pc], ('BRK', hex(cpu.pc), model.rawtags)
        minimum = min(minimum, cpu.sp)
        cpu.step()
    else: raise AssertionError(('CPU bound', hex(cpu.pc)))
    assert cpu.sp == 224
    return dict(A=cpu.a, X=cpu.x, Y=cpu.y, P=cpu.p, minimum_SP=minimum)


def cold(raw, cookie, *, cuts=False):
    native = M.NesMPU
    entries = []
    rows = []
    fresh_entries = []
    fresh_pc = 0xbf9a if raw[Compose.rom_at(36, 0xbf9a)] == 0xad else 0xbfa5
    cut_points = set()
    cut_minimum = 255
    class Trace(native):
        def step(self):
            nonlocal cut_minimum
            tag = self.memory.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else -1
            if cuts and tag == 0xa4 and 0xbf46 <= self.pc < 0xbfbf:
                point = (self.pc, self.sp, self.p & 4)
                if point not in cut_points:
                    cut_points.add(point)
                    assert self.p & 4, ('cold IRQ enabled', point)
                    clone = M.fork(self.memory)
                    cpu = native(memory=clone, pc=self.pc)
                    for field in ('a', 'x', 'y', 'p', 'sp', 'pc'): setattr(cpu, field, getattr(self, field))
                    cut_minimum = min(cut_minimum, inject(cpu, native, 'lagNMI'))
            if tag == 0xa4 and self.pc == 0xbf46:
                entries.append(dict(A=self.a, X=self.x, Y=self.y, P=self.p))
            if tag == 0xa4 and self.pc == fresh_pc:
                fresh_entries.append(dict(X=self.x, P=self.p))
            if ((tag == 0xa4 and self.pc == 0xbf48) or
                    (tag == 0xa2 and self.pc == 0xbd9e)) and len(rows) < 60:
                rows.append((hex(self.pc), self.a, self.x, self.y, list(self.memory[3:6])))
            return native.step(self)
    M.NesMPU = Trace
    try: result, proof = Flower.cold(raw, cookie)
    except Exception as error: raise AssertionError(('cold_copy_entries', entries, rows, str(error))) from error
    finally: M.NesMPU = native
    assert len(entries) == 1 and entries[0]['X'] == 0, entries
    assert len(fresh_entries) == 1 and fresh_entries[0]['P'] & 4, fresh_entries
    return result, dict(proof, copy_entry=entries[0], cold_fresh_entry=fresh_entries[0],
        cold_lagNMI_cuts=len(cut_points), cold_lagNMI_minimum_SP=cut_minimum if cuts else None)


def event(seed, *, query_y=158, page=1, column=5, tile=0xc1, dy=250):
    model = M.fork(seed)
    packet = model.ram[2]
    packet[0x880:0x888] = bytes((0xa7, M.get(model, 'FrameCounter'), tile,
                                query_y, column | (0xd0 if page & 1 else 0), 0x50, dy, 164))
    row = (query_y & 0xf0) - 0x20
    if row >= 0: model[0x300 + packet[0x884] + row] = tile
    M.put(model, Player_Y_Speed=0, Player_Y_Position=164)
    return model


def basic(parent, candidate):
    counts = Counter()
    for p in (0x20, 0x21, 0x60, 0x61, 0x24, 0x65):
        old, new = M.fork(parent), M.fork(candidate)
        a, b = M.invoke(old, 'HuHead', a=85, x=7, y=91, p=p), M.invoke(new, 'HuHead', a=85, x=7, y=91, p=p)
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (a, b)
        assert bytes(old[3:11]) == bytes(new[3:11])
        counts['no_event_native_ABI'] += 1
    for query_y, page, column, p in product((68, 78, 132, 158, 196, 222), (0, 1, 2), (0, 5, 15), (0x21, 0x61)):
        model = event(candidate, query_y=query_y, page=page, column=column)
        result = M.invoke(model, 'HuHead', a=85, x=7, y=91, p=p)
        row = (query_y & 0xf0) - 32
        v = 0x40 if (query_y & 0xf0) in (0x80, 0x90) else 0
        expected_p = (p & ~(0x80 | 0x40 | 2 | 1)) | 0x80 | v | 1 | 0x30
        assert (result['A'], result['X'], result['Y'], result['P']) == (0xc1, 0, 91, expected_p), (query_y, result, expected_p)
        assert bytes(model[5:11]) == bytes((row, 0xc1, 4, 0x50, column | (0xd0 if page & 1 else 0), 3))
        assert M.get(model, 'Player_Y_Speed') == 250 and model.ram[2][0x880] == 0
        old = M.fork(parent)
        old[0x300:0x800] = model[0x300:0x800]
        M.put(old, Player_Y_Speed=250, Player_Y_Position=164)
        a, b = M.invoke(old, 'HuHead', a=85, x=7, y=91, p=p), M.invoke(model, 'HuHead', a=85, x=7, y=91, p=p)
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P'))
        assert bytes(old[3:11]) == bytes(model[3:11])
        counts['accepted_exact_cell_and_one_shot'] += 1
    for reason in ('stale', 'lowY', 'changed', 'scene', 'ready', 'tag'):
        model = event(candidate)
        if reason == 'stale': model.ram[2][0x881] ^= 1
        if reason == 'lowY': model.ram[2][0x887] = 160
        if reason == 'changed': model[0x300 + 0xd5 + 0x70] = 0x61
        if reason == 'scene': M.put(model, GameEngineSubroutine=7)
        if reason == 'ready': model.ram[2][0x800] = 0
        if reason == 'tag': model.ram[2][0x880] = 0xff
        old = M.fork(parent)
        old[0x300:0x800] = model[0x300:0x800]
        M.put(old, GameEngineSubroutine=M.get(model, 'GameEngineSubroutine'),
              Player_Y_Position=M.get(model, 'Player_Y_Position'))
        a, b = M.invoke(old, 'HuHead'), M.invoke(model, 'HuHead')
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (reason, a, b)
        assert bytes(old[3:11]) == bytes(model[3:11])
        assert M.get(model, 'Player_Y_Speed') == 0
        counts['negative_' + reason] += 1
    for byte in range(32):
        model = event(candidate)
        model.ram[2 + byte // 16][0x1fe0 + byte % 16] ^= 1
        old = M.fork(parent)
        old[0x300:0x800] = model[0x300:0x800]
        M.put(old, Player_Y_Position=164)
        a, b = M.invoke(old, 'HuHead'), M.invoke(model, 'HuHead')
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (byte, a, b)
        counts['complete_header_native_fallback'] += 1
    return dict(counts)


def source_fixture(seed, *, tile=0xc1, gravity=0, dy=250, clock=1, source_y=158):
    model = M.fork(seed)
    model.raw_page(2, 2)
    M.put(model, CurrentBankC=2)
    M.put(model, Player_PageLoc=1, Player_X_Position=84, Player_Y_Position=164, Player_Y_Speed=0)
    Flower.Host.terrain(model, lambda x, y: tile if 336 <= x < 352 and 144 <= y < 160 else 0)
    source = model.ram[2]
    for at, value in ((0x480, 76), (0x498, 1), (0x4b0, source_y), (0x4c8, 0),
                      (0x570, dy), (0x5b8, clock), (0x734, gravity), (0x50, 0)):
        source[at] = value
    source[0x880:0x888] = bytes(8)
    return model


def source_capture(parent, candidate):
    _, labels = Compose.Flower.inputs()
    old, new = source_fixture(parent), source_fixture(candidate)
    a, b = call(old, labels['Ms_B744'], 3), call(new, labels['Ms_B744'], 3)
    assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (a, b)
    assert bytes(old.ram[2][:0x800]) == bytes(new.ram[2][:0x800])
    assert new.ram[2][0x880] == 0xa7, dict(packet=list(new.ram[2][0x880:0x887]),
        source=list(new.ram[2][0x59:0x5d]), flags=new.ram[2][0x810], result=b)
    assert list(new.ram[2][0x880:0x888]) == [0xa7, M.get(new, 'FrameCounter'), 0xc1, 158, 0xd5, 80, 250, 164]
    result = M.invoke(new, 'HuHead')
    assert result['A'] == 0xc1 and M.get(new, 'Player_Y_Speed') == 250
    return dict(real_B744_to_B798=True, original_physics_AXYP_equal=True,
                exact_contact=[336, 158, 193], packet_consumed=True)


def block_effect(candidate):
    _, labels = Compose.Flower.inputs()
    model = source_fixture(candidate)
    M.put(model, PlayerStatus=0, AreaType=1, Player_Y_HighPos=1,
          DisableCollisionDet=0, BlockBounceTimer=0, GuestHurtTicks=0,
          PlayerSize=0, CrouchingFlag=0, SwimmingFlag=0)
    call(model, labels['Ms_B744'], 3)
    # The actual source export changes nativeY164 to160 before native BG.
    M.put(model, Player_Y_Position=160)
    result = M.invoke(model, 'PlayerBGCollision', p=0x21)
    record = dict(result=result, type=M.get(model, 'PowerUpType'),
        flags=[M.get(model, 'Enemy_Flag', i) for i in range(6)],
        ids=[M.get(model, 'Enemy_ID', i) for i in range(6)],
        used_cell=model[0x300 + 0xd5 + 0x70], packet=model.ram[2][0x880],
        dy=M.get(model, 'Player_Y_Speed'))
    assert any(record['flags'][i] and record['ids'][i] == 0x2e for i in range(6)), record
    assert record['packet'] == 0 and record['type'] == 0, record
    return record


def router(parent, candidate):
    counts = Counter()
    for selected, row in product(range(35, 44), range(37)):
        results = []
        for seed in (parent, candidate):
            model = M.fork(seed)
            model.raw_page(1, 207)
            M.put(model, SelectedCharacter=selected)
            model[0x16c:0x16e] = [0x55, 0x66]
            model[0x162] = 0x77
            cpu = M.NesMPU(memory=model, pc=0xbfad)
            cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = selected, 7, row, 0x61, 224
            cpu.stPush(0x61)
            cpu.stPush(91)
            for _ in range(100):
                if cpu.pc in (0xb8b2, 0xbae7): break
                cpu.step()
            else: raise AssertionError(('router bound', selected, row, hex(cpu.pc)))
            results.append((model[0x16c] | model[0x16d] << 8, model[0x162], cpu.x, cpu.sp, cpu.pc))
        if selected == 35 and row == 10:
            assert results[0][:2] == (0xab8b, 0xce) and results[1][:2] == (0xbf8b, 0xa4), results
            assert results[0][2:] == results[1][2:]
        else: assert results[0] == results[1], (selected, row, results)
        counts['owner_row_destinations'] += 1
    native = M.NesMPU
    arrivals = []
    class Trace(native):
        def step(self):
            if self.pc == 0xbfad and self.memory.rawtags[1] == 207:
                arrivals.append((M.get(self.memory, 'SelectedCharacter'), self.a, self.y))
            return native.step(self)
    M.NesMPU = Trace
    try:
        for selected in range(44):
            old, new = M.fork(parent), M.fork(candidate)
            M.put(old, SelectedCharacter=selected)
            M.put(new, SelectedCharacter=selected)
            a, b = M.invoke(old, 'HuHead'), M.invoke(new, 'HuHead')
            assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (selected, a, b)
            assert bytes(old[3:11]) == bytes(new[3:11]), selected
            counts['public_head_owners'] += 1
    finally: M.NesMPU = native
    assert arrivals and all(owner == a and row == 10 for owner, a, row in arrivals), arrivals
    counts['real_BFAD_A_equals_selected_arrivals'] = len(arrivals)
    return dict(counts)


def source_controls(parent, candidate):
    _, labels = Compose.Flower.inputs()
    counts = Counter()
    for gravity, dy, clock, tile in product((0, 128), (0, 1, 127, 128, 250, 255), (0, 1, 25, 26, 30), (0, 0x61, 0xc1, 0xc2, 0x26)):
        old, new = (source_fixture(seed, tile=tile, gravity=gravity, dy=dy, clock=clock) for seed in (parent, candidate))
        a, b = call(old, labels['Ms_B744'], 3), call(new, labels['Ms_B744'], 3)
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (gravity, dy, clock, tile, a, b)
        assert bytes(old.ram[2][:0x800]) == bytes(new.ram[2][:0x800])
        captured = new.ram[2][0x880] == 0xa7
        if captured: assert gravity == 0 and dy & 128 and 0 < clock < 26 and tile in (0x61, 0xc1, 0xc2), (
            gravity, dy, clock, tile, list(new.ram[2][0x880:0x887]))
        counts['source_physics_pairs'] += 1
        counts['authentic_head_events'] += captured
    assert counts['authentic_head_events']
    for name in ('CrossoverSourceFootProbe', 'BlockBufferColli_Feet', 'HuWall'):
        if name not in parent.bundle['syms']: continue
        old, new = event(parent), event(candidate)
        a, b = M.invoke(old, name, y=0), M.invoke(new, name, y=0)
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (name, a, b)
        assert new.ram[2][0x880] == 0xa7 and M.get(new, 'Player_Y_Speed') == 0
        counts['non_head_consumers_preserve_pending'] += 1
    return dict(counts)


def lifecycle(parent, candidate):
    _, labels = Compose.Flower.inputs()
    counts = Counter()
    for p, tag in product((0x20, 0x21, 0x60, 0x61, 0x24), (0, 32, 0xa7, 0xff)):
        old, new = (source_fixture(seed, tile=0, dy=0, clock=0, source_y=176) for seed in (parent, candidate))
        for model in (old, new):
            M.put(model, FrameCounter=2, GamePauseStatus=0)
            model.ram[2][0x880] = tag
        a, b = call(old, labels['MsHostStep'], 3, p=p), call(new, labels['MsHostStep'], 3, p=p)
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (a, b)
        assert bytes(old.ram[2][:0x800]) == bytes(new.ram[2][:0x800])
        assert new.ram[2][0x880] != 0xa7
        counts['accepted_step_clears_old_event_AXYP_equal'] += 1
    for name in ('HuFresh',):
        if name not in candidate.bundle['syms']: continue
        model = event(candidate)
        headers = tuple(bytes(model.ram[bank][0x1fe0:0x1ff0]) for bank in (2, 3))
        M.invoke(model, name)
        assert model.ram[2][0x800] == 0
        assert tuple(bytes(model.ram[bank][0x1fe0:0x1ff0]) for bank in (2, 3)) == headers
        assert M.invoke(model, 'HuHead')['A'] == 0
        counts['fresh_rejects_pending_without_header_revoke'] += 1
    for pre, post, dy, after in product((0, 3, 4, 15), (0, 4, 15), (128, 250, 255), (0, 1, 7)):
        model = event(candidate, dy=dy)
        model.ram[2][0x887] = 160 | pre
        M.put(model, Player_Y_Position=160 | post, Player_Y_Speed=after)
        result = M.invoke(model, 'HuHead')
        assert result['A'] == (0xc1 if pre >= 4 else 0), (pre, post, result)
        assert M.get(model, 'Player_Y_Speed') == (dy if pre >= 4 else after)
        if pre >= 4: assert model[M.address(model.bundle, 'R4')] == pre
        assert model.ram[2][0x880] == 0
        counts['pre_contact_lowY_and_DY_vs_post_export'] += 1
    return dict(counts)


def interrupts(candidate):
    _, labels = Compose.Flower.inputs()
    totals = Counter()
    points = set()
    minimum = 255
    native = M.NesMPU
    watch = ((3, 0xad54, 0xad57), (3, 0xb599, 0xb5b7), (3, 0xbfc0, 0xbfdd),
             (2, 0xd8af, 0xd900), (2, 0xdcd9, 0xdd00),
             (0xa4, 0xbf8b, 0xbfbf), (0xcf, 0xa707, 0xa734),
             (0xcf, 0xbfad, 0xbfcd), (0xce, 0xab8b, 0xab8e))
    class Probe(native):
        def step(self):
            nonlocal minimum
            tag = self.memory.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else -1
            if any(tag == bank and lo <= self.pc < hi for bank, lo, hi in watch):
                key = (tag, self.pc, self.sp, self.p & 4)
                if key not in points:
                    points.add(key)
                    for kind in ('IRQ', 'lagNMI'):
                        if kind == 'IRQ' and self.p & 4: continue
                        model = M.fork(self.memory)
                        cpu = native(memory=model, pc=self.pc)
                        for field in ('a', 'x', 'y', 'p', 'sp', 'pc'): setattr(cpu, field, getattr(self, field))
                        try: depth = inject(cpu, native, kind)
                        except AssertionError as error: raise AssertionError(('interrupt cut', kind, key, dict(totals))) from error
                        minimum = min(minimum, depth)
                        totals[kind] += 1
            return native.step(self)
    M.NesMPU = Probe
    try:
        M.invoke(event(candidate), 'PlayerBGCollision', p=0x21)
        call(source_fixture(candidate), labels['Ms_B744'], 3, p=0x21)
        model = source_fixture(candidate, tile=0, clock=0, dy=0, source_y=176)
        M.put(model, FrameCounter=2)
        call(model, labels['MsHostStep'], 3, p=0x21)
        call(M.fork(candidate), 0xbfa5, 0xa4, p=0x25)
    finally: M.NesMPU = native
    assert totals['IRQ'] and totals['lagNMI'] and minimum >= 128, (totals, minimum)
    return dict(cuts=dict(totals), minimum_SP=minimum,
                unique_instruction_SP_points=len(points),
                scope='Actual head/nativeBG and accepted original actor contact/update unmasked; unchanged Fresh at real cold I-set precondition. Direct callers, not deepest Main or nested ISR.')


def readback_faults(raw, layout, additional_cases=()):
    _, _, chunks, symbols, _ = Compose.recipe()
    cases = ((3, 0xbfc0, chunks['CAPTURE'][0]),
             (3, symbols['MsHeadScene'], chunks['SAVE_POINT'][25]),
             (2, 0xd8af, chunks['GETTER'][0]),
             (2, 0xdcd9, chunks['CAPTURE_TAIL'][0]),
             (2, 0xdcff, chunks['CAPTURE_TAIL'][-1])) + tuple(additional_cases)
    receipts = []
    native, native_fresh = M.NesMPU, M.fresh
    for bank, address, expected in cases:
        holder = {}
        def fresh(bundle):
            model = native_fresh(bundle)
            parent_bus = type(model)
            class Fault(parent_bus):
                def __getitem__(self, at):
                    value = parent_bus.__getitem__(self, at)
                    if (isinstance(at, int) and 0x8000 <= at < 0xe000
                            and self.rawtags[(at - 0x8000) // 8192] == bank
                            and at & 0x1fff == address & 0x1fff
                            and self.head_verify_active and not self.head_fault_seen
                            and value == expected):
                        self.head_fault_seen = True
                        self.head_fault_alias = at
                        self.head_fault_reads = self.ppu_reads
                        return value ^ 1
                    return value
            model.__class__ = Fault
            model.head_verify_active = False
            model.head_fault_seen = False
            holder['model'] = model
            return model
        class Probe(native):
            def step(self):
                model = self.memory
                if hasattr(model, 'head_verify_active'):
                    tag = model.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else -1
                    model.head_verify_active = tag == 0xa4 and self.pc == symbols['MsHeadColdVerify'] + 3
                    holder['cpu'] = self
                return native.step(self)
        M.fresh, M.NesMPU = fresh, Probe
        try:
            try: Flower.cold(raw, bytes.fromhex(layout['cookie']))
            except AssertionError as error:
                assert not error.args, ('unexpected cold fault failure', error.args)
            else: raise AssertionError('Fault did not reject publication')
        finally: M.fresh, M.NesMPU = native_fresh, native
        model, cpu = holder['model'], holder['cpu']
        assert model.head_fault_seen and cpu.pc == 0x5fff and cpu.sp == 224 and not cpu.p & 1
        assert all(bytes(model.ram[b][0x1fe0:0x1ff0]) != bytes.fromhex(layout['cookie']) for b in (2, 3))
        receipts.append(dict(bank=bank, opcode_at=hex(address), copied_opcode=expected,
            readback_alias=hex(model.head_fault_alias), PPU_reads=model.head_fault_reads,
            returned_carry_clear=True, full_headers_unpublished=True))
    return receipts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--basic', action='store_true')
    parser.add_argument('--faults-only', action='store_true')
    args = parser.parse_args()
    raw = Flower.NIGHTLY.read_bytes()
    flower, flower_layout = Compose.Flower.transform(raw)
    changed, layout = Compose.transform(flower)
    assert Compose.transform(changed, True)[0] == flower
    if args.faults_only:
        _, cold_proof = cold(changed, bytes.fromhex(layout['cookie']), cuts=True)
        print('METAL_HEAD_COLD_INTERRUPTS ' + json.dumps(cold_proof, separators=(',', ':')), flush=True)
        print('METAL_HEAD_READBACK ' + json.dumps(dict(passed=True,
            candidate_SHA256=layout['candidate_SHA256'], cases=readback_faults(changed, layout)),
            separators=(',', ':')), flush=True)
        return
    parent, parent_cold = cold(flower, bytes.fromhex(flower_layout['cookie']))
    candidate, candidate_cold = cold(changed, bytes.fromhex(layout['cookie']))
    print('METAL_HEAD_BASIC ' + json.dumps(dict(passed=True,
        layout=layout, parent_cold=parent_cold, candidate_cold=candidate_cold,
        basic=basic(parent, candidate), source=source_capture(parent, candidate),
        block_effect=block_effect(candidate)), separators=(',', ':')), flush=True)
    if not args.basic:
        print('METAL_HEAD_CONTROLS ' + json.dumps(dict(router=router(parent, candidate),
            source=source_controls(parent, candidate), lifecycle=lifecycle(parent, candidate),
            interrupts=interrupts(candidate)), separators=(',', ':')), flush=True)


if __name__ == '__main__': main()
