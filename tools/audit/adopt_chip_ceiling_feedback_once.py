"""Install the verified one-byte Chip/Dale feedback repair; never rerun."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from prepare_chip_ceiling_feedback import feedback_source

ROOT = Path(__file__).resolve().parents[2]
PARENT = '054d9e33a84f628947b0dea15914ba2aae7796ca610a25548eab96407064384a'
CURRENT = '274fff8613d98a281d7549d13e59430c4d6b4553eb16bd9d2c651e0b409c8b3b'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidates', type=Path, required=True)
    args = p.parse_args()
    candidates = args.candidates.resolve()
    cpu = json.loads((candidates / 'cpu-proof.json').read_text())
    assert cpu['passed'] and len(cpu['rows']) == 2
    evidence = []
    for mapper in ['mmc5', 'mmc3']:
        digest = sha(candidates / mapper / 'candidate.nes')
        for name in ['native-routes-v2', 'direct-v1']:
            proof_path = candidates / mapper / name / 'proof.json'
            proof = json.loads(proof_path.read_text())
            assert proof['passed'] and proof['complete'] and proof['ROM_sha256'] == digest
            assert len(proof['runs']) == (4 if name.startswith('native') else 2)
            evidence.append(dict(path=str(proof_path), sha256=sha(proof_path)))
    assert sha(candidates / 'mmc5/candidate.nes') == CURRENT
    source = ROOT / 'src/chip_dale_motion.s'
    before = source.read_bytes()
    after = feedback_source(source)
    output = candidates / 'adoption-v1'
    output.mkdir(exist_ok=False)
    (output / 'chip_dale_motion.before.s').write_bytes(before)
    source.write_bytes(after)
    rom = output / 'candidate.nes'
    try:
        with (output / 'root-build.log').open('w') as log:
            result = subprocess.run([sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
                                     '--source-overlay', str(ROOT), '--output', str(rom)],
                                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        assert result.returncode == 0 and sha(rom) == CURRENT
    except BaseException:
        source.write_bytes(before)
        raise
    destination = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(destination) == PARENT
    backup = output / ('SMB-Crossover-Current-MMC5-' + PARENT + '.nes')
    shutil.copy2(destination, backup)
    assert sha(backup) == PARENT
    shutil.copy2(rom, destination)
    assert sha(destination) == CURRENT
    receipt = dict(adopted=True, goal_complete=False, mapper='mmc5', ROM_sha256=CURRENT,
                   parent_ROM_sha256=PARENT, root_build=str(rom), installed=str(destination),
                   old_download_backup=str(backup), changed_source='src/chip_dale_motion.s',
                   source_before_sha256=hashlib.sha256(before).hexdigest(), source_after_sha256=sha(source),
                   root_build_bytes_exact_to_native_and_pixel_tested_candidate=True,
                   native_route_cases=8, independent_full_PPU_routes=4, component_cases=13440,
                   evidence=evidence,
                   scope='Adopt only the shared Chip/Dale positive ceiling-feedback instruction, exactly one ROM byte on the MMC5 build. Native Easy/Hard routes on both mappers and independent ChipEasy/DaleHard pixels pass. Human overview samples inspected. Original failures retained; MMC3 architecture remains private/unadopted due separate parser-cycle concern. This does not certify all current-hash roster/powerup/passive/SFX/lag/source-fidelity requirements.')
    (output / 'proof.json').write_text(json.dumps(receipt, indent=2))
    checkpoint = ROOT / 'build/verification/chip-ceiling-feedback'
    checkpoint.mkdir(exist_ok=False)
    (checkpoint / 'proof.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
