"""Current shared UI-row study; direct CPU fixtures, stdout only."""
from hashlib import sha256
import argparse
import json

import audit_current_roster_powerups_1110 as Roster
import check_bub_current_budget_1113 as B
from check_ff_head_lifetime_irq_1110 import clone


ROW = 0xb0e3
LEAF = 0xa7eb
SHIM = 0xafd5
ROWS = (
    dict(slot=0, cycle=8, raw=41, name='MINI MARIO'),
    dict(slot=5, cycle=4, raw=5, name='GETSU FUMA'),
    dict(slot=25, cycle=1, raw=39, name='BUB'),
    dict(slot=25, cycle=2, raw=39, name='BOB'),
    dict(slot=25, cycle=3, raw=43, name='SONIC'),
    dict(slot=25, cycle=4, raw=43, name='SUPER SONIC'),
    dict(slot=27, cycle=1, raw=40, name='DONKEY KONG JR'),
    dict(slot=29, cycle=0, raw=37, name='EXCITEBIKE'),
    dict(slot=29, cycle=1, raw=38, name='PRINCE PERSIA'),
)


def at(pc):
    return 16 + 65 * 8192 + pc - 0xa000


def bare_leaf_fixture(raw):
    assert sha256(raw).hexdigest() == B.PIN
    assert raw[at(ROW):at(ROW)+3] == bytes.fromhex('4c40a7')
    assert raw[at(LEAF):at(LEAF)+5] == bytes.fromhex('ad6a011860')
    image = bytearray(raw)
    image[at(ROW):at(ROW)+3] = bytes.fromhex('4ceba7')
    return bytes(image)


def fixture_image(raw):
    image = bytearray(bare_leaf_fixture(raw))
    assert raw[at(SHIM):at(SHIM)+5] == raw[at(0xaa61):at(0xaa61)+5] == bytes.fromhex('626a6c6d79')
    bank = raw[at(0xa000):at(0xa000)+8192]
    readers = [0xa000+i for i in range(8190)
               if bank[i+1:i+3] == SHIM.to_bytes(2, 'little')]
    assert readers == [0xae1d, 0xaec8], readers
    # Both actual indexed loops are explicitly bounded to X0..4. The common
    # table is the exact preexisting immutable data, not new state or a cache.
    for pc, code in ((0xae1b, 'a200bcd5afb9000148e8e005d0f4'),
                     (0xaec6, 'a204bcd5af68990001ca10f6')):
        expected = bytes.fromhex(code)
        assert raw[at(pc):at(pc)+len(expected)] == expected, hex(pc)
    for pc in readers:
        assert raw[at(pc):at(pc)+3] == bytes.fromhex('bcd5af')
        image[at(pc):at(pc)+3] = bytes.fromhex('bc61aa')
    image[at(SHIM):at(SHIM)+5] = bytes.fromhex('08284ceba7')
    image[at(ROW):at(ROW)+3] = b'\x4c' + SHIM.to_bytes(2, 'little')
    return bytes(image)


def changes():
    return ((ROW, bytes.fromhex('4c40a7'), bytes.fromhex('4cd5af')),
            (SHIM, bytes.fromhex('626a6c6d79'), bytes.fromhex('08284ceba7')),
            (0xae1d, bytes.fromhex('bcd5af'), bytes.fromhex('bc61aa')),
            (0xaec8, bytes.fromhex('bcd5af'), bytes.fromhex('bc61aa')))


def proposal(raw):
    image = fixture_image(raw)
    edits = [dict(PC=pc, file=at(pc), old=old.hex(), new=new.hex())
             for pc, old, new in changes()]
    allowed = {at(pc)+i for pc, old, new in changes() for i in range(len(old))}
    assert all(a == z or i in allowed for i, (a, z) in enumerate(zip(raw, image)))
    return image, dict(parent_SHA256=B.PIN, candidate_SHA256=sha256(image).hexdigest(),
        edits=edits, source_component_cookie_changed=False, native_code_bytes=5,
        additional_native_storage=0, shared_table_alias=0xaa61,
        Source_UI_row=29, emitted_ROM_files=0,
        direct_callee_ABI_exact=False,
        intentional_callee_difference='Prince role87 clears V; Sonic header rejection returns A0/X0 and stamps SMC179=0. Shortcut preserves incoming registers. Actual UI caller kills these dead values before any gameplay consumer; direct oracles remain negative.',
        physical_cadence_qualified=False, private_budget_probe=True)


def reverse(raw):
    out = bytearray(raw)
    for pc, old, new in changes():
        assert raw[at(pc):at(pc)+len(new)] == new
        out[at(pc):at(pc)+len(old)] = old
    parent = bytes(out)
    assert sha256(parent).hexdigest() == B.PIN
    assert proposal(parent)[0] == raw
    return parent


inverse = reverse


