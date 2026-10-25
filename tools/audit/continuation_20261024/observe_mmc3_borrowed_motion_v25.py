from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-ship-lives-v25';O=V/'borrowed-motion-v1';O.mkdir(exist_ok=False);ROM=V/'candidate.nes';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('img',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(ROM)
OBSERVER=r'''
local frame,lastDrawX,lastDrawY=0,-1,-1
local f=assert(io.open(ROSTER_CONFIG.out..'committed-movement.csv','w'));f:write('frame,world,level,mode,task,engine,x,y,camera,blockAttack\n')
local b=assert(io.open(ROSTER_CONFIG.out..'borrowed-origin.csv','w'));b:write('frame,pc,bankA,blockAttack,x,y,savedX,savedY,probeX,probeY,lastDrawX,lastDrawY\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function bank(pc)local p=emu.convertAddress(pc);return p and p.address//8192 or -1 end
local function hook(h,fn)emu.addMemoryCallback(function()if bank(h.address)~=h.physical_bank then return end;for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Exact actual native motion instruction')end;fn()end,emu.callbackType.exec,h.address)end
hook(BORROW_HOOKS.finish,function()
 assert(r('MmBlockAttack')==0,'Actual completed GameLoop restores source borrowed origin')
 f:write(table.concat({frame,r('WorldNumber'),r('LevelNumber'),r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),x(),r('Player_Y_Position'),r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),r('MmBlockAttack')},',')..'\n')
end)
hook(BORROW_HOOKS.draw,function()assert(r('MmBlockAttack')==0,'Actual body drawing never consumes source borrowed origin');lastDrawX=x();lastDrawY=r('Player_Y_Position')end)
emu.addEventCallback(function()
 frame=frame+1;if r('MmBlockAttack')==0 or r('OperMode')~=1 then return end
 local s=emu.getState();b:write(table.concat({frame,s['cpu.pc'],bank(0xa000),r('MmBlockAttack'),x(),r('Player_Y_Position'),r('MmSavedPlayer')+256*r('MmSavedPlayer',1),r('MmSavedPlayer',2),(r('MmProbeX')&240)+256*r('MmProbePage'),r('MmProbeY')&240,lastDrawX,lastDrawY},',')..'\n')
end,emu.eventType.endFrame)
local stop=emu.stop;emu.stop=function(code)f:close();b:close();stop(code)end
'''
report=dict(complete=False,passed=False,goal_complete=False,ROM_sha256=sha(ROM),runs=[],scope='Read-only exact-input/trace native MMC3 observations of three previously rejected raw endFrame motion traces. A valid result requires actual tagged query origin and saved body state, no borrowed origin during body drawing, and unchanged strict bounds at every completed native loop. No blanket waiver, fixture mutation or physical pixel/campaign admission.')
for name in ['proto','bill','lance']:
 route=V/'remaining-routes-v1'/(name+'-easy');manifest=json.loads((route/'manifest.json').read_text());assert manifest['ROM_sha256']==sha(ROM)and manifest['exit']==0 and manifest['result']['cleared'];out=O/(name+'-easy');out.mkdir();observer=out/'observer.lua';observer.write_text('BORROW_HOOKS='+im.lua(dict(finish=image.hook('GameLoop',delta='last'),draw=image.hook('DrawAllMetasprites')))+'\n'+OBSERVER)
 text=(route/'run.lua').read_text();old='out='+json.dumps(route.as_posix()+'/');assert text.count(old)==1;text=text.replace(old,'out='+json.dumps(out.as_posix()+'/'));assert text.count('replay=nil')==1;text=text.replace('replay=nil','replay='+json.dumps((route/'inputs.csv').as_posix()));at=text.index('dofile(');script=out/'run.lua';script.write_text(text[:at]+'dofile('+im.lua(observer.as_posix())+')\n'+text[at:])
 with(out/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(ROM),'--timeout','240','--emulator',str(D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 row=dict(identity=name,exit=p.returncode,passed=False);report['runs'].append(row)
 if p.returncode==0:
  for n in ['inputs.csv','trace.csv']:assert(out/n).read_bytes()==(route/n).read_bytes(),'Exact original '+n
  trace=list(csv.DictReader((route/'trace.csv').open()));raw={z['frame']:z for z in trace};borrowed=list(csv.DictReader((out/'borrowed-origin.csv').open()));assert borrowed
  for z in borrowed:
   original=raw[z['frame']];assert z['blockAttack']=='1';assert int(original['x'])==int(z['x'])==int(z['probeX'])and int(original['y'])==int(z['y'])==int(z['probeY']);assert abs(int(z['savedX'])-int(z['lastDrawX']))<=8 and abs(int(z['savedY'])-int(z['lastDrawY']))<=8
  completed=[z for z in csv.DictReader((out/'committed-movement.csv').open())if z['mode']=='1'and z['task']=='3'and z['engine']=='8'and z['world']==z['level']=='0'];assert len(completed)>1000 and all(z['blockAttack']=='0'for z in completed)
  # Check every adjacent committed logical update, including two in one PPU frame.
  dx=[abs(int(y['x'])-int(x['x']))for x,y in zip(completed,completed[1:])];dc=[int(y['camera'])-int(x['camera'])for x,y in zip(completed,completed[1:])];assert max(dx)<=8 and min(dc)>=0 and max(dc)<=4
  row.update(passed=True,completed_updates=len(completed),max_committed_world_step=max(dx),min_committed_camera_step=min(dc),max_committed_camera_step=max(dc),borrowed_frames=[int(z['frame'])for z in borrowed],borrowed_sha256=sha(out/'borrowed-origin.csv'),committed_sha256=sha(out/'committed-movement.csv'),script_sha256=sha(script),observer_sha256=sha(observer))
 (O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report.update(complete=True,passed=all(z['passed']for z in report['runs']));(O/'proof.json').write_text(json.dumps(report,indent=2))
