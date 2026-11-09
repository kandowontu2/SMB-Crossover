"""Rebase the qualified Getsu component and chain its name through Giant."""

import argparse
from collections import Counter
from difflib import SequenceMatcher
import json
from pathlib import Path

import check_getsu_ba3_rebase_1110 as Getsu
import check_mega_giant_selection_1110 as Giant


R, O, S, H, N, W, SHA = Getsu.R, Getsu.O, Getsu.S, Getsu.H, Getsu.N, Getsu.W, Getsu.SHA
P = S.Preview
BASE = R / 'build/mega-giant-current-native-1110/candidate.nes'
PIN = '94650fbc11ede25b9d08e579bdc6b1d6da81fca8f29c6b0c25dadad2e685ede1'
DELIVERY = R / 'build/mega-giant-delivery-1110/candidate-proof.json'
GF = R / 'build/getsu-ba3-rebase-1110/proof.json'
GIANT = R / 'build/mega-giant-selection-1110/proof-v2.json'
NAME = 0xb0ab


def far_args(target, bank):
    return bytes((0xa9, target & 255, 0x8d, 0x6c, 1, 0xa9, target >> 8, 0x8d, 0x6d, 1, 0xa9, bank))


def compose():
    parent, released = Getsu.BASE.read_bytes(), BASE.read_bytes()
    getsu = O.Page.load_json(GF)
    giant = O.Page.load_json(GIANT)
    assert SHA(released) == PIN and SHA(parent) == getsu['parent_SHA256'] == Getsu.PIN
    assert getsu['passed'] and giant['passed']
    delivery = O.Page.load_json(DELIVERY)
    assert delivery['candidate_SHA256'] == PIN and delivery['parent_SHA256'] == Getsu.PIN
    old_getsu = Getsu.install(parent, getsu['patches'])
    assert SHA(old_getsu) == getsu['expected_memory_only_SHA256']
    location = S.FRONT.off
    giant_name = giant['symbols']['GiantMenuName']
    ingress = location(66, 0xacc3)
    assert released[ingress:ingress + 12] == far_args(giant_name, 0xbf)
    assert parent[ingress:ingress + 12] == far_args(0xb720, 0xcf)
    assert old_getsu[ingress:ingress + 12] == far_args(NAME, 0xdb)
    conflicts = {ingress + i for i in (1, 6, 11)}
    rows, found = [], set()
    for row in getsu['patches']:
        at = row['file_offset']
        before = bytes.fromhex(row['old_hex'])
        assert before and len(before) == len(bytes.fromhex(row['new_hex']))
        if released[at:at + len(before)] != before:
            assert len(before) == 1 and at in conflicts, row
            found.add(at)
        else:
            rows.append(row)
    assert found == conflicts

    # Keep the released Giant test first. Its source-defined StockName tail
    # already preserves incoming A/P and drops its local farcall return pair.
    # It forwards to the authentic Getsu name decorator, which still queues
    # the native record before recognizing Simon variant 4.
    source = Giant.SOURCE.read_text()
    assert 'StockName:\n    pla\n    plp\n    lda #$20' in source
    assert '    sta $0162\n    pla\n    pla\n    jmp $0161\nGiantName:' in source
    stock_tail = far_args(0xb720, 0xcf) + bytes.fromhex('8d620168684c6101')
    start = location(63, giant_name)
    at = released.index(stock_tail, start, start + 83)
    assert at == start + 62
    assert released[at - 2:at] == bytes.fromhex('6828')
    for i in (1, 6, 11):
        rows.append(dict(file_offset=at + i, old_hex=stock_tail[i:i + 1].hex(),
                         new_hex=far_args(NAME, 0xdb)[i:i + 1].hex()))
    rows.sort(key=lambda row: row['file_offset'])
    assert all(a['file_offset'] + len(bytes.fromhex(a['old_hex'])) <= b['file_offset']
               for a, b in zip(rows, rows[1:]))
    result = Getsu.install(released, rows)
    assert result[ingress:ingress + 12] == released[ingress:ingress + 12]
    assert result[O.Page.CHR:O.Page.CHR + 990 * 1024] == released[O.Page.CHR:O.Page.CHR + 990 * 1024]
    assert result[O.Page.CHR + 993 * 1024:] == released[O.Page.CHR + 993 * 1024:]
    side = Getsu.Side.OFFSET
    assert result[side:side + Getsu.Side.HI - Getsu.Side.LO] == old_getsu[side:side + Getsu.Side.HI - Getsu.Side.LO]
    return [W.bundle(raw) for raw in (released, old_getsu, result)], rows, getsu, giant


