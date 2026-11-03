"""Preserve the two small horizontal-motion proofs without compiler caches."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/mini-mario-motion-freeze-1103-v4'
DEST = ROOT/'docs/qa/checkpoints/2026-11-03/mini-mario-motion-v4'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__), *(ROOT/'tools/audit'/name for name in (
        'port_mini_mario_ground_x_1103_v2.py', 'port_mini_mario_air_x_1103_v3.py'))]
    expected = [(2, 432760, 328, '662193e07b61fafd5ce089274ab97a24b21d1e99c63a0c4772afcde13a383eb6'),
                (3, 963824, 483, 'd65ee8cf327646fdee069561a18278b1afa361d105322624d34aa8c19bf2ba17')]
    for version, cases, size, digest in expected:
        parent = ROOT/f'build/mini-mario-motion-1103-v{version}'
        receipt = json.loads((parent/'receipt.json').read_text())
        assert receipt['passed'] and receipt['cases'] == cases and receipt['code_bytes'] == size
        stem = 'ground-x' if version == 2 else 'motion-x'
        assert sha((parent/f'{stem}.bin').read_bytes()) == receipt['code_sha256'] == digest
        files += [parent/'receipt.json', *(parent/f'{stem}.{suffix}' for suffix in ('s', 'cfg', 'bin')),
            parent/('original-ground-x.c' if version == 2 else 'original-motion-x.c')]
        if version == 3:
            files.append(parent/'motion-x.lbl')
    DEST.mkdir(parents=True, exist_ok=False)
    target = DEST/'inputs.zip'
    with ZipFile(target, 'w', ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            z.writestr(f.relative_to(ROOT).as_posix(), f.read_bytes())
    assert target.stat().st_size < 64000
    with ZipFile(target) as z:
        for f in files:
            assert z.read(f.relative_to(ROOT).as_posix()) == f.read_bytes()
    result = dict(passed=True, installed=False, ROM_produced=False,
        checkpoint=DEST.relative_to(ROOT).as_posix(), archive_bytes=target.stat().st_size,
        archive_SHA256=sha(target.read_bytes()),
        scope='Original-source C versus assembled 6502 CPU fixtures only. Ground328B/432760cases; unified ground/jump/fall483B/963824cases,98..271cycles. Jump/fall horizontal source token identity independently asserted. Entire supported X-velocity domain, all L/R/run combinations and platform-delta signs; animation/attack branch boundaries. No persistent per-case fixtures or emulator captures.',
        remaining='GB machine-code comparison and full caller/state/Y/jump/swim/native terrain/graphics/audio/lifecycle/menu/1-1. The source ground/air primitives do not constitute a playable Mini Mario. No allocation or helper need established.',
        source_files=[f.relative_to(ROOT).as_posix() for f in files[:3]],
        bindings={f.relative_to(ROOT).as_posix(): sha(f.read_bytes()) for f in files})
    for f in (OUT/'receipt.json', DEST/'receipt.json'):
        f.write_text(json.dumps(result, indent=2)+'\n')
    handoff = ROOT/'docs/qa/continuation-current.json'
    current = json.loads(handoff.read_text())
    current['mini_mario_current_1102'].update(
        motion_status='SOURCE_C_VS_6502_GROUND_AND_AIR_HORIZONTAL_PASS_NO_GAMEPLAY',
        motion_checkpoint=DEST.relative_to(ROOT).as_posix(), motion_scope=result['scope'],
        motion_remaining=result['remaining'])
    handoff.write_text(json.dumps(current, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'bindings'}, indent=2))


if __name__ == '__main__':
    main()
