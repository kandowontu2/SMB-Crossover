"""Measure a typed Getsu sword admission before the authenticated contact row."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import profile_getsu_idle_budget_1110 as Budget
from check_mini_funded_actor_1108_v3 import registers, slim_fork


R, O, S, H, N, W, SHA = Budget.R, Budget.O, Budget.S, Budget.H, Budget.N, Budget.W, Budget.SHA
SOURCE = R / 'tools/reference/getsu_fuma_empty_sword_1110.s'
ROM = R / 'build/getsu-giant-native-1110/candidate.nes'
SUNNY = R / 'docs/qa/checkpoints/2026-10-28/sunny-runtime-integration/build__sunny_integrated.patch'
CELESTE = R / 'src/celeste_mario_host.s'
SWORD = R / 'tools/reference/getsu_fuma_host_sword_1110.s'
GATE = 0xb6ec
FLAGS = 0xbd16
PROXY = 0xbfe0
BANK = 81
TAG = 0xd1
POST = 0xa1f5
STOP = 0x5b00


def place(out):
    raw = ROM.read_bytes()
    assert SHA(raw) == Budget.PIN
    assert 'Sunny code must not overlap relocated menu names' in SUNNY.read_text(encoding='utf-8')
    assert 'jmp CmHostAreaColors\n .res 15,$ea' in CELESTE.read_text()
    assert '    lda Enemy_Flag,x\n    cmp #1\n    jne NoHit' in SWORD.read_text()
    off = S.FRONT.off
    assert raw[off(81, 0xb6e5):off(81, GATE)] == bytes.fromhex('4c7fb6284c7fb6')
    assert raw[off(81, 0xbd13):off(81, FLAGS)] == bytes.fromhex('4c35bf')
    assert raw[off(81, PROXY):off(81, PROXY) + 4] == bytes.fromhex('c904f00e')
    # The only typed caller binds the exact combined owner gate. Both live
    # destinations remain intact. Any other bank-address alias is independent.
    packet = bytes.fromhex('a9e08d6c01a9bf8d6d01a9d1')
    assert raw[16:O.Page.CHR].count(packet) == 1
    assert raw[off(0, 0xa20f):off(0, 0xa20f) + len(packet)] == packet
    owner = W.bundle(raw)
    assert S.address(owner, 'Enemy_Flag') == 0x10
    code, labels = O.assemble(out, SOURCE.read_text(), (('G', GATE, 20, ('ADMISSION',)), ('F', FLAGS, 15, ('FLAGS',))))
    assert len(code) == 19 + 13 and labels == {'GfPostAdmission': GATE, 'GfNativeActors': FLAGS}
    new = bytearray(raw)
    patches = []
    for pc, pre, post in ((GATE, b'\xff' * 19, code[:19]), (FLAGS, b'\xea' * 13, code[19:]),
                          (PROXY, bytes.fromhex('c904f00e'), bytes.fromhex('4cecb6ea'))):
        at = off(BANK, pc)
        assert raw[at:at + len(pre)] == pre and len(pre) == len(post)
        new[at:at + len(post)] = post
        patches.append(dict(file_offset=at, old_hex=pre.hex(), new_hex=post.hex()))
    return owner, W.bundle(bytes(new)), patches


def post(m, status=0x21, watch=None):
    O.clear_logs(m)
    m.raw_page(1, 0x80)
    N.put(m, CurrentBank=0x80)
    c = Budget.Rebase.Getsu.Empty.Sword.cpu_at(m, POST, 91, 4, 37, status)
    W.run(c, Budget.Rebase.Getsu.Empty.Sword.done, watch)
    return c


def direct(left, right):
    seeds = [H.prepare(b) for b in (left, right)]
    n = 0
    for actor, flag, status, poison in product(range(6), (1, 2, 255), (0x21, 0x64, 0xa1), (False, True)):
        m, z = (slim_fork(seed) for seed in seeds)
        for q in (m, z):
            q[0x10 + actor] = flag
            if poison:
                q.ram[3][0x1fef] ^= 1
        a, b = (post(q, status) for q in (m, z))
        assert registers(a, 0xef) == registers(b, 0xef) and W.memory(m) == W.memory(z)
        assert [(p, v) for p, v in m.writes if p < 0x17b or p >= 0x200] == [
            (p, v) for p, v in z.writes if p < 0x17b or p >= 0x200]
        n += 1
    for status in (0x21, 0x64, 0xa1):
        m, z = (slim_fork(seed) for seed in seeds)
        for q in (m, z):
            N.put(q, SelectedCharacter=4)
        a, b = (post(q, status) for q in (m, z))
        assert registers(a, 0xef) == registers(b, 0xef) and W.memory(m) == W.memory(z)
        n += 1
    return n


def full(left, right):
    buses = [H.prepare(b) for b in (left, right)]
    results, cuts, minima = Counter(), set(), []
    attack = None
    for step in range(205):
        m = buses[0]
        enemy = next((a for a in H.Host.actors(m) if a['id'] == 6 and not a['state'] & 32), None)
        pad = int(step >= 24)
        if pad and attack is None and enemy and 42 <= enemy['x'] - S.word_position(m) <= 49:
            attack = step
            pad |= 64

        def sample(c):
            tag, pc = H.point(c)
            key = tag, pc, c.sp, c.p & 4
            if tag == TAG and (GATE <= pc < GATE + 19 or FLAGS <= pc < FLAGS + 13) and key not in cuts:
                cuts.add(key)
                for kind in ('FF', 'IRQ') if not c.p & 4 else ('FF',):
                    minima.append((kind, H.vector(H.clone(c), kind)))

        cpus = []
        empty = not any(m[0x10:0x16])
        for i, q in enumerate(buses):
            W.Match.controls(q, pad)
            O.clear_logs(q)
            c = Budget.Rebase.Getsu.Empty.Sword.cpu_at(q, S.address(q.bundle, 'GameLoop'))
            W.run(c, Budget.Rebase.Getsu.Empty.Sword.done, sample if i else None)
            cpus.append(c)
        assert registers(cpus[0], 0xef) == registers(cpus[1], 0xef), (step, empty)
        a, b = (W.memory(q) for q in buses)
        assert a == b, (step, empty, [i for i, (x, y) in enumerate(zip(a, b, strict=True)) if x != y])
        assert buses[0].ppu_log == buses[1].ppu_log and buses[0].ram_writes == buses[1].ram_writes
        results['idle' if not pad else 'walk', cpus[0].processorCycles - cpus[1].processorCycles] += 1
        for q in buses:
            N.consume(q)
        if attack is not None and any(a['id'] == 6 and a['state'] & 32 for a in H.Host.actors(m)):
            break
    else:
        raise AssertionError('No natural sword defeat')
    return dict(updates=step + 1, actual_B=attack, timings=[[phase, cycles, n] for (phase, cycles), n in results.items()],
                cuts=Counter(k for k, _ in minima), min_SP=min(n for _, n in minima))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    out = ap.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build') and not (out / 'proof.json').exists()
    out.mkdir(exist_ok=True)
    a, b, rows = place(out)
    direct_cases = direct(a, b)
    print('Direct positive/foreign cases', direct_cases, flush=True)
    game = full(a, b)
    print('Whole active state', game, flush=True)
    q = dict(passed=True, parent_SHA256=Budget.PIN, expected_memory_only_SHA256=SHA(b['raw']),
             patches=rows, direct_cases=direct_cases, gameplay=game, ROM_written=False,
             bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                       (Path(__file__), SOURCE, SUNNY, CELESTE, SWORD, Budget.RECEIPT)})
    (out / 'proof.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