def profile(m):
    _, cells = O.Page.menu_name(m)
    return (m[0x6002], tuple(cells), bytes(m[0x5fe0:0x5fff]), m[0x730a])


def compare_state(a, z, label, *, retirement=False):
    before, after = P.snapshot(a), P.snapshot(z)
    assert before[:-1] == after[:-1], (label, [i for i, (x, y) in enumerate(zip(before, after, strict=True)) if x != y])
    left, right = before[-1], after[-1]
    if retirement:
        # During menu confirmation, both C2/C3 headers are invalid. The
        # expanded table probes Getsu once and then reaches the relocated
        # Prince cookie. Only this exact failed transport packet is extra.
        assert all(header[0] == 0 for header in O.headers(a))
        packet = [(8, 0x81), (9, 0xab), (6, 0xcd), (7, 0xaf), (0x7da1, 3), (0x5116, 3)]
        normalized = []
        i = 0
        while i < len(right):
            if right[i:i + 6] == packet:
                (shadow, value), (mapper, mapped) = right[i + 6:i + 8]
                assert (shadow, mapper, value) == (0x7da1, 0x5116, mapped)
                i += 8
                continue
            x = right[i]
            if x == (8, 0x9d) and right[i + 1:i + 2] == [(9, 0xab)]:
                x = (8, 0xa4)
            normalized.append(x)
            i += 1
        right = normalized
    if left != right:
        delta = [(tag, left[s:e], right[t:u]) for tag, s, e, t, u in
                 SequenceMatcher(None, left, right, autojunk=False).get_opcodes() if tag != 'equal']
        raise AssertionError((label, delta[:10]))


def menu(stock, trial):
    counts, totals = Counter(), Counter()
    vector_seeds = {}
    for slot in range(32):
        m, n = P.seed(stock, slot), P.seed(trial, slot)
        seen = set()
        for _ in range(32):
            sig = profile(m)
            if sig in seen:
                assert sig == profile(n)
                break
            seen.add(sig)
            assert sig == profile(n), (slot, sig[:2], profile(n)[:2])
            if slot == 0 and m[0x730a] == 9:
                assert O.Page.menu_name(n)[0] == 'MEGA GIANT MARIO'
                vector_seeds['Giant'] = N.fork(n)
            elif slot == 5:
                vector_seeds['Simon'] = N.fork(n)
            for cursor in (0, 58):
                a, z = N.fork(m), P.rebind(N.fork(m), trial)
                for q in (a, z):
                    N.put(q, VRAM_Buffer1_Offset=cursor)
                    O.clear_logs(q)
                r0, r1 = (P.RUN(q, 'QueueSelection') for q in (a, z))
                assert {k: v for k, v in r0.items() if k != 'minimum_SP'} == {
                    k: v for k, v in r1.items() if k != 'minimum_SP'}, (slot, cursor, r0, r1)
                compare_state(a, z, ('QueueSelection', slot, cursor))
                totals['queue_cases'] += 1
            for buttons in (16, 128, 48, 160, 176):
                a, z = N.fork(m), P.rebind(N.fork(m), trial)
                for q in (a, z):
                    O.clear_logs(q)
                    P.key(q, buttons)
                if slot == 5 and m[0x5fe7] == 3 and buttons & 32:
                    assert (a[0x6002], a[0x5fe7], z[0x6002], z[0x5fe7]) == (5, 0, 42, 4)
                    totals['intentional_Select_confirm'] += 1
                else:
                    compare_state(a, z, ('confirmation', slot, buttons), retirement=True)
                    totals['foreign_confirm'] += 1
            P.key(m, 32)
            P.key(n, 32)
            if slot == 5 and n[0x5fe7] == 4:
                assert n[0x7309] == n[0x6002] == 5
                assert O.Page.menu_name(n)[0].strip() == 'GETSU FUMA'
                assert n[0x147] == (990 & 255) and n[0x73e0] == 0x83
                vector_seeds['Getsu'] = N.fork(n)
                for buttons in (16, 128, 144):
                    z = N.fork(n)
                    P.key(z, buttons)
                    assert z[0x6002] == 42 and z[0x5fe7] == 4
                    totals['Getsu_confirm'] += 1
                P.key(n, 32)
                assert n[0x5fe7] == 0
            counts[slot] += 1
        else:
            raise AssertionError(('native Select bound', slot))
    assert counts[0] == 16 and counts[5] == 4 and sum(counts.values()) == 101, counts
    assert totals == dict(queue_cases=202, foreign_confirm=502, intentional_Select_confirm=3, Getsu_confirm=3)
    return dict(existing_profiles=101, combined_profiles=102, slots=dict(counts), **totals), vector_seeds


