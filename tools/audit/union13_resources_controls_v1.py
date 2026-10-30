"""Retarget the unchanged qualified renderer assertions to both V13 stages."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
O = R/'build/character-host-union-resources-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    assert not (O/'controls.json').exists()
    proof = json.loads((O/'ice/build-proof.json').read_text())
    for path, digest in proof['source_bindings'].items():
        assert sha(path) == digest, path
    inputs = dict(proof['source_bindings'])
    cases = [dict(name='pn', original='parodius_chr_compact_controls_v1.py', edits=[
        ("O = R / 'build/parodius-chr-compact-v1'", "O = R / 'build/character-host-union-resources-v1/pn'"),
        ("R / 'build/character-host-union-v5/candidate.nes'", "R / 'build/character-host-union-v13/candidate.nes'")]),
        dict(name='ice', original='ice_pose_aliases_controls_v1.py', edits=[
        ("O=R/'build/ice-pose-aliases-v2'", "O=R/'build/character-host-union-resources-v1/ice'"),
        ("R/'build/parodius-chr-compact-v1/candidate.nes'", "R/'build/character-host-union-resources-v1/pn/candidate.nes'")])]
    receipts = {}
    for case in cases:
        original = R/'tools/audit'/case['original']
        text = original.read_text()
        for old, new in case['edits']:
            text = once(text, old, new)
        driver = O/(case['name']+'-controls-adapter.py')
        assert not driver.exists()
        driver.write_text(text, newline='\n')
        result = subprocess.run([sys.executable, str(driver)], cwd=R, capture_output=True, text=True)
        log = O/(case['name']+'-controls-run.json')
        log.write_text(json.dumps(dict(command=[sys.executable, str(driver)], returncode=result.returncode,
                                       stdout=result.stdout, stderr=result.stderr), indent=2)+'\n')
        assert result.returncode == 0, result.stdout+result.stderr
        receipt = O/case['name']/'controls.json'
        value = json.loads(receipt.read_text())
        assert value['passed']
        receipts[case['name']] = value
        for path in [original, driver, receipt, log]:
            inputs[str(path)] = sha(path)
    for path in [Path(__file__).resolve(), O/'pn/build-proof.json', O/'ice/build-proof.json']:
        inputs[str(path)] = sha(path)
    report = dict(passed=True, native=False, ROM_sha256=proof['ROM_sha256'],
                  exact_V13_reproduction=True, PN_stage=receipts['pn'], Ice_stage=receipts['ice'],
                  scope='Only original/candidate/output paths changed in frozen renderer controls. Every behavior assertion is unchanged. Ice compares against the already dense PN stage, so its all-CHR-exact assertion remains true.',
                  source_bindings=inputs,
                  limits=['No native PPU/gameplay or new character admission from these CPU fixtures.',
                          'Existing V13 Bill extra missed frame remains unaddressed by data compaction.'])
    (O/'controls.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, PN_OAM_pairs=receipts['pn']['decoded_actual_OAM_pairs'],
                         Ice_cases=receipts['ice']['cases'], Ice_parts=receipts['ice']['authentic_OAM_parts_checked'])))


if __name__ == '__main__':
    main()
