"""Fresh supported A from the actual H castle platform, before its right edge."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-water-bank-fd'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
local phase,age,release='release',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'water-bank-fb.csv','w'))
f:write('frame,poll,x,y,state,phase,previousAB,footL,footR,mask\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<500,'Bounded supported water bank crossing')
 assert(c.world==1 and c.level==1 and c.areaType==0,'Actual Samus water')
 local l,r=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 local b={b=c.poll%8<4}
 if phase=='release'then
  assert(c.grounded and c.y==96 and(l~=0 or r~=0),'Actual coral top before freshA')
  release=release+1
  if release>=3 and c.r('PreviousA_B_Buttons')&128==0 then phase='cross';b.a=true;b.right=true end
 elseif phase=='cross'then
  b.a=true;b.right=true
  if c.x>=1264 then phase='done';return base(c)end
 end
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,phase,c.r('PreviousA_B_Buttons'),l,r,mask},',')..'\n');f:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 parent=R/'build/roster-through-2-2/root49-h-samus-resume-ex-2-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')));trace=rr(parent/'trace.csv');at=next(z for z in trace if int(z['frame'])>=28600 and (z['world'],z['level'],z['x'],z['y'],z['state'],z['engine'])==('1','1','1148','96','0','8'));n=int(at['frame'])-1
 assert trace[n]==at
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:n])
 original=V/'root49-current-g-samus-a/resume-f-co/policy.lua';base=J/'guide.lua';g=original.read_text();g=g.replace(' or q[4]~=c.area','').replace("..'-'..c.area..'-'..c.areaType","..'-'..c.areaType");base.write_text(g)
 policy=J/'policy.lua';policy.write_text(BODY.replace('BASE',json.dumps(base.as_posix())))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=n,next_parent_trace=at,policy_sha256=sha(policy),base_sha256=sha(base),workspace_before=used,phase_cap=200000000,reserve=100000000,global_cap=80000000000,scope='Actual unchanged H prefix includes four cleared stages and late supported castle jump. Prior DN guide wrongly kept recomputing beyond its permanent fallback and rejected a future parser AreaPointer change. Continue ordinary floor Right to900 then use valid F proposals with world/level/areaType, retaining live H positions. One injury observer only; no duplicate callbacks/log streams. No state writes/grants; discovery only, final full fixed proof required.'),indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-samus-water-fd','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80','--discovery-fast']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2/root49-h-samus-water-fd-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