def menu_interrupts(seeds):
    cuts, minimum = Counter(), 224
    for name, seed in seeds.items():
        m = N.fork(seed)
        N.put(m, VRAM_Buffer1_Offset=0, NmiDisable=255)
        seen = set()

        def visit(c):
            nonlocal minimum
            tag, pc = H.point(c)
            if (tag, pc) in seen or not (tag == 0xbf and 0xa80e <= pc < 0xa860 or
                    tag == 0xdb and (NAME <= pc < 0xb0c7 or 0xb1fc <= pc < 0xb20b) or
                    tag == 0 and 0x15a <= pc < 0x17b):
                return
            seen.add((tag, pc))
            for mode in ('FF', 'IRQ') if not c.p & 4 else ('FF',):
                minimum = min(minimum, H.vector(H.clone(c), mode))
                cuts[name, mode] += 1

        P.RUN(m, 'QueueSelection', watch=visit)
    assert all(cuts[name, mode] for name in seeds for mode in ('FF', 'IRQ'))
    return dict(cuts=[(name, mode, n) for (name, mode), n in sorted(cuts.items())], minimum_SP=minimum)


def payloads(released, final, getsu, giant):
    def page(raw, no):
        at = O.Page.CHR + no * 1024
        return raw[at:at + 1024]

    cookie = bytes.fromhex(getsu['cookie'])
    code = page(final['raw'], 991) + page(final['raw'], 992)
    assert SHA(code) == getsu['kernel_SHA256']
    assert cookie == bytes((0xa7, 42, 1)) + bytes.fromhex(SHA(code + page(final['raw'], 990)))[:13]
    for row in giant['physical_carriers']:
        assert SHA(page(final['raw'], row['page'])) == row['new_SHA256']
    # The exact current Mini code, metadata, art and cookie remain published.
    assert all(page(final['raw'], p) == page(released['raw'], p) for p in range(962, 969))
    return code, cookie


