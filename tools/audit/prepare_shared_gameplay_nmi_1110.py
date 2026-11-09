"""Add a bounded interrupted-PC observer to the verified Bill replay."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_current_helper_3_3_1110 import PIN, ROM
from prepare_selected_native_packet_v1 import R, prepare, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output
    prior = R / 'build/shared-gameplay-cadence-1110/current-bill'
    ready, controller = (prior / name for name in ('ready.json', 'controller.lua'))
    template = json.loads(ready.read_text())
    assert template['ROM_sha256'] == PIN and template['bindings'][str(controller)] == sha(controller)
    old = prior / 'capture/result.json'
    profile = Path(__file__).with_suffix('.lua').with_name('shared_gameplay_nmi_1110.lua')
    script = controller.read_text(encoding='utf-8')
    replacements = (
        ('local function count(phase, countFrames, lastX)', profile.read_text(encoding='utf-8') +
         '\nlocal function count(phase, countFrames, lastX)\n profilePhase=phase'),
        (" local file=assert(io.open(OUTPUT..'result.json','w'))",
         " writeDeadlines(idle.lag_nmi+walk.lag_nmi)\n local file=assert(io.open(OUTPUT..'result.json','w'))"),
    )
    for before, after in replacements:
        assert script.count(before) == 1, before
        script = script.replace(before, after)
    prepare(out, ROM, script, {Path(__file__), profile, controller, ready, old}, expected=PIN, timeout=50,
            allow_interactive=True, scope='Bill Easy 1-1 idle/walk. Exact interrupted PC and bank at missed NMIs.')
    subprocess.run([sys.executable, '-B', str(out / 'run.py')], check=True)
    assert json.loads((out / 'capture/result.json').read_text()) == json.loads(old.read_text())


if __name__ == '__main__':
    main()
