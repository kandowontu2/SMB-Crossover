"""Capture actual Samus movement producers from the valid ordinary F prefix."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-g-samus-a/clock-f-ci'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''dofile(OBSERVER)
local C=CLOCK_CAPTURE
local frame,poll,index=0,0,0
local active,returns=nil,{}
local f=assert(io.open(ROSTER_CONFIG.out..'samus-producers.csv','w'))
local fields={'index','frame','poll','world','level','area','areaType','engine','x','y','yHigh','state','power','held','ab','previousAB','ball','crouch','flip','jumped','vx0','vx1','vx2','vy0','vy1','vy2','xf0','xf1','yf0','yf1','released','timer','injury','returnPC','returnSP'}
f:write(table.concat(fields,',')..'\n')
local ret=assert(io.open(ROSTER_CONFIG.out..'samus-producer-returns.csv','w'));ret:write('index,frame,poll,pc,SP,x,y,state\n')
local audio=assert(io.open(ROSTER_CONFIG.out..'audio-starts.jsonl','w'))
local raw=assert(io.open(ROSTER_CONFIG.out..'audio-starts.ram','wb'));local offset=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function phys(pc)local a=emu.convertAddress(pc);return a and a.memType==emu.memType.nesPrgRom and a.address//8192 or-1 end
local function guard(h)
 if phys(h.address)~=h.physical_bank then return false end
 for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'F exact producer/audio entry8')end
 return true
end
emu.addMemoryCallback(function()
 if frame<540 or r('SelectedCharacter')~=2 or not guard(C.entry)then return end
 assert(not active,'No source movement recursion')
 local s=emu.getState();local sp=s['cpu.sp']
 local pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 local bytes={};for i=0,7 do bytes[i+1]=emu.read(pc+i,emu.memType.nesDebug)end
 if phys(pc)<0 then
  assert(pc==C.ramReturn.address,'Only exact compiled source farcall RAM return')
  for i,b in ipairs(C.ramReturn.bytes)do assert(bytes[i]==b,'Compiled farcall return8')end
 end
 index=index+1
 local a={index,frame,poll,r('WorldNumber'),r('LevelNumber'),r('AreaPointer'),r('AreaType'),r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('PlayerStatus'),r('SavedJoypadBits'),r('A_B_Buttons'),r('PreviousA_B_Buttons'),r('SmBall'),r('SmCrouch'),r('SmFlip'),r('SmSourceJumped'),r('MmVX'),r('MmVX',1),r('MmVX',2),r('MmVY'),r('MmVY',1),r('MmVY',2),r('MmXFraction'),r('MmXFraction',1),r('MmYFraction'),r('MmYFraction',1),r('MmJumpReleased'),r('TimerControl'),r('InjuryTimer'),pc,(sp+2)&255}
 f:write(table.concat(a,',')..'\n');f:flush()
 active={pc=pc,sp=(sp+2)&255,bank=phys(pc),bytes=bytes,index=index}
 if returns[pc]then return end;returns[pc]=true
 emu.addMemoryCallback(function()
  if not active or active.pc~=pc or active.bank~=phys(pc)or emu.getState()['cpu.sp']~=active.sp then return end
  for i,b in ipairs(active.bytes)do assert(emu.read(pc+i-1,emu.memType.nesDebug)==b,'Actual source producer return8')end
  ret:write(table.concat({active.index,frame,poll,pc,active.sp,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State')},',')..'\n');ret:flush();active=nil
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,C.entry.address)
emu.addMemoryCallback(function()
 if frame<540 or frame%240~=0 or not guard(C.audio)then return end
 local s=emu.getState();local b={}
 for a=0,2047 do b[#b+1]=string.char(emu.read(a,emu.memType.nesDebug))end
 for a=0x6000,0x7fff do b[#b+1]=string.char(emu.read(a,emu.memType.nesDebug))end
 raw:write(table.concat(b));raw:flush()
 audio:write(string.format('{"frame":%d,"ramOffset":%d,"A":%d,"X":%d,"Y":%d,"P":%d,"SP":%d,"bank8":%d,"bankA":%d,"bankC":%d,"bankE":%d}\n',frame,offset,s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps'],s['cpu.sp'],phys(0x8000),phys(0xa000),phys(0xc000),phys(0xe000)))
 audio:flush();offset=offset+10240
end,emu.callbackType.exec,C.audio.address)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
emu.addEventCallback(function()poll=poll+1 end,emu.eventType.inputPolled)
return function()return{}end
'''
def main():
 assert not H.exists();H.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text());assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('F_clock_capture',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(cp.parent/'smb-crossover-mmc3.nes')
 pc=image.ram['FarcallJmpTarget_SMC']+3
 ram=image.hook('FarCallCommon',delta=pc-image.ram['FarCallCommon']);assert ram['bytes'][0]==0x8d
 config=dict(entry=image.hook('SamusMovement'),audio=image.hook('AudioUpdate'),ramReturn=ram)
 observer=V/'root49-current-f-samus-a/observer-a.lua';parent=R/'build/roster-through-2-2/root49-f-samus-route-v-2-v0-mmc3'
 policy=H/'policy.lua';policy.write_text('CLOCK_CAPTURE='+im.lua(config)+'\n'+BODY.replace('dofile(OBSERVER)','dofile('+im.lua(observer.as_posix())+')'))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);owned=sum(p.stat().st_size for p in H.parent.rglob('*')if p.is_file())
 for p in(R/'build/roster-through-2-2').glob('root49-g-samus-*'):owned+=sum(q.stat().st_size for q in p.rglob('*')if q.is_file())
 assert total+100000000<80000000000 and owned+100000000+100000000<650000000
 pre=dict(script_sha256=sha(__file__),checkpoint_sha256=sha(cp),policy_sha256=sha(policy),hooks=config,dependencies={str(p.relative_to(R)):sha(p)for p in [helper,observer,parent/'inputs.csv',parent/'trace.csv',parent/'manifest.json']},source_role='Frozen valid F input/pose producer reference only. Shared main isG. F V after29923 is invalid, so stop29916. Source input clock does not assume original physics or AI phase equivalence.',workspace_before=total,phase_before=owned,phase_cap=650000000,reserve=100000000,global_cap=80000000000,goal_complete=False)
 (H/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(image.path),'--tag','root49-g-samus-Fclock-ci','--policy',str(policy),'--replay',str(parent/'inputs.csv'),'--frames','29916','--timeout','900','--workspace-cap-gb','80']
 (H/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(H/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 p=R/'build/roster-through-2-2/root49-g-samus-Fclock-ci-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text())
 result=dict(exit=q.returncode,result=m['result'],manifest_sha256=sha(p/'manifest.json'),native_log_sha256=sha(H/'native.log'),preparation_sha256=sha(H/'preparation.json'),analysis_pending=True,goal_complete=False)
 (H/'native-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
