"""Observe the first native terrain writes after the original 64px pipe climb."""

import argparse
import json
from pathlib import Path

import check_prince_pose_reservation_1103_v186 as Q
from observe_chip_committed_write import lua
from prepare_prince_climb_exit_trace_1109 import NAMES, TRACE
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import R, prepare, sha


OLD = R / 'build/prince-full11-native-1110-v4'
PROOF = R / 'build/prince-climb-descent-1110/shaft-proof.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ready, control, negative = OLD / 'ready.json', OLD / 'controller.lua', OLD / 'capture/full11.json'
    old, route, proof = (json.loads(path.read_text()) for path in (ready,negative,PROOF))
    assert old['ROM_sha256'] == route['ROM_sha256'] == proof['expected_memory_only_SHA256']
    assert old['bindings'][str(control.resolve())] == sha(control)
    assert not route['passed'] and route['route']['index'] == 2 and route['HP'] == 5
    top = route['route']['on_top']
    assert (top['world_x'],top['native_y'],top['physical_foot']) == (723,112,145)
    rom = Path(old['ROM'])
    assert sha(rom) == old['ROM_sha256']
    base, _ = Q.M.OLD.image()
    raw = rom.read_bytes()
    points = {}
    for name in NAMES:
        pc, at = Q.I.address(base,name),Q.I.location(base,name)
        assert raw[at:at+3] == base['raw'][at:at+3],name
        points[name] = dict(pc=pc,physical=at-16,op=raw[at])
    at = 16 + 10*8192 + (0xa2dc & 0x1fff)
    assert raw[at:at+2] == bytes.fromhex('8575')
    points['generic native right clamp'] = dict(pc=0xa2dc,physical=at-16,op=0x85)
    trace = once(TRACE,'EXACT_INGRESS',lua(points))
    trace = once(trace,'pipeRoute.exit_trace = exitRows','route.third_pipe_writers = exitRows')
    trace = once(trace,"part=='pipe-over' and admitted-partCommit>=44 and admitted-partCommit<=76",
                 "part=='full11' and route.index==2 and admitted>=1187 and admitted<=1200")
    trace = once(trace,'qx<408 or qx>=496 or qy<144 or qy>212','qx<688 or qx>=784 or qy<128 or qy>216')
    anchor = 'local function controls_tick(finish)'
    source = once(control.read_text(),anchor,trace+'\n'+anchor)
    assert 'emu.write(' not in source
    prepare(args.output,rom,source,[Path(__file__),ready,control,negative,PROOF],
            expected=old['ROM_sha256'],timeout=225,allow_interactive=True,
            scope='Unchanged full route through the real 64px pipe descent with bounded native writer trace.')


if __name__ == '__main__':
    main()
