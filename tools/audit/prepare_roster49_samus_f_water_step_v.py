"""Replace the observed blocked underwater walk with a real coral jump."""
from pathlib import Path
import csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age='release',0
local f=assert(io.open(ROSTER_CONFIG.out..'water-step-v.csv','w'))
f:write('frame,poll,x,y,state,previousAB,phase,age,leftFoot,rightFoot,front,mask,actors\n')
return function(c)
 if phase=='done'or c.world~=1 or c.level~=1 then return base(c)end
 age=age+1;assert(age<220,'Bounded actual underwater coral-step jump')
 local lf,rf=c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32)
 local front=c.block(c.x+16,c.y+16);local b={b=c.poll%8<4}
 if phase=='release'then
  assert(c.x>=1233 and c.x<=1235 and c.y==176 and c.grounded,'Actual supported stop at coral wall')
  if age>=4 and c.r('PreviousA_B_Buttons')&128==0 then
   assert((lf~=0 or rf~=0)and front~=0,'Actual floor and coral before ordinary freshA');phase='jump'
  end
 elseif phase=='jump'then
  b.right=true;b.a=true
  if c.x>=1290 or(c.grounded and c.y<=128 and c.x>=1248)then phase='done'end
 end
 local actors={}
 for i=0,5 do actors[#actors+1]=table.concat({i,c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i)},':')end
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),phase,age,lf,rf,front,(b.right and 1 or 0)+(b.a and 128 or 0)+(b.b and 64 or 0),table.concat(actors,';')},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-v.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-u-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text());assert m['result']['frames']==30050 and m['result']['failure']=='death'
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='29916');assert pose['x']=='1233'and pose['y']=='176'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-29916-v.csv';prefix.write_text('\n'.join(lines[:29917])+'\n')
    policy=H/'policy-v.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-t.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix));(H/'preparation-v-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    owned={q for q in H.rglob('*')if q.is_file()}
    for p in(R/'build/roster-through-2-2').glob('root49-f-samus-*'):owned.update(q for q in p.rglob('*')if q.is_file())
    owned.update(V.glob('smb-crossover-*-run-root49-f-samus-*.log'));size=sum(p.stat().st_size for p in owned);total=workspace_bytes(R)
    assert size+60000000+100000000<1050000000 and total+60000000<70000000000
    allocation=dict(old_cap=900000000,new_cap=1050000000,actual_phase_bytes=size,global_bytes=total,global_cap=70000000000,final_reserve=100000000,
      basis='Retained actual phase plus60MB discovery,60MB independent fixed and100MB reserve exceeds900MB. Raise this internal phase cap only; preserve all earlier receipts and user-requested lossless evidence.')
    (H/'allocation-extension-v.json').write_text(json.dumps(allocation,indent=2)+'\n')
    runner=(H/'run-u.py').read_text()
    for a,b in [('native-u.log','native-v.log'),('native-result-u.json','native-result-v.json'),('allocation-u.json','allocation-v.json'),('preparation-u-run.json','preparation-v-run.json'),('policy-u.lua','policy-v.lua'),('prefix-29650-u.csv','prefix-29916-v.csv'),('root49-f-samus-route-u','root49-f-samus-route-v'),('900000000','1050000000')]:runner=runner.replace(a,b)
    (H/'run-v.py').write_text(runner)
    report=dict(status='PREPARED_ACTUAL_UNDERWATER_CORAL_SUPPORTED_JUMP',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-v.py'),actual_prefix_pose=pose,allocation=allocation,
      mechanism='U actual waiting lets Red0 pass, then avoids original highGrey1 and reaches floor1233/Y176 at29916. Its walk-low endcondition1260 is beyond a real coral wall, so it stands134frames until Bloober3 descends onto its head at30050. Use ordinary supported freshA before that delay, then hand back after native elevated landing or real crossing.',
      runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),size,total,flush=True)
if __name__=='__main__':main()
