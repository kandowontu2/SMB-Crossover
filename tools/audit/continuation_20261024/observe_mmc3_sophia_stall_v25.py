from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-ship-lives-v25';O=V/'sophia-stall-v1';O.mkdir(exist_ok=False);(O/'frames').mkdir();ROM=V/'candidate.nes';route=V/'remaining-routes-v1/sophia-easy';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('img',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(ROM)
observer=O/'observer.lua';observer.write_text('DEBUG_LOOP='+im.lua(image.hook('GameLoop',delta='last'))+r'''
local frame,last,stalled,updates=0,nil,0,0
local trace=assert(io.open(ROSTER_CONFIG.out..'stall-state.csv','w'));local fields={'FrameCounter','NmiDisable','NmiSkipped','Mirror_PPUCTRL','Mirror_PPUMASK','GameEngineSubroutine','OperMode','OperMode_Task','Player_X_Position','Player_PageLoc','Player_Y_Position','TimerControl','InvRefill','InvRefillRemain','GuestPowerupActive','GamePauseStatus','CurrentBank','CurrentBankC','BankShadow','ReloadCHRBank','MmBlockAttack','SmPosePtr','CurrentOAMOffset','SelectedCharacter'}
trace:write('frame,pc,sp,bankA,bankC,completedLoops,'..table.concat(fields,',')..'\n')
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function bank(pc)local q=emu.convertAddress(pc);return q and q.address//8192 or -1 end
emu.addMemoryCallback(function()if bank(DEBUG_LOOP.address)==DEBUG_LOOP.physical_bank then for i,b in ipairs(DEBUG_LOOP.bytes)do assert(emu.read(DEBUG_LOOP.address+i-1,emu.memType.nesDebug)==b,'Actual completed-loop opcode')end;updates=updates+1 end end,emu.callbackType.exec,DEBUG_LOOP.address)
local stop=emu.stop;emu.stop=function(code)trace:close();stop(code)end
emu.addEventCallback(function()
 frame=frame+1;local st=emu.getState();local a={frame,st['cpu.pc'],st['cpu.sp'],bank(0xa000),bank(0xc000),updates};for _,n in ipairs(fields)do a[#a+1]=r(n)end;trace:write(table.concat(a,',')..'\n');trace:flush()
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and frame>700 then if updates==last then stalled=stalled+1 else stalled=0 end else stalled=0 end;last=updates
 if stalled==90 or frame==4000 then
  local f=assert(io.open(ROSTER_CONFIG.out..'observed-state.json','w'));f:write('{');local first=true
  for k,v in pairs(st)do if type(v)=='number'or type(v)=='boolean'then if not first then f:write(',')end;first=false;f:write(string.format('%q:%s',k,tostring(v)))end end
  f:write('}');f:close();local f=assert(io.open(ROSTER_CONFIG.out..'observed-screen.png','wb'));f:write(emu.takeScreenshot());f:close()
  local f=assert(io.open(ROSTER_CONFIG.out..'observed-ram.bin','wb'));for a=0,2047 do f:write(string.char(emu.read(a,emu.memType.nesDebug)))end;for a=0x6000,0x7fff do f:write(string.char(emu.read(a,emu.memType.nesDebug)))end;f:close()
  local f=assert(io.open(ROSTER_CONFIG.out..'debug-stop.json','w'));f:write(string.format('{"observed":true,"frame":%d,"consecutivePhysicalFramesWithoutCompletedLoop":%d,"completedLoops":%d,"pc":%d,"sp":%d,"game_state_writes":false,"campaign_pass":false}',frame,stalled,updates,st['cpu.pc'],st['cpu.sp']));f:close();print('OBSERVED bounded read-only Sophia stall witness; not a campaign pass');emu.stop(0)
 end
end,emu.eventType.endFrame)
''')
text=(route/'run.lua').read_text();old='out='+json.dumps(route.as_posix()+'/');assert text.count(old)==1;text=text.replace(old,'out='+json.dumps(O.as_posix()+'/'));assert text.count('replay=nil')==1;text=text.replace('replay=nil','replay='+json.dumps((route/'inputs.csv').as_posix()));at=text.index('dofile(');script=O/'run.lua';script.write_text(text[:at]+'dofile('+im.lua(observer.as_posix())+')\n'+text[at:])
with(O/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(O),str(script),str(ROM),'--timeout','180','--emulator',str(D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
z=O/'debug-stop.json';q=dict(observed=p.returncode==0 and z.exists(),exit=p.returncode,ROM_sha256=sha(ROM),source_inputs_sha256=sha(route/'inputs.csv'),script_sha256=sha(script),observer_sha256=sha(observer),campaign_pass=False,result=json.loads(z.read_text())if z.exists()else None);(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
