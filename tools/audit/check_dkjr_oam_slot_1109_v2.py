"""Exercise actual cold raw40 render and finite whole-ring OAM ownership."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import prepare_dkjr_oam_slot_1109_v1 as P

I, N, F, OUT = P.I, P.N, P.F, P.OUT


def direct(m, pc, a=0x87, x=7, y=0x17, p=0x71):
    c = N.NesMPU(memory=m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = a, x, y, p, 224
    c.stPushWord(0x5aff)
    for _ in range(5000):
        if c.pc == 0x5b00:
            break
        assert m[c.pc], (hex(c.pc), c.sp)
        c.step()
    else:
        raise AssertionError(('DK render bound', hex(c.pc)))
    assert (c.a, c.x, c.y, c.p & 254, c.sp) == (a, x, y, p & 254, 224)
    return c.p & 1, c.processorCycles


def packet(m):
    src = m.ram[2]
    return [bytes((src[i], src[i+1] | 1, src[i+2] & 0xe0 | 3, src[i+3])) for i in range(0x210, 0x230, 8)]


def oam_image(seed, rows, cursor, rotation):
    out = bytearray(seed)
    for i, row in enumerate(rows):
        at = (cursor + rotation + i*4) & 255
        out[at:at+4] = row
    return bytes(out)


def focused(b, code, labels):
    observed = json.loads(P.TRACE.read_text())['body']['first']['source_oam']
    original = bytes(observed[str(i)] for i in range(32))
    start = bytes((i*13+41)&255 for i in range(256))
    m = N.Bus(b)
    m.raw_page(1, 3)
    m.raw_page(2, 2)
    m.ram[3][:len(code)] = code
    m.ram[2][0x8fe] = 2
    body_pc, draw_pc = labels['DkjrNativeDrawBody'], labels['DkNativeDraw']
    count = Counter()

    def init(cursor, active, rotation):
        m.writes.clear()
        m.ram_writes.clear()
        m.ram[2][0x210:0x230] = original
        m[0x200:0x300] = start
        N.put(m, CurrentOAMOffset=cursor, GuestOamRotationActive=active, RgOamRotation=rotation)

    def compare(pc, cursor, rotate, rows, accepted):
        before = bytes(m.ram[2])
        regs = bytes(m[3:11]), bytes(m[0x15a:0x17b]), tuple(m.rawtags)
        c, cycles = direct(m, pc)
        assert c == accepted and N.get(m, 'CurrentOAMOffset') == cursor + 4*len(rows), (pc, cursor, rotate, rows, c)
        after = bytearray(m.ram[2])
        scratch = [0x8fa] if pc == body_pc else [0x8fa, 0x8db, 0x8dd, 0x8e8, 0x8ea, 0x8ec]
        for at in scratch:
            after[at] = before[at]
        assert before == after
        assert regs == (bytes(m[3:11]), bytes(m[0x15a:0x17b]), tuple(m.rawtags))
        assert bytes(m[0x200:0x300]) == oam_image(start, rows, cursor, rotate), (pc, cursor, rotate, rows)
        assert N.get(m,'ObjectMetasprite') == 0 and (N.get(m,'SmPosePtr') + 256*N.get(m,'SmPosePtr',1)) == I.UI.address(b, 'ObjectMetasprite')
        return cycles

    for cursor, rotate, active in product(range(256), [0, 1, 3, 4, 124, 236, 248, 252, 255], [0, 1]):
        init(cursor, active, rotate)
        accepted = cursor < 240 and not cursor & 3 and (not active or not rotate & 3)
        rows = packet(m) if accepted else []
        compare(body_pc, cursor, rotate if active else 0, rows, accepted)
        count['all_cursor_values_rotation_boundary_and_alignment'] += 1
    for rotate in range(256):
        init(0, 1, rotate)
        accepted = not rotate & 3
        compare(body_pc, 0, rotate, packet(m) if accepted else [], accepted)
        count['all_rotation_values_initial_zero'] += 1
    for corrupt, v in [(0, 240), (1, 1), (1, 88), (4, 198), (5, 31), (6, 2), (7, 33), (2, 0x81), (6, 0x81)]:
        init(0, 1, 252)
        m.ram[2][0x210+corrupt] = v
        compare(body_pc, 0, 252, [], False)
        count['malformed_source_no_oam_write'] += 1
    # An authentic initial body, a hanging fruit, a falling fruit and a hit
    # tile share the same rotation and remaining logical capacity. The old
    # code allowed the last entry to publish zero; this cannot happen now.
    for cursor, rotation, kind in product(range(0,256,4), [0, 4, 124, 248, 252], range(3)):
        init(cursor, 1, rotation)
        m.ram[2][0x200:0x210] = bytes([255])*16
        m.ram[2][0x230:0x300] = bytes([255])*208
        m.ram[2][0x9a] = 1
        m.ram[2][0x434] = 1
        m.ram[2][0x42c] = 0xa4 + 4*kind
        m.ram[2][0x420] = 96
        m.ram[2][0x428] = 80
        m.ram[2][0x8d] = 0 if kind == 0 else 2
        m.ram[2][0x230:0x238] = bytes([80,0xa4+4*kind,0,112,88,0xa5+4*kind,0,112])
        m.ram[2][0x238:0x240] = bytes([80,0xa6+4*kind,0,120,88,0xa7+4*kind,0,120])
        m.ram[2][0x2c0:0x2c4] = bytes([80,0x90+kind,1,152])
        rows = packet(m) if cursor < 240 else []
        rows += [bytes([79,89+4*kind,2 if kind==0 else 1,96]),
                 bytes([79,91+4*kind,2 if kind==0 else 1,104]),
                 bytes([80,129+4*kind,2,112]), bytes([80,131+4*kind,2,120]),
                 bytes([80,141+2*kind,3,152])]
        compare(draw_pc, cursor, rotation, rows[:(252-cursor)//4], True)
        count['full_body_fruit_and_hit_cells_at_every_aligned_cursor'] += 1
    return dict(count)


def native_gamecore(raw, cookie, labels):
    cpu, invoke = N.NesMPU, N.invoke
    point = labels['DkNativeDraw']
    counts = Counter()
    snapshots = []
    active = False
    entry = None
    result = []

    class Trace(cpu):
        def step(self):
            nonlocal entry
            m = self.memory
            if active and m.rawtags[1] == 3 and m.ram[2][0x8fe] == 2:
                if self.pc == point:
                    logical = N.get(m, 'CurrentOAMOffset')
                    rotation = N.get(m, 'RgOamRotation') if N.get(m, 'GuestOamRotationActive') else 0
                    entry = logical, rotation, packet(m)
                    counts['native_row2_entry'] += 1
                    counts['native_initial_zero'] += logical == 0
                elif self.pc == point + 3:
                    logical, rotation, rows = entry
                    valid = m.ram[2][0x8fa] == 1
                    assert valid and N.get(m, 'CurrentOAMOffset') == logical + 16, (entry, valid)
                    slots = [((logical+rotation+4*i)&255, row) for i, row in enumerate(rows)]
                    assert all(bytes(m[0x200+at:0x204+at]) == row for at, row in slots)
                    result.append(slots)
                    counts['logical_reservation_physical_8x16_pairs'] += 1
                    if len(snapshots) < 3:
                        snapshots.append([logical, rotation, [[at, row.hex()] for at, row in slots]])
            return super().step()

    def record(memory, name, *args, **kwargs):
        nonlocal active
        active = name == 'GameCoreRoutine'
        result.clear()
        try:
            z = invoke(memory, name, *args, **kwargs)
            if active and result:
                assert len(result) == 1
                # Enemies, native OAM clear, and later tail work must leave the
                # actual private body slots intact in the final DMA staging.
                for at, row in result[0]:
                    assert bytes(memory[0x200+at:0x204+at]) == row, ('Later native OAM overwrite', at, row)
                counts['actual_full_GameCore_retains_body_at_DMA_source'] += 1
            return z
        finally:
            active = False

    N.NesMPU, N.invoke = Trace, record
    try:
        profile = I.cpu(raw, cookie)
    finally:
        N.NesMPU, N.invoke = cpu, invoke
    assert counts['native_initial_zero'] and counts['actual_full_GameCore_retains_body_at_DMA_source'] > 50
    return dict(witnesses=dict(counts), first_native_slots=snapshots, controls=profile['controls'],
                source_anchor=profile['source_anchor'], cold_init_min_SP=profile['init_min_SP'])


def main():
    manifest_path = OUT/'oam-source.json'
    q = json.loads(manifest_path.read_text())
    original = P.PRIVATE.read_bytes()
    new = P.compose(original, q['patches'])
    assert P.sha(original) == P.PIN and P.sha(new) == q['memory_only_hashes'][P.PIN]
    b = I.SYMBOLS.bundle()
    b['raw'] = new
    counts = focused(b, (OUT/'new-linked.bin').read_bytes(), q['labels'])
    print('Capacity and whole OAM comparison', counts, flush=True)
    actual = native_gamecore(new, bytes.fromhex(q['patches'][-1]['new_hex']), q['labels'])
    print('Native draw and DMA source', actual['witnesses'], flush=True)
    receipt = dict(passed=True, CPU_only=True, ROM_written=False, base_SHA256=P.PIN,
                   memory_only_SHA256=P.sha(new), whole_OAM_cases=counts, actual_native=actual,
                   scope='Real cold InitScreen/Fresh/entrance and full controller-driven GameCore fixtures. Whole OAM compares exact reserved slot bytes and all untouched sprites. Physical DMA/video still needs root native replay.',
                   bindings={str(p):P.sha(p.read_bytes()) for p in [Path(__file__), manifest_path, Path(P.__file__),
                             P.TRACE, P.R/'src/metasprite_engine.s', P.R/'src/hot_render_gate.s']})
    (OUT/'oam-CPU.json').write_text(json.dumps(receipt, indent=2)+'\n')


if __name__ == '__main__':
    main()
