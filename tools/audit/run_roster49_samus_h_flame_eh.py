"""Stay below the observed castle flame, then use a genuine bridge takeoff."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-flame-eh'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
local phase,age,release='under-flame',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'flame-eh.csv','w'))
f:write('frame,poll,world,level,x,y,state,phase,previousAB,feetL,feetR,actors,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 if phase=='resume'then
  if c.world==0 and c.level==3 and c.x>=2095 and c.grounded then phase='bridge-release';age=0;release=0
  elseif c.world~=0 or c.level~=3 then phase='done';return base(c)
  else return base(c)end
 end
 age=age+1;assert(age<900,'Bounded actual flame/bridge controls')
 assert(c.world==0 and c.level==3 and c.areaType==3,'Actual H castle')
 local b={b=c.poll%8<4}
 if phase=='under-flame'then
  -- The retained failure jumps from the real floor into a flame atY112.
  -- Keep ordinary Right/A-released below that projectile instead.
  b.right=true
  if c.x>=1640 then phase='resume';return base(c)end
 elseif phase=='bridge-release'then
  assert(c.grounded and c.x<2110,'Actual bridge before fresh A')
  release=release+1
  if release>=4 and c.r('PreviousA_B_Buttons')&128==0 then
   assert(c.y%16==0 and(c.block(c.x+2,c.y+32)~=0 or c.block(c.x+13,c.y+32)~=0),'Actual aligned bridge support')
   phase='bridge-jump';b.a=true;b.right=true
  end
 elseif phase=='bridge-jump'then
  b.a=true;b.right=true
  if c.x>=2195 then phase='done' end
 end
 local actors={}
 for i=0,5 do if c.r('Enemy_Flag',i)>0 then
  actors[#actors+1]=table.concat({i,c.r('Enemy_ID',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i)},':')
 end end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.world,c.level,c.x,c.y,c.state,phase,c.r('PreviousA_B_Buttons'),c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32),table.concat(actors,';'),mask},',')..'\n');f:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 parent=R/'build/roster-through-2-2/root49-h-samus-firebar-ea-2-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')));t=rr(parent/'trace.csv');n=19408;at=t[n]
 assert(at['frame'],at['world'],at['level'],at['state'],at['y'],at['engine'])==('19409','0','3','0','128','8')
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:n])
 base=V/'root49-samus-h-pose-dn/policy.lua';policy=J/'policy.lua';policy.write_text(BODY.replace('BASE',json.dumps(base.as_posix())))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=n,next_parent_trace=at,policy_sha256=sha(policy),base_sha256=sha(base),workspace_before=used,phase_cap=200000000,reserve=100000000,global_cap=80000000000,scope='Ordinary actual H prefix; A-off below real flame then current terrain/bridge A. Native positions remain H, no manufactured state or source defect claim. Discovery-fast retains custom injury/control observers; final complete fixed hardware proof still required.'),indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-samus-flame-eh','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80','--discovery-fast']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2/root49-h-samus-flame-eh-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
