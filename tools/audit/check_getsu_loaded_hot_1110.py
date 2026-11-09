"""Qualify Getsu's loaded stage OAM, post-enemy parity, and hot vectors."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_getsu_native_stage_1110 as S
import check_getsu_fuma_host_motion_1110 as Host
from check_mini_audio_mixer_irq_1108_v2 import lag_path
import trace_getsu_loaded_oam_1110 as Trace


R, O, N, SHA = S.R, S.O, S.N, S.SHA
LOAD = Trace.LOAD


def existing_post(stock, trial):
    cases = 0
    for raw in range(42):
        for active in (False, True) if raw in (2, 4, 5, 10) else (False,):
            for status in (0x21, 0x60, 0xa1):
                m = N.fresh(stock)
                N.put(m, SelectedCharacter=raw, OperMode=1, OperMode_Task=3, GameEngineSubroutine=8,
                      NmiDisable=255, DisableScreenFlag=0, Player_Y_HighPos=1,
                      Player_X_Position=48, Player_Y_Position=176, ObjectOffset=5)
                if active:
                    m[0x10], m[0x17], m[0x76], m[0xbe] = 1, 6, 72, 184
                    for name in ('RgEnemyStun', 'MmEnemyFlash', 'LsrFrozenPose'):
                        m[S.address(stock, name)] = 1
                n = S.Preview.rebind(N.fork(m), trial)
                O.clear_logs(m)
                O.clear_logs(n)
                a = S.FRONT.F.invoke(m, 'GuestPostEnemyCollision', a=0x5a, x=6, y=0x4d, p=status)
                z = S.FRONT.F.invoke(n, 'GuestPostEnemyCollision', a=0x5a, x=6, y=0x4d, p=status)
                assert {k: v for k, v in a.items() if k != 'minimum_SP'} == {
                    k: v for k, v in z.items() if k != 'minimum_SP'}, (raw, active, status, a, z)
                m_state, n_state = S.Preview.snapshot(m), S.Preview.snapshot(n)
                assert m_state == n_state, (raw, active, status,
                                             [i for i in range(len(m_state)) if m_state[i] != n_state[i]],
                                             bytes(m[0x15a:0x17b]).hex(), bytes(n[0x15a:0x17b]).hex())
                cases += 1
    return cases


def prepare(b):
    m = S.ColdBus(b)
    cpu = O.NesMPU(memory=m, pc=None)
    cpu.reset()
    for _ in range(300000):
        if cpu.pc == S.address(b, 'IdleLoop'):
            break
        assert m[cpu.pc]
        cpu.step()
    else:
        raise AssertionError('No native IdleLoop')
    m.vblank_at_boot = False
    for i in range(120):
        if m[0x7307] == 2:
            break
        S.frame(m, 16 if i == 40 else 0, None)
    else:
        raise AssertionError('No native menu')
    for pad, count in ((1, 5), (32, 4), (16, 1)):
        for _ in range(count):
            S.frame(m, 0, None)
            S.frame(m, pad, None)
    assert m[0x6002] == 42
    for _ in range(600):
        if tuple(N.get(m, k) for k in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
            return m
        S.frame(m, 0, None)
    raise AssertionError('No active stage')


def clone(c):
    n = O.NesMPU(memory=N.fork(c.memory), pc=c.pc)
    n.a, n.x, n.y, n.p, n.sp = c.a, c.x, c.y, c.p, c.sp
    return n


def point(c):
    return (c.memory.rawtags[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else 0, c.pc)


def snapshot(c):
    m = c.memory
    return (c.pc, c.a, c.x, c.y, c.p & 0xcf, c.sp, bytes(m[3:11]), bytes(m[0x15a:0x17b]),
            bytes(m[0x101 + c.sp:0x200]), tuple(bytes(bank) for bank in m.ram), tuple(m.chr_latches), tuple(m.rawtags))


def vector(c, kind, visit=None):
    m = c.memory
    before = snapshot(c)
    lag, normal = lag_path(m)
    skips = m[0x13a]
    if kind == 'FF':
        assert m[0x139] == 255
        c.nmi()
    else:
        assert not c.p & 4
        c.irq()
        assert c.pc == 0x8000
    minimum, hits = c.sp, 0
    for _ in range(30000):
        if (c.pc, c.sp) == (before[0], before[5]):
            break
        minimum = min(minimum, c.sp)
        assert c.pc != normal and m[c.pc], ('real ISR failure', kind, point(c), c.sp)
        hits += c.pc == lag
        if visit:
            visit(c)
        c.step()
    else:
        raise AssertionError(('real vector return bound', kind, point(c)))
    after = snapshot(c)
    assert after[:-1] == before[:-1], (kind, before[0], before[5], minimum,
                                       [i for i in range(len(before)) if before[i] != after[i]])
    if after[-1] != before[-1]:
        ins = bytes(m[c.pc:c.pc + 3])
        assert ins in (b'\x8d\x15\x51', b'\x8d\x16\x51', b'\x8e\x16\x51')
        window = 1 if ins[1] == 0x15 else 2
        assert after[-1][window] == m[0x145 if window == 1 else 0x7da1]
        assert all(before[-1][i] == after[-1][i] for i in range(4) if i != window)
    assert hits == (kind == 'FF') and m[0x13a] == (skips + hits) & 255
    assert minimum >= 0x7b, (kind, before[0], before[5], minimum)
    return minimum


def hot(b, proof):
    m = prepare(b)
    seen, stats = set(), Counter()
    deepest = {}
    floor = {'main': 224, 'FF': 224, 'IRQ': 224, 'nested': 224}
    start_attack = False
    sword_leaf = O.Page.load_json(S.OWNER / 'proof.json')['kernel_labels']['GfHostSwordContact']

    def watch(c):
        bank, pc = point(c)
        armed = bool(m.ram[2][15])
        wanted = (bank == 3 and 0xa000 <= pc < 0xa800 or bank == 128 and 0xa1f5 <= pc < 0xa237 or
                  bank == 209 and 0xbfe0 <= pc < 0xc000 or bank == 193 and pc in (0xaee2, 0xaf27, 0xab12, 0xab35, 0xab71) or
                  bank == 0 and 0x15a <= pc < 0x17b and c.sp <= 158)
        if not wanted:
            return
        key = bank, pc, c.sp, c.p & 4, armed
        if key in seen:
            return
        seen.add(key)
        floor['main'] = min(floor['main'], c.sp)
        O.clear_logs(m)
        group = 'sword' if armed else 'ordinary'

        def deepest_audio(q):
            if not q.p & 4 and (group not in deepest or q.sp < deepest[group].sp):
                deepest[group] = clone(q)

        floor['FF'] = min(floor['FF'], vector(clone(c), 'FF', deepest_audio))
        stats['FF'] += 1
        if not c.p & 4:
            floor['IRQ'] = min(floor['IRQ'], vector(clone(c), 'IRQ'))
            stats['IRQ'] += 1
        if bank == 3 and pc == sword_leaf:
            stats['sword_sites'] += 1

    for tick in range(185):
        enemy = next((actor for actor in Host.actors(m) if actor['id'] == 6 and not actor['state'] & 32), None)
        key = 1
        if not start_attack and enemy and 42 <= enemy['x'] - S.word_position(m) <= 49:
            key |= 64
            start_attack = True
        S.frame(m, key, watch)
        if start_attack and any(actor['id'] == 6 and actor['state'] & 32 for actor in Host.actors(m)):
            break
    assert start_attack and stats['sword_sites'] and set(deepest) == {'ordinary', 'sword'}
    for c in deepest.values():
        floor['nested'] = min(floor['nested'], vector(c, 'IRQ'))
        stats['nested_IRQ'] += 1
    assert O.headers(m)[0].hex() == proof['cookie'] and N.get(m, 'NumberofLives') == 2
    return dict(cuts=dict(stats), minimum_SP=floor, active_updates=tick + 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    output = parser.parse_args().output.resolve()
    assert output.is_relative_to(R / 'build')
    trial, proof = Trace.image()
    stock = O.Page.bundle()
    # A cold native full OAM DMA already independently demonstrates the
    # body using rotated slots outside the first five shadow entries.
    trace = Trace.trace(trial)
    sprites = trace['pre_DMA_visible']
    assert len(sprites) == 5 and all(y < 240 and tile % 2 == 0 and tile <= 58 for y, tile, _, _ in sprites)
    dma = [e['visible'] for e in trace['events'] if e.get('address') == 0x4014]
    assert dma == [sprites] and trace['chr'][0] == 990
    cases = existing_post(stock, trial)
    print(json.dumps(dict(existing_post=cases, renderer_installed=True, DMA=dma)), flush=True)
    irq = hot(trial, proof)
    result = dict(passed=True, ROM_written=False, renderer_installed=True,
                  parent_SHA256=O.PIN, expected_memory_only_SHA256=proof['expected_memory_only_SHA256'],
                  main_proof_SHA256=SHA((LOAD / 'proof.json').read_bytes()),
                  cookie=proof['cookie'], kernel_SHA256=proof['kernel_SHA256'], native_DMA=dma[0],
                  foreign_post_enemy_cases=cases, real_hot_vectors=irq,
                  bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                            (Path(__file__), Path(Trace.__file__), LOAD / 'proof.json', LOAD / 'kernel.bin')})
    output.mkdir(exist_ok=True)
    (output / 'verified.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
