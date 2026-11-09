"""Remove inactive Getsu sword slot calls from the existing authenticated row."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_getsu_loaded_hot_1110 as H
import check_native_sparse_world_draw_1110 as W
from check_mini_funded_actor_1108_v3 import registers, slim_fork


R, O, S, N, SHA = H.R, H.O, H.S, H.N, H.SHA
BASE = R / 'build/getsu-presentation-native-1110/candidate.nes'
PRESENTATION = R / 'build/getsu-stage-presentation-1110/proof.json'
SOURCE = R / 'tools/reference/getsu_fuma_sword_admission_1110.s'
BODY = R / 'tools/reference/getsu_fuma_host_sword_1110.s'
OWNER = S.OWNER / 'proof.json'
PIN = 'e3412ac2bb5497975249b215aa0888f9c32a1d2f2dee55a8bdd2dd57f192ac78'
CODE, GUARD, CONTACT, SLOTS = 0xa000, 0xa242, 0xa267, 0xa7f2
STOP = 0x5b00
OLD = bytes.fromhex('ad0260c92af0034c27a3a50fc908f0034c27a3ad0fc0d0034c27a3ad10c0c902b0034c27a3')


def build(output):
    raw = BASE.read_bytes()
    assert SHA(raw) == PIN
    prior = O.Page.load_json(PRESENTATION)
    owner = O.Page.load_json(OWNER)
    assert prior['passed'] and prior['expected_memory_only_SHA256'] == PIN
    assert owner['kernel_labels']['GfHostSwordContact'] == GUARD
    assert '    lda GfSwordPhase\n    cmp #2\n    jcc NoHit\n    lda Enemy_Flag,x' in BODY.read_text()
    at, following = [p['file_offset'] for p in owner['code_pages']]
    assert following == at + 1024
    old_code = raw[at:at + 2048]
    assert SHA(old_code) == prior['kernel_SHA256']
    kernel = bytearray(old_code)
    guard, labels = O.assemble(output, SOURCE.read_text(), (('K', GUARD, len(OLD), ('SWORD_GUARD',)),))
    assert len(guard) == len(OLD) == CONTACT - GUARD and labels['GfSwordAdmission'] == GUARD
    assert kernel[GUARD - CODE:CONTACT - CODE] == OLD and kernel[CONTACT - CODE:CONTACT - CODE + 2] == b'\xb5\x10'
    assert kernel[SLOTS - CODE:] == bytes.fromhex('a2058a482042a268aaca10f61860')
    assert kernel[12:15] == b'\x4c' + SLOTS.to_bytes(2, 'little')
    kernel[12:15] = b'\x4c' + GUARD.to_bytes(2, 'little')
    kernel[GUARD - CODE:CONTACT - CODE] = guard
    kernel[SLOTS - CODE + 5:SLOTS - CODE + 7] = CONTACT.to_bytes(2, 'little')
    assert kernel[0x4be:0x7f2] == old_code[0x4be:0x7f2]
    atlas = (S.ART.parent / 'atlas.chr').read_bytes()
    atlas_at = O.Page.CHR + 990 * 1024
    assert raw[atlas_at:atlas_at + 1024] == atlas
    cookie_at = S.FRONT.off(65, 0xab81)
    old_cookie = bytes.fromhex(prior['cookie'])
    cookie = old_cookie[:3] + bytes.fromhex(SHA(kernel + atlas))[:13]
    assert raw[cookie_at:cookie_at + 16] == old_cookie
    patches = []
    result = bytearray(raw)
    for offset, data in ((at, kernel), (cookie_at, cookie)):
        patches.append(dict(file_offset=offset, old_hex=raw[offset:offset + len(data)].hex(), new_hex=data.hex()))
        result[offset:offset + len(data)] = data
    return [W.bundle(blob) for blob in (raw, bytes(result))], [old_code, bytes(kernel)], [old_cookie, cookie], patches


def snapshot(m, code, cookie):
    state = list(W.memory(m))
    banks = list(state[5])
    assert banks[3][:2048] == code
    for index in (2, 3):
        bank = banks[index]
        assert bank[0x1fe0:0x1ff0] == cookie
        if index == 3:
            bank = bank[2048:]
            offset = 0x1fe0 - 2048
        else:
            offset = 0x1fe0
        banks[index] = bank[:offset] + bank[offset + 16:]
    state[5] = tuple(banks)
    return state


def return_writes(m):
    return [(at, v) for at, v in m.writes if not 0x17b <= at < 0x200], tuple(m.ram_writes)


def cpu_at(m, pc, a=0, x=0, y=0, p=0x21):
    c = O.NesMPU(memory=m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = a, x, y, p, 224
    c.stPushWord(STOP - 1)
    return c


def done(c):
    return (c.pc, c.sp) == (STOP, 224)


def direct(m, p):
    A = 83
    m[0x16a], m[0x16c], m[0x16d] = A, 0x98, 0xb0
    O.clear_logs(m)
    return cpu_at(m, 0x15a, 193, 71, 109, p)


def boundary(seeds, kernels, cookies):
    hist = Counter()
    for engine, active, phase, status in product((4, 7, 8, 9, 11), (0, 1, 255), range(7), (0x21, 0x60, 0xa5)):
        pair = []
        for seed in seeds:
            m = slim_fork(seed)
            N.put(m, GameEngineSubroutine=engine, NmiDisable=255)
            m.ram[2][15:17] = bytes((active, phase))
            c = direct(m, status)
            W.run(c, done)
            pair.append(c)
        assert registers(pair[0], 0xef) == registers(pair[1], 0xef), (engine, active, phase, status)
        a, b = [snapshot(c.memory, k, h) for c, k, h in zip(pair, kernels, cookies, strict=True)]
        assert a == b and return_writes(pair[0].memory) == return_writes(pair[1].memory), (engine, active, phase, status)
        hist[engine == 8 and active != 0 and phase >= 2, pair[0].processorCycles - pair[1].processorCycles] += 1
    for seed in seeds:
        for bank, index in product((2, 3), range(16)):
            m = slim_fork(seed)
            m.ram[bank][0x1fe0 + index] ^= 1
            c = direct(m, 0x21)
            visits = Counter()

            def watch(q):
                if H.point(q) in ((3, GUARD), (3, SLOTS), (3, CONTACT)):
                    visits[H.point(q)] += 1

            W.run(c, done, watch)
            assert not visits and not c.p & 1
    return [[live, cycles, n] for (live, cycles), n in sorted(hist.items())]


def gameplay(seeds, kernels, cookies):
    results, last = {}, None
    for phase, limit in (('idle', 24), ('walk_and_first_sword', 240)):
        hist = Counter()
        attack = False
        for age in range(limit):
            m = seeds[0]
            enemy = next((actor for actor in H.Host.actors(m) if actor['id'] == 6 and not actor['state'] & 32), None)
            keys = int(phase != 'idle')
            if keys and not attack and enemy and 42 <= enemy['x'] - S.word_position(m) <= 49:
                keys |= 64
                attack = True
            pair = []
            hits = []
            for index, bus in enumerate(seeds):
                W.Match.controls(bus, keys)
                O.clear_logs(bus)
                c = cpu_at(bus, S.address(bus.bundle, 'GameLoop'))
                count = 0

                def observe(q):
                    nonlocal count
                    if H.point(q) == (3, CONTACT):
                        count += 1

                W.run(c, done, observe)
                pair.append(c)
                hits.append(count)
                assert N.get(bus, 'NumberofLives') == 2
            assert registers(pair[0], 0xef) == registers(pair[1], 0xef)
            a, b = [snapshot(bus, k, h) for bus, k, h in zip(seeds, kernels, cookies, strict=True)]
            assert a == b and return_writes(seeds[0]) == return_writes(seeds[1]), (phase, age, keys)
            assert hits[0] == hits[1] and hits[0] in (0, 6)
            hist[pair[0].processorCycles - pair[1].processorCycles] += 1
            for bus in seeds:
                N.consume(bus)
            assert snapshot(seeds[0], kernels[0], cookies[0]) == snapshot(seeds[1], kernels[1], cookies[1])
            assert return_writes(seeds[0]) == return_writes(seeds[1])
            if attack and any(actor['id'] == 6 and actor['state'] & 32 for actor in H.Host.actors(seeds[0])):
                assert hits == [6, 6]
                last = dict(update=age, world_X=S.word_position(seeds[0]), native_enemy_state=34)
                break
        results[phase] = dict(cycles_saved=dict(hist), updates=age + 1)
    assert last is not None
    return results, last


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    output = cli.parse_args().output.resolve()
    assert output.is_relative_to(R / 'build')
    output.mkdir(exist_ok=True)
    images, kernels, cookies, patches = build(output)
    seeds = [H.prepare(image) for image in images]
    direct_tests = boundary(seeds, kernels, cookies)
    measured, sword = gameplay(seeds, kernels, cookies)
    print(json.dumps(dict(direct_tests=direct_tests, gameplay=measured, sword=sword)), flush=True)
    hot = H.hot(images[1], dict(cookie=cookies[1].hex()))
    proof = dict(passed=True, ROM_written=False, renderer_installed=True, parent_SHA256=PIN,
                 expected_memory_only_SHA256=SHA(images[1]['raw']), patches=patches,
                 kernel_SHA256=SHA(kernels[1]), cookie=cookies[1].hex(), direct_tests=direct_tests,
                 header_poison_denies=64, paired_gameplay=measured, natural_sword=sword, real_hot_vectors=hot,
                 private_vector=GUARD, unchanged_contact_body=CONTACT, unchanged_draw=0xa4be,
                 bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                           (Path(__file__), SOURCE, BODY, PRESENTATION, OWNER, Path(H.__file__))})
    (output / 'kernel.bin').write_bytes(kernels[1])
    (output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(SHA256=proof['expected_memory_only_SHA256'], hot=hot)))


if __name__ == '__main__':
    main()
