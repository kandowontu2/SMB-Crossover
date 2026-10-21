"""Land on the real2064 bank and shoot the actual approaching fish."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-bank-ft'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''dofile(OBSERVER)
local finish=dofile(FINISH)
local age,release,phase=0,0,0
local f=assert(io.open(ROSTER_CONFIG.out..'bank-ft.csv','w'))
f:write('frame,poll,x,y,yHigh,state,previousAB,footL,footR,phase,fishFlag,fishID,fishState,fishX,fishY,fishHP,mask\n')
return function(c)
 if c.areaType~=0 then return finish(c)end
 age=age+1;assert(age<3500,'Bounded actual H water bank controller')
 local l,r=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local fx=c.r('Enemy_X_Position',2)+256*c.r('Enemy_PageLoc',2)
 local hp=c.r('MmEnemyHealthLo',2)+256*c.r('MmEnemyHealthHi',2)
 local b={b=c.poll%8<4}
 if phase==0 then
  assert(c.grounded and c.x==2049 and c.y==176 and(l~=0 or r~=0),'Actual supported fresh launch')
  assert(c.r('PreviousA_B_Buttons')&128==0,'Real released A')
  b.a=true;b.right=true;phase=1
 elseif phase==1 then
  b.right=c.x<2070;b.a=c.x<2070
  if c.x>=2070 then phase=2 end
 elseif phase==2 then
  if c.grounded then
   assert(c.y==112 and(l~=0 or r~=0),'Land on actual144 bank')
   phase=3
  end
 elseif phase==3 then
  if c.r('Enemy_Flag',2)==0 or c.r('Enemy_ID',2)~=10 or c.r('Enemy_State',2)&32~=0 or fx<c.x-32 then phase=4 end
 else
  b.right=true
  if c.x>=2840 then b.a=false
  elseif c.grounded then
   assert(c.yHigh==1 and c.y%16==0 and(l~=0 or r~=0),'Actual aligned water ground before A')
   b.right=false;release=release+1
   if release>=3 and c.r('PreviousA_B_Buttons')&128==0 then b.a=true;b.right=true;release=0 end
  else b.a=true;release=0 end
 end
 local mask=(b.a and128 or0)+(b.b and64 or0)+(b.right and1 or0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.yHigh,c.state,c.r('PreviousA_B_Buttons'),l,r,phase,c.r('Enemy_Flag',2),c.r('Enemy_ID',2),c.r('Enemy_State',2),fx,c.r('Enemy_Y_Position',2),hp,mask},',')..'\n');f:flush()
 return b
end
'''.replace('and128','and 128').replace('or0','or 0').replace('and64','and 64').replace('and1','and 1')

def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 parent=R/'build/roster-through-2-2/root49-h-samus-water-fh-2-v0-mmc3'
 rr=lambda p:list(csv.DictReader(p.open(newline='')))
 trace=rr(parent/'trace.csv');at=trace[29464];assert at['frame']=='29465' and (at['x'],at['y'],at['state'],at['buttons'])==('2049','176','0','64');n=29464
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:n])
 observer=V/'root49-current-g-samus-a/observer-g.lua';base=R/'tools/playthroughs/roster_policy.lua';policy=J/'policy.lua';policy.write_text(BODY.replace('OBSERVER',json.dumps(observer.as_posix())).replace('FINISH',json.dumps(base.as_posix())),encoding='utf-8')
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=n,next_parent_trace=at,policy_sha256=sha(policy),base_sha256=sha(base),workspace_before=used,phase_cap=200000000,reserve=100000000,global_cap=80000000000,scope='Actual unchanged H five-stage prefix. Fresh supported jump from2049/176; cut horizontal and A at2070 to land on2064 bank, shoot approaching actualfish owner2 before crossing the gap. Native terrain/ownership checked. No state writes/grants; discovery only, full independent proof remains required.'),indent=2)+'\n',encoding='utf-8')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-samus-bank-ft','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80','--discovery-fast']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n',encoding='utf-8')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2/root49-h-samus-bank-ft-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
