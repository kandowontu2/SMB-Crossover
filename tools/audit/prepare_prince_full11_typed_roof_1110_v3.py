"""Bind the two-row typed pipe roof and use Up during the original jump arc."""

import argparse
import json
from pathlib import Path
import re

from observe_chip_committed_write import lua
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import R, prepare, sha


OLD = R / 'build/prince-full11-native-1110-v2'
PROOF = R / 'build/prince-climb-descent-1110/two-row-proof.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ready = OLD / 'ready.json'
    controller = OLD / 'controller.lua'
    negative = OLD / 'capture/full11.json'
    old, failure, proof = (json.loads(p.read_text()) for p in (ready, negative, PROOF))
    assert proof['passed'] and not proof['ROM_written'] and not proof['Mesen_run']
    assert old['ROM_sha256'] == failure['ROM_sha256'] == proof['previous_private_SHA256']
    assert old['bindings'][str(controller.resolve())] == sha(controller)
    assert proof['bindings'][str(negative.resolve())] == sha(negative)
    assert not failure['passed'] and failure['route']['index'] == 1 and failure['HP'] == 5
    worker = PROOF.with_name('tall-workers.bin')
    assert proof['bindings'][str(worker.resolve())] == sha(worker)
    pc, end = proof['layout']['descent_half_open']
    start, edge_end = proof['layout']['edge_half_open']
    assert pc == edge_end and len(worker.read_bytes()) == end - start
    hook = worker.read_bytes()[pc - start:pc - start + 5]
    source = controller.read_text()
    expected = proof['expected_memory_only_SHA256']
    source = once(source, old['ROM_sha256'], expected)
    cookie, = re.findall(r'Q\.cookie=\{[^}]+\}', source)
    source = once(source, cookie, 'Q.cookie=' + lua(list(bytes.fromhex(proof['Prince_cookie']))))
    source = once(source, 'local projectionPC,projectionBytes=55397,{173,22,198,201,7}',
                  f'local projectionPC,projectionBytes={pc},' + lua(list(hook)))
    source = once(source, "     and s.physical_foot-24<=o.top+15 then route.pad={'right','up'} end",
                  "     and s.source_action==4 and s.source_frame>=40 and s.source_frame<=42\n"
                  "     and s.physical_foot-24<=o.top+31 then route.pad={'right','up'} end")
    assert 'emu.write(' not in source
    prepare(args.output, args.rom, source, [Path(__file__), ready, controller, negative, PROOF, worker],
            expected=expected, timeout=225, allow_interactive=True,
            scope='Original Prince full route with typed two-row pipe roof and source-arc Up timing.')


if __name__ == '__main__':
    main()
