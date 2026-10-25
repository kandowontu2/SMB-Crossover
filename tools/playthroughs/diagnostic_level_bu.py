"""Use the real Cheats menu for explicitly cheated world-actor diagnostics.

No RAM/register/ROM writes. These runs are not ordinary final-route clears.
"""
from pathlib import Path
import argparse,csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from workspace_storage import locate
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--world',type=int,required=True,choices=range(1,9));p.add_argument('--level',type=int,required=True,choices=range(1,5));p.add_argument('--character',type=int,default=3,choices=(0,3));p.add_argument('--mapper',choices=('mmc3','mmc5'),default='mmc3');p.add_argument('--frames',type=int,default=6000);p.add_argument('--record',action='store_true');p.add_argument('--rom',type=Path);p.add_argument('--policy',type=Path,default=R/'tools/playthroughs/roster_policy.lua');a=p.parse_args()
O=R/'build/verification'/('diagnostic-config-'+a.tag);assert not O.exists();O.mkdir()
edges={60:4,80:16,120:4,140:4,160:128,200:128,220:4,420:64,460:64,520:16,660:16}
value=(a.world-1)*4+a.level-1
for n in range(value):edges[240+n*4]=1
if a.character==3:
 for n in(560,580,600):edges[n]=1
clock=locate(R/'build/roster-through-2-2/claude-final-video-0-v0-mmc3/inputs.csv')
with clock.open(newline='')as f:prefix=[z for z in csv.DictReader(f)if int(z['frame'])<900]
with(O/'menu.csv').open('w',newline='')as f:
 w=csv.writer(f);w.writerow(('poll','frame','mask'))
 for z in prefix:w.writerow((z['poll'],z['frame'],edges.get(int(z['frame']),0)))
observer=(R/'build/verification/world-actors-ba-mario/audit.lua').read_text(encoding='utf-8')
start=observer.index(' local base=assert(dofile(');end=observer.index('\n',start)
observer=observer[:start]+' local base={frame=function()end,finish=function()end}'+observer[end:]
(O/'actor-observer.lua').write_text(observer,encoding='utf-8')
policy=r'''
local factory=assert(dofile(OBSERVER))
local actor=factory(ROSTER_CONFIG)
local choose=assert(dofile(POLICY))
local frame,closed,seen=0,false,false
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local status=assert(io.open(ROSTER_CONFIG.out..'diagnostic-state.csv','w'))
status:write('frame,world,level,area,mode,task,engine,character,invincible,levelCheat,x,y,camera\n')
emu.addEventCallback(function()
 frame=frame+1
 if closed then return end
 actor.frame(frame)
 if frame>=900 then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('WorldNumber')==WORLD and r('LevelNumber')==LEVEL,'The real menu launches the diagnostic stage')
   assert(r('SelectedCharacter')==CHARACTER and r('CheatInvincible')==1 and r('CheatStartLevel')==(32+START),'The real menu selects the diagnostic character and explicit cheats')
   seen=true
  end
  status:write(table.concat({frame,r('WorldNumber'),r('LevelNumber'),r('AreaNumber'),r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),r('SelectedCharacter'),r('CheatInvincible'),r('CheatStartLevel'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')},',')..'\n')
 end
 if frame==1000 then assert(seen,'Real menu input reaches the diagnostic level')end
 if frame>=ROSTER_CONFIG.limit or frame>900 and(r('GameEngineSubroutine')==11 or r('OperMode')==3)then
  actor.finish();status:close();closed=true
 end
end,emu.eventType.endFrame)
return choose
'''
for token,v in [('OBSERVER',json.dumps((O/'actor-observer.lua').as_posix())),('POLICY',json.dumps(a.policy.resolve().as_posix())),('WORLD',str(a.world-1)),('LEVEL',str(a.level-1)),('CHARACTER',str(a.character)),('START',str(value))]:policy=policy.replace(token,v)
(O/'policy.lua').write_text(policy,encoding='utf-8')
rom=a.rom.resolve()if a.rom else R/'build/checkpoints/cheats-options-bt/build'/f'smb-crossover-{a.mapper}.nes'
cmd=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(a.character),'--mapper',a.mapper,'--tag',a.tag,'--rom',str(rom),'--policy',str(O/'policy.lua'),'--prefix',str(O/'menu.csv'),'--frames',str(a.frames),'--timeout','160','--workspace-cap-gb','30']
if a.record:cmd+=['--record-segments']
(O/'config.json').write_text(json.dumps(dict(world=a.world,level=a.level,character=a.character,mapper=a.mapper,ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),explicit_cheats='Invincibility ON and user-selected level, through actual menu input. This is not an ordinary final-route or all-abilities clear.',emulated_writes=False,command=cmd),indent=2)+'\n',encoding='utf-8')
raise SystemExit(subprocess.run(cmd,cwd=R).returncode)
