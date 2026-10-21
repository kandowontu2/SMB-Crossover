"""Resume actual G ordinary play after both underground bomb encounters."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-g-samus-a';J=H/'boss-g-cp'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert J.exists() and (J/'preflight-negative.json').exists() and not (J/'preparation.json').exists()
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';c=json.loads(cp.read_text());assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0'
 parent=R/'build/roster-through-2-2/root49-g-samus-resume-f-2-v0-mmc3';rows=lambda p:list(csv.DictReader(p.open(newline='')))
 t=rows(parent/'trace.csv');at=t[22279];assert(at['frame'],at['world'],at['level'],at['x'],at['y'],at['state'])==('22280','0','3','2100','128','0')
 prefix=J/'prefix.csv'
 with prefix.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(rows(parent/'inputs.csv')[:22280])
 policy=J/'policy.lua';body=(H/'policy-a.lua').read_text();old='if mask==0 and c.grounded and c.vx==0 then floor=math.min(#ref,best+1);cursor=floor end';new='if mask&131==0 and c.grounded and c.vx==0 then floor=math.min(#ref,best+1);cursor=floor end';assert body.count(old)==1;body=body.replace(old,new)
 body='local base=dofile('+json.dumps((H/'resume-f-co/policy.lua').as_posix())+')\n'+r'''
local phase,age='release',0
local log=assert(io.open(ROSTER_CONFIG.out..'boss-jump-g.csv','w'))
log:write('frame,poll,x,y,state,previousAB,phase,age,mask,bosses,leftFoot,rightFoot\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<240,'Bounded actual bridge jump')
 assert(c.world==0 and c.level==3 and c.areaType==3 and c.engine==8,'Actual castle bridge')
 local bosses={};for i=0,5 do
  bosses[#bosses+1]=table.concat({i,c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i),c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},':')
 end
 local b={b=c.poll%8<4}
 if phase=='release'then
  assert(c.grounded and c.x>=2095 and c.x<=2110,'Attained actual bridge support before fresh A')
  if age>=4 and c.r('PreviousA_B_Buttons')&128==0 then
   assert(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0,'Actual bridge tile before takeoff');phase='jump'
  end
 elseif phase=='jump'then
  b.right=true;b.a=true
  if c.x>=2190 then phase='done'end
 end
 local mask=(b.right and 1 or 0)+(b.a and 128 or 0)+(b.b and 64 or 0)
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),phase,age,mask,table.concat(bosses,';'),c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32)},',')..'\n');log:flush()
 return b
end
'''
 policy.write_text(body)
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);owned=sum(p.stat().st_size for p in H.rglob('*')if p.is_file())
 for p in(R/'build/roster-through-2-2').glob('root49-g-samus-*'):owned+=sum(q.stat().st_size for q in p.rglob('*')if q.is_file())
 assert total+100000000<80000000000 and owned+200000000<650000000
 pre=dict(script_sha256=sha(__file__),checkpoint_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),parent_inputs_sha256=sha(parent/'inputs.csv'),prefix_rows=22280,prefix_sha256=sha(prefix),actual_pose=at,policy_sha256=sha(policy),parent_policy_sha256=sha(H/'policy-a.lua'),controller_change='Advance a stationary, grounded no-A/no-horizontal proposal even if B is held. This addresses a measured nearest-pose stationary-B controller ambiguity; no runtime patch or scheduling-equivalence claim.',phase_before=owned,phase_cap=650000000,reserve=100000000,workspace_before=total,global_cap=80000000000,scope='Actual E power-on prefix retained. Valid F poses after prefix are ordinary-button proposals only. F29923+ excluded, no state/RAM/register/ROM writes or grants.')
 (J/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
 image=next(b['artifacts']['nes']['frozen_path']for b in c['builds']if b['mapper']=='mmc3')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(R/image),'--tag','root49-g-samus-boss-g','--policy',str(policy),'--prefix',str(prefix),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 p=R/'build/roster-through-2-2/root49-g-samus-resume-f-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text())
 result=dict(exit=q.returncode,result=m.get('result'),manifest_sha256=sha(p/'manifest.json'),native_log_sha256=sha(J/'native.log'),preparation_sha256=sha(J/'preparation.json'),analysis_pending=True,goal_complete=False)
 (J/'native-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
