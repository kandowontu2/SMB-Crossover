"""Replay held-button proposals by actual G Samus movement completions."""
from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-g-samus-a';J=H/'clock-b-cj'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''dofile(OBSERVER)
local C=SOURCE_CLOCK
local ref=dofile(REFERENCE)
local fallback=dofile(FALLBACK)
local frame,completed=0,0
local active,returns=nil,{}
local coral,age='release',0
local entries=assert(io.open(ROSTER_CONFIG.out..'source-clock-b.csv','w'))
entries:write('frame,index,referenceFrame,x,y,state,held,AB,previousAB,ball,crouch,match,differences\n')
local pacing=assert(io.open(ROSTER_CONFIG.out..'clock-pacing-b.csv','w'));pacing:write('frame,poll,completed,referenceFrame,mask,phase\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function phys(pc)local a=emu.convertAddress(pc);return a and a.memType==emu.memType.nesPrgRom and a.address//8192 or-1 end
local function values()
 return{0,frame,0,r('WorldNumber'),r('LevelNumber'),r('AreaPointer'),r('AreaType'),r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('PlayerStatus'),r('SavedJoypadBits'),r('A_B_Buttons'),r('PreviousA_B_Buttons'),r('SmBall'),r('SmCrouch'),r('SmFlip'),r('SmSourceJumped'),r('MmVX'),r('MmVX',1),r('MmVX',2),r('MmVY'),r('MmVY',1),r('MmVY',2),r('MmXFraction'),r('MmXFraction',1),r('MmYFraction'),r('MmYFraction',1),r('MmJumpReleased'),r('TimerControl'),r('InjuryTimer')}
end
emu.addMemoryCallback(function()
 if frame<540 or r('SelectedCharacter')~=2 or phys(C.entry.address)~=C.entry.physical_bank then return end
 for i,b in ipairs(C.entry.bytes)do assert(emu.read(C.entry.address+i-1,emu.memType.nesDebug)==b,'Exact G Samus source-entry8')end
 assert(not active,'No actual Samus movement recursion')
 local s=emu.getState();local sp=s['cpu.sp'];local pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 local bytes={};for i=0,7 do bytes[i+1]=emu.read(pc+i,emu.memType.nesDebug)end
 if phys(pc)<0 then assert(pc==C.ramReturn.address,'Only actual compiled farcall RAM return');for i,b in ipairs(C.ramReturn.bytes)do assert(bytes[i]==b,'Compiled RAM return8')end end
 local ix=completed+1;local q=ref[ix];local got=values();local dif={}
 if q then for i=4,33 do if q[i]~=got[i]then dif[#dif+1]=i..':'..q[i]..'/'..got[i]end end end
 entries:write(table.concat({frame,ix,q and q[2]or-1,got[9],got[10],got[12],got[14],got[15],got[16],got[17],got[18],#dif==0 and1 or0,table.concat(dif,';')},',')..'\n');entries:flush()
 active={pc=pc,sp=(sp+2)&255,bank=phys(pc),bytes=bytes}
 if returns[pc]then return end;returns[pc]=true
 emu.addMemoryCallback(function()
  if not active or active.pc~=pc or active.bank~=phys(pc)or emu.getState()['cpu.sp']~=active.sp then return end
  for i,b in ipairs(active.bytes)do assert(emu.read(pc+i-1,emu.memType.nesDebug)==b,'Actual source-return8/SP/bank')end
  completed=completed+1;active=nil
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,C.entry.address)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
return function(c)
 local q=ref[completed+1];local mask=q and q[14]or0;local phase='source-reference'
 if not q then
  phase=coral
  if coral=='done'then return fallback(c)end
  age=age+1;assert(age<220,'Bounded actual G coral jump')
  assert(c.world==1 and c.level==1,'Completed valid F source clock must reach actual water before new control')
  local b={b=c.poll%8<4}
  if coral=='release'then
   assert(c.x>=1200 and c.x<=1240 and c.y==176 and c.grounded,'Actual G water floor, not reference coordinates')
   if age>=4 and r('PreviousA_B_Buttons')&128==0 then
    assert(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0,'Real floor before new coral jump')
    coral='jump'
   end
  elseif coral=='jump'then
   b.right=true;b.a=true
   if c.x>=1290 then coral='done'end
  end
  mask=(b.right and1 or0)+(b.a and128 or0)+(b.b and64 or0)
 end
 pacing:write(table.concat({c.frame,c.poll,completed,q and q[2]or-1,mask,phase},',')..'\n');pacing:flush()
 local b={};for n,v in pairs(bits)do b[n]=mask&v~=0 end;return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';c=json.loads(cp.read_text());assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0'
 captured=R/'build/roster-through-2-2/root49-g-samus-Fclock-ci-2-v0-mmc3';parent=R/'build/roster-through-2-2/root49-f-samus-route-v-2-v0-mmc3'
 r=lambda p:list(csv.DictReader(p.open(newline='')))
 assert r(captured/'trace.csv')==r(parent/'trace.csv')[:29916]
 assert r(captured/'inputs.csv')==r(parent/'inputs.csv')[:29915]
 rows=r(captured/'samus-producers.csv');ret=r(captured/'samus-producer-returns.csv')
 assert len(rows)==len(ret)and[int(q['index'])for q in rows]==list(range(1,len(rows)+1))and[int(q['index'])for q in ret]==list(range(1,len(ret)+1))
 assert int(rows[0]['frame'])==540
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('G_clock_B',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(cp.parent/'smb-crossover-mmc3.nes')
 fields=list(rows[0]);ref=[[int(q[n])for n in fields]for q in rows];reference=J/'source-F-reference.lua';reference.write_text('return '+im.lua(ref)+'\n')
 prefix=J/'prefix-540.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(r(captured/'inputs.csv')[:540])
 fallback=J/'fallback-D-pose.lua';body=(V/'root49-current-f-samus-a/reference-policy-p.lua').read_text();first=body.index('\n');assert body[:first].startswith('dofile(');fallback.write_text(body[first+1:])
 pc=image.ram['FarcallJmpTarget_SMC']+3;config=dict(entry=image.hook('SamusMovement'),ramReturn=image.hook('FarCallCommon',delta=pc-image.ram['FarCallCommon']))
 policy=J/'policy.lua';body=BODY.replace('dofile(OBSERVER)','dofile('+im.lua((H/'observer-g.lua').as_posix())+')').replace('dofile(REFERENCE)','dofile('+im.lua(reference.as_posix())+')').replace('dofile(FALLBACK)','dofile('+im.lua(fallback.as_posix())+')')
 for a,b in [('and1','and 1'),('or0','or 0'),('and128','and 128'),('and64','and 64')]:body=body.replace(a,b)
 policy.write_text('SOURCE_CLOCK='+im.lua(config)+'\n'+body)
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);owned=sum(p.stat().st_size for p in H.rglob('*')if p.is_file())
 for p in(R/'build/roster-through-2-2').glob('root49-g-samus-*'):owned+=sum(q.stat().st_size for q in p.rglob('*')if q.is_file())
 assert total+100000000<80000000000 and owned+100000000+100000000<650000000
 pre=dict(script_sha256=sha(__file__),checkpoint_sha256=sha(cp),captured_F_manifest_sha256=sha(captured/'manifest.json'),producer_sha256=sha(captured/'samus-producers.csv'),returns_sha256=sha(captured/'samus-producer-returns.csv'),literal_F_physical_trace_rows=29916,literal_F_input_rows=29915,actual_F_producers=len(ref),fields=fields,policy_sha256=sha(policy),reference_sha256=sha(reference),prefix_sha256=sha(prefix),fallback_sha256=sha(fallback),workspace_before=total,phase_before=owned,phase_cap=650000000,reserve=100000000,global_cap=80000000000,
  scope='Actual source producer completion clock selects ordinary held buttons; all actual input/kinematic mismatches logged. Neither identical physics/AI phase nor an input-latch scheduling fix is assumed. ValidF ends29916; currentG coral and later D pose proposal are separate actual controls.')
 (J/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(image.path),'--tag','root49-g-samus-clock-b','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 p=R/'build/roster-through-2-2/root49-g-samus-clock-b-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text())
 result=dict(exit=q.returncode,result=m['result'],manifest_sha256=sha(p/'manifest.json'),native_log_sha256=sha(J/'native.log'),preparation_sha256=sha(J/'preparation.json'),analysis_pending=True,goal_complete=False)
 (J/'native-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
