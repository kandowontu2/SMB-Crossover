from pathlib import Path
import importlib.util,json,re
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'mmc3-ship-state-v24';O=D/'mmc3-ship-lives-v25/observer-v3';O.mkdir(parents=True,exist_ok=False)
sp=importlib.util.spec_from_file_location('image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(P/'candidate.nes')
for line in (P/'candidate.lbl').read_text().splitlines():
 z=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
 if z and int(z[1],16)<0x8000:image.ram[z[2]]=int(z[1],16)
sp=importlib.util.spec_from_file_location('runner',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(sp);sp.loader.exec_module(runner);runner.ROOT=O
extra='\nOBS_RAM='+im.lua(image.ram)+'\nOBS_HOOKS='+im.lua({n:image.hook(n)for n in ['PnPortrait','X5PortraitRender','X5SetPhysicalChr']})+'''
local trace=assert(io.open(OUTPUT..'lives-state.jsonl','w'))
local function rr(n)return emu.read(assert(OBS_RAM[n],n),emu.memType.nesDebug)end
local function row(kind,v)
 if rr('OperMode')~=1 or rr('GameEngineSubroutine')==8 then return end
 local st=emu.getState();local a={};for _,n in ipairs({'PlayerChrBank','M3HardwareBody','X5ChrMode','SmChrBank','PnPool','M3CacheProfile','VvVariant','ScreenRoutineTask','GameEngineSubroutine','OperMode_Task'})do a[#a+1]=string.format('"%s":%d',n,rr(n))end
 a[#a+1]=string.format('"a":%d,"x":%d,"y":%d',st['cpu.a'],st['cpu.x'],st['cpu.y'])
 trace:write('{"kind":"'..kind..'","value":'..(v or 0)..','..table.concat(a,',')..'}\\n');trace:flush()
end
emu.addMemoryCallback(function(a,v)row('body-write',v)end,emu.callbackType.write,OBS_RAM.PlayerChrBank)
for n,h in pairs(OBS_HOOKS)do emu.addMemoryCallback(function()
 local p=emu.convertAddress(h.address);if p and p.address//8192==h.physical_bank then row(n)end
end,emu.callbackType.exec,h.address)end
'''
base=(P/'cold-entries-v1/octopus/entry.lua').read_text();script=O/'observer.lua';script.write_text(extra+'\n'+base)
code=runner.run(script,P/'candidate.nes',emulator=str(D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'),timeout=90,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false','--doNotSaveSettings'])
print(json.dumps(dict(exit=code,output=str(O))),flush=True)
