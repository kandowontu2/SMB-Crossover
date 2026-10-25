from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-flag-fix-v23';S=D/'mmc3-full-route-v22/twinbee-easy';T=O/'native-tests-v1';T.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();helper=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('img',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
report=dict(complete=False,passed=False,goal_complete=False,runs=[],scope='Retained failed controller stream on parent and private flag fix, read-only actual X/state writer evidence; plus fresh controller discovery on the fix. No emulated state writes or failure waiver. Independent physical frames and broader mapper admission remain separate.')
for version,rom in [('parent',D/'mmc3-tools-v16/canonical-build/smb-crossover-mmc3-oversized.nes'),('fixed',O/'candidate.nes')]:
 out=T/version;out.mkdir();image=im.Image(rom)
 lua=r'''
local frame=0;local f=assert(io.open(OUTPUT..'pole-writes.csv','w'));f:write('frame,event,old,new,pc,bank,engine,x,y,state,camera\n')
local function r(n,i)return emu.read(assert(POLE_RAM[n],n)+(i or 0),emu.memType.nesDebug)end
local function emit(event,old,v)
 local s=emu.getState();local pc=s['cpu.pc'];local a=emu.convertAddress(pc)
 f:write(table.concat({frame,event,old,v,pc,a and a.address//8192 or -1,r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')},',')..'\n')
end
emu.addMemoryCallback(function(_,v)if frame>1000 and r('GameEngineSubroutine')==4 then emit('X',r('Player_X_Position'),v)end end,emu.callbackType.write,POLE_RAM.Player_X_Position)
emu.addMemoryCallback(function(_,v)if frame>1000 and(r('GameEngineSubroutine')==4 or v==3)then emit('state',r('Player_State'),v)end end,emu.callbackType.write,POLE_RAM.Player_State)
emu.addEventCallback(function()frame=frame+1;if frame%60==0 then f:flush()end end,emu.eventType.endFrame)
local stop=emu.stop;emu.stop=function(code)f:close();stop(code)end
'''
 observer=out/'observer.lua';observer.write_text('POLE_RAM='+im.lua(image.ram)+'\n'+lua)
 t=(S/'run.lua').read_text();a='out='+json.dumps(S.as_posix()+'/');assert t.count(a)==1;t=t.replace(a,'out='+json.dumps(out.as_posix()+'/')).replace('replay=nil','replay='+json.dumps((S/'inputs.csv').as_posix())).replace('capture=12,','capture=0,').replace('limit=16000,','limit=9000,')
 at=t.index('dofile(');t=t[:at]+'dofile('+json.dumps(observer.as_posix())+')\n'+t[at:];script=out/'run.lua';script.write_text(t)
 with(out/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(rom),'--timeout','240','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 result=json.loads((out/'result.json').read_text())if(out/'result.json').exists()else None
 actual=(out/'inputs.csv').read_bytes();assert actual==(S/'inputs.csv').read_bytes()[:len(actual)],'Identical retained physical inputs'
 if version=='parent':
  actual=(out/'trace.csv').read_bytes();assert actual==(S/'trace.csv').read_bytes()[:len(actual)],'Exact retained failed trace'
 row=dict(version=version,exit=p.returncode,ROM_sha256=sha(rom),result=result,mapper_guard=json.loads((out/'mmc3-cache-guard.json').read_text())if(out/'mmc3-cache-guard.json').exists()else None,identical_retained_input_prefix=True);report['runs'].append(row);(T/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
assert report['runs'][0]['exit']==1 and report['runs'][0]['result']['failure']=='frame limit'
fixed=report['runs'][1];assert fixed['exit']==0 and fixed['result']['cleared']and fixed['result']['deaths']==0 and fixed['mapper_guard']['passed']
out=T/'fresh-twinbee-easy'
with(T/'fresh.log').open('w')as log:p=subprocess.run([sys.executable,str(D/'mmc3-full-route-v22/bound-mmc3-runner.py'),'twinbee','--rom',str(O/'candidate.nes'),'--output',str(out),'--mapper','mmc3','--behavior','easy','--frames','16000','--capture','12','--policy',str(S/'policy.lua'),'--timeout','240'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
m=json.loads((out/'manifest.json').read_text());g=json.loads((out/'mmc3-cache-guard.json').read_text());assert p.returncode==0 and m['result']['cleared']and m['result']['deaths']==0 and g['passed']
report['fresh_discovery']=dict(passed=True,manifest_sha256=sha(out/'manifest.json'),mapper_guard_sha256=sha(out/'mmc3-cache-guard.json'),frames=m['result']['frames'],folder=str(out));report.update(complete=True,passed=True);(T/'proof.json').write_text(json.dumps(report,indent=2));(T/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(report['fresh_discovery']),flush=True)
