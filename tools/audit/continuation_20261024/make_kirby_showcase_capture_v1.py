from pathlib import Path
import importlib.util, subprocess, sys, os, json, hashlib, csv, gzip, struct, time
import numpy as np
from PIL import Image

R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover')
D=Path(__file__).resolve().parent
O=D/'kirby-showcase-v1'
O.mkdir(exist_ok=False)
ROM=D/'food-candidate-v3/candidate.nes'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert sha(ROM)=='70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9'
dll=O/'capture_segments.dll'
p=subprocess.run(['gcc','-shared','-O2','-Wall','-Wextra','-Wno-cast-function-type','-o',str(dll),str(R/'tools/playthroughs/capture_segments.c')],capture_output=True,text=True)
(O/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0
spec=importlib.util.spec_from_file_location('cap',D/'capture_food_v4.py');cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
observer=cap.OBSERVER.replace("local frame=0",'''local frame=0
local waveStart=assert(package.loadlib('''+json.dumps(dll.as_posix())+''','luaopen_segment_wave_start'))
local waveStop=assert(package.loadlib('''+json.dumps(dll.as_posix())+''','luaopen_segment_wave_stop'))''')
observer=observer.replace('stop(code)','waveStop();stop(code)')
observer=observer.replace('frame=frame+1;if frame<200 then return end','frame=frame+1;if frame==1 then waveStart()end;if frame<200 then return end')
original=(D/'kirby-copies-final-v3/easy/run.lua').read_text()
prefix=original.split('-- Prefix supplies cold actual menus')[0]
core=(D/'kirby-copy-core-v4.lua').read_text()
helpers=core[core.index('local function baseArena()'):core.index('local function startCase()')]
base=prefix+'''\nlocal stage,tick,phase=1,0,'base'
local pending=nil;local seen={};local rows={}
local out=assert(io.open(OUTPUT..'base-trace.csv','w'))
out:write('frame,case,tick,x,y,hp,mouth,action,float,dash,crouch,shot0,shot1,shot2,kind0,kind1,kind2\\n')
'''+helpers+'''
local names={'walk-run','jumps','float-puff','crouch-slide','inhale-spit','swim-water-gun'}
local durations={160,185,190,155,160,160}
local function begin()
 baseArena();w('AvStopwatch',0);w('SwimmingFlag',stage==6 and 1 or 0)
 if stage==1 or stage==4 then w('Player_X_Position',40);w('MmOldX',40)end
 if stage==5 then w('AvStopwatch',255);actor(6,136,184)end
 if stage==6 then w('Player_Y_Position',128);w('Player_State',2)end
 seen={};tick=0;phase=names[stage]
end
emu.addMemoryCallback(function()
 if emu.convertAddress(L.GameLoop).address//8192~=B.GameLoop or not pending then return end
 local f=pending;pending=nil;f()
end,emu.callbackType.exec,L.GameLoop)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local b={}
 if stage==1 then b.right=(tick>=10 and tick<42)or(tick>=65 and tick<68)or(tick>=72 and tick<111)
 elseif stage==2 then b.a=(tick>=10 and tick<15)or(tick>=100 and tick<126)
 elseif stage==3 then b.up=tick>=10 and tick<70;b.right=tick>=35 and tick<70;b.b=tick>=95 and tick<97
 elseif stage==4 then b.down=tick>=10 and tick<60;b.a=tick>=25 and tick<27
 elseif stage==5 then b.b=(tick>=10 and tick<60)or(tick>=90 and tick<92)
 elseif stage==6 then b.right=tick>=10 and tick<40;b.up=tick>=45 and tick<62;b.down=tick>=82 and tick<100;b.b=tick>=10 and tick<110 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;assert(frame<3000,'Base showcase deadline')
 if not entered then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then assert(r('SelectedCharacter')==13 and r('KbVariant')==0);entered=true end
  return
 end
 boot=boot+1;if boot<30 then return end
 if boot==30 then pending=begin end
 tick=tick+1;COPY_CASE=stage;COPY_PHASE=phase;COPY_TICK=tick
 out:write(table.concat({frame,stage,tick,r('Player_X_Position'),r('Player_Y_Position'),r('KbHealth'),r('KbMouth'),r('KbAction'),r('KbFloat'),r('KbDash'),r('RgCrouch'),r('KbShotType'),r('KbShotType',1),r('KbShotType',2),r('KbShotKind'),r('KbShotKind',1),r('KbShotKind',2)},',')..'\\n')
 assert(r('KbHealth')==6 and r('MmDeathFlag')==0,'Base moves retain full health')
 if r('KbDash')~=0 then seen.dash=true end
 if r('Player_Y_Position')<150 then seen.air=true end
 if r('KbFloat')~=0 then seen.float=true end
 if r('RgCrouch')~=0 then seen.crouch=true end
 if r('KbAction')==5 then seen.slide=true end
 if r('KbMouth')~=0 then seen.mouth=true end
 for i=0,2 do
  if r('KbShotType',i)==1 then seen.star=true end
  if r('KbShotType',i)==2 then seen.puff=true end
  if r('KbShotType',i)~=0 and r('KbShotKind',i)==7 then seen.water=true end
 end
 if stage==5 and tick==70 then pending=function()w('AvStopwatch',0);actor(6,192,184)end end
 if tick>=durations[stage] then
  local required=({{'dash'},{'air'},{'float','puff'},{'crouch','slide'},{'mouth','star'},{'water'}})[stage]
  for _,v in ipairs(required)do assert(seen[v],names[stage]..' actual native action '..v)end
  rows[#rows+1]={name=names[stage],frame=frame}
  stage=stage+1
  if stage>#names then
   out:close();local f=assert(io.open(OUTPUT..'base-result.json','w'));f:write('{"passed":true,"lastFrame":'..frame..'}');f:close();print('PASS all six base move scenes');emu.stop(0);return
  end
  pending=begin
 end
end,emu.eventType.endFrame)
'''
# Add an open-arena attack after every unchanged, verified contact sequence.
# Positioning is a declared scene reset; abilities are still acquired by inhale/Down.
copies=original.replace("elseif phase=='attack'then b.b=tick>=4 and tick<35", "elseif phase=='attack'or phase=='flourish'then b.b=tick>=4 and tick<35")
needle="pending=function()w('Enemy_Flag',0)end;setPhase('drop')"
assert copies.count(needle)==1
copies=copies.replace(needle,"""pending=function()
    w('Enemy_Flag',0);w('Player_X_Position',96);w('Player_PageLoc',0);w('MmOldX',96)
    for i=0,2 do w('MmVX',0,i)end
    if c.power==10 then w('Player_Y_Position',128);w('Player_State',2);w('Player_Y_Speed',1);w('MmVY',1,2)end
   end;setPhase('flourish')""")
needle="elseif phase=='drop'then\n  if tick>=8"
assert copies.count(needle)==1
copies=copies.replace(needle,"""elseif phase=='flourish'then
  if tick>=160 and r('Player_State')==0 then setPhase('drop')end
  assert(tick<400,'Showcase copied action settles naturally')
 elseif phase=='drop'then
  if tick>=8""")
copies=copies.replace("frame<9000","frame<13000")
health=(D/'health-food-final-v3/kirby-easy/run.lua').read_text()

def run(name,text):
 out=O/name;out.mkdir();(out/'frames').mkdir()
 (out/'fixture.lua').write_text(text)
 (out/'observer.lua').write_text(observer)
 script=out/'run.lua';script.write_text('dofile('+json.dumps((out/'observer.lua').as_posix())+')\ndofile('+json.dumps((out/'fixture.lua').as_posix())+')\n')
 env=os.environ.copy();env['SMB_CAPTURE_SEGMENT_DIR']=out.as_posix()
 cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(ROM),'--timeout','240','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 with(out/'host.log').open('w')as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=R,env=env,timeout=270)
 print(json.dumps(dict(capture=name,exit=p.returncode)),flush=True)
 assert p.returncode==0,(out/'host.log').read_text()[-3000:]
 raw=out/'direct.argb';archive=out/'direct.argb.gz';digest=hashlib.sha256();n=0
 with raw.open('rb')as f,gzip.open(archive,'xb',compresslevel=1)as z,(out/'frames.csv').open('w',newline='')as idx:
  writer=csv.writer(idx);writer.writerow(['frame','ppu','cpuCycle','rgbSHA256'])
  while header:=f.read(24):
   frame,pixels,ppu,cycle=struct.unpack('<IIQQ',header);assert frame==ppu==200+n and pixels==61440
   data=f.read(245760);assert len(data)==245760;digest.update(header+data);z.write(header+data)
   v=np.frombuffer(data,dtype='<u4').reshape(240,256);rgb=np.stack(((v>>16)&255,(v>>8)&255,v&255),axis=2).astype('uint8')
   Image.fromarray(rgb).save(out/'frames'/f'{frame:06d}.png');writer.writerow([frame,ppu,cycle,hashlib.sha256(rgb.tobytes()).hexdigest()]);n+=1
 restored=hashlib.sha256()
 with gzip.open(archive,'rb')as f:
  for b in iter(lambda:f.read(1048576),b''):restored.update(b)
 assert restored.hexdigest()==digest.hexdigest()==sha(raw)
 raw.unlink()
 report=dict(passed=True,ROM_sha256=sha(ROM),frames=n,first_frame=200,last_frame=199+n,raw_sha256=digest.hexdigest(),archive_sha256=sha(archive),wave_sha256=sha(out/'native-audio.wav'),fixture_sha256=sha(out/'fixture.lua'),scope='Staged native gameplay showcase. Scenes/actors are arranged; each action and copy acquisition executes the current ROM. Audio is native WaveRecorder PCM. No ROM edits.')
 (out/'capture.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(done=name,frames=n)),flush=True)

for name,fixture in [('base',base),('copies',copies),('food',health)]:run(name,fixture)
(O/'capture-manifest.json').write_text(json.dumps(dict(ROM_sha256=sha(ROM),captures=['base','copies','food'],source_changed=False),indent=2))
