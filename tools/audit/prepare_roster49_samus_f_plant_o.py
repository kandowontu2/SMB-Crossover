"""Stop outside the live plant and finish it with ordinary airborne beam shots."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local age,done=0,false
local f=assert(io.open(ROSTER_CONFIG.out..'plant-combat-o.csv','w'))
f:write('frame,poll,x,y,state,previousAB,face,age,flag,id,enemyX,enemyY,enemyHP,mask,shots\n')
return function(c)
 if done then return base(c)end
 age=age+1;assert(age<700,'Bounded actual first2-1 live Piranha beam defense')
 local flag,id,state=c.r('Enemy_Flag',0),c.r('Enemy_ID',0),c.r('Enemy_State',0)
 local x=c.r('Enemy_X_Position',0)+256*c.r('Enemy_PageLoc',0)
 local hp=c.r('MmEnemyHealthLo',0)+256*c.r('MmEnemyHealthHi',0)
 if flag==0 or id~=13 or state&32~=0 then done=true;return base(c)end
 assert(c.world==1 and c.level==0 and c.x>=1610 and c.x<=1614 and x==1656,'Actual stationary beam range outside first2-1 pipe')
 assert(c.r('PlayerFacingDir')==1,'Retain actual right-facing beam; no oscillating air turn')
 local b={b=c.poll%8<4}
 if c.grounded then
  if c.r('PreviousA_B_Buttons')&128==0 then
   assert(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0,'Actual floor support before ordinary vertical jump')
   b.a=true
  end
 else b.a=true end
 local shots={}
 for i=0,2 do shots[#shots+1]=table.concat({c.r('SmShotType',i),c.r('SmShotAge',i),c.r('SmShotX',i)+256*c.r('SmShotPage',i),c.r('SmShotY',i)},':')end
 local mask=(b.b and 64 or 0)+(b.a and 128 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),c.r('PlayerFacingDir'),age,flag,id,x,c.r('Enemy_Y_Position',0),hp,mask,table.concat(shots,';')},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-o.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-n-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text());assert m['result']['frames']==24385
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='24350');assert pose['x']=='1612'and pose['y']=='100'and pose['state']=='1'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-24350-o.csv';prefix.write_text('\n'.join(lines[:24351])+'\n')
    policy=H/'policy-o.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-l.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-o-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-n.py').read_text().replace('native-n.log','native-o.log').replace('native-result-n.json','native-result-o.json').replace('allocation-n.json','allocation-o.json').replace('preparation-n-run.json','preparation-o-run.json').replace('policy-n.lua','policy-o.lua').replace('prefix-21200-n.csv','prefix-24350-o.csv').replace('root49-f-samus-route-n','root49-f-samus-route-o')
    (H/'run-o.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_OUT_OF_CONTACT_RANGE_SECOND_PLANT_HIT',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-o.py'),actual_prefix_pose=pose,
      hypothesis='N hits plant0 once75→35 but continues into its body before the second beam. Preserve actual24350 safeX1612/airY100 and neutral horizontal control, repeated B and supported vertical jump edges until actual owner defeat; HP0 alone is not defeat.',
      runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
