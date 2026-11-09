"""Bind all full-route native labels and retain the failed v1 observer."""

import argparse
import json
from pathlib import Path
import re

import measure_prince_climb_descent_1110 as M
from observe_chip_committed_write import lua
from prepare_prince_full11_1110 import ROUTE, PIN, once
from prepare_selected_native_packet_v1 import R, prepare, sha


OLD = R/'build/prince-full11-native-1110'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    prior = OLD/'ready.json'
    controller = OLD/'controller.lua'
    binding = OLD/'capture/binding.json'
    q = json.loads(prior.read_text())
    trace = json.loads(binding.read_text())
    assert q['ROM_sha256'] == trace['ROM_sha256'] == PIN
    assert trace['exit_code'] == 1 and trace['ready_sha256'] == sha(prior)
    assert q['bindings'][str(controller.resolve())] == sha(controller)
    assert q['bindings'][str(ROUTE.resolve())] == sha(ROUTE)
    names = {a or b for a,b in re.findall(r"r\('([^']+)'\)|L\.([A-Za-z_]\w*)",ROUTE.read_text())}
    base = M.image()
    mapping = {name:M.I.address(base,name) for name in sorted(names)}
    assert mapping['WorldNumber']==0x764 and mapping['LevelNumber']==0x761
    src = controller.read_text()
    src = once(src,'Q.maxFrames=8000','Q.maxFrames=18000')
    anchor = '-- Source-phase-aware continuation after the native first pipe proof.'
    src = once(src,anchor,'for n,a in pairs('+lua(mapping)+')do L[n]=a end\n'+anchor)
    assert 'emu.write(' not in src
    prepare(args.output,Path(q['ROM']),src,[Path(__file__),controller,prior,binding,ROUTE],
            expected=PIN,timeout=225,allow_interactive=True,
            scope='Exact native label bindings for controller-only full Prince 1-1 replay.')


if __name__ == '__main__':
    main()
