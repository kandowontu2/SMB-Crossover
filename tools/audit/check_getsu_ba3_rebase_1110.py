"""Rebase Getsu's qualified source onto ba3 and check the combined live paths."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_getsu_empty_services_1110 as Empty
import check_shared_side_tank_precheck_1110 as Side
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


R, O, S, H, N, W, SHA = Empty.R, Empty.O, Empty.S, Empty.H, Empty.N, Empty.W, Empty.SHA
BASE = R / 'build/shared-side-cadence-native-1110/candidate.nes'
PIN = 'ba3cba071547402fd81398d8b69659fa1b7d20cef9dfcda4df3fe8554ec592de'
SHARED = R / 'build/shared-side-tank-precheck-1110/proof.json'
SHARED_IRQ = SHARED.with_name('shadow.json')
OPT = R / 'build/getsu-empty-services-1110/proof.json'
OLD = R / 'build/getsu-presentation-native-1110/candidate.nes'
PRESENTATION = Empty.Sword.PRESENTATION
OWNER = S.OWNER / 'proof.json'
STOP = 0x5b00


def install(raw, rows):
    result = bytearray(raw)
    for row in rows:
        at = row['file_offset']
        before, after = (bytes.fromhex(row[k]) for k in ('old_hex', 'new_hex'))
        assert len(before) == len(after) and result[at:at + len(before)] == before, at
        result[at:at + len(after)] = after
    return bytes(result)


def linked_side(output, baseline):
    source = Side.SOURCE.read_text() + '\n.export SourceSide\n'
    old, labels = O.assemble(output, source, (('B', Side.LO, Side.HI - Side.LO, ('SIDE',)),))
    assert old == baseline[Side.OFFSET:Side.OFFSET + len(old)]
    assert old[labels['SourceSide'] - Side.LO:labels['SourceSide'] - Side.LO + 5] == bytes.fromhex('68288d6a01')

    # BEA2 owns the only live bank33 ingress. Its original path reloads
    # SafecallA before BEE2, so the later same-value store is redundant.
    prg = baseline[16:O.Page.CHR]
    for op in (0x20, 0x4c, 0x6c):
        hits = []
        at = -1
        while (at := prg.find(bytes((op, 0xe2, 0xbe)), at + 1)) >= 0:
            hits.append((at // 8192, 0xa000 + at % 8192))
        assert hits == ([(65, pc) for pc in (0xbe5f, 0xbe69, 0xbe71, 0xbe7b, 0xbe8c)] if op == 0x4c else [])
    assert prg.count(bytes.fromhex('a9a28d6c01a9be8d6d01a9a1')) == 1
    assert bytes.fromhex('a9e28d6c01a9be8d6d01') not in prg
    source = O.one(source, 'SourceSide:\n    pla\n    plp\n    sta SavedA',
                   'CheckHigh:\n    cmp #42\n    beq Native\nSourceSide:\n    pla\n    plp')
    source = O.one(source, '    bcs SourceSide\n    pla\n    plp\n    jmp BlockBufferColli_Side',
                   '    bcs CheckHigh\nNative:\n    pla\n    plp\n    jmp BlockBufferColli_Side')
    new, new_labels = O.assemble(output, source, (('B', Side.LO, Side.HI - Side.LO, ('SIDE',)),))
    assert len(new) == len(old) and all(new_labels[n] == labels[n] for n in ('ForeignSide', 'LegacySide', 'Rejected'))
    return new, labels['SourceSide'] + 2, new_labels


def composition(output):
    old = OLD.read_bytes()
    presentation = O.Page.load_json(PRESENTATION)
    owner = O.Page.load_json(OWNER)
    assert presentation['passed'] and owner['passed'] and SHA(old) == presentation['expected_memory_only_SHA256']
    current = BASE.read_bytes()
    f33 = Side.BASE.read_bytes()
    shared = O.Page.load_json(SHARED)
    assert shared['passed'] and shared['parent_SHA256'] == SHA(f33) and install(f33, shared['patches']) == current
    assert SHA(current) == PIN == shared['expected_memory_only_SHA256']
    irq = O.Page.load_json(SHARED_IRQ)
    assert irq['passed'] and irq['expected_memory_only_SHA256'] == PIN
    sword, sword_proof = Empty.parent()
    optimized = O.Page.load_json(OPT)
    assert optimized['passed'] and optimized['parent_SHA256'] == SHA(sword)
    private = install(sword, optimized['patches'])
    assert SHA(private) == optimized['expected_memory_only_SHA256']

    # Bind all private PRG edits to the frozen ordered source records. The
    # three CHR pages are carried at their original physical page boundaries.
    rows = owner['patch_PRG'] + presentation['patch_PRG']
    f33_prg = install(f33, rows)[:O.Page.CHR]
    assert f33_prg == old[:O.Page.CHR]
    kernel = (Empty.SWORD.parent / 'kernel.bin').read_bytes()
    assert SHA(kernel) == sword_proof['kernel_SHA256']
    chr_at = O.Page.CHR + 990 * 1024
    atlas = (S.ART.parent / 'atlas.chr').read_bytes()
    assert private[chr_at:chr_at + 3072] == atlas + kernel
    assert private[O.Page.CHR:chr_at] == f33[O.Page.CHR:chr_at] and private[chr_at + 3072:] == f33[chr_at + 3072:]
    side, old_store, labels = linked_side(output, current)
    side_at = Side.OFFSET
    extent = Side.HI - Side.LO
    assert [row['file_offset'] for row in shared['patches']] == [side_at]
    assert all(current[i] == f33[i] for i in range(len(current)) if not side_at <= i < side_at + extent)
    result = private[:side_at] + side + private[side_at + extent:]
    assert result[side_at + extent:side_at + extent + 16] == current[side_at + extent:side_at + extent + 16]

    patches = []
    start = None
    for i, (a, b) in enumerate(zip(current[:O.Page.CHR], result[:O.Page.CHR], strict=True)):
        if a != b:
            if start is None:
                start = i
        elif start is not None:
            patches.append(dict(file_offset=start, old_hex=current[start:i].hex(), new_hex=result[start:i].hex()))
            start = None
    assert start is None
    for page in (990, 991, 992):
        at = O.Page.CHR + page * 1024
        patches.append(dict(physical_CHR=page, file_offset=at, old_hex=current[at:at + 1024].hex(),
                            new_hex=result[at:at + 1024].hex()))
    assert install(current, patches) == result
    return [W.bundle(raw) for raw in (current, private, result)], patches, old_store, labels, sword_proof


def side_checks(images, old_store):
    stock, private, candidate = images
    at, stop = Side.OFFSET, Side.OFFSET + Side.HI - Side.LO
    before = candidate['raw'][:at] + stock['raw'][at:stop] + candidate['raw'][stop:]
    foreign = W.bundle(before)
    seeds = [N.fresh(b) for b in (foreign, private, candidate)]
    loaded = [Side.Tank.cold(b, 0) for b in (foreign, candidate)]
    hist, redundant = Counter(), 0
    cases = [(raw, raw & 7, (4, 8)[raw & 1], (17, 20)[raw & 1], (1, 253)[raw >> 1 & 1],
              (63, 191)[raw >> 2 & 1], tile, p, None)
             for raw, tile, p in product(range(1, 256), (0, 0x54, 0xc3), (0x21, 0x60, 0xa5))]
    cases += [(0, variant, engine, y, 253, 191, tile, p, None)
              for variant, engine, y, tile, p in product(range(9), (4, 8), (17, 20), (0, 0x54), (0x21, 0x60))]
    cases += [(0, 7, 8, 17, 253, 191, 0x54, 0x21, fault) for fault in range(16)]
    for case in cases:
        raw, variant = case[:2]
        sources = loaded if raw == 0 and variant == 7 else (seeds[1 if raw == 42 else 0], seeds[2])
        pair = [Side.new_leaf(seed, *case) for seed in sources]
        for c in pair:
            def watch(q):
                nonlocal redundant
                tag, pc = H.point(q)
                if (tag, pc) == (161, 0xbee2):
                    assert q.a == q.memory[0x016a]
                if raw != 42 and q is pair[0] and (tag, pc) == (161, old_store):
                    assert q.a == q.memory[0x016a]
                    redundant += 1
            W.run(c, Side.done, watch)
        try:
            Side.compare(*pair, int(raw == 42))
        except AssertionError as error:
            a, b = (c.memory for c in pair)
            left, right = Side.writes(a, 0), Side.writes(b, 0)
            delta = next(((i, x, y) for i, (x, y) in enumerate(zip(left[0], right[0])) if x != y), None)
            raise AssertionError((case, delta, [len(left[0]), len(right[0])],
                                  [[v for at, v in m.writes if at == 0x5115] for m in (a, b)])) from error
        role = 'Getsu' if raw == 42 else 'public Tank' if raw == 0 and variant == 7 else 'other public'
        hist[role, pair[0].processorCycles - pair[1].processorCycles] += 1
    return dict(cases=len(cases), redundant_store_ingress=redundant,
                foreign_baseline='Exact composed image with only public ba3 bank33 restored',
                cycles_saved=[[role, cycles, n] for (role, cycles), n in sorted(hist.items())])


def gameplay(images, cookie):
    buses = [H.prepare(b) for b in images[1:]]
    reports = {}
    for phase, limit in (('idle', 24), ('walk_sword', 220)):
        histogram, probes = Counter(), Counter()
        attack = None
        for age in range(limit):
            player = S.word_position(buses[0])
            actor = next((a for a in H.Host.actors(buses[0]) if a['id'] == 6 and not a['state'] & 32), None)
            keys = int(phase != 'idle')
            if keys and attack is None and actor and 42 <= actor['x'] - player <= 49:
                keys |= 64
                attack = dict(update=age, world_X=player, enemy_X=actor['x'])
            pair, counts = [], []
            for m in buses:
                W.Match.controls(m, keys)
                O.clear_logs(m)
                c = Side.cpu_at(m, S.address(m.bundle, 'GameLoop'), a=0, x=0, y=0)
                n = Counter()
                depth = None

                def watch(q):
                    nonlocal depth
                    point = H.point(q)
                    if depth is not None and q.sp > depth:
                        depth = None
                    if point == (161, 0xbea2):
                        depth = q.sp
                    if point in ((161, 0xbea2), (254, 0x958b)) or point == Side.CHECK and depth is not None:
                        n[point] += 1

                W.run(c, Side.done, watch)
                assert N.get(m, 'NumberofLives') == 2 and O.headers(m) == (cookie, cookie)
                pair.append(c)
                counts.append(n)
            skipped = counts[0][Side.CHECK]
            assert not counts[1][Side.CHECK] and counts[0][161, 0xbea2] == counts[1][161, 0xbea2] == skipped, counts
            assert counts[0][254, 0x958b] == counts[1][254, 0x958b]
            Side.compare(*pair, skipped)
            probes[skipped] += 1
            histogram[pair[0].processorCycles - pair[1].processorCycles] += 1
            for m in buses:
                O.clear_logs(m)
                N.consume(m)
            assert W.memory(buses[0]) == W.memory(buses[1]) and buses[0].writes == buses[1].writes
            if attack and any(actor['id'] == 6 and actor['state'] & 32 for actor in H.Host.actors(buses[0])):
                attack.update(defeat_update=age, world_X_at_defeat=S.word_position(buses[0]))
                break
        assert phase == 'idle' or attack and 'defeat_update' in attack
        reports[phase] = dict(updates=age + 1, cycles_saved=histogram, skipped_Tank_checks=probes, natural_sword=attack)
    return reports


def active_vectors(images):
    optimized = images[1:]
    hits, floors, deepest = Counter(), [255, 255], {}

    def pair(c, kind, role, nested=False):
        result = []
        for i, b in enumerate(optimized):
            z = fork(c, b)

            def visit(q):
                if kind == 'FF' and i == 0 and not q.p & 4:
                    key = role, H.point(q)
                    if key not in deepest or q.sp < deepest[key].sp:
                        deepest[key] = fork(q)

            floors[1] = min(floors[1], H.vector(z, kind, visit))
            result.append((semantic(z), tuple(z.memory.writes)))
        assert result[0] == result[1], (kind, H.point(c))
        hits[role, 'nested_IRQ' if nested else kind] += 1

    for index, image in enumerate(optimized):
        m = H.prepare(image)
        O.clear_logs(m)
        W.Match.controls(m, 0)
        c = Side.cpu_at(m, S.address(image, 'GameLoop'), a=0, x=0, y=0)
        cuts = set()
        active = None

        def watch(q):
            nonlocal active
            tag, pc = H.point(q)
            if active is not None and q.sp > active:
                active = None
            if (tag, pc) == (254, Side.SIDE):
                active = q.sp
            changed = (tag == 161 and Side.LO <= pc < Side.HI
                       or tag == 193 and (pc in Empty.ROWS or 0xa7e4 <= pc < 0xa7f0)
                       or tag == 156 and 0xbfb0 <= pc < 0xbfe7)
            transport = active is not None and tag == 0 and 0x15a <= pc < 0x17b
            key = tag, pc, q.sp, q.p & 4
            if key in cuts or not (changed or transport):
                return
            cuts.add(key)
            floors[0] = min(floors[0], q.sp)
            role = ('private_parent' if index == 0 else 'rebased')
            pair(q, 'FF', role)
            if not q.p & 4:
                pair(q, 'IRQ', role)

        W.run(c, Side.done, watch)
        assert all(any(tag == 193 and pc == target for tag, pc, _, _ in cuts) for target in Empty.ROWS)
        assert any(tag == 161 and pc == 0xbee2 for tag, pc, _, _ in cuts)
    for (role, _), c in deepest.items():
        pair(c, 'IRQ', role, nested=True)
    return dict(cuts=[[role, kind, n] for (role, kind), n in sorted(hits.items())],
                minimum_SP=floors, exact_same_cut_ordered_IRQ_NMI=True)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', required=True, type=Path)
    output = cli.parse_args().output.resolve()
    assert output.is_relative_to(R / 'build')
    output.mkdir(exist_ok=True)
    images, patches, old_store, labels, sword = composition(output)
    digest = SHA(images[2]['raw'])
    cookie = bytes.fromhex(sword['cookie'])
    print(json.dumps(dict(SHA256=digest, side=labels, patches=len(patches))), flush=True)
    checks = side_checks(images, old_store)
    play = gameplay(images, cookie)
    print(json.dumps(dict(side=checks, play=play)), flush=True)
    irq = active_vectors(images)
    hot = H.hot(images[2], dict(cookie=sword['cookie']))
    proof = dict(passed=True, ROM_written=False, renderer_installed=True, native_HUD=True, parent_SHA256=PIN,
                 expected_memory_only_SHA256=digest, patches=patches, side=checks, gameplay=play,
                 live_rebase_vectors=irq, real_hot_vectors=hot, kernel_SHA256=sword['kernel_SHA256'],
                 cookie=sword['cookie'], public_vector_rows=O.Page.load_json(PRESENTATION)['public_vector_rows'],
                 scope='Exact ba3 with the qualified Getsu components and the same-bank shared side merge. Real '
                       'controller-fed CPU opening, native sword, full application state/OAM/CHR/APU and real '
                       'active interrupt behavior. Public ba3 empty-probe savings preserved. Mesen replay pending.',
                 bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                           (Path(__file__), Side.SOURCE, SHARED, SHARED_IRQ, OWNER, PRESENTATION, Empty.SWORD, OPT)})
    proof['public_vector_rows']['4'] = sword['private_vector']
    (output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(SHA256=digest, vectors=irq, hot=hot)))


if __name__ == '__main__':
    main()
