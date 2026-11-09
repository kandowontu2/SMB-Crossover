"""Verify live farcall operand copies around the f33 side precheck."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_shared_draw_retarget_irq_1110 as Audio
import check_shared_side_tank_precheck_1110 as Side
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_native_relative_offscreen_irq_1110 import StackGuard


R, N, SHA = Side.R, Side.N, Side.SHA
SAVED, SHADOW = Audio.SAVED, Audio.SHADOW


def rebind(raw, proof):
    assert proof['passed'] and proof['parent_SHA256'] == SHA(raw)
    for row in proof['patches']:
        at = row['file_offset']
        old, new = (bytes.fromhex(row[k]) for k in ('old_hex', 'new_hex'))
        assert len(old) == len(new) and raw[at:at + len(old)] == old
        raw = raw[:at] + new + raw[at + len(old):]
    assert SHA(raw) == proof['expected_memory_only_SHA256']
    return raw


def qualify(before, after):
    images = [Side.W.bundle(raw) for raw in (before, after)]
    sites = Audio.copies(before)
    assert Audio.copies(after) == sites
    counts, minima, deepest = Counter(), [255, 255], {}

    def paired(c, kind, role, nested=False):
        outcomes = []
        for i, image in enumerate(images):
            z = fork(c, image)
            m = z.memory
            transfers = []
            pending = None

            def visit(q):
                nonlocal pending
                minima[1] = min(minima[1], q.sp)
                point = Side.ISR.point(q)
                if pending is not None:
                    target, destination, value = pending
                    assert point == target and q.a == value
                    transfers.append((point, destination, value))
                    pending = None
                if point in sites:
                    source, destination = sites[point]
                    pending = ((point[0], point[1] + 3), destination, m[source])
                if kind == 'FF' and i == 0 and not q.p & 4:
                    key = (role, point)
                    if key not in deepest or q.sp < deepest[key].sp:
                        saved = fork(q)
                        saved.memory.vector_floor = None
                        deepest[key] = saved

            m.vector_floor, m.written_stack = 0x100 + z.sp, set()
            Side.ISR.vector(z, kind, visit)
            m.vector_floor = None
            assert pending is None
            writes = [(at, value) for at, value in m.writes if at in SHADOW]
            assert writes == [(at, value) for _, at, value in transfers if at in SHADOW]
            assert bytes(m[a] for a in SAVED) == bytes(c.memory[a] for a in SAVED)
            outcomes.append((semantic(z), tuple(m.writes), tuple(transfers)))
        assert outcomes[0] == outcomes[1], (role, kind, Side.ISR.point(c))
        counts[role, 'nested_IRQ' if nested else kind] += 1
        counts[role, 'shadow_writes'] += sum(at in SHADOW for _, at, _ in outcomes[0][-1])

    def trace(c, role):
        side_depth = None
        seen = set()

        def watch(q):
            nonlocal side_depth
            tag, pc = Side.ISR.point(q)
            if side_depth is not None and q.sp > side_depth:
                side_depth = None
            if (tag, pc) == (254, Side.SIDE):
                side_depth = q.sp
            relevant = tag == 161 and Side.LO <= pc < Side.HI or tag == 156 and 0xbfb0 <= pc < 0xbfe7
            transport = side_depth is not None and tag == 0 and 0x15a <= pc < 0x17b
            key = tag, pc, q.sp, q.p & 4
            if not (relevant or transport) or key in seen:
                return
            seen.add(key)
            minima[0] = min(minima[0], q.sp)
            paired(q, 'FF', role)
            if not q.p & 4:
                paired(q, 'IRQ', role)

        Side.W.run(c, Side.done, watch)
        assert seen

    original_bus = N.Bus
    N.Bus = StackGuard
    try:
        for index, image in enumerate(images):
            side = 'old' if index == 0 else 'new'
            for raw in (2, 3):
                m = Side.W.cold(image, raw)
                Side.W.Match.controls(m, 0)
                trace(Side.cpu_at(m, Side.W.P.address(image, 'GameLoop'), a=0, x=0, y=0),
                      f'{side}_opening_{raw}')
            rogue = Side.W.cold(image, 2, True)
            for _ in range(4):
                N.consume(rogue)
            c = Side.new_leaf(rogue, 2, 0, 8, 17, 40, 176, 0x54, 0x21)
            assert c.memory[0x5fee] == 1
            trace(c, f'{side}_rogue_live_audio')
            tank = Side.Tank.cold(image, 0)
            # Rebind the existing genuine cold Tank cartridge into the same
            # stack model for the source-authenticated side leaf.
            m = list.__new__(StackGuard)
            list.extend(m, list.__iter__(tank))
            vars(m).update(vars(tank))
            trace(Side.new_leaf(m, 0, 7, 8, 17, 253, 191, 0x54, 0x21),
                  f'{side}_authenticated_Tank')
    finally:
        N.Bus = original_bus

    for (role, _), c in deepest.items():
        paired(c, 'IRQ', role, nested=True)
    assert all(counts[role, 'shadow_writes'] for role in ('old_rogue_live_audio', 'new_rogue_live_audio'))
    return dict(cases=[[role, kind, n] for (role, kind), n in sorted(counts.items())],
                minimum_SP=minima, ordered_hardware_and_shadow_exact=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    proof_path = out / 'proof.json'
    proof = json.loads(proof_path.read_text())
    before = Side.BASE.read_bytes()
    after = rebind(before, proof)
    result = qualify(before, after)
    result.update(passed=True, parent_SHA256=SHA(before), expected_memory_only_SHA256=SHA(after),
                  bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                            (Path(__file__), Path(Audio.__file__), proof_path)})
    (out / 'shadow.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
