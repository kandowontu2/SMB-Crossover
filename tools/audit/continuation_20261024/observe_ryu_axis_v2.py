"""Observe every native player-axis write around the retained12px Ryu event."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;out=D/'ryu-axis-observer-v2';out.mkdir(exist_ok=False)
route=D/'known-routes-v3/discover-ryu-easy';rom=D/'food-candidate-v3/candidate.nes';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
q=qualified(rom);aliases=''.join('L['+json.dumps(n)+']='+str(q[(n,)])+'\n'for n in ['RyuSourceBodyProfile','RyWallOldHeight','RyWallSupported','RyWallWasGround','RgAttack','RgCrouch','Local_eb'])
observer=out/'observer.lua';observer.write_text(aliases+'AXIS_OUT='+json.dumps(out.as_posix()+'/')+'\n'+r'''
local frame=0
local log=assert(io.open(AXIS_OUT..'axis-writes.csv','w'))
local fields={'Player_PageLoc','Player_X_Position','Player_Y_Position','Player_Y_Speed','Player_State','PlayerSize','PlayerStatus','MmOldX','MmBlockAttack','XgWall','XgJumpUsed','Block_Orig_XPos','Block_Orig_YPos','BlockBounceTimer','XgHeadAdder','RyuSourceBodyProfile','RyWallOldHeight','RyWallSupported','RyWallWasGround','RgAttack','RgCrouch','Local_eb','R2','R3','R4','CrouchingFlag','CurrentBank','ObjectOffset','SavedJoypadBits'}
log:write('frame,address,newValue,pc,physicalAddress,cpuCycle,a,x,y,sp,p,'..table.concat(fields,',')..'\n')
local stop=emu.stop;emu.stop=function(code)log:close();stop(code)end
local function r(n)if not L[n]then return -1 end;return emu.read(L[n],emu.memType.nesDebug)end
local function hook(name)
 emu.addMemoryCallback(function(addr,value)
  if frame<3679 or frame>3700 then return end
  local s=emu.getState();local pc=s['cpu.pc'];local a=emu.convertAddress(pc)
  local row={frame+1,addr,value,pc,a and a.address or -1,s['cpu.cycleCount'],s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.sp'],s['cpu.ps']or s['cpu.p']or -1}
  for _,n in ipairs(fields)do row[#row+1]=r(n)end
  log:write(table.concat(row,',')..'\n')
 end,emu.callbackType.write,assert(L[name],name))
end
hook('Player_X_Position');hook('Player_PageLoc');hook('Player_Y_Position');hook('Player_Y_Speed')
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
''')
t=(route/'run.lua').read_text();old='out='+json.dumps(route.as_posix()+'/');assert t.count(old)==1;t=t.replace(old,'out='+json.dumps(out.as_posix()+'/'));assert t.count('replay=nil')==1;t=t.replace('replay=nil','replay='+json.dumps((route/'inputs.csv').as_posix()));assert t.count('capture=12,')==1;t=t.replace('capture=12,','capture=0,');at=t.index('dofile(');t=t[:at]+'dofile('+json.dumps(observer.as_posix())+')\n'+t[at:];script=out/'run.lua';script.write_text(t)
cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(rom),'--timeout','150','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
with(out/'host.log').open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0
for name in ['inputs.csv','trace.csv']:assert(out/name).read_bytes()==(route/name).read_bytes()
assert json.loads((out/'result.json').read_text())==json.loads((route/'result.json').read_text())
q=dict(passed=True,goal_complete=False,ROM_sha256=sha(rom),observer_sha256=sha(observer),driver_sha256=sha(Path(__file__)),original_manifest_sha256=sha(route/'manifest.json'),fixed_inputs_and_trace_exact=True,writes_sha256=sha(out/'axis-writes.csv'),scope='Read-only native axis write/PC/bank/state recording around the original Ryu12px movement rejection. Full original controller/state/CPU-cycle trace and endpoint remain exact. This is diagnosis, not a repaired movement pass.')
(out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
