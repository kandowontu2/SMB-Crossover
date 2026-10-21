"""Use a real supported jump at the third pipe after actual beam defeat."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local phase,age='release',0
local f=assert(io.open(ROSTER_CONFIG.out..'pipe-step-s.csv','w'))
f:write('frame,poll,x,y,state,previousAB,phase,age,leftFoot,rightFoot,front,mask\n')
return function(c)
 if phase=='done'or c.world~=1 or c.level~=0 then return base(c)end
 age=age+1;assert(age<220,'Bounded actual third pipe supported takeoff')
 local lf,rf=c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32)
 local front=c.block(c.x+16,c.y+16)
 local b={}
 if phase=='release'then
  assert(c.x==1937 and c.y==176 and c.grounded,'Actual stopped pipe approach')
  if age>=4 and c.r('PreviousA_B_Buttons')&128==0 then
   assert((lf~=0 or rf~=0)and front~=0,'Actual floor and pipe side before ordinary jump');phase='jump'
  end
 elseif phase=='jump'then
  b.right=true;b.a=true;b.b=c.poll%8<4
  if c.x>=2000 then phase='done'end
 end
 local mask=(b.right and 1 or 0)+(b.a and 128 or 0)+(b.b and 64 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),phase,age,lf,rf,front,mask},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-s.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-r-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text());assert m.get('result')is None
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='25380');assert pose['x']=='1937'and pose['y']=='176'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-25380-s.csv';prefix.write_text('\n'.join(lines[:25381])+'\n')
    policy=H/'policy-s.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-r.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix));(H/'preparation-s-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-r.py').read_text()
    for a,b in [('native-r.log','native-s.log'),('native-result-r.json','native-result-s.json'),('allocation-r.json','allocation-s.json'),('preparation-r-run.json','preparation-s-run.json'),('policy-r.lua','policy-s.lua'),('prefix-25020-r.csv','prefix-25380-s.csv'),('root49-f-samus-route-r','root49-f-samus-route-s')]:runner=runner.replace(a,b)
    (H/'run-s.py').write_text(runner)
    report=dict(status='PREPARED_ACTUAL_SUPPORTED_THIRD_PIPE_JUMP',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-s.py'),actual_prefix_pose=pose,
      mechanism='R stationary beam defeats third plant3, then retained reference points at Right on the tall pipe side and reaches bounded stillness guard. A genuinely grounded1937/Y176 with released native latch can jump using actual foot and front terrain; preserve original guard and all negatives.',
      phase_cap=800000000,reserve=100000000,global_cap=70000000000,runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
