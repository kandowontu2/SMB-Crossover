"""Request a fresh supported jump at the observed underground brick step."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age='release',0
local f=assert(io.open(ROSTER_CONFIG.out..'step-jump-i.csv','w'))
f:write('frame,poll,x,y,state,phase,age,previousAB,mask,leftFoot,rightFoot,front\n')
return function(c)
 if phase=='done'then return base(c)end
 age=age+1;assert(age<100,'Bounded actual underground brick-step jump')
 local b={}
 local lf,rf=c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32)
 if phase=='release'then
  assert(c.world==0 and c.level==1 and c.x>=1360 and c.x<=1362 and c.y==96 and c.grounded,'Actual observed grounded step approach')
  if age>=4 and c.r('PreviousA_B_Buttons')&128==0 then
   assert(lf~=0 or rf~=0,'Actual supporting terrain below one native foot before fresh A')
   phase='jump'
  end
 elseif phase=='jump'then
  b.right=true;b.a=true
  if c.x>=1410 then phase='done'end
 end
 local mask=(b.a and 128 or 0)+(b.right and 1 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,phase,age,c.r('PreviousA_B_Buttons'),mask,lf,rf,c.block(c.x+16,c.y+16)},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-i.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-h-2-v0-mmc3'
    trace=list(csv.DictReader((parent/'trace.csv').open()));pose=next(z for z in trace if z['frame']=='11410')
    assert pose['x']=='1361'and pose['y']=='96'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-11410-i.csv';prefix.write_text('\n'.join(lines[:11411])+'\n')
    policy=H/'policy-i.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-h.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-i-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-h.py').read_text().replace('native-h.log','native-i.log').replace('native-result-h.json','native-result-i.json').replace('allocation-h.json','allocation-i.json').replace('preparation-h-run.json','preparation-i-run.json').replace('policy-h.lua','policy-i.lua').replace('prefix-10770-h.csv','prefix-11410-i.csv').replace('root49-f-samus-route-h','root49-f-samus-route-i')
    (H/'run-i.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_SUPPORTED_STEP_JUMP_FROM_ACTUAL_F_POSE',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-i.py'),actual_prefix_pose=pose,
      hypothesis='H closest-pose reference repeatedly walks into the16px brick step at1361/Y96. Propose an ordinary fresh A from actual grounded terrain, retaining the completed prefix.',
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
