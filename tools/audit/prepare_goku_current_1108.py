"""Replay Goku's Hard 1-1 route from the exact Downloads launch path."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from nightly_patch_guard_v1 import check
from prepare_prince_resume_1108 import CURRENT, NIGHTLY
from prepare_selected_native_packet_v1 import R, prepare, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert check(NIGHTLY)['ROM_sha256'] == CURRENT
    rom = R/'build/mini-two-fireballs-1103/mini-empty-draw.nes'
    assert sha(rom) == CURRENT
    original = R/'build/goku-gap-1102-v4/native/controller.lua'
    old_policy = original.parents[1]/'policy.lua'
    policy = R/'tools/playthroughs/dragon_power_11_current_1108.lua'
    old_pin = '22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'
    controller = original.read_text()
    assert controller.count(old_pin) == controller.count(old_policy.as_posix()) == 1
    controller = controller.replace(old_pin,CURRENT).replace(old_policy.as_posix(),policy.as_posix())
    policies = R/'tools/playthroughs'
    refs = [Path(__file__), original, old_policy, policy, NIGHTLY,
            R/'build/goku-source-route-1102-v3/policy.lua', policies/'full_roster_policy_og.lua',
            *(policies/f'dragon_power_11_v{version}.lua' for version in range(3,8))]
    prepare(output, rom, controller, refs, expected=CURRENT, timeout=180,
            allow_interactive=True, scope='Installed MMC5 ROM, Goku Hard 1-1 with grounded takeoff at the last gap.')
    ready = output/'ready.json'
    packet = json.loads(ready.read_text())
    packet['ROM'] = str(NIGHTLY)
    ready.write_text(json.dumps(packet,indent=2)+'\n')
    return subprocess.call([sys.executable,'-B',output/'run.py'])


if __name__ == '__main__':
    raise SystemExit(main())
