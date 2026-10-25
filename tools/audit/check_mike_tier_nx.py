"""Compare linked tier ABI/results to NW; only HUD invalidation may be added."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import re
from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[2]


def labels(path):
    result = {}
    for line in path.read_text().splitlines():
        match = re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\w+)', line)
        if match:
            result[match[2]] = int(match[1], 16)
    return result


def execute(raw, entry, owned, health, previous, dirty, status):
    memory = [0] * 65536
    memory[0xa000:0xc000] = raw[16 + 96 * 8192:16 + 97 * 8192]
    memory[0x5f32], memory[0x5f30] = owned, health
    memory[0x5c0c], memory[0x5c0e] = previous, dirty
    memory[0x1fe], memory[0x1ff] = 0xff, 0x5f
    cpu = MPU(memory=memory, pc=entry); cpu.sp = 0xfd
    cpu.a, cpu.x, cpu.y, cpu.p = 0x37, 0xa5, 0x77, status
    for _ in range(80):
        if cpu.pc == 0x6000:
            break
        assert 0xa000 <= cpu.pc < 0xc000
        cpu.step()
    assert cpu.pc == 0x6000 and cpu.sp == 0xff
    return (cpu.a, cpu.x, cpu.y, cpu.p & 0xcf), memory[0x5c0c], memory[0x5c0e], cpu.processorCycles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    parent = ROOT / 'build/checkpoints/vic-hud-font-nw/candidate.nes'
    a, b = parent.read_bytes(), args.rom.read_bytes()
    old, new = labels(parent.with_suffix('.lbl')), labels(args.rom.with_suffix('.lbl'))
    assert old['JnEffectiveTier'] == new['JnEffectiveTier']
    checked = 0; overhead = set()
    for owned, health, previous, dirty, status in itertools.product(range(4), range(45), range(4), (0, 7), (0x20, 0x21, 0xa4, 0xef)):
        before = execute(a, old['JnEffectiveTier'], owned, health, previous, dirty, status)
        after = execute(b, new['JnEffectiveTier'], owned, health, previous, dirty, status)
        assert before[:2] == after[:2], (owned, health, previous, before, after)
        assert after[2] == (1 if previous != after[1] else dirty)
        overhead.add(after[3] - before[3]); checked += 1
    report = dict(passed=True, cases=checked, ROM_sha256=hashlib.sha256(b).hexdigest(),
                  baseline_ROM_sha256=hashlib.sha256(a).hexdigest(), extra_cycles=sorted(overhead),
                  scope='Linked bank96 returns identical A/X/Y/meaningful status/effective tier; only UiDirty is added on tier changes. No movement or global performance claim.')
    args.output.write_text(json.dumps(report, indent=2) + '\n'); print(json.dumps(report))


if __name__ == '__main__':
    main()
