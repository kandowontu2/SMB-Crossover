"""Read-only prospective ordinary-enemy bounding-box shortcut analysis.

The small proposed program executes only in a standalone unit interpreter's
RAM. It never patches an NES ROM or supplies emulator/gameplay acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import itertools
import json
import random

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('native_unit', ROOT/'tools/audit/verify_native_relocation.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    before, labels = native.load(a.rom)
    after, _ = native.load(a.rom)
    word = lambda n: [labels[n] & 255, labels[n] >> 8]
    # LDA offscreen / BNE native / LDA0 / STA masked,X / JMP shared setup /
    # native:JMP original. The real caller guarantees slot0..5.
    program = [0xad, *word('Enemy_OffscreenBits'), 0xd0, 8, 0xa9, 0,
               0x9d, *word('EnemyOffscrBitsMasked'), 0x4c, *word('SetupEOffsetFBBox'),
               0x4c, *word('GetEnemyBoundBox')]
    proposed = 0x6000
    after.memory[proposed:proposed+len(program)] = program
    rng = random.Random(0x20235)
    cases = itertools.chain(
        itertools.product(range(6), range(256), (0, 1, 0x44, 0x48, 0xff), (0, 1, 8, 11)),
        ((rng.randrange(6), rng.randrange(256), rng.randrange(256), rng.randrange(12)) for _ in range(10000)))
    stats = {k: {'cases': 0, 'delta_min': 10000, 'delta_max': -10000, 'before_sum': 0, 'after_sum': 0}
             for k in ('zero', 'fallback')}
    count = 0
    for slot, relative, offscreen, box in cases:
        ram = [rng.randrange(256) for _ in range(2048)]
        def put(name, value, index=0): ram[labels[name]+index] = value & 255
        put('ObjectOffset', (slot, 5-slot, 0, 5, 127, 128, 255)[count % 7])
        put('Enemy_BoundBoxCtrl', box, slot)
        put('Enemy_OffscreenBits', offscreen)
        put('Enemy_Rel_XPos', relative)
        put('Enemy_Rel_YPos', (0, 31, 32, 184, 223, 255)[count % 6])
        put('Enemy_X_Position', (relative+count*17)&255, slot)
        put('Enemy_PageLoc', (0, 1, 127, 255)[count % 4], slot)
        put('ScreenLeft_X_Pos', (count*17)&255)
        put('ScreenLeft_PageLoc', (0, 1, 127, 255)[(count//4)%4])
        outputs, clocks = [], []
        for cpu, entry in ((before, labels['GetEnemyBoundBox']), (after, proposed)):
            cpu.memory[:2048] = ram
            cpu.a, cpu.x, cpu.y, cpu.p = count & 255, slot, (count*29)&255, (count*73)&255
            cpu.sp = (0xfd, 0xed, 0xdd)[count % 3]
            cpu.stPushWord(0x7eff)
            cpu.pc, cpu.processorCycles = entry, 0
            steps = 0
            while cpu.pc != 0x7f00:
                cpu.step(); steps += 1
                assert steps < 1000, (count, hex(cpu.pc))
            outputs.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp,
                            tuple(cpu.memory[:256]), tuple(cpu.memory[512:2048])))
            clocks.append(cpu.processorCycles)
        assert outputs[0] == outputs[1], {'case': count, 'slot': slot, 'relative': relative,
                'offscreen': offscreen, 'box': box, 'registers': [o[:5] for o in outputs],
                'ram': [(i,before.memory[i],after.memory[i]) for i in range(2048)
                        if not 256 <= i < 512 and before.memory[i] != after.memory[i]][:10]}
        s = stats['zero' if offscreen == 0 else 'fallback']
        delta = clocks[1]-clocks[0]
        s['cases'] += 1; s['delta_min'] = min(s['delta_min'], delta); s['delta_max'] = max(s['delta_max'], delta)
        s['before_sum'] += clocks[0]; s['after_sum'] += clocks[1]
        count += 1
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    report = {'result': 'passed-prospective-analysis-only', 'cases': count, 'rom_sha256': sha(a.rom),
              'script_sha256': sha(Path(__file__)), 'interpreter_sha256': sha(ROOT/'tools/audit/verify_native_relocation.py'),
              'program': program, 'stats': stats, 'compared': 'A/X/Y/allP/SP and native2048RAM except discarded stack',
              'limits': ['Proposed bytes are interpreter RAM only; no candidate ROM was created or tested.',
                         'Real actual-caller/interrupt/gameplay-state/CPU/DMA evidence is required before production adoption.']}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS prospective analysis only', count, stats)


if __name__ == '__main__': main()