def cold(images, getsu, giant):
    released, _, final = images
    code, cookie = payloads(released, final, getsu, giant)
    # Compare against the exact before-compaction owner table so the reused
    # checker also observes every legacy and relocated cold reader.
    unoptimized, _ = Getsu.Empty.parent()
    _, transactions = Getsu.Empty.transactions((W.bundle(unoptimized), final))
    labels = giant['symbols']
    giant_code, giant_meta = (Giant.P.chr_page(final['raw'], page) for page in (Giant.G.CODE, Giant.G.ATLAS))
    pc = labels['GiantSceneEnd']
    start = S.FRONT.off(84, pc) - 20
    signature = bytes.fromhex('a7000902331ad79e8d280b2d020101d0')
    assert final['raw'][start:start + 16] == signature
    giant_seed, giant_entrance = Giant.select_and_start(final, labels, signature, giant_meta, giant_code)
    giant_to_mini = Giant.retire(giant_seed, labels, signature)
    native = [S.cold_stage(final, code, cookie, {int(k): v for k, v in getsu['public_vector_rows'].items()}, key)
              for key in (16, 128)]

    # Follow the same actual GameOver path through title, then select and
    # start the other owner. Both stages use the real blank-screen ingress.
    def transition(seed, old, new):
        m = N.fork(seed)
        assert O.headers(m) == (old, old)
        N.put(m, OperMode=3, OperMode_Task=0, NumberofLives=255)
        events = []
        for age in range(220):
            _, seen = Giant.frame(m, 16 if age % 20 == 10 else 0, labels)
            events.extend(seen)
            if m[0x7307] == 2:
                break
        else:
            raise AssertionError('Actual GameOver did not return to selection')
        assert all(h[0] == 0 for h in O.headers(m))
        def tap(pad):
            Giant.frame(m, 0, labels)
            Giant.frame(m, pad, labels)

        slot, variant, address = (5, 4, 0x5fe7) if new == cookie else (0, 9, 0x730a)
        for _ in range(33):
            if m[0x7309] == slot:
                break
            tap(1)
        else:
            raise AssertionError(('slot is unreachable from native GameOver menu', slot))
        for _ in range(18):
            if m[address] == variant:
                break
            tap(32)
        else:
            raise AssertionError(('variant is unreachable from native GameOver menu', slot, variant))
        cells = bytes(m.vram[0x2328:0x2338])
        name = ''.join(chr(cell + 55) if 10 <= cell <= 35 else ' ' if cell == 36 else '?' for cell in cells).strip()
        assert name == ('GETSU FUMA' if new == cookie else 'MEGA GIANT MARIO'), (slot, variant, name)
        tap(16)
        reads = m.ppu_reads
        for entrance in range(600):
            if tuple(N.get(m, k) for k in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
                break
            Giant.frame(m, 0, labels)
        else:
            raise AssertionError('No active stage after native transition')
        assert O.headers(m) == (new, new)
        assert (m[0x6002], N.get(m, 'NumberofLives')) == (new[1], 2)
        if new == cookie:
            assert bytes(m.ram[3][:2048]) == code and labels['GiantSceneRetire'] in events
        else:
            assert bytes(m.ram[2][0x1000:0x1400]) == giant_meta
        return dict(gameover_updates=age+1, entrance_updates=entrance,
                    PPU_reads=m.ppu_reads-reads, headers=[x.hex() for x in O.headers(m)])

    return dict(incumbents=transactions, Giant_native_entrance=giant_entrance, Giant_to_Mini=giant_to_mini,
                Getsu_native_entrances=native, Giant_to_Getsu=transition(giant_seed, signature, cookie),
                Getsu_to_Giant=transition(H.prepare(final), cookie, signature))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build') and not (out / 'proof.json').exists()
    images, rows, getsu, giant = compose()
    released, _, final = images
    print('Exact memory image', SHA(final['raw']), flush=True)
    frontend, seeds = menu(released, final)
    print('Complete frontend', frontend, flush=True)
    vectors = menu_interrupts(seeds)
    print('Frontend FF/IRQ', vectors, flush=True)
    ownership = cold(images, getsu, giant)
    print('Cold owners and native transitions passed', flush=True)
    hot_vectors = H.hot(final, getsu)
    print('Active final-image FF/IRQ', hot_vectors, flush=True)
    source_inputs = (Path(__file__), BASE, Getsu.BASE, GF, GIANT, DELIVERY, Giant.SOURCE, S.SOURCE,
                     R / 'src/character_select.s')
    receipt = dict(passed=True, ROM_written=False, renderer_installed=True, native_HUD=True,
                   parent_SHA256=PIN, expected_memory_only_SHA256=SHA(final['raw']), patches=rows,
                   frontend=frontend, frontend_vectors=vectors, ownership=ownership, hot_vectors=hot_vectors,
                   kernel_SHA256=getsu['kernel_SHA256'], cookie=getsu['cookie'],
                   public_vector_rows=getsu['public_vector_rows'], inherited_active_proof=SHA(GF.read_bytes()),
                   bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in source_inputs})
    out.mkdir(exist_ok=True)
    (out / 'proof.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
