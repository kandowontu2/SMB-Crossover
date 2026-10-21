"""Use actual H terrain takeoffs to climb the observed 1-1 staircase."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-stairs-dp'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
local phase,age,release,airSeen='stairs',0,0,false
local f=assert(io.open(ROSTER_CONFIG.out..'stairs-dp.csv','w'))
f:write('frame,poll,x,y,state,previousAB,feetL,feetR,phase,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<600,'Bounded actual H staircase controls')
 assert(c.world==0 and c.level==0 and c.areaType==1,'Actual1-1 staircase')
 local l,r=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local b={right=true,b=c.poll%8<4}
 if c.grounded then
  release=release+1
  if c.x>=2220 then phase='done';return base(c)end
  if release>=4 and c.r('PreviousA_B_Buttons')&128==0 then
   assert(c.y%16==0 and(l~=0 or r~=0),'Actual aligned terrain for staircase takeoff')
   b.a=true;airSeen=false
  end
 else
  b.a=true;release=0;airSeen=true
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),l,r,phase,mask},',')..'\n');f:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 parent=R/'build/roster-through-2-2/root49-h-samus-pose-dn-2-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')));tr=rr(parent/'trace.csv')
 at=next(q for q in tr if q['x']=='2129'and q['y']=='176'and q['state']=='0'and q['engine']=='8');n=int(at['frame']);tape=rr(parent/'inputs.csv')[:n]
 assert len(tape)==n
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(tape)
 base=V/'root49-samus-h-pose-dn/policy.lua';policy=J/'policy.lua';policy.write_text(BODY.replace('BASE',json.dumps(base.as_posix())))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=n,observed_ground=at,policy_sha256=sha(policy),base_sha256=sha(base),phase_cap=200000000,reserve=100000000,global_cap=80000000000,workspace_before=used,scope='Ordinary native H prefix, then actual supported staircase A edges and nearest actual G-pose guidance. No runtime changes, state/grants or theoretical hidden support. No complete route assertion.'),indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-samus-stairs-dp','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2/root49-h-samus-stairs-dp-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
