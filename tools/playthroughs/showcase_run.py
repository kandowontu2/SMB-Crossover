"""Ordinary menu/controller showcase discovery; no emulated state writes."""
from pathlib import Path
import argparse,csv,json,subprocess,sys,hashlib
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from workspace_storage import locate
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mode',choices=('easy','hard'),required=True);p.add_argument('--policy',type=Path,required=True);p.add_argument('--frames',type=int,default=5000);p.add_argument('--mapper',choices=('mmc3','mmc5'),default='mmc3');p.add_argument('--wait',type=int,default=0);p.add_argument('--record',action='store_true');p.add_argument('--fast',action='store_true');a=p.parse_args()
O=R/'build/verification'/('showcase-config-'+a.tag);assert not O.exists();O.mkdir()
if a.mode=='hard':edges={60:4,80:16,120:4,140:1,180:64,280:16,320:1,340:1,360:1,400:16}
else:edges={60:16,80:1,100:1,120:1,240:16}
template=locate(R/'build/roster-through-2-2/bill-easy-progression-w-3-v0-mmc3/inputs.csv')
with template.open(newline='')as f:prefix=[z for z in csv.DictReader(f)if int(z['frame'])<540]
with(O/'menu.csv').open('w',newline='')as f:
 w=csv.writer(f);w.writerow(('poll','frame','mask'))
 for z in prefix:w.writerow((z['poll'],z['frame'],edges.get(int(z['frame']),0)))
source=a.policy.resolve();policy=O/'policy.lua';mode=int(a.mode=='hard')
lua='SHOWCASE_MODE='+str(mode)+'\nSHOWCASE_WAIT='+str(a.wait)+'\n'
lua+=r'''
local frame=0
local seen=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local f=assert(io.open(ROSTER_CONFIG.out..'showcase-state.csv','w'))
f:write('frame,mode,character,engine,x,y,power,owned,selected,pickup,pickupFlag,pickupState,pickupX,pickupY\n')
local menu=assert(io.open(ROSTER_CONFIG.out..'menu-state.csv','w'))
menu:write('frame,operMode,task,menu,focus,behavior,buttons,sampled,character\n')
emu.addEventCallback(function()
 frame=frame+1
 if frame<800 then menu:write(table.concat({frame,r('OperMode'),r('OperMode_Task'),r('CrossoverMenuState'),r('CrossoverOptionsFocus'),r('CrossoverBehaviorVersion'),r('CrossoverMenuButtons'),r('SavedJoypad1Bits'),r('SelectedCharacter')},',')..'\n');menu:flush()end
 if frame>=500 and r('OperMode')==1 and r('OperMode_Task')==3 then
  assert(r('CrossoverBehaviorVersion')==SHOWCASE_MODE,'The real Options menu selected the requested mode')
  assert(r('SelectedCharacter')==3 and r('BillVariant')==0,'The real character menu selected Bill')
  assert(r('PlayerOutlinesOff')==1,'The actual power-on outline default remains off')
  seen=true
  f:write(table.concat({frame,r('CrossoverBehaviorVersion'),r('SelectedCharacter'),r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('PlayerStatus'),r('InvOwnedLo',3)+256*r('InvOwnedHi',3),r('InvSelected',3),r('InvPickup',5),r('Enemy_Flag',5),r('Enemy_State',5),r('Enemy_X_Position',5)+256*r('Enemy_PageLoc',5),r('Enemy_Y_Position',5)},',')..'\n');f:flush()
 end
 if frame==800 then assert(seen,'Showcase reaches ordinary gameplay after menu input')end
end,emu.eventType.endFrame)
'''
lua+='return assert(dofile('+json.dumps(source.as_posix())+'))\n';policy.write_text(lua,encoding='utf-8')
cmd=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','3','--tag',a.tag,'--mapper',a.mapper,'--policy',str(policy),'--prefix',str(O/'menu.csv'),'--frames',str(a.frames),'--timeout','150','--workspace-cap-gb','30']
if a.fast:cmd+=['--discovery-fast']
if a.record:cmd+=['--record-segments']
(O/'config.json').write_text(json.dumps(dict(mode=a.mode,wait=a.wait,source_policy=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),command=cmd,controller_only=True,emulated_memory_writes=False),indent=2)+'\n',encoding='utf-8')
raise SystemExit(subprocess.run(cmd,cwd=R).returncode)
