"""Prepare an exact-image, controller-only full 1-1 Prince replay."""

import argparse
import json
from pathlib import Path

from prepare_selected_native_packet_v1 import R, prepare, sha


FIRST = R/'build/prince-descent-native-1110/native'
READY = FIRST/'ready.json'
BASE = FIRST/'controller.lua'
ROUTE = R/'tools/playthroughs/prince_full11_1110_v1.lua'
PIN = '37d3146b2441142c50a3b44b74af074c01192d61a567212ebf70c5ea1142b2d7'


def once(source,old,new):
    assert source.count(old)==1,old
    return source.replace(old,new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    bound = json.loads(READY.read_text())
    capture = json.loads((FIRST/'capture/prince-diagnostic.json').read_text())
    assert bound['ROM_sha256'] == capture['ROM_sha256'] == PIN and capture['passed']
    assert capture['first_pipe_route']['first_pipe_cleared']
    assert bound['bindings'][str(BASE.resolve())] == sha(BASE)
    rom = Path(bound['ROM'])
    assert sha(rom) == PIN
    src = BASE.read_text()
    src = once(src,'local function control_keys()','''local fullKeys
local function control_keys()
 if part=='full11' then return fullKeys()end''')
    anchor = 'local function controls_tick(finish)'
    src = once(src,anchor,ROUTE.read_text()+'\nfullKeys=function()return route.pad end\n'+anchor)
    src = once(src,anchor,anchor+"\n if part=='full11' then fullTick(finish);return end")
    src = once(src,"   shot('prince-after-draw-DMA')\n",'')
    src = once(src,"  shot('prince-first-pipe-descent')\n",'')
    src = once(src,'''   summary(true,'Actual originalUp first32pxpipe cleared and far-side floor landed; native lives retained, genuine HP injuries recorded')
   csv:close();finish()''',"""   beginPart('full11')
   routeBegin()""")
    src = once(src,'Q.maxFrames=12000','Q.maxFrames=18000') if 'Q.maxFrames=12000' in src else once(src,'["maxFrames"]=12000','["maxFrames"]=18000')
    src = once(src,'"full_stage":false,"helpers_added":false','"full_stage":true,"helpers_added":false')
    assert 'emu.write(' not in src
    prepare(args.output,rom,src,[Path(__file__),BASE,READY,ROUTE,FIRST/'capture/prince-diagnostic.json'],
            expected=PIN,timeout=225,allow_interactive=True,
            scope='Cold actual Prince, original movement, native first pipe and supported full-1-1 controller continuation.')


if __name__ == '__main__':
    main()
