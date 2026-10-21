"""Continue the verified coral crossing with finer actual water timing scopes."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent = V / 'root49-el-bass-profile-gd-driver.py'
    driver = V / 'root49-el-bass-profile-gg-driver.py'
    assert not driver.exists()
    source = parent.read_text().replace('root49-el-bass-profile-gd', 'root49-el-bass-profile-gg')
    source = source.replace('root49gd-bass-live', 'root49gg-bass-live')
    source = source.replace('root49-gb-bass-22-middle-fish-a', 'root49-ge-bass-22-coral-gap-a')
    # The immutable corrected GD core is reused, not regenerated or edited.
    source = source.replace("core = V / 'root49-el-bass-profile-gg-core.lua'",
        "core = V / 'root49-el-bass-profile-gd-core.lua'")
    anchor = "    hooks.update(NMI=im.hook('NonMaskableInterrupt'), IRQ=im.hook('IrqScrollSplit'))"
    assert source.count(anchor) == 1
    extras = """    for n in ('ExpandedMovement', 'ExpandedWeapons', 'SpecialWeapons',
            'SpecialDrawShots', 'ExpandedDrawShots', 'RosterDrawShots',
            'MetaspriteRenderLoop', 'ExpandedPose', 'CrossoverGraphicsBank',
            'InventoryUpdateDrops', 'InventoryDrawPickups', 'DrawMetasprite',
            'GuestHudOamOrder', 'DrawBrickDebris', 'MegaManFullShotBank',
            'GuestAudioBegin', 'GuestAudioFinish', 'MegaManAudioNativeUpdate'):
        hooks[n] = im.hook(n)
"""
    source = source.replace(anchor, extras + anchor)
    driver.write_text(source)
    report = dict(script_sha256=sha(__file__), parent_driver_sha256=sha(parent),
        derived_driver_sha256=sha(driver),
        reused_core_sha256=sha(V / 'root49-el-bass-profile-gd-core.lua'),
        diagnosis='GD genuinely walks from the112-high ledge and falls into the later gap; no native hostile injury at its24826 pit death. GE changes only controls and must independently cold-verify before this driver accepts it.',
        refined_cost_scope='Add actual expanded/special movement, weapon, draw and audio children to the existing whole-loop scopes. Inclusive times overlap and must not be summed as disjoint CPU work.',
        runtime_changes=False, goal_complete=False)
    (V / 'root49-el-bass-profile-gg-preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    raise SystemExit(subprocess.run([sys.executable, str(driver)], cwd=R).returncode)


if __name__ == '__main__':
    main()
