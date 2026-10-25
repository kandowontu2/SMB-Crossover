"""Read-only replay trace of the real16px native wall correction."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--route',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 run=(a.route/'run.lua').read_text();run=run.replace('out='+json.dumps(a.route.as_posix()+'/'),'out='+json.dumps(a.output.as_posix()+'/')).replace('replay=nil','replay='+json.dumps((a.route/'inputs.csv').as_posix())).replace('capture=12,','capture=0,')
 pre='WALL_OUT='+json.dumps(a.output.as_posix()+'/')+'\n'+r'''
local wf=assert(io.open(WALL_OUT..'wall.csv','w'))
wf:write('event,frame,pc,bank,x,nextX,y,vy,vx,r0,r2,r3,r4,r5,r6,r7,seq,phase,pose,nativeState,air,hurt,held,face,contact\n')
local wallFrame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function row(event,value)
 local x=r('Player_X_Position')+256*r('Player_PageLoc')
 if x<2600 or x>2800 or r('GameEngineSubroutine')~=8 then return end
 local st=emu.getState();local pc=st['cpu.pc'];local converted=emu.convertAddress(pc)
 local b=converted and converted.address and converted.address//8192 or -1
 local q={event,wallFrame,pc,b,x,value or x,r('Player_Y_Position'),r('Player_Y_Speed'),r('Player_X_Speed'),r('R0'),r('R2'),r('R3'),r('R4'),r('R5'),r('R6'),r('R7'),r('TnSeq'),r('TnPhase'),r('TnPose'),r('TnNativeState'),r('Player_State'),r('TnHurt'),r('TnHeld'),r('PlayerFacingDir'),r('XgWallContact')}
 wf:write(table.concat(q,',')..'\n')
end
emu.addMemoryCallback(function(_,value)row('xwrite',value+256*r('Player_PageLoc'))end,emu.callbackType.write,L.Player_X_Position)
for _,n in ipairs({'SamusStopAtWallBanked','TnSideDispatch','TnMovement','TnInjuryStart'})do
 emu.addMemoryCallback(function()row(n)end,emu.callbackType.exec,L[n])
end
emu.addEventCallback(function()wallFrame=wallFrame+1 end,emu.eventType.endFrame)
emu.addEventCallback(function()wf:close()end,emu.eventType.scriptEnded)
'''
 at=run.index('dofile(');script=a.output/'run.lua';script.write_text(run[:at]+pre+run[at:])
 z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom.resolve()),'--timeout','120','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True,cwd=ROOT)
 (a.output/'host.log').write_text(z.stdout+z.stderr);q=dict(passed=z.returncode==0,ROM_sha256=sha(a.rom),source_inputs_sha256=sha(a.route/'inputs.csv'),script_sha256=sha(script),read_only=True,exit=z.returncode)
 if z.returncode==0:
  q['inputs_exact']=(a.output/'inputs.csv').read_bytes()==(a.route/'inputs.csv').read_bytes();q['trace_exact']=(a.output/'trace.csv').read_bytes()==(a.route/'trace.csv').read_bytes();assert q['inputs_exact']and q['trace_exact']
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));return z.returncode
if __name__=='__main__':raise SystemExit(main())
