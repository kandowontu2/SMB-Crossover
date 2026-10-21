"""Correct GP's above-screen air-jump assumption without changing native receipts."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent = R / 'tools/audit/review_easy49_bass_support_gp.py'
    source = parent.read_text()
    original = "        assert z['fresh'] & 128 and z['yHigh'] == 1"
    replacement = """        assert z['fresh'] & 128
        if z['state'] == 0:
            assert z['yHigh'] == 1
        else:
            assert z['yHigh'] in (0, 1)
        z['canonical_world_y'] = (z['yHigh']-1)*256+z['y']"""
    assert source.count(original) == 1
    source = source.replace(original, replacement)
    source = source.replace('root49-el-bass-support-gp.json', 'root49-el-bass-support-gt.json')
    driver = V / 'root49-el-bass-support-gt-driver.py'
    assert not driver.exists()
    driver.write_text(source)
    report = dict(script_sha256=sha(__file__), retained_GP_reviewer_sha256=sha(parent),
        corrected_driver_sha256=sha(driver),
        retained_negative='GP incorrectly required highY1 for airborne launches. Actual14037 X2326/Y254/high0 is canonical Y-2, a fresh secondary jump with token1 above the screen; no terrain support is required for that air jump. All135 grounded receipts do have highY1.',
        emulated_evidence_changes=False, runtime_changes=False)
    (V / 'root49-el-bass-support-gt-preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    raise SystemExit(subprocess.run([sys.executable, str(driver)], cwd=R).returncode)


if __name__ == '__main__':
    main()
