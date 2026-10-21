"""Leave the observed 2-1 shell-bounce proposal loop by ordinary controls."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-g-samus-a';J=H/'forward-h-cu'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local base=dofile(BASE)
local phase,age,release='cross',0,0
local log=assert(io.open(ROSTER_CONFIG.out..'forward-h.csv','w'))
log:write('frame,poll,x,y,state,previousAB,phase,age,release,mask,leftFoot,rightFoot\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<600,'Bounded actual shell-area forward progression')
 assert(c.world==1 and c.level==0 and c.areaType==1 and c.engine==8,'Actual 2-1')
 local b={right=true,b=c.poll%8<4,a=true}
 if c.grounded then
  if phase~='release'then phase='release';release=0 end
  release=release+1;b.right=false;b.a=false
  if release>=4 and c.r('PreviousA_B_Buttons')&128==0 then
   assert(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0,'Actual terrain before new grounded A')
   phase='takeoff';b.a=true;b.right=true
  end
 elseif phase=='takeoff'then phase='cross'end
 if c.x>=900 then phase='done'end
 local mask=(b.right and 1 or 0)+(b.a and 128 or 0)+(b.b and 64 or 0)
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),phase,age,release,mask,c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32)},',')..'\n');log:flush()
 return b
end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0';c=json.loads(cp.read_text())
 parent=R/'build/roster-through-2-2/root49-g-samus-boss-g-2-v0-mmc3';rr=lambda p:list(csv.DictReader(p.open(newline='')));at=rr(parent/'trace.csv')[24144]
 assert(at['frame'],at['world'],at['level'],at['mode'],at['task'],at['x'],at['y'])==('24145','1','0','1','3','781','113')
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rr(parent/'inputs.csv')[:24144])
 policy=J/'policy.lua';policy.write_text(BODY.replace('BASE',json.dumps((H/'resume-f-co/policy.lua').as_posix())))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);owned=sum(p.stat().st_size for p in H.rglob('*')if p.is_file())
 for p in(R/'build/roster-through-2-2').glob('root49-g-samus-*'):owned+=sum(q.stat().st_size for q in p.rglob('*')if q.is_file())
 assert total+100000000<80000000000 and owned+200000000<650000000
 pre=dict(script_sha256=sha(__file__),checkpoint_G_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),prefix_rows=24144,actual_preinput_pose=at,policy_sha256=sha(policy),base_sha256=sha(H/'resume-f-co/policy.lua'),scope='Actual G ordinary prefix, then Right/B/held-A and only actual supported fresh A after release. Rejoins valid F pose guidance at attained X900. No state/grants/ROM/RAM/register writes; no source/arsenal or fullclear claim.',phase_before=owned,phase_cap=650000000,reserve=100000000,global_cap=80000000000,workspace_before=total)
 (J/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
 rom=cp.parent/'smb-crossover-mmc3.nes';tag='root49-g-samus-forward-h';out=R/'build/roster-through-2-2'/(tag+'-2-v0-mmc3')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(rom),'--tag',tag,'--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80'];(J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,result=m.get('result'),actual_output=str(out.relative_to(R)),manifest_sha256=sha(out/'manifest.json'),native_log_sha256=sha(J/'native.log'),preparation_sha256=sha(J/'preparation.json'),analysis_pending=True,goal_complete=False)
 (J/'native-result.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
