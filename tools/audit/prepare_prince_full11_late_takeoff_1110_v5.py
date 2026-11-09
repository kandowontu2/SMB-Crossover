"""Try original running A at the first recovered running pose near a tall pipe."""

import argparse
import json
from pathlib import Path

from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import R, prepare, sha


OLD = R / 'build/prince-full11-native-1110-v4'
TRACE = R / 'build/prince-third-pipe-writer-1110/capture/full11.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ready, control, negative = OLD / 'ready.json', OLD / 'controller.lua', OLD / 'capture/full11.json'
    old, failed, trace = (json.loads(path.read_text()) for path in (ready,negative,TRACE))
    assert old['ROM_sha256'] == failed['ROM_sha256'] == trace['ROM_sha256']
    assert old['bindings'][str(control.resolve())] == sha(control)
    assert not failed['passed'] and failed['route']['index'] == 2 and failed['HP'] == 5
    top = failed['route']['on_top']
    assert (top['world_x'],top['native_y'],top['physical_foot']) == (723,112,145)
    assert any(r['Main']==1192 and r['PC']==0xc42a for r in trace['route']['third_pipe_writers'])
    source = control.read_text()
    source = once(source, "   if o.kind=='pipe' and not route.aerial_attempt and x<=o.left-67 then",
                  "   local lateTall=o.kind=='pipe' and o.top==144 and x<=o.left-17\n"
                  "   if o.kind=='pipe' and not route.aerial_attempt and (x<=o.left-67 or lateTall) then")
    source = once(source, " if o and o.kind=='pipe' and x>=o.left-48 then routeMode('settle',{});return end",
                  " if o and o.kind=='pipe' and x>=o.left-48\n"
                  "    and (o.top~=144 or route.aerial_attempt or x>=o.left-16) then\n"
                  "  routeMode('settle',{});return\n end")
    assert 'emu.write(' not in source
    prepare(args.output,Path(old['ROM']),source,[Path(__file__),ready,control,negative,TRACE],
            expected=old['ROM_sha256'],timeout=225,allow_interactive=True,
            scope='Same exact image; late original running-A admission near genuine 64px pipe.')


if __name__ == '__main__':
    main()
