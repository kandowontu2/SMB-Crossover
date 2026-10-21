"""Retain GV's missing observer-label negative and restart with that field removed."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent = R / 'tools/audit/run_easy49_sophia_gq_gv.py'
    negative = R / 'build/roster-through-2-2/root49gv-sophia-live-11-v0-mmc3/manifest.json'
    assert json.loads(negative.read_text()).get('result') is None
    text = parent.read_text()
    assert text.count(",'RgPower'") == 1
    text = text.replace(",'RgPower'", '')
    text = text.replace('root49-gq-sophia-route-gv', 'root49-gq-sophia-route-gw')
    text = text.replace('root49gv-sophia-live', 'root49gw-sophia-live')
    anchor = '    H.mkdir()'
    assert text.count(anchor) == 1
    checks = """    for name in ('WorldNumber', 'LevelNumber', 'SelectedCharacter',
            'CrossoverBehaviorVersion', 'Player_X_Position', 'Player_PageLoc',
            'Player_Y_Position', 'Player_Y_HighPos', 'Player_State', 'PlayerStatus',
            'PlayerSize', 'RgPreviousButtons', 'InjuryTimer', 'ObjectOffset',
            'PlayerOutlinesOff', 'BoundingBox_UL_Corner'):
        assert im.sym(name)['val'] is not None, name
"""
    text = text.replace(anchor, checks + anchor)
    driver = V / 'root49-gq-sophia-gw-driver.py'
    assert not driver.exists()
    driver.write_text(text)
    out = V / 'root49-gq-sophia-gw-preparation.json'
    assert not out.exists()
    out.write_text(json.dumps(dict(status='OBSERVER_LABEL_CORRECTION_ONLY',
        parent_sha256=sha(parent), retained_GV_negative_sha256=sha(negative),
        corrected_driver_sha256=sha(driver),
        correction='GV attempted to log a nonexistent RgPower label. Remove that observation field, validate all remaining labels before launch; same immutable GQ ROM/controller. No native game defect inferred.',
        runtime_changes=False), indent=2) + '\n')
    raise SystemExit(subprocess.run([sys.executable, str(driver)], cwd=R).returncode)


if __name__ == '__main__':
    main()
