"""Qualify Getsu's two empty native services and sword admission on public 9906."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_getsu_empty_sword_1110 as Sword
import compose_manual_title_1110 as Public
from check_getsu_owner_vectors_1110 import interrupt as cold_interrupt
from check_mini_funded_actor_1108_v3 import slim_fork


B = Sword.Budget
R, O, S, H, N, W, SHA = B.R, B.O, B.S, B.H, B.N, B.W, B.SHA
EMPTY = B.Rebase.Getsu.Empty
CURRENT = R/'build/manual-title-delivery-1110/candidate.nes'
CURRENT_PIN = '9906787a73b6d319cd30a2d3a89f50e4aa6892d912a9c22e9c5e19a14e581835'
CURRENT_PROOF = R/'build/manual-title-compose-1110/proof.json'
SWORD_PROOF = R/'build/getsu-empty-sword-1110/proof.json'
SOURCE = R/'tools/reference/getsu_fuma_empty_special_1110.s'
SHINOBI = R/'tools/reference/shinobi_resident_loader_1101_v1.inc'
OWNER = R/'build/mini-mario-final-owner-1103-v40/owner-final-v40.s'
ROWS = (0xb0a7, 0xb0f2)
SIDE = 0xb0b6
NEW = 0xaf9d
PHYSICAL = 65
OFF = lambda pc: S.FRONT.off(PHYSICAL, pc)
SCROLL = bytes.fromhex('ad79078d00202c0220ad42078d0520ad43078d052060')


def build(out):
    released = CURRENT.read_bytes()
    public = Public.read(CURRENT_PROOF)
    getsu = Public.read(B.RECEIPT)
    sword = Public.read(SWORD_PROOF)
    for q in (public, getsu, sword):
        assert q['passed']
        Public.check_paths(q['bindings'])
    base = Public.BASE.read_bytes()
    assert SHA(released) == public['expected_memory_only_SHA256'] == CURRENT_PIN
    assert Public.apply(base, public['patches']) == released
    older = Public.apply(base, getsu['patches'])
    assert SHA(older) == getsu['expected_memory_only_SHA256'] == sword['parent_SHA256'] == B.PIN
    assert SHA(Public.apply(older, sword['patches'])) == sword['expected_memory_only_SHA256']
    assert Public.apply(base, public['patches'] + getsu['patches']) == Public.apply(released, getsu['patches'])
    before = Public.apply(released, getsu['patches'])
    assert before == Public.apply(older, public['patches'])
    with_sword = Public.apply(before, sword['patches'])

    assert 'ShRestorePpu:\n ShRomFar X5PublishChr,Bank_X5PublishChr\n lda Mirror_PPUCTRL' in SHINOBI.read_text()
    assert 'CoRestorePpu:\n jsr CoPublishChr\n lda Mirror_PPUCTRL' in OWNER.read_text()
    assert 'PrCopyLiveDone:\n rts\nCoPublishChr:' in OWNER.read_text()
    assert before[OFF(0xaa4b):OFF(0xaa4b)+22] == SCROLL
    assert before[OFF(0xaf97):OFF(0xafb0)] == bytes.fromhex('20b0af') + SCROLL
    assert before[OFF(0xafc2):OFF(0xafc6)] == bytes.fromhex('4926d0e9')
    assert before[OFF(0xa7eb):OFF(0xa7f0)] == bytes.fromhex('ad6a011860')
    assert all(before[OFF(pc):OFF(pc)+3] == bytes.fromhex('4c17a8') for pc in (*ROWS, SIDE))
    code_at = 16+128*8192+991*1024
    kernel = before[code_at:code_at+2048]
    assert SHA(kernel) == getsu['kernel_SHA256']
    for pc in ROWS:
        offset = pc-0xb08c
        assert kernel[offset:offset+3] == bytes.fromhex('1860ea')
    assert kernel[SIDE-0xb08c:SIDE-0xb08c+3] == bytes.fromhex('4c8b95')

    # The replaced interior has no absolute control/data readers in the
    # actual resident bank. Retain the relative AFC4 -> AFAF entry explicitly.
    bank = before[OFF(0xa000):OFF(0xa000)+8192]
    opcodes = {0x20, 0x4c, 0x6c, 0xad, 0xbd, 0xb9, 0x8d, 0xcd, 0xdd, 0xd9}
    hits = [0xa000+i for i in range(len(bank)-2)
            if bank[i] in opcodes and 0xaf9a <= bank[i+1]+256*bank[i+2] < 0xafaf]
    # AD41 is the high operand of LDA $AD79,Y, followed by STA $04AF,X.
    assert hits == [0xad41] and bank[0xd3f:0xd45] == bytes.fromhex('b979ad9daf04')
    linked, labels = O.assemble(out, SOURCE.read_text(), (('R', 0xaf9a, 22, ('TAIL',)),))
    assert labels == {'GfEmptySpecial': NEW} and len(linked) == 22 and linked[-1] == 0x60
    patch = [(0xaf9a, SCROLL, linked)] + [(pc, bytes.fromhex('4c17a8'), bytes.fromhex('4c9daf')) for pc in ROWS]
    resident = [dict(file_offset=OFF(pc), old_hex=old.hex(), new_hex=new.hex()) for pc, old, new in patch]
    after = Public.apply(with_sword, resident)
    # Sword replaces the first four bytes of its own previously added
    # proxy. Collapse that exact overlap into one released-parent row.
    start = S.FRONT.off(Sword.BANK, Sword.PROXY)
    base_rows = [dict(row) for row in getsu['patches']]
    proxy, = (row for row in base_rows if row['file_offset'] <= start < row['file_offset']+len(bytes.fromhex(row['old_hex'])))
    first, size = proxy['file_offset'], len(bytes.fromhex(proxy['old_hex']))
    proxy['new_hex'] = after[first:first+size].hex()
    sword_rows = [row for row in sword['patches'] if row['file_offset'] != start]
    assert len(sword_rows) == 2
    all_rows = sorted(base_rows+sword_rows+resident, key=lambda q:q['file_offset'])
    assert Public.apply(released, all_rows) == after
    assert Public.apply(base, public['patches']+all_rows) == after
    return (W.bundle(before), W.bundle(with_sword), W.bundle(after)), all_rows, getsu


def trace(armed=False):
    active = None
    skipped = []
    events = Counter()

    def watch(c):
        nonlocal active
        tag, pc = H.point(c)
        m = c.memory
        if active and c.sp > active[0]:
            start = active[1]
            assert all(at in EMPTY.ALLOWED_NOOP_WRITES or 0x17b <= at < 0x200 for at, _ in m.writes[start:])
            skipped.extend(range(start, len(m.writes)))
            active = None
        if m[0x6002] == 42 and (tag == 193 and pc in ROWS or armed and tag == Sword.TAG and
                pc == Sword.PROXY and not any(m[0x10:0x16])):
            assert not active
            active = c.sp, len(m.writes)
            events[pc] += 1
        if (tag, pc) in ((193, 0xa817), (193, NEW), (254, 0x958b), (193, 0xafaf)):
            events[pc] += 1

    return watch, skipped, events


def cold(before, after):
    snapshots, timing, cuts = {}, Counter(), Counter()
    min_sp = 224

    def pair(buses, pc, expect=None, irq=False):
        nonlocal min_sp
        results = []
        sites = set()
        def visit(c):
            nonlocal min_sp
            tag, at = H.point(c)
            if tag != 193 or not (0xaa4b <= at < 0xaa61 or at in (0xaf9a, 0xafaf)):
                return
            key = at, c.sp, c.p & 4
            if key in sites:
                return
            sites.add(key)
            for kind in ('FF', 'IRQ') if not c.p & 4 else ('FF',):
                min_sp = min(min_sp, cold_interrupt(H.clone(c), kind))
                cuts[kind] += 1
        for i, m in enumerate(buses):
            results.append(EMPTY.call(m, pc, watch=visit if i and irq else None))
        if expect is not None:
            assert all((c.p & 1) == expect for c in results)
        EMPTY.compare(*results, *(EMPTY.clean_writes(m) for m in buses))
        timing[pc, results[1].processorCycles-results[0].processorCycles] += 1

    for owner in range(37, 43):
        buses = [O.blank(b) for b in (before, after)]
        for m in buses:
            O.scene(m, owner)
        pair(buses, O.COLD, 1, irq=True)
        snapshots[owner] = [slim_fork(m) for m in buses]
        pair(buses, O.COLD, 1)
        assert not any(m.ram_writes for m in buses)
        pair(buses, O.AUTH, 1)
        pair(buses, O.RETIRE)
        assert all(h[0] == 0 for m in buses for h in O.headers(m))
    for owner in range(37, 42):
        for source, dest in ((owner, 42), (42, owner)):
            buses = [slim_fork(m) for m in snapshots[source]]
            for m in buses:
                O.scene(m, dest)
            pair(buses, O.COLD, 1)
            assert all(O.headers(m) == O.headers(snapshots[dest][0]) for m in buses)
    return snapshots, dict(cases=[(hex(pc), added, n) for (pc, added), n in sorted(timing.items())],
                           vector_cuts=cuts, min_SP=min_sp)


def leaf(before, after, seeds):
    generic = [N.fresh(b) for b in (before, after)]
    hist, sites = Counter(), Counter()

    def compare(owner, target, a, status, poison):
        pair, logs = [], []
        for seed in seeds.get(owner, generic):
            m = slim_fork(seed)
            N.put(m, SelectedCharacter=owner, NmiDisable=255, OperMode=1, OperMode_Task=3, GameEngineSubroutine=8)
            if poison:
                bank, index = poison
                m.ram[bank][0x1fe0+index] ^= 1
            visit, skipped, events = trace()
            c = EMPTY.call(m, target, a, x=0, y=0, status=status, watch=visit)
            pair.append(c)
            logs.append(EMPTY.clean_writes(m, skipped))
            sites.update(events)
        EMPTY.compare(*pair, *logs)
        hist['Getsu' if owner == 42 else 'foreign', pair[0].processorCycles-pair[1].processorCycles] += 1

    for case in product((*range(44), 255), (*ROWS, SIDE), (0, 83, 255), (0x21, 0x60, 0xa5), (None,)):
        compare(*case)
    for owner, pc, bank, index in product(range(37, 43), (*ROWS, SIDE), (2, 3), range(16)):
        compare(owner, pc, 83, 0x21, (bank, index))
    assert all(sites[k] for k in (*ROWS, 0xa817, NEW, 0x958b))
    return dict(cycles_saved=[(name, delta, n) for (name, delta), n in sorted(hist.items())], cases=sum(hist.values()),
                entry_hits={hex(k):v for k,v in sites.items()})


def gameplay(before, after):
    buses = [H.prepare(b) for b in (before, after)]
    hist, entries, cuts = Counter(), Counter(), Counter()
    observed, deepest = set(), {}
    floor = 224
    attack = None
    for tick in range(225):
        m = buses[0]
        enemy = next((a for a in H.Host.actors(m) if a['id'] == 6 and not a['state'] & 32), None)
        keys = int(tick >= 24)
        if keys and attack is None and enemy and 42 <= enemy['x'] - S.word_position(m) <= 49:
            keys |= 64
            attack = tick
        cpus, writes = [], []
        for i, q in enumerate(buses):
            W.Match.controls(q, keys)
            O.clear_logs(q)
            c = EMPTY.Sword.cpu_at(q, S.address(q.bundle, 'GameLoop'))
            local, skipped, hits = trace(armed=True)
            def visit(cpu):
                nonlocal floor
                local(cpu)
                tag, pc = H.point(cpu)
                key = tag, pc, cpu.sp, cpu.p & 4
                if not i or key in observed or not (tag == 193 and NEW <= pc < NEW+16 or tag == Sword.TAG and
                        (Sword.GATE <= pc < Sword.GATE+19 or Sword.FLAGS <= pc < Sword.FLAGS+13)):
                    return
                observed.add(key)
                def nested(n):
                    if not n.p & 4 and (tag not in deepest or n.sp < deepest[tag].sp):
                        deepest[tag] = H.clone(n)
                for kind in ('FF', 'IRQ') if not cpu.p & 4 else ('FF',):
                    floor = min(floor, H.vector(H.clone(cpu), kind, nested if kind == 'FF' else None))
                    cuts[kind] += 1
            W.run(c, EMPTY.Sword.done, visit)
            cpus.append(c)
            writes.append(EMPTY.clean_writes(q, skipped))
            entries.update(hits)
        EMPTY.compare(*cpus, *writes)
        hist['idle' if not keys else 'walk', cpus[0].processorCycles-cpus[1].processorCycles] += 1
        for q in buses:
            N.consume(q)
        if attack is not None and any(a['id'] == 6 and a['state'] & 32 for a in H.Host.actors(m)):
            break
    else:
        raise AssertionError('No original sword defeat from actual B input')
    assert set(deepest) == {193, Sword.TAG}
    for n in deepest.values():
        floor = min(floor, H.vector(n, 'IRQ'))
        cuts['nested_IRQ'] += 1
    return dict(updates=tick+1, natural_sword=attack, cycles_saved=[(phase, delta, n) for (phase,delta),n in sorted(hist.items())],
                vector_cuts=cuts, min_SP=floor, entry_hits={hex(k):v for k,v in entries.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    (before, with_sword, after), rows, getsu = build(out)
    print('Exact current memory successor', SHA(after['raw']), flush=True)
    seeds, cold_result = cold(with_sword, after)
    print('Shared cold/retire parity', cold_result, flush=True)
    direct = leaf(with_sword, after, seeds)
    print('Typed service and live side parity', direct, flush=True)
    hot = gameplay(before, after)
    print('Genuine active full-state and vectors', hot, flush=True)
    refs = (Path(__file__), SOURCE, SHINOBI, OWNER, CURRENT, CURRENT_PROOF, SWORD_PROOF, B.RECEIPT)
    q = dict(passed=True, ROM_written=False, parent_SHA256=CURRENT_PIN, expected_memory_only_SHA256=SHA(after['raw']),
             renderer_installed=True, native_HUD=True, cookie=getsu['cookie'], kernel_SHA256=getsu['kernel_SHA256'],
             public_vector_rows=getsu['public_vector_rows'], patches=rows, cold=cold_result, direct=direct, active=hot,
             scope='Only Getsu tags9/34 skip the public empty kernel rows. Tag14 and all foreign fallbacks retain A817. '
                   'Cold PPU tail and PrCopyLiveDone remain active with identical writes. The complete current public '
                   'manual platform and title payload is byte-exact.',
             bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