def combined_proposal(raw):
    """Explicit independent UI plus a77 composition, never the default API."""
    import bub_empty_loops_1113 as Empty
    ui, ui_info = proposal(raw)
    empty, empty_info = Empty.proposal(raw)
    ui_offsets = {i for i, (a,z) in enumerate(zip(raw, ui)) if a != z}
    empty_offsets = {i for i, (a,z) in enumerate(zip(raw, empty)) if a != z}
    assert not ui_offsets & empty_offsets
    first, second = bytearray(empty), bytearray(ui)
    for i in ui_offsets:
        assert first[i] == raw[i]
        first[i] = ui[i]
    for i in empty_offsets:
        assert second[i] == raw[i]
        second[i] = empty[i]
    assert first == second
    image = bytes(first)
    return image, dict(parent_SHA256=B.PIN, candidate_SHA256=sha256(image).hexdigest(),
        UI_only=ui_info['candidate_SHA256'], empty_only=Empty.CANDIDATE,
        exact_disjoint_commutation=True, UI_changed_bytes=len(ui_offsets),
        empty_changed_bytes=len(empty_offsets), Source_UI=ui_info,
        empty_loop_source=empty_info, physical_cadence_qualified=False,
        private_budget_probe=True, emitted_ROM_files=0)


def combined_reverse(raw):
    import bub_empty_loops_1113 as Empty
    out = bytearray(raw)
    for pc, old, new in changes():
        assert raw[at(pc):at(pc)+len(new)] == new
        out[at(pc):at(pc)+len(old)] = old
    parent = Empty.reverse(bytes(out))
    assert sha256(parent).hexdigest() == B.PIN
    assert combined_proposal(parent)[0] == raw
    return parent


def controller(raw, identity=0, *, combined=False):
    """Strict new read-only UI-only or explicitly combined native profile."""
    import profile_bub_empty_native_1113 as Profile
    digest = sha256(raw).hexdigest()
    if combined:
        import bub_empty_loops_1113 as Empty
        parent = combined_reverse(raw)
        empty = Empty.proposal(parent)[0]
        text = Empty.controller(empty, identity)
        original = Empty.CANDIDATE
    else:
        parent = reverse(raw)
        text = Profile.controller(parent, identity)
        original = B.PIN
    assert text.count(original) == 1
    text = text.replace(original, digest)
    check = '\nlocal uiNative={' + ','.join(
        '{offset='+str(at(pc)-16)+',data="'+new.hex()+'"}'
        for pc, old, new in changes()) + '}\n'
    check += ('for _,h in ipairs(uiNative)do for k=1,#h.data,2 do '
              'assert(emu.read(h.offset+(k-1)//2,emu.memType.nesPrgRom)=='
              'tonumber(h.data:sub(k,k+1),16),"Exact native UI shim/table alias")end end\n')
    marker="assert(os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,'Exact current ROM identity')"
    assert text.count(marker) == 1
    text = text.replace(marker, marker + check)
    assert not any(token in text for token in ('emu.write','emu.setState','io.open',
                                             'loadState','saveState','takeScreenshot'))
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def bindings(raw):
    ui, ui_info = proposal(raw)
    combined, combined_info = combined_proposal(raw)
    assert reverse(ui) == combined_reverse(combined) == raw
    lua = []
    for mode, image in (('UI-only', ui), ('UI+a77', combined)):
        for identity in (0, 1):
            text = controller(image, identity, combined=mode == 'UI+a77')
            lua.append(dict(mode=mode, identity=identity,
                            SHA256=sha256(text.encode()).hexdigest(), bytes=len(text.encode())))
    return dict(passed=True, UI_only=ui_info, UI_plus_a77=combined_info,
                readonly_Lua=lua, output_files=0, native_qualified=False)


def streams(raw):
    import profile_bub_empty_native_1113 as Profile
    result = []
    for combined in (False, True):
        image = (combined_proposal if combined else proposal)(raw)[0]
        for identity in (0,1):
            text = controller(image,identity,combined=combined)
            proof = Profile.source_check(image,identity,lag_cut=True,
                controller_text=text,expected=sha256(image).hexdigest())
            receipt = proof['receipt']
            row = dict(mode='UI+a77' if combined else 'UI-only',
                name=('BUB','BOB')[identity], passed=proof['passed'],
                controller_SHA256=proof['controller_SHA256'],
                actual_CPU_scheduler_calls=proof['CPU_Main_NMI'],
                actual_busy_NMI_cut=proof['actual_busy_NMI_cut'],
                entered=receipt['entered_Main'],returned=receipt['Main_updates'],
                source=receipt['source_updates'],outside_pending=receipt['source_outside_pending'],
                returns=receipt['returned_Main_histogram'],terminal=receipt['terminal'])
            result.append(row)
            print(json.dumps(dict(event='readonly_stream_CPU',**row)),flush=True)
    return dict(passed=True,rows=result,output_files=0,
                natural_actor_position_health_ability_seeds=False,
                scope='Actual cold/menu then identical readonly Lua post-ingress controls; each campaign adds one real busy NMI to qualify catch-up. CPU scheduler counts are not physical cadence.')


