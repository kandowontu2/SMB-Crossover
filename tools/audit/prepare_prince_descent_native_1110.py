"""Prepare the bounded native first-pipe projection and landing replay."""

import argparse
import json
from pathlib import Path
import re

from observe_chip_committed_write import lua
from prepare_selected_native_packet_v1 import R, prepare, sha
from prepare_prince_climb_exit_trace_1109 import CONTROLLER, CONTROLLER_SHA, PARENT


OBSERVE = r'''
local projectionPC,projectionBytes=BOUND_PROJECTION
local function firstPipe(s)
 return s.world_x>=445 and s.world_x<480
end
local function pipeLandingObservation()
 if not lastDMA or not lastDMA.complete or lastDMA.complete.host_frame>=frame then return end
 local s=lastDMA.draw.state
 if not firstPipe(s) then return end
 local top=pipeRoute.pipe.top
 local visual=visibleEvidence(lastDMA)
 if pipeRoute.first_projection and not pipeRoute.projection_image
   and s.source_action==7 and s.physical_foot>top and s.native_y==top-32 then
  require(lastDMA.exact and lastDMA.body_preserved and visual.within_first8_opaque_pixels>0,
    'Projected descent retains actual original-pose hardware sprite bytes')
  pipeRoute.projection_image={source=s,hardware=visual}
  shot('prince-first-pipe-descent')
 elseif pipeRoute.donor_landing and not pipeRoute.settled_image
   and s.physical_foot>=top and s.physical_foot<=top+4
   and math.abs(s.native_y-(top-32))<=2 then
  require(lastDMA.exact and lastDMA.body_preserved and visual.within_first8_opaque_pixels>0,
    'Original terrain landing retains actual hardware sprite bytes')
  pipeRoute.settled_image={source=s,hardware=visual}
  shot('prince-first-pipe-settled')
 end
end
emu.addMemoryCallback(function()
 if part~='pipe-over' or pipeRoute.first_projection or not sourceActive() then return end
 local at=emu.convertAddress(projectionPC)
 if not at or at.memType~=emu.memType.nesWorkRam or at.address~=2*8192+projectionPC-0xc000 then return end
 for i,v in ipairs(projectionBytes)do
  assert(ram(projectionPC+i-1)==v,'Exact current cold-backed projection')
 end
 local before=state()
 local top=pipeRoute.pipe.top
 if before.source_action~=7 or before.physical_foot<=top or not firstPipe(before) then return end
 onReturn(function()
  local after=state()
  if after.native_y~=top-32 or before.native_y==after.native_y then return end
  require(before.source_x==after.source_x and before.source_y==after.source_y
    and before.physical_foot==after.physical_foot and before.source_frame==after.source_frame
    and before.world_x==after.world_x and before.phase==after.phase,
    'Projection changes only native Y before native collision')
  pipeRoute.first_projection={before=before,after=after,frame=frame,Main=admitted}
 end)
end,emu.callbackType.exec,projectionPC)
emu.addMemoryCallback(function()
 if part~='pipe-over' or pipeRoute.donor_landing or not pipeRoute.first_projection or not sourceActive() then return end
 local at=emu.convertAddress(0xc362)
 if not at or at.memType~=emu.memType.nesWorkRam or at.address~=2*8192+0x362 then return end
 assert(ram(0xc362)==0xb9 and ram(0xc363)==0x11 and ram(0xc364)==0xc6,'Original donor landing adapter')
 local before=state()
 local surface=ps(0x7f)+256*ps(0x80)
 if before.source_action~=7 or surface~=pipeRoute.pipe.top or not firstPipe(before) then return end
 onReturn(function()
  pipeRoute.donor_landing={before=before,after=state(),surface=surface,frame=frame,Main=admitted}
 end)
end,emu.callbackType.exec,0xc362)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    proof = json.loads(args.proof.read_text())
    assert proof['passed'] and sha(args.rom) == proof['expected_memory_only_SHA256']
    assert sha(CONTROLLER) == CONTROLLER_SHA
    for path,digest in proof['bindings'].items():
        assert sha(Path(path)) == digest,path
    controller = CONTROLLER.read_text()
    assert controller.count(PARENT)==1 and controller.count('local function controls_tick(finish)')==1
    controller = controller.replace(PARENT,proof['expected_memory_only_SHA256'])
    controller,n = re.subn(r'^Q\.cookie=\{[\d,]+\}$',
                           'Q.cookie='+lua(list(bytes.fromhex(proof['Prince_cookie']))),controller,flags=re.M)
    assert n==1
    worker = args.proof.with_name('climb-descent.bin')
    pc,stop = proof['layout']['descent_half_open']
    data = worker.read_bytes()
    assert stop-pc==len(data)-178 and data[178:183] == bytes.fromhex('ad16c6c907')
    observe = OBSERVE.replace('BOUND_PROJECTION',f'{pc},{lua(list(data[178:183]))}')
    anchor = 'local function controls_tick(finish)'
    controller = controller.replace(anchor,observe+'\n'+anchor)
    anchor = " elseif part=='pipe-over'then\n  if wx()>=496"
    assert controller.count(anchor)==1
    controller = controller.replace(anchor," elseif part=='pipe-over'then\n  pipeLandingObservation()\n  if wx()>=496")
    old = "   completePart();shot('prince-first-pipe-cleared')"
    assert controller.count(old)==1
    controller = controller.replace(old,'''   require(pipeRoute.first_projection and pipeRoute.donor_landing
     and pipeRoute.projection_image and pipeRoute.settled_image,
     'Native descent projection, donor landing and both hardware views were observed')
   completePart()''')
    old = "   if shots<3 then shot('prince-original-pipe-hang')end\n"
    assert controller.count(old)==1 and 'emu.write(' not in controller
    controller = controller.replace(old,'')
    prepare(args.output,args.rom,controller,[Path(__file__),CONTROLLER,args.proof,worker],
            expected=proof['expected_memory_only_SHA256'],timeout=150,allow_interactive=True,
            scope='Unchanged first-pipe controller with source-verified descent, real landing and two hardware pose views.')


if __name__ == '__main__':
    main()
