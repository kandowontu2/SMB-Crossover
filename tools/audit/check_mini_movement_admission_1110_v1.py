"""Rebind one native movement tail to the same existing Mini row-zero veneer."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import profile_mini_busy_1108_v1 as P
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_visibility_dispatch_1110_v1 import address_in_rom, memory, require_bytes

R, N = P.R, P.N
BASE = R / 'build/mini-box-terrain-visible-1110/candidate.nes'
PIN = '6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
SOURCE = R / 'tools/reference/mini_movement_admission_1110_v1.s'
OUT = R / 'build/mini-movement-admission-1110'
TAG = 214
PAD, ENTRY, END = 0xa3d9, 0xa73d, 0xa786
MINI_VENEER = (212, 0xb420)
MINI_CHECK = (212, 0xb44d)
OLD = bytes.fromhex(
    '0848ad0260c90ef02cc913d01468288d6a01a9528d6c01a9a38d6d01a9d74c5a01'
    '68288d6a01a9b08d6c01a9a08d6d01a9dd4c5a01'
    '68288d6a01a9b28d6c01a9a08d6d01a9d14c5a01')


def patches(raw, out):
    require_bytes(raw, 86, PAD - 3, bytes.fromhex('4c14a5') + b'\xea' * 15)
    require_bytes(raw, 86, ENTRY, OLD)
    require_bytes(raw, 86, 0xa63f, bytes.fromhex('4c3da7'))
    require_bytes(raw, 84, 0xb420, bytes.fromhex('4c4db4'))
    cfg, obj, data, lbl = (out / f'movement.{ext}' for ext in ('cfg', 'o', 'bin', 'lbl'))
    cfg.write_text(
        'MEMORY{T:start=$A3D9,size=$0F,file=%O;C:start=$A73D,size=$49,file=%O;}\n'
        'SEGMENTS{MINI_TAIL:load=T,type=ro;CAMERA:load=C,type=ro;}\n')
    cc = R / 'tools/Windows/cc65/bin'
    subprocess.run([cc / 'ca65.exe', SOURCE, '-o', obj], check=True)
    subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', data, '-Ln', lbl], check=True)
    obj.unlink()
    labels = {row.split()[2][1:]: int(row.split()[1], 16) for row in lbl.read_text().splitlines()}
    assert labels == dict(CameraMovementAdmission=ENTRY, CameraMovementEnd=END, MiniMovementTail=PAD)
    packed = data.read_bytes()
    assert len(packed) == 15 + len(OLD)
    return [dict(file_offset=address_in_rom(86, pc), old_hex=before.hex(), new_hex=after.hex(),
                 physical_PRG=86, CPU_half_open=[pc, pc+len(before)], role=role)
            for pc, before, after, role in (
                (PAD, b'\xea' * 15, packed[:15], 'source-declared movement dispatcher tail padding'),
                (ENTRY, OLD, packed[15:], 'existing camera movement owner admission'))]


def point(c):
    if c.pc < 0x8000:
        return -1, c.pc
    return c.memory.rawtags[(c.pc - 0x8000) // 0x2000], c.pc


def state(c):
    return registers(c, 0xef), live_stack(c), memory(c.memory)


def local(seed, fields, a, x, y, p):
    m = slim_fork(seed)
    m.raw_page(1, TAG)
    N.put(m, CurrentBank=TAG, **fields)
    c = N.NesMPU(memory=m, pc=ENTRY)
    c.a, c.x, c.y, c.p, c.sp = a, x, y, p, 224
    c.stPushWord(0x5aff)
    return c


def end(c):
    return (c.pc, c.sp) == (0x5b00, 224)


def foreign_target(raw):
    return {14: (209, 0xa0b2), 19: (215, 0xa352)}.get(raw, (221, 0xa0b0))


def foreign(images):
    seeds = [N.fresh(b) for b in images]
    savings = Counter()
    for raw, phase, p in product(range(256), [0, 1], [0x20, 0x65, 0xa0, 0xef]):
        if raw == 41:
            continue
        cpus = [local(seed, dict(SelectedCharacter=raw), phase*255, 7+phase, 91-phase, p)
                for seed in seeds]
        target = foreign_target(raw)
        for c in cpus:
            run(c, lambda q: point(q) == target)
        assert state(cpus[0]) == state(cpus[1]), (raw, phase, p, [state(c)[0] for c in cpus])
        savings[raw if raw in (14, 19) else 'legacy',
                cpus[0].processorCycles-cpus[1].processorCycles] += 1
    return [dict(path=k[0], cycle_delta=k[1], cases=v) for k,v in savings.items()]


def mini(images):
    # All cases start from the real loader's state, then perturb only the
    # exact engine/readiness bytes consumed by the existing veneer.
    seeds = [P.fixture(b, 0, False, False) for b in images]
    outcomes = Counter()
    for engine, variant, poison, p in product([5, 8, 9, 11], [0, 8],
            [None, 'ready', (2, 0), (2, 1), (3, 0), (3, 1)], [0x20, 0x65]):
        cpus, paths = [], []
        for seed in seeds:
            c = local(seed, dict(GameEngineSubroutine=engine, MarioVariant=variant), 0, 0, 91, p)
            if poison == 'ready':
                c.memory.ram[2][0x300] = 1
            elif poison is not None:
                bank, index = poison
                c.memory.ram[bank][0x1fe0+index] ^= 1
            visits = []
            def observe(q):
                if point(q) in (MINI_VENEER, MINI_CHECK, (3, 0xa000), (193, 0xb08c)):
                    visits.append(point(q))
            run(c, end, observe)
            cpus.append(c)
            paths.append(visits)
        a, b = cpus
        left, right = state(a), state(b)
        assert left == right, ('Mini', engine, variant, poison, p, left[:2], right[:2],
                               [i for i, (v, w) in enumerate(zip(left[2], right[2])) if v != w],
                               paths, [q.memory[0x15a:0x17b] for q in cpus])
        assert paths[0] == paths[1] and MINI_VENEER in paths[0] and MINI_CHECK in paths[0], paths
        fast = engine == 8 and poison is None
        assert ((193, 0xb08c) in paths[0]) == (not fast), (engine, poison, paths)
        if fast:
            assert (3, 0xa000) in paths[0]
        outcomes[fast, (3, 0xa000) in paths[0], a.processorCycles - b.processorCycles] += 1
    return [dict(warm_path=k[0], source_row_entered=k[1], cycle_delta=k[2], cases=v)
            for k, v in outcomes.items()]


def whole(images):
    receipt = {}
    for actors, parser in [(0, False), (4, False), (4, True), (6, True)]:
        machines = [P.fixture(b, actors, False, parser) for b in images]
        samples = []
        for age in range(24):
            key = 0 if age < 8 else 1 if age < 16 else 129
            for m in machines:
                N.put(m, FrameCounter=(N.get(m,'FrameCounter')+1)&255, SavedJoypadBits=key,
                      SavedJoypad1Bits=key, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
            a, b = [N.invoke(m, 'GameCoreRoutine', x=0, y=0) for m in machines]
            left, right = [memory(m) for m in machines]
            assert left == right, (actors, parser, age, a, b,
                                   [i for i, (v,w) in enumerate(zip(left, right)) if v != w])
            assert all(a[n] == b[n] for n in 'AXYP'), (actors, parser, age, a, b)
            samples.append((a['CPU'], b['CPU']))
        receipt[f'{actors}_parser_{int(parser)}'] = dict(updates=len(samples),
            saved_cycles=[min(a-b for a,b in samples), max(a-b for a,b in samples)],
            old_cycles=[min(a for a,b in samples), max(a for a,b in samples)],
            new_cycles=[min(b for a,b in samples), max(b for a,b in samples)])
    return receipt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=OUT)
    args = ap.parse_args()
    raw = BASE.read_bytes()
    assert P.sha(raw) == PIN
    args.output.mkdir(parents=True, exist_ok=True)
    rows = patches(raw, args.output)
    after = install(raw, rows)
    images = [P.bundle(raw), P.bundle(after)]
    data = dict(base_ROM_SHA256=PIN, expected_memory_ROM_SHA256=P.sha(after), patches=rows)
    for test in (foreign, mini, whole):
        data[test.__name__] = test(images)
        print(test.__name__, data[test.__name__], flush=True)
    paths = [SOURCE, Path(__file__), R / 'src/x5_bounce.s',
             R / 'tools/audit/profile_mini_busy_1108_v1.py',
             R / 'tools/audit/check_mini_funded_actor_1108_v3.py',
             R / 'tools/audit/check_mini_visibility_dispatch_1110_v1.py']
    data.update(passed=True, source_CPU_only=True, ROM_written=False,
                bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes()) for p in paths})
    (args.output / 'movement-CPU.json').write_text(json.dumps(data, indent=2)+'\n')


if __name__ == '__main__':
    main()
