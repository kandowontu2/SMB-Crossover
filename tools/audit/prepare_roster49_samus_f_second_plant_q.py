"""Preserve real airborne range and defeat the second pipe plant with the beam."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local age,done=0,false
local f=assert(io.open(ROSTER_CONFIG.out..'second-plant-q.csv','w'))
f:write('frame,poll,x,y,state,previousAB,face,age,flag,id,enemyState,enemyX,enemyY,enemyHP,mask\n')
return function(c)
 if done then return base(c)end
 age=age+1;assert(age<900,'Bounded actual second2-1 Piranha beam defense')
 local flag,id,state=c.r('Enemy_Flag',2),c.r('Enemy_ID',2),c.r('Enemy_State',2)
 local x=c.r('Enemy_X_Position',2)+256*c.r('Enemy_PageLoc',2)
 local hp=c.r('MmEnemyHealthLo',2)+256*c.r('MmEnemyHealthHi',2)
 if flag==0 or id~=13 or state&32~=0 then done=true;return base(c)end
 assert(c.world==1 and c.level==0 and c.x>=1791 and c.x<=1793 and x==1848,'Actual stationary range outside second pipe')
 assert(c.r('PlayerFacingDir')==1,'Actual right-facing stationary beam')
 local b={b=c.poll%8<4}
 if c.grounded then
  if c.r('PreviousA_B_Buttons')&128==0 then
   assert(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0,'Actual supported ordinary vertical jump')
   b.a=true
  end
 else b.a=true end
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),c.r('PlayerFacingDir'),age,flag,id,state,x,c.r('Enemy_Y_Position',2),hp,(b.a and128 or0)+(b.b and64 or0)},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-q.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-p-2-v0-mmc3'
    m=json.loads((parent/'manifest.json').read_text());assert m['result']['frames']==24886 and m['result']['failure']=='death'
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='24820')
    assert pose['x']=='1792'and pose['y']=='100'and pose['state']=='1'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-24820-q.csv';prefix.write_text('\n'.join(lines[:24821])+'\n')
    policy=H/'policy-q.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-p.lua').as_posix())).replace('and128','and 128').replace('and64','and 64').replace('or0','or 0'))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-q-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-p.py').read_text()
    for a,b in [('native-p.log','native-q.log'),('native-result-p.json','native-result-q.json'),('allocation-p.json','allocation-q.json'),('preparation-p-run.json','preparation-q-run.json'),('policy-p.lua','policy-q.lua'),('prefix-24680-p.csv','prefix-24820-q.csv'),('root49-f-samus-route-p','root49-f-samus-route-q')]:runner=runner.replace(a,b)
    (H/'run-q.py').write_text(runner)
    report=dict(status='PREPARED_ACTUAL_SECOND_PLANT_STATIONARY_BEAM',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-q.py'),actual_prefix_pose=pose,
      mechanism='At actual24820 X1792/Y100, neutral Samus horizontal input resets velocity. Retain right-facing beam and ordinary supported vertical jumps until actual plant2 defeat, not lazyHP0. Rear Goomba moves away while Samus remains above; verify actual runtime rather than assume survival.',
      retained_P_negative='P dies24886 on actual plant2 ID13 at1848/Y152; native player bottom166 touches plant proxy top166. No source geometry defect inferred.',
      phase_cap=800000000,reserve=100000000,global_cap=70000000000,runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
