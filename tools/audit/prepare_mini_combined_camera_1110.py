"""Compose qualified camera lifts and performance components for native QA."""
import argparse
import json
from pathlib import Path
import shutil
from compose_mini_frame_budget_1108 import compose,load,digest
from qualify_mini_busy_1109 import bind_kernel
from prepare_selected_native_packet_v1 import prepare,sha

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
base=Path('build/mini-box-terrain-visible-1110/candidate.nes')
raw=base.read_bytes()
assert digest(raw)=='6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
candidate=bytearray(raw)
paths=[Path(p) for p in (
    'build/mini-camera-lifts-v2-1110/proof.json',
    'build/mini-lift-retention-1110/proof-v2.json',
    'build/mini-movement-admission-1110/movement-CPU.json',
    'build/mini-offscreen-1110/proof.json',
    'build/mini-side-pair-1110/proof.json')]
for i,path in enumerate(paths):
    q=load(path)
    if 'base_ROM_SHA256' in q:
        q['parent_SHA256']=q['base_ROM_SHA256']
        q['expected_memory_only_SHA256']=q.get('expected_memory_only_SHA256',q.get('expected_memory_ROM_SHA256'))
    parent=bytes(candidate) if i==1 else raw
    compose(parent,candidate,q,parent=digest(parent))
out=args.output;out.mkdir()
rom=out/'candidate.nes';rom.write_bytes(candidate)
for ext in ('.dbg','.lbl'):shutil.copyfile(base.with_suffix(ext),rom.with_suffix(ext))
meta=load(base.with_suffix('.json'))
meta.pop('whole_GameCore',None)
meta.update(parent_SHA256=digest(raw),candidate_SHA256=sha(rom),camera_lifts=True,
            composed_proofs={str(p):sha(p) for p in paths},verification='Private native candidate; no delivery yet')
rom.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
source=Path('build/mini-move-offscreen-recovery-v2-1110/controller.lua')
kernel=Path('build/mini-lift-retention-1110/kernel-v2.bin')
text=source.read_text().replace('b096eaa968c1b52b60477b7105fae79b2b13bee164e00414795ba7742845c673',sha(rom))
text=bind_kernel(text,kernel)
text=text.replace(sha(Path('build/mini-kernel-transport-1109/v2/kernel.bin')),sha(kernel))
old=' local slot = ram(0xc30b)-1\n'
assert text.count(old)==1
text=text.replace(old,''' local slot = -1
 for candidate=0,5 do
  if read(L.Enemy_Flag+candidate)==1 and read(L.Enemy_ID+candidate)==0x25
   and read(L.Enemy_X_Position+candidate)+256*read(L.Enemy_PageLoc+candidate)==left then
   slot=candidate;break
  end
 end
''')
text=text.replace('local mini_lift_runs = {}','local mini_lift_runs, camera_lift_spawns = {}, {}')
old='if not row.spawn_top then row.spawn_top=top;row.spawn_frame=frame;row.slot=slot end'
new='''if not row.spawn_top then
   local spawn=camera_lift_spawns[left]
   check(spawn~=nil,'Camera lift has an observed native constructor')
   row.spawn_top=spawn.top;row.spawn_frame=spawn.frame;row.spawn_relative_x=spawn.relative_x;row.slot=slot
  end'''
assert text.count(old)==1;text=text.replace(old,new)
text+='''
-- Observe constructor ingress after the real actor fields are published.
-- No emulator writes: every lift must start at or beyond the right edge.
emu.addMemoryCallback(guard(function()
 local loc=emu.convertAddress(0xa74f)
 if not loc or loc.memType~=emu.memType.nesPrgRom or loc.address~=0x474f then return end
 local state=emu.getState();local slot=state['cpu.x']
 if read(L.SelectedCharacter)~=41 or slot>5 or read(L.Enemy_ID+slot)~=0x25 then return end
 local x=read(L.Enemy_X_Position+slot)+256*read(L.Enemy_PageLoc+slot)
 if x~=560 and x~=688 and x~=864 then return end
 local camera=read(0x071d)*256+read(0x071f)
 local relative=x-camera
 check(relative>=256 and relative<=288,'Lift begins offscreen before its edge enters view')
 check(not camera_lift_spawns[x],'Visible lift is not reconstructed/retargeted')
 camera_lift_spawns[x]={frame=frame,slot=slot,top=read(L.Enemy_Y_Position+slot),relative_x=relative}
end),emu.callbackType.exec,0xa74f)
local beforeCameraFinish=profileFinish
profileFinish=function()
 beforeCameraFinish()
 local f=assert(io.open(OUTPUT..'camera-lifts.json','w'))
 f:write(json(camera_lift_spawns));f:close()
end
'''
prepare(out/'route',rom,text,{source,kernel,kernel.with_suffix('.lbl'),Path(__file__),*paths},
        expected=sha(rom),timeout=180,allow_interactive=True,
        scope='Controller-only full1-1: retained native lifts construct offscreen and enter with scrolling; three actual board/departures, both lives, active1-2 required.')
print(json.dumps(dict(candidate_SHA256=sha(rom),run=str(out/'route/run.py'))))
