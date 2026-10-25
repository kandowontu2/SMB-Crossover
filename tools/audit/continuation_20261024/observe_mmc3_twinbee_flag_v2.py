from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,re
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=D/'mmc3-flag-observer-v2';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
helper=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('img',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
lua=r'''
local f=assert(io.open(OUTPUT..'state-writes.csv','w'));f:write('frame,event,old,new,pc,bank,engine,x,y,state,collisionDisabled,character,variant\n')
local frame=0
local function r(n,i)return emu.read(assert(STATE_RAM[n],n)+(i or 0),emu.memType.nesDebug)end
local function emit(event,old,v)
 local s=emu.getState();local pc=s['cpu.pc'];local p=emu.convertAddress(pc)
 f:write(table.concat({frame,event,old,v,pc,p and p.address//8192 or -1,r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('DisableCollisionDet'),r('SelectedCharacter'),r('VvVariant')},',')..'\n')
end
emu.addMemoryCallback(function(_,v)
 if frame>1000 and(r('GameEngineSubroutine')==4 or v==3)then emit('player-state',r('Player_State'),v)end
end,emu.callbackType.write,STATE_RAM.Player_State)
emu.addMemoryCallback(function(_,v)
 if frame>1000 and(r('GameEngineSubroutine')>=4 and r('GameEngineSubroutine')<=5 or v==4 or v==5)then emit('engine',r('GameEngineSubroutine'),v)end
end,emu.callbackType.write,STATE_RAM.GameEngineSubroutine)
emu.addEventCallback(function()frame=frame+1;if frame%60==0 then f:flush()end end,emu.eventType.endFrame)
local stop=emu.stop;emu.stop=function(code)f:close();stop(code)end
'''
report=dict(complete=False,runs=[],scope='Read-only exact fixed-input observations of actual player-state writers around the flag. MMC3 uses its retained failed stream with a6000-frame diagnostic bound; MMC5 replays its verified complete clear. No game/source/controller mutation or failure waiver.')
for version,rom,source,limit in [('mmc3',D/'mmc3-tools-v16/canonical-build/smb-crossover-mmc3-oversized.nes',D/'mmc3-full-route-v22/twinbee-easy',6000),('mmc5',P/'candidate.nes',P/'remaining-roster-v1/twinbee-easy',None)]:
 out=O/version;out.mkdir();image=im.Image(rom);image.ram['VvVariant']=int(re.search(r'al ([0-9A-Fa-f]+) \.VvVariant',rom.with_suffix('.lbl').read_text())[1],16);observer=out/'observer.lua';observer.write_text('STATE_RAM='+im.lua(image.ram)+'\n'+lua)
 t=(source/'run.lua').read_text();a='out='+json.dumps(source.as_posix()+'/');assert t.count(a)==1;t=t.replace(a,'out='+json.dumps(out.as_posix()+'/'));assert t.count('replay=nil')==1;t=t.replace('replay=nil','replay='+json.dumps((source/'inputs.csv').as_posix())).replace('capture=12,','capture=0,')
 if limit:t=t.replace('limit=16000,','limit='+str(limit)+',')
 at=t.index('dofile(');t=t[:at]+'dofile('+json.dumps(observer.as_posix())+')\n'+t[at:];script=out/'run.lua';script.write_text(t)
 with(out/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(rom),'--timeout','240','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 actual=(out/'inputs.csv').read_bytes();assert actual==(source/'inputs.csv').read_bytes()[:len(actual)];actual=(out/'trace.csv').read_bytes();assert actual==(source/'trace.csv').read_bytes()[:len(actual)]
 row=dict(version=version,ROM_sha256=sha(rom),exit=p.returncode,result=json.loads((out/'result.json').read_text())if(out/'result.json').exists()else None,source_manifest_sha256=sha(source/'manifest.json'),read_only=True);report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report['complete']=True;(O/'observation.json').write_text(json.dumps(report,indent=2))
