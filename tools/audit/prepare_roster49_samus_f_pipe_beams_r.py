"""Use observed stationary beam kills for subsequent live pipe plants."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local target,age=nil,0
local f=assert(io.open(ROSTER_CONFIG.out..'pipe-beams-r.csv','w'))
f:write('frame,poll,x,y,state,previousAB,face,age,target,flag,id,enemyState,enemyX,enemyY,enemyHP,mask\n')
return function(c)
 if c.world~=1 or c.level~=0 then return base(c)end
 if target==nil then
  for i=0,5 do
   local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local dx=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)-c.x
   if flag>0 and flag<128 and id==13 and state&32==0 and dx>=48 and dx<=76 then target=i;age=0;break end
  end
 end
 if target==nil then return base(c)end
 local flag,id,state=c.r('Enemy_Flag',target),c.r('Enemy_ID',target),c.r('Enemy_State',target)
 local x=c.r('Enemy_X_Position',target)+256*c.r('Enemy_PageLoc',target)
 local hp=c.r('MmEnemyHealthLo',target)+256*c.r('MmEnemyHealthHi',target)
 if flag==0 or id~=13 or state&32~=0 then target=nil;age=0;return base(c)end
 age=age+1;assert(age<900,'Bounded actual next live Piranha beam defense')
 assert(x-c.x>=44 and x-c.x<=78 and c.r('PlayerFacingDir')==1,'Actual stationary right-facing range outside live pipe')
 local b={b=c.poll%8<4}
 if c.grounded then
  if c.r('PreviousA_B_Buttons')&128==0 then
   assert(c.block(c.x+4,c.y+32)~=0 or c.block(c.x+12,c.y+32)~=0,'Actual floor before ordinary vertical beam jump')
   b.a=true
  end
 else b.a=true end
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),c.r('PlayerFacingDir'),age,target,flag,id,state,x,c.r('Enemy_Y_Position',target),hp,(b.a and 128 or 0)+(b.b and 64 or 0)},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-r.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-q-2-v0-mmc3'
    m=json.loads((parent/'manifest.json').read_text());assert m['result']['frames']==25095 and m['result']['failure']=='death'
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='25020');assert pose['x']=='1888'and pose['y']=='167'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-25020-r.csv';prefix.write_text('\n'.join(lines[:25021])+'\n')
    policy=H/'policy-r.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-p.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-r-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-q.py').read_text()
    for a,b in [('native-q.log','native-r.log'),('native-result-q.json','native-result-r.json'),('allocation-q.json','allocation-r.json'),('preparation-q-run.json','preparation-r-run.json'),('policy-q.lua','policy-r.lua'),('prefix-24820-q.csv','prefix-25020-r.csv'),('root49-f-samus-route-q','root49-f-samus-route-r')]:runner=runner.replace(a,b)
    (H/'run-r.py').write_text(runner)
    report=dict(status='PREPARED_ACTUAL_PIPE_PLANT_BEAM_COMBAT',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-r.py'),actual_prefix_pose=pose,
      positive_Q='Second live pipe plant2 defeated by actual stationary beam: observer labeled24915/state34/rawHP65531; rawHP is an overkill wrap, not an alive/dead test.',
      negative_Q='Then ordinary inherited guidance approaches third live plant3/1960, takes one real40damage to35HP but collides25095 before finishing. Preserve exact prefix25020 and inspect nearby Goomba4 as an additional live threat.',
      runtime_changed=False,emulated_writes=False,state_loads=False,phase_cap=800000000,reserve=100000000,global_cap=70000000000,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
