"""Rebind the full Prince controller and observe genuine original ledge alignment."""

import argparse
import json
from pathlib import Path
import re

from observe_chip_committed_write import lua
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import R, prepare, sha


OLD = R / 'build/prince-full11-native-1110-v3'
PROOF = R / 'build/prince-climb-descent-1110/shaft-proof.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ready, control, negative = OLD / 'ready.json', OLD / 'controller.lua', OLD / 'capture/full11.json'
    old, route, proof = (json.loads(path.read_text()) for path in (ready, negative, PROOF))
    assert proof['passed'] and not proof['ROM_written'] and not proof['Mesen_run']
    assert old['ROM_sha256'] == route['ROM_sha256'] == proof['previous_private_SHA256']
    assert old['bindings'][str(control.resolve())] == sha(control)
    assert proof['bindings'][str(negative.resolve())] == sha(negative)
    assert not route['passed'] and route['route']['index'] == 2 and route['HP'] == 5
    worker = PROOF.with_name('tall-shaft-workers.bin')
    assert proof['bindings'][str(worker.resolve())] == sha(worker)
    blob = worker.read_bytes()
    start, pc = proof['layout']['edge_half_open']
    assert proof['layout']['descent_half_open'] == [pc, start + len(blob)]
    source = control.read_text()
    expected = proof['expected_memory_only_SHA256']
    source = once(source, old['ROM_sha256'], expected)
    cookie, = re.findall(r'Q\.cookie=\{[^}]+\}', source)
    source = once(source, cookie, 'Q.cookie=' + lua(list(bytes.fromhex(proof['Prince_cookie']))))
    projection, = re.findall(r'local projectionPC,projectionBytes=\d+,\{[^}]+\}', source)
    source = once(source, projection, f'local projectionPC,projectionBytes={pc},' +
                  lua(list(blob[pc-start:pc-start+5])))
    anchor = 'local routeCSV'
    source = once(source, anchor, f'''local typedLedgePC,typedLedgeBytes={start},{lua(list(blob[:5]))}
route.alignments={{}}
emu.addMemoryCallback(function()
 if part~='full11' or #route.alignments>=16 or not sourceActive() then return end
 local at=emu.convertAddress(typedLedgePC)
 if not at or at.memType~=emu.memType.nesWorkRam or at.address~=2*8192+typedLedgePC-0xc000 then return end
 for i,v in ipairs(typedLedgeBytes)do assert(ram(typedLedgePC+i-1)==v,'Cold-backed typed ledge bytes')end
 local sp=emu.getState()['cpu.sp']
 local caller=ram(0x101+sp)+256*ram(0x102+sp)+1
 assert(caller==0xb0dd,'Actual original F801 ledge alignment caller')
 local q={{Main=admitted,obstacle=route.index,before=state(),caller=caller}}
 route.alignments[#route.alignments+1]=q
 onReturn(function()q.after=state()end)
end,emu.callbackType.exec,typedLedgePC)
'''+anchor)
    assert 'emu.write(' not in source
    prepare(args.output,args.rom,source,[Path(__file__),ready,control,negative,PROOF,worker],
            expected=expected,timeout=225,allow_interactive=True,
            scope='Same full-route controller with actual original F801 shaft/cap alignment observation.')


if __name__ == '__main__':
    main()