def call(m, a=83, x=71, y=109, p=0x21, *, stop=(0x5b00,224)):
    m[0x16a], m[0x16c], m[0x16d] = a, ROW & 255, ROW >> 8
    c = B.N.NesMPU(memory=m, pc=B.W.address(m.bundle, 'FarCallCommon'))
    c.a, c.x, c.y, c.p, c.sp = 193, x, y, p, 224
    c.stPushWord(0x5aff)
    source = []
    for _ in range(500000):
        if (c.pc,c.sp) == stop:
            break
        bank = m.rawtags[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1
        if bank in (2, 3) and c.pc >= 0x8000:
            source.append((bank, c.pc, bytes(m[c.pc+i] for i in range(3)).hex()))
        assert m[c.pc], ('UI BRK', hex(c.pc), m.rawtags)
        c.step()
    else:
        raise AssertionError(('UI bound', hex(c.pc), m.rawtags))
    return c, source


def compare(a, z, ca, cz):
    assert (ca.a, ca.x, ca.y, ca.p & 0xef, ca.sp) == (cz.a, cz.x, cz.y, cz.p & 0xef, cz.sp)
    compare_data(a, z, ca, cz)


def compare_data(a, z, ca, cz):
    assert a.rawtags == z.rawtags
    assert bytes(a[:0x100]) == bytes(z[:0x100])
    assert bytes(a[0x200:0x8000]) == bytes(z[0x200:0x8000])
    assert bytes(a[0x15a:0x17b]) == bytes(z[0x15a:0x17b])
    assert bytes(a[0x101+ca.sp:0x200]) == bytes(z[0x101+cz.sp:0x200])
    assert a.ram == z.ram


def compare_except_dead_return(a, z, ca, cz):
    assert a.rawtags == z.rawtags and a.ram == z.ram
    assert bytes(a[:0x100]) == bytes(z[:0x100])
    assert bytes(a[0x200:0x8000]) == bytes(z[0x200:0x8000])
    assert bytes(a[0x15a:0x179]) == bytes(z[0x15a:0x179])
    assert a[0x17a] == z[0x17a]
    assert bytes(a[0x101+ca.sp:0x200]) == bytes(z[0x101+cz.sp:0x200])


def caller_delta(a, z, ca, cz, owner, incoming_p, *, poisoned=False):
    """Classify the retained callee negative; do not alter compare's oracle."""
    old = (ca.a, ca.x, ca.y, ca.p & 0xef, ca.sp)
    new = (cz.a, cz.x, cz.y, cz.p & 0xef, cz.sp)
    if old == new:
        compare(a, z, ca, cz)
        return 0
    if owner == 43 and poisoned:
        assert old[0:2] == (0, 0) and old[2] == new[2] and old[4] == new[4]
        assert old[3] & 0x2d == new[3] & 0x2d
        assert a[0x179] == ca.a and z[0x179] == cz.a
        compare_except_dead_return(a, z, ca, cz)
        return 1
    assert owner == 38 and old[:3] == new[:3] and old[4] == new[4]
    assert old[3] ^ new[3] == 0x40
    assert not old[3] & 0x40 and bool(new[3] & 0x40) == bool(incoming_p & 0x40)
    compare_data(a, z, ca, cz)
    return 1


def prince_role87(path):
    """Current compiled role87 has no mutable actor read or store."""
    assert path[0] == (2, 0xdf1e, '48ad79')
    assert path[-1] == (3, 0xbfad, '60684c')
    immediate = {0xe9, 0xc9}
    control = {0x48, 0x38, 0x90, 0xb0, 0xf0, 0xd0, 0x20, 0x60,
               0xea, 0x4c, 0x68, 0x18}
    reads = []
    for bank, pc, text in path:
        code = bytes.fromhex(text)
        op = code[0]
        if op == 0xad:
            operand = int.from_bytes(code[1:3], 'little')
            assert operand == 0x179
            reads.append(operand)
        else:
            assert op in immediate | control, (bank, hex(pc), text)
    assert reads == [0x179, 0x179]
    assert (3, 0xbdcb, 'c903d0') in path
    return dict(role=87, actual_source_instruction_count=len(path),
                sole_nonstack_data_reads=reads, actor_reads_or_writes=0,
                callee_V_is_cleared_by_role_SBC=True,
                path_SHA256=sha256(json.dumps(path).encode()).hexdigest())


def caller_closure(raw):
    """Bind current UI/RNG/score machine code and close every score CFG edge."""
    from py65.disassembler import Disassembler
    assert sha256(raw).hexdigest() == B.PIN
    bundle = B.W.Symbols.bundle()
    bundle['raw'] = raw
    def native(bank, pc, count):
        start = 16 + bank * 8192 + (pc & 8191)
        return raw[start:start+count]
    ui = bytes.fromhex('8d6a01089848a01d4c40b8')
    assert native(79, 0xb7d0, len(ui)) == ui
    rare = bytes.fromhex('088d6a019848a00e4c2aa2')
    assert native(124, 0xa4c6, len(rare)) == rare
    assert native(124, 0xa8c4, 3) == bytes.fromhex('4cc6a4')
    assert native(124, 0xa179, 23) == bytes.fromhex(
        '9818690f0a0a0a0a8d6c01a9b669008d6d01a9cf4c0da6')
    rare_bank = native(124,0xa000,8192)
    local_ui = [0xa000+i for i in range(8190) if rare_bank[i] in (0x20,0x4c)
                and rare_bank[i+1:i+3] == bytes.fromhex('c6a4')]
    assert local_ui == [0xa8c4]
    role14 = [0xa000+i for i in range(8188)
              if rare_bank[i:i+5] == bytes.fromhex('a00e4c2aa2')]
    assert role14 == [0xa4cc]
    # The exact API row14 is translated to high-bank slot29 (HuUi). These
    # operations are followed by the existing restore/three FRC return tails.
    rng = native(126, 0x82f3, 47)
    assert rng.hex() == ('ada007290285034da1072902c9016ea007a201a0067ea007e888d0f9ea'
                         '8d6a01a93f8d6c01a9b88d6d01a983205a01')
    memory = [0] * 65536
    memory[0x8000:0xa000] = native(126,0x8000,8192)
    memory[0xa000:0xc000] = native(3, 0xa000, 8192)
    cpu = B.N.NesMPU(memory=memory)
    decoder = Disassembler(cpu)
    pc = 0x82f3
    rng_ops = {0xad,0x29,0x85,0x4d,0xc9,0x6e,0xa2,0xa0,0x7e,
               0xe8,0x88,0xd0,0xea,0x8d,0xa9,0x20}
    while pc < 0x8322:
        op = memory[pc]
        assert op in rng_ops and op not in (0x50,0x70,0x08)
        size, text = decoder.instruction_at(pc)
        if op == 0x20:
            assert pc == 0x831f and memory[pc+1:pc+3] == [0x5a,0x01]
        pc += size
    assert pc == 0x8322
    assert native(3, 0xb83f, 10) == bytes.fromhex('208cb838adba07edae07')
    # The primary comparison may inspect/copy any score digits; all paths
    # return to unconditional SEC/LDA/SBC. Close its full branch graph,
    # including the zero-counter unconditional BEQ following LDY #0.
    pending, visited = [0xb88c], set()
    no_v_reads = {0x50, 0x70, 0x08}  # BVC, BVS, PHP
    allowed = {0xad, 0xcd, 0xd0, 0xf0, 0x90, 0xa2, 0xa0, 0xbd,
               0x99, 0xe8, 0xc8, 0xc0, 0x60}
    while pending:
        pc = pending.pop()
        if pc in visited:
            continue
        assert 0xb86f <= pc <= 0xb8c2
        visited.add(pc)
        op = memory[pc]
        assert op in allowed and op not in no_v_reads, (hex(pc), hex(op))
        size, text = decoder.instruction_at(pc)
        if op == 0x60:
            assert pc == 0xb88b
            continue
        if op in (0xd0, 0xf0, 0x90):
            delta = memory[pc+1]
            target = pc + 2 + (delta if delta < 128 else delta - 256)
            pending.append(target)
            if pc == 0xb8c2:
                assert native(3, 0xb8be, 6) == bytes.fromhex('a200a000f0ab')
            else:
                pending.append(pc+size)
        else:
            pending.append(pc+size)
    assert len(visited) == 37, sorted(visited)
    # This direct source bind explains the machine invariant; it is not used
    # instead of the actual compiled instruction assertions above.
    game = (B.R/'src/game.s').read_text()
    assert game.index('farcall X5BounceUiDispatch') < game.index('farcall UpdateTopScore')
    return dict(source_call_domain='Current shared UI role29 reached through NrUi role14/HuUi; normal and catch-up GameLoop execute the same fixed continuation.',
        high_UI_entry=0xb7d0, rare_UI_role=14, shared_UI_role=29,
        rare_UI_target_formula='B600 +16*(14+15) =B7D0',
        first_unconditional_V_overwrite=dict(physical_PRG=3, PC=0xb846, opcode='ed ae 07'),
        first_V_read_before_that=False, primary_score_CFG_instruction_PCs=len(visited),
        A_NZ_overwrite=0x82f3, X_overwrite_before_indexed_use=0x8304,
        dead_SMC_return_byte=0x179, return_byte_overwrite='Next real score farcall return, before LDA immediate at0178 consumes the new value',
        exact_RNG_farcall_bytes=len(rng),
        score_CFG_SHA256=sha256(b''.join(pc.to_bytes(2,'little')+bytes(memory[pc:pc+3])
                                     for pc in sorted(visited))).hexdigest(),
        scope='Source/compiled caller route and complete score-comparison CFG. End-to-end Main plus interrupt gates remain separate; the direct callee V negative is retained.')


def route_targets(raw):
    """All101 actual menu/confirm profiles, stopped before executing UI target."""
    import check_remaining_roster_starts_1110 as Inventory
    bundle = B.W.Symbols.bundle()
    bundle['raw'] = raw
    inventory = Inventory.inventory(raw)
    unique = {(row['slot'], row['raw'], row['name']): row for row in inventory['rows']}
    assert len(unique) == 101
    targets = []
    eligible = []
    for row in unique.values():
        old = B.N.Bus
        B.N.Bus = B.W.ControllerBus
        try:
            m = B.W.UI.seed(bundle, row['slot'])
        finally:
            B.N.Bus = old
        for _ in range(row['cycle']):
            B.W.UI.key(m, 32)
        assert B.W.UI.menu_name(m)[0] == row['name']
        start = B.W.UI.key(m, 16)
        B.N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue',
                   a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
        owner = B.N.get(m, 'SelectedCharacter')
        m[0x16a], m[0x16c], m[0x16d] = 83, 0xd0, 0xb7
        c = B.N.NesMPU(memory=m, pc=B.W.address(bundle, 'FarCallCommon'))
        c.a, c.x, c.y, c.p, c.sp = 207, 71, 109, 0x21, 224
        c.stPushWord(0x5aff)
        seen = False
        target = None
        for _ in range(10000):
            if c.pc == 0x5b00:
                break
            if c.pc == 0xb7d0 and m.rawtags[1] == 207:
                seen = True
            if seen and c.pc == 0x15d:
                target = (m[0x162], m[0x16c]+256*m[0x16d])
                break
            assert m[c.pc], ('routing BRK', row['name'], hex(c.pc), m.rawtags)
            c.step()
        else:
            raise AssertionError(('routing bound', row['name'], hex(c.pc)))
        assert seen
        item = dict(name=row['name'], owner=owner, target=target)
        targets.append(item)
        if target == (193, ROW):
            eligible.append(item)
    assert {q['owner'] for q in eligible} == {37,38,39,40,42,43}, dict(eligible=eligible,
        shared_owners=[q for q in targets if q['owner'] in (37,38,39,40,41,42)])
    assert len(eligible) == 8, eligible
    return dict(passed=True, actual_menu_confirm_profiles=len(targets),
        shared_row29_eligible=eligible,
        every_other_profile_excludes_changed_UI_vector=True,
        target_histogram={str(target):sum(q['target']==target for q in targets)
                          for target in {q['target'] for q in targets}},
        scope='Actual native menu Select/confirm plus immutable UI front-door classification; stops before target execution, not 101 active-stage claims.',
        output_files=0)


def census(raw):
    image = fixture_image(raw)
    bundle = B.W.Symbols.bundle()
    bundle['raw'] = raw
    results = []
    for row in ROWS:
        opening, seed = Roster.cold(bundle, row)
        pair = [clone(seed), clone(seed)]
        pair[1].bundle = dict(pair[1].bundle, raw=image)
        old, old_source = call(pair[0])
        new, new_source = call(pair[1])
        try:
            compare(*pair, old, new)
            equal = True
        except AssertionError:
            equal = False
        results.append(dict(name=row['name'], selected=B.N.get(seed, 'SelectedCharacter'),
            active_opening=opening, original_source_instructions=old_source,
            fixture_source_instructions=new_source, returned_old=[old.a,old.x,old.y,old.p,old.sp],
            returned_fixture=[new.a,new.x,new.y,new.p,new.sp],
            complete_ABI_state_equal=equal, CPU_saved=old.processorCycles-new.processorCycles))
        print(json.dumps(results[-1]), flush=True)
    return dict(passed=all(q['complete_ABI_state_equal'] for q in results), cases=results,
        fixture_only=True, production_proposal=False, output_files=0)


def direct(raw, *, caller_contract=False):
    image = fixture_image(raw)
    bundle = B.W.Symbols.bundle()
    bundle['raw'] = raw
    rows = []
    seeds = {}
    for row in ROWS:
        opening, seed = Roster.cold(bundle, row)
        owner = B.N.get(seed, 'SelectedCharacter')
        seeds[owner] = seed
        pair = [clone(seed), clone(seed)]
        pair[1].bundle = dict(pair[1].bundle, raw=image)
        source_path = None
        flags_cases = a_cases = header_cases = 0
        parent_source_on_poison = 0
        classified_dead_V_differences = 0
        cost = set()
        for flags in range(256):
            for regs in ((0, 0, 0), (83, 71, 109), (255, 255, 255)):
                a, z = [call(m, *regs, p=flags) for m in pair]
                if caller_contract:
                    classified_dead_V_differences += caller_delta(*pair, a[0], z[0], owner, flags)
                else:
                    compare(*pair, a[0], z[0])
                if source_path is None:
                    source_path = a[1]
                assert a[1] == source_path and not z[1]
                cost.add(a[0].processorCycles-z[0].processorCycles)
                flags_cases += 1
        for value in range(256):
            a, z = [call(m, a=value, p=0x61) for m in pair]
            if caller_contract:
                classified_dead_V_differences += caller_delta(*pair, a[0], z[0], owner, 0x61)
            else:
                compare(*pair, a[0], z[0])
            assert a[1] == source_path
            a_cases += 1
        for bank in (2, 3):
            for byte in range(16):
                for m in pair:
                    m.ram[bank][0x1fe0+byte] ^= 1
                for flags in (0, 0x21, 0x60, 0x65, 0xa5, 0xff):
                    a, z = [call(m, p=flags) for m in pair]
                    if caller_contract:
                        classified_dead_V_differences += caller_delta(
                            *pair, a[0], z[0], owner, flags, poisoned=True)
                    else:
                        compare(*pair, a[0], z[0])
                    # Some inherited owner-specific empty-vector paths do
                    # execute their literal no-op under a poisoned header.
                    # Compare that actual behavior, without claiming a full
                    # fail-closed oracle for the old conditional loaders.
                    assert not z[1]
                    parent_source_on_poison += bool(a[1])
                    header_cases += 1
                for m in pair:
                    m.ram[bank][0x1fe0+byte] ^= 1
        rows.append(dict(owner=owner, name=row['name'], valid_flags_register_cases=flags_cases,
            all_A_cases=a_cases, invalid_header_cases=header_cases,
            parent_RAM_execution_on_poison=parent_source_on_poison,
            classified_dead_return_differences=classified_dead_V_differences,
            source_UI_PC_path=source_path, CPU_saved=sorted(cost),
            source_RAM3_SHA256=sha256(bytes(seed.ram[3][:0x1fe0])).hexdigest()))
        print(json.dumps(dict(event='owner_UI_ABI', **{k:v for k,v in rows[-1].items()
                        if k != 'source_UI_PC_path'})), flush=True)
        if owner == 38:
            role = prince_role87(source_path)
        else:
            assert {bytes.fromhex(text)[0] for bank,pc,text in source_path} <= {0x4c,0x18,0x60}
            assert source_path[-2][2].startswith('18') and source_path[-1][2].startswith('60')
    foreign = 0
    foreign_negatives = []
    base = seeds[39]
    # Directed out-of-domain public-row calls retain their exact old rejection.
    # Each registered owner above instead uses its genuine cold-mounted image.
    for owner in range(256):
        if owner in seeds:
            continue
        pair = [clone(base), clone(base)]
        pair[1].bundle = dict(pair[1].bundle, raw=image)
        for m in pair:
            B.N.put(m, SelectedCharacter=owner)
        for flags in (0, 0x21, 0x60, 0xa5, 0xff):
            a, z = [call(m, p=flags) for m in pair]
            try:
                compare(*pair, a[0], z[0])
            except AssertionError:
                if not caller_contract:
                    raise
                foreign_negatives.append(dict(owner=owner, p=flags,
                    old=[a[0].a,a[0].x,a[0].y,a[0].p,a[0].sp],
                    new=[z[0].a,z[0].x,z[0].y,z[0].p,z[0].sp]))
            foreign += 1
    return dict(passed=True, parent_SHA256=B.PIN, fixture_SHA256=sha256(image).hexdigest(),
        owners=rows, out_of_domain_identity_cases=foreign,
        out_of_domain_direct_negative_count=len(foreign_negatives),
        out_of_domain_direct_negative_examples=foreign_negatives[:8],
        out_of_domain_direct_negative_SHA256=sha256(json.dumps(foreign_negatives).encode()).hexdigest(),
        actual_foreign_route_exclusion_required=bool(foreign_negatives),
        prince_role87=role, direct_ABI_oracle_unchanged=True,
        direct_callee_ABI_exact=not caller_contract,
        actual_caller_liveness_required=caller_contract,
        caller_closure=caller_closure(raw) if caller_contract else None,
        actual101_front_door=route_targets(raw) if caller_contract else None,
        new_native_code_bytes=5, new_native_storage=0,
        direct_return_deltas_explicitly_classified=True,
        direct_other_native_and_source_RAM_equal=True,
        source_only=True, output_files=0)


def main_pairs(raw, count=20):
    """Complete unmodified cold/menu/Main/NMI on each loaded UI owner."""
    image = fixture_image(raw)
    result = []
    for row in ROWS:
        models, openings = [], []
        for candidate in (raw, image):
            bundle = B.W.Symbols.bundle()
            bundle['raw'] = candidate
            opening, model = Roster.cold(bundle, row)
            models.append(model)
            openings.append(opening)
        assert openings[0] == openings[1]
        cycles = []
        for epoch in range(count):
            pad = (0 if epoch < 4 else 1 if epoch < 10 else 64 if epoch < 16 else 0)
            cpu = []
            totals = []
            for model in models:
                model.controller_pad = pad
                observed = []
                totals.append(B.frame(model, lambda _m, c: observed.__setitem__(slice(None), [c])))
                cpu.append(observed[0])
            compare(*models, *cpu)
            cycles.append(totals[0]-totals[1])
        result.append(dict(name=row['name'], actual_cold_and60opening_equal=True,
                           complete_additional_Main_NMI=count, CPU_saved=[min(cycles),max(cycles)],
                           terminal=B.state(models[1])))
        print(json.dumps(dict(event='whole_Main_pair', **result[-1])), flush=True)
    return dict(passed=True, models=result, exact_full_Main_AXYP_SP_all_RAM_SMC_maps=True,
                direct_callee_V_negative_retained=True, output_files=0)


def fault_liveness(raw):
    """Declared Sonic header-fault UI returns through the real RNG/score code."""
    image = fixture_image(raw)
    cut_count = {'IRQ': 0, 'busy_NMI': 0}
    lowest = 255
    results = []
    for name in ('SONIC', 'SUPER SONIC'):
        bundle = B.W.Symbols.bundle()
        bundle['raw'] = raw
        opening, seed = Roster.cold(bundle, next(q for q in ROWS if q['name'] == name))
        pair = [clone(seed), clone(seed)]
        pair[1].bundle = dict(pair[1].bundle, raw=image)
        for model in pair:
            model.ram[2][0x1fe0] ^= 1
            B.N.put(model, NmiDisable=255)
        cpu = [call(model, p=0x61, stop=(0x16e,221))[0] for model in pair]
        assert (cpu[0].a, cpu[0].x) == (0, 0)
        assert (cpu[1].a, cpu[1].x) == (83, 71)
        compare_except_dead_return(*pair, *cpu)
        # This is explicitly a native continuation ABI fixture. No actor,
        # position, health, weapon or stage state is supplied. Both CPUs now
        # execute the exact GameLoop continuation after its UI returns.
        cut_contexts = set()
        def finish(models, cpus):
            for _ in range(20000):
                assert (cpus[0].pc, cpus[0].sp) == (cpus[1].pc, cpus[1].sp)
                if (cpus[0].pc,cpus[0].sp) == (0x5b00,224):
                    for c in cpus:
                        c.pc = 0x82f3
                    continue
                if (cpus[0].pc, cpus[0].sp) == (0x8322, 224):
                    compare(*models, *cpus)
                    return
                for model, c in zip(models, cpus):
                    assert model[c.pc], ('fault continuation BRK', hex(c.pc))
                    c.step()
            raise AssertionError('fault continuation bound')
        for _ in range(20000):
            a, z = cpu
            assert (a.pc, a.sp) == (z.pc, z.sp)
            if (a.pc,a.sp) == (0x5b00,224):
                for c in cpu:
                    c.pc = 0x82f3
                continue
            if (a.pc, a.sp) == (0x8322, 224):
                compare(*pair, *cpu)
                break
            pending = (a.a,a.x,a.p & 0xef,pair[0][0x179]) != (z.a,z.x,z.p & 0xef,pair[1][0x179])
            key = (a.pc,a.sp,tuple(pair[0].rawtags))
            if pending and key not in cut_contexts:
                cut_contexts.add(key)
                for kind in ('IRQ', 'busy_NMI'):
                    if kind == 'IRQ' and a.p & 4:
                        continue
                    copies = [clone(model,c) for model,c in zip(pair,cpu)]
                    models = [q[0] for q in copies]
                    cpus = [q[1] for q in copies]
                    cycles = []
                    for model, c in zip(models,cpus):
                        regs = (c.pc,c.sp,c.a,c.x,c.y,c.p & 0xef)
                        before_maps = model.rawtags[:]
                        start = c.processorCycles
                        c.irq() if kind == 'IRQ' else c.nmi()
                        for _ in range(200000):
                            lowest = min(lowest,c.sp)
                            if (c.pc,c.sp) == regs[:2]:
                                break
                            assert model[c.pc], ('fault ISR BRK',kind,hex(c.pc))
                            c.step()
                        else:
                            raise AssertionError(('fault ISR bound',kind))
                        assert (c.pc,c.sp,c.a,c.x,c.y,c.p & 0xef) == regs
                        if model.rawtags != before_maps:
                            # Exact existing SMC pending-STA exception only.
                            # Execution remains in RAM through the pending
                            # store and its next instruction before any fetch
                            # from the newly selected PRG window.
                            assert c.pc in (0x166,0x175)
                            assert bytes(model[c.pc:c.pc+3]) == bytes.fromhex('8d1551')
                            assert c.a == B.N.get(model,'CurrentBank') == model.rawtags[1]
                            assert model.rawtags[0] == before_maps[0]
                            assert model.rawtags[2:] == before_maps[2:]
                            assert c.pc+3 in (0x169,0x178)
                        cycles.append(c.processorCycles-start)
                    assert cycles[0] == cycles[1]
                    compare_except_dead_return(*models,*cpus)
                    # Any permanent ISR backup of the differing return byte
                    # would fail here or at the real score return below.
                    finish(models,cpus)
                    cut_count[kind] += 1
            for model,c in zip(pair,cpu):
                assert model[c.pc], ('fault foreground BRK',hex(c.pc))
                c.step()
        else:
            raise AssertionError('fault path bound')
        results.append(dict(name=name, declared_header_fault='RAM2 headerbyte0 XOR1',
            actual_UI_FRC_return_tail=[0x16e,0x17a],
            fixture_only_native_continuation=[0x82f3,0x8322],
            actual_dead_value_contexts=len(cut_contexts), final_full_state_equal=True))
    assert lowest >= 0x7b
    return dict(passed=True, cases=results, paired_ISR_cuts=cut_count,
                minimum_ISR_SP=lowest, output_files=0,
                scope='Cold-derived declared header-fault UI/continuation ABI fixtures, not naturally corrupted gameplay. Every differing A/X/NZ/V/SMC179 interval is cut with actual IRQ/busy-NMI; complete state and P converge at real score return8322.')


def interrupts(raw, *, combined=False):
    """Actual new native PCs: rendered busy-NMI/IRQ and Prince V0/V1 pairs."""
    if combined:
        import bub_empty_loops_1113 as Empty
        reference_raw = Empty.proposal(raw)[0]
        image = combined_proposal(raw)[0]
        cases = [row for row in ROWS if row['name'] in ('BUB','BOB')]
    else:
        reference_raw = raw
        image = fixture_image(raw)
        cases = ROWS
    wanted = {ROW, SHIM, SHIM+1, SHIM+2, LEAF, LEAF+3, LEAF+4}
    seen = set()
    counts = {'IRQ': 0, 'busy_NMI': 0}
    lowest = 255
    v_pairs = 0
    for row in cases:
        bundle = B.W.Symbols.bundle()
        bundle['raw'] = image
        opening, m = Roster.cold(bundle, row)
        owner = B.N.get(m, 'SelectedCharacter')
        if owner in (37, 41, 42, 43):
            # These current Main paths return higher in the UI pipeline.
            # The exact public-row fixture still qualifies their native path.
            m[0x16a], m[0x16c], m[0x16d] = 83, ROW & 255, ROW >> 8
            c = B.N.NesMPU(memory=m, pc=B.W.address(bundle, 'FarCallCommon'))
            c.a, c.x, c.y, c.p, c.sp = 193, 71, 109, 0x21, 224
            c.stPushWord(0x5aff)
            stop = (0x5b00, 224)
            directed = True
        else:
            B.N.consume(m)
            c = B.N.NesMPU(memory=m, pc=B.W.address(bundle, 'IdleLoop'))
            c.sp, c.p = 255, 0x31
            c.stPushWord(0xe33b)
            stop = (B.W.address(bundle, 'IdleLoop')+12, 252)
            directed = False
        B.N.put(m, NmiDisable=255)
        def vector(q, d, kind):
            nonlocal lowest
            regs = (d.pc, d.sp, d.a, d.x, d.y, d.p & 0xef)
            live = bytes(q[0x101+d.sp:0x200])
            maps = q.rawtags[:]
            skipped = B.N.get(q, 'NmiSkipped')
            reference, rc = clone(q, d)
            reference.bundle = dict(reference.bundle, raw=reference_raw)
            starts = []
            for model, cpu in ((q,d), (reference,rc)):
                starts.append(cpu.processorCycles)
                cpu.irq() if kind == 'IRQ' else cpu.nmi()
                for _ in range(200000):
                    lowest = min(lowest, cpu.sp)
                    if (cpu.pc, cpu.sp) == regs[:2]:
                        break
                    assert model[cpu.pc], ('UI ISR BRK', kind, hex(cpu.pc))
                    cpu.step()
                else:
                    raise AssertionError(('UI ISR bound', kind))
                assert (cpu.pc, cpu.sp, cpu.a, cpu.x, cpu.y, cpu.p & 0xef) == regs
            # Foreign music is allowed to advance exactly as on the actual
            # parent, rather than freezing Bub's three specific sound clocks.
            compare(q, reference, d, rc)
            assert d.processorCycles-starts[0] == rc.processorCycles-starts[1]
            assert q.rawtags == maps
            assert bytes(q[0x101+d.sp:0x200]) == live
            assert B.N.get(q, 'NmiSkipped') == (skipped+(kind == 'busy_NMI')) & 255
            return q, d
        for _ in range(500000):
            if (c.pc, c.sp) == stop:
                break
            bank = m.rawtags[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1
            if bank == 193 and c.pc in wanted:
                key = (row['name'], c.pc, directed)
                if key not in seen:
                    seen.add(key)
                    for kind in ('IRQ', 'busy_NMI'):
                        if kind == 'IRQ' and c.p & 4:
                            continue
                        q, d = clone(m, c)
                        vector(q, d, kind)
                        counts[kind] += 1
                        if owner == 38:
                            # The only direct-ABI delta is V. Test the actual
                            # ISR with both V values before its caller kills V;
                            # no P oracle is weakened in vector().
                            z, e = clone(m, c)
                            e.p ^= 0x40
                            vector(z, e, kind)
                            compare_data(q, z, d, e)
                            assert (d.a,d.x,d.y,d.sp) == (e.a,e.x,e.y,e.sp)
                            assert d.p ^ e.p == 0x40
                            assert d.processorCycles == e.processorCycles
                            v_pairs += 1
            assert m[c.pc], ('UI foreground BRK', row['name'], hex(c.pc))
            c.step()
        else:
            raise AssertionError(('UI foreground bound', row['name'], hex(c.pc)))
    assert {pc for name,pc,directed in seen} == wanted
    assert lowest >= 0x7b
    return dict(passed=True, actual_native_PCs=len(wanted), contexts=len(seen),
                vectors=counts, Prince_V0_V1_actual_ISR_pairs=v_pairs,
                minimum_ISR_SP=lowest, output_files=0,
                combined_with_a77=combined,
                scope='Actual new native opcode IRQ/rendered busy-NMI. Bub/Bob/DK/Prince cuts occur in whole Main; the higher-return owners use explicitly directed public-row fixtures. Registers/full incoming P, maps and live stack are preserved; complete app results and cycles match actual parent ISR including foreign audio progress. Paired Prince V inputs have identical handler cycles/app effects.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--direct', action='store_true')
    p.add_argument('--caller-contract', action='store_true')
    p.add_argument('--caller-closure', action='store_true')
    p.add_argument('--route-targets', action='store_true')
    p.add_argument('--main-pairs', action='store_true')
    p.add_argument('--interrupts', action='store_true')
    p.add_argument('--bindings', action='store_true')
    p.add_argument('--fault-liveness', action='store_true')
    p.add_argument('--combined-interrupts', action='store_true')
    p.add_argument('--streams', action='store_true')
    a = p.parse_args()
    result = (streams(B.ROM.read_bytes()) if a.streams else
              interrupts(B.ROM.read_bytes(), combined=True) if a.combined_interrupts else
              fault_liveness(B.ROM.read_bytes()) if a.fault_liveness else
              bindings(B.ROM.read_bytes()) if a.bindings else
              interrupts(B.ROM.read_bytes()) if a.interrupts else
              main_pairs(B.ROM.read_bytes()) if a.main_pairs else
              route_targets(B.ROM.read_bytes()) if a.route_targets else
              caller_closure(B.ROM.read_bytes()) if a.caller_closure else
              direct(B.ROM.read_bytes(), caller_contract=a.caller_contract)
              if a.direct or a.caller_contract else census(B.ROM.read_bytes()))
    print(json.dumps(result, separators=(',', ':')))
