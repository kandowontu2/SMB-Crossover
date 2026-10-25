from pathlib import Path
import sys,json,hashlib,subprocess,re
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
O=D/'ryu-head-native-v5';O.mkdir(exist_ok=False)
ROM=D/'ryu-head-candidate-v5/candidate.nes'
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
q=qualified(ROM)
prefix=(D/'kirby-copies-final-v3/easy/run.lua').read_text().split('-- Prefix supplies cold actual menus')[0]
body=r'''
local stage,tick,pending=1,0,nil
local cases={{x=112,power=0,tile=0x51},{x=252,power=1,tile=0x51},{x=112,power=0,tile=0xc1},{x=252,power=1,tile=0xc1}}
local attackStart=nil;local resolves=0;local blocks=0;local snapshots={};local realHeads=0
local trace=assert(io.open(OUTPUT..'contacts.csv','w'));trace:write('frame,case,x,y,attack,attackAge,profile,tile,event\n')
local function log(kind)
 trace:write(table.concat({frame,stage,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('RgAttack'),r('RgAttackAge'),r('RyuSourceBodyProfile'),r('R3'),kind},',')..'\n')
end
local function arena()
 assert(r('RgAttack')==0,'Previous real attack ended')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do
  for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end
  for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col);w('Block_Buffer_1',0x54,p*208+192+col)end
 end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i);w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for _,n in ipairs({'BlockBounceTimer','SmBall','MmSliding','Player_X_Speed','Player_Y_Speed','ScrollThirtyTwo','AreaParserTaskNum','InjuryTimer','StarInvincibleTimer','GamePauseStatus','TimerControl','XgWall','XgWallLock','RyPlatformSlot','RyWallResolved'})do w(n,0)end
 local c=cases[stage];local bx=((c.x+8)//16)*16;local page=bx//256;local col=(bx%256)//16
 w('Block_Buffer_1',c.tile,page%2*208+112+col);tile(page%2,col,9,c.tile)
 local camera=c.x==252 and 128 or 0
 w('ScrollLock',1);w('ScreenLeft_X_Pos',camera);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',camera==0 and 255 or 127);w('ScreenRight_PageLoc',camera==0 and 0 or 1);w('HorizontalScroll',camera)
 w('Player_X_Position',c.x);w('Player_PageLoc',0);w('MmOldX',c.x);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('PlayerStatus',c.power);w('GameEngineSubroutine',8)
 tick=0;attackStart=nil;resolves=0;blocks=0;realHeads=0;COPY_CASE=stage
end
emu.addMemoryCallback(function()
 if emu.convertAddress(L.GameLoop).address//8192~=B.GameLoop or not pending then return end
 local f=pending;pending=nil;f()
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if not entered or boot<30 or emu.convertAddress(HEAD_RESOLVE).address//8192~=22 then return end
 if r('RgAttack')~=0 and r('RgAttackAge')>=2 and r('RyuSourceBodyProfile')==25 then resolves=resolves+1;log('resolve')end
end,emu.callbackType.exec,HEAD_RESOLVE)
emu.addMemoryCallback(function()
 if entered and boot>=30 and emu.convertAddress(L.PlayerHeadCollision).address//8192==B.PlayerHeadCollision then
  realHeads=realHeads+1;log('native-head-effect')
 end
end,emu.callbackType.exec,L.PlayerHeadCollision)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 if tick>=20 and not attackStart and r('Player_State')==1 and r('Player_Y_Position')<171 then attackStart=tick end
 emu.setInput({a=tick>=20 and tick<60,b=attackStart and tick>=attackStart and tick<attackStart+30 or false},0)
end,emu.eventType.inputPolled)
local function shot()
 local b=emu.getScreenBuffer();local f=assert(io.open(OUTPUT..'case-'..stage..'.argb','wb'))
 for i=1,#b,8 do f:write(string.pack('<I4I4I4I4I4I4I4I4',b[i],b[i+1],b[i+2],b[i+3],b[i+4],b[i+5],b[i+6],b[i+7]))end
 f:close()
end
emu.addEventCallback(function()
 frame=frame+1;assert(frame<2500,'Retained head native deadline')
 if not entered then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('SelectedCharacter')==10 and r('CrossoverBehaviorVersion')==(C.hard and 1 or 0));entered=true
  end
  return
 end
 boot=boot+1;if boot<30 then return end
 if boot==30 then pending=arena end
 tick=tick+1
 local c=cases[stage];local px=r('Player_X_Position')+256*r('Player_PageLoc')
 if tick>=3 then assert(px>=c.x-1 and px<=c.x+1,'Stationary aerial head/weapon collision does not move X');assert(r('MmDeathFlag')==0,'Head contact survives')end
 for i=0,3 do
  if r('Block_State',i)~=0 then
   local bx=r('Block_X_Position',i)+256*r('Block_PageLoc',i)
   if r('Block_State',i)%16==1 then assert(bx==((c.x+8)//16)*16,'Native bumped block keeps its actual column')end;blocks=blocks+1
  end
 end
 if resolves>0 and tick==60 then shot()end
 if tick>=210 then
  assert(resolves>0,'Actual retained25 air attack reaches source head resolution case '..stage)
  assert(blocks>0,'Actual native block effect executes case '..stage)
  snapshots[#snapshots+1]={resolves=resolves,blocks=blocks,heads=realHeads}
  stage=stage+1
  if stage>#cases then
   trace:close();local f=assert(io.open(OUTPUT..'proof.json','w'));f:write('{"passed":true,"cases":4,"retained_source_resolves":[')
   for i,v in ipairs(snapshots)do if i>1 then f:write(',')end;f:write(v.resolves)end
   f:write(']}');f:close();print('PASS four retained-air brick/question contacts');emu.stop(0);return
  end
  pending=arena
 end
end,emu.eventType.endFrame)
'''
rows=[]
for hard in [False,True]:
 out=O/('hard'if hard else'easy');out.mkdir()
 pre=re.sub(r'NATIVE_ITEMS=.*?\n-- Source-native', 'NATIVE_ITEMS={name="ryu",slot=10,character=10,hard='+str(hard).lower()+'}\n-- Source-native',prefix,count=1)
 assert 'slot=10' in pre
 script=out/'run.lua';script.write_text(pre+'HEAD_RESOLVE='+str(q[('RyuSourceHeadGate','Resolve')])+'\n'+body)
 with(out/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(ROM),'--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 rows.append(dict(mode='hard'if hard else'easy',exit=p.returncode));print(json.dumps(rows[-1]),flush=True)
 if p.returncode:print((out/'host.log').read_text()[-2300:]);break
(O/'results.json').write_text(json.dumps(dict(ROM_sha256=hashlib.sha256(ROM.read_bytes()).hexdigest(),runs=rows,passed=len(rows)==2 and all(x['exit']==0 for x in rows),scope='Scene/status/map seeds at GameLoop boundary. Actual controller jump/attack, natural body cache and native question/brick effects at aligned/seam coordinates. No attack/copy cache grants.'),indent=2))
raise SystemExit(0 if len(rows)==2 and all(x['exit']==0 for x in rows)else 1)
