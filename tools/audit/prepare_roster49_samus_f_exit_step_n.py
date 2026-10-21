"""Retain the real Bowser defeat; jump from the supported raised exit approach."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local age,phase=0,'release'
local f=assert(io.open(ROSTER_CONFIG.out..'castle-step-n.csv','w'))
f:write('frame,poll,x,y,state,previousAB,phase,age,mask,leftFoot,rightFoot,front\n')
return function(c)
 if phase=='done'or c.world~=0 or c.level~=3 then return base(c)end
 age=age+1;assert(age<180,'Bounded actual post-Bowser raised exit jump')
 local b={}
 local lf,rf=c.block(c.x+4,c.y+32),c.block(c.x+12,c.y+32)
 if phase=='release'then
  assert(c.x==2241 and c.y==128 and c.grounded,'Actual post-defeat supported exit approach')
  if age>=4 and c.r('PreviousA_B_Buttons')&128==0 then
   assert(lf~=0 or rf~=0,'Actual bridge support before fresh ordinary exit jump');phase='jump'
  end
 elseif phase=='jump'then
  b.right=true;b.a=true
  if c.x>=2300 then phase='done'end
 end
 local mask=(b.right and 1 or 0)+(b.a and 128 or 0)
 f:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.r('PreviousA_B_Buttons'),phase,age,mask,lf,rf,c.block(c.x+16,c.y+16)},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-n.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-m-2-v0-mmc3'
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='21200')
    assert pose['x']=='2241'and pose['y']=='128'and pose['state']=='0'
    deaths=[z for z in csv.DictReader((parent/'live-boss-m.csv').open())if z['defeated']=='1'];assert deaths[0]['frame']=='21054'
    assert deaths[0]['actors'].split(';')[0].split(':')[1:4]==['1','6','35']
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-21200-n.csv';prefix.write_text('\n'.join(lines[:21201])+'\n')
    policy=H/'policy-n.lua';policy.write_text(POLICY.replace('BASE',json.dumps((H/'policy-l.lua').as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-n-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-m.py').read_text().replace('native-m.log','native-n.log').replace('native-result-m.json','native-result-n.json').replace('allocation-m.json','allocation-n.json').replace('preparation-m-run.json','preparation-n-run.json').replace('policy-m.lua','policy-n.lua').replace('prefix-21000-m.csv','prefix-21200-n.csv').replace('root49-f-samus-route-m','root49-f-samus-route-n')
    (H/'run-n.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_SUPPORTED_POST_DEFEAT_EXIT_JUMP',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-n.py'),actual_prefix_pose=pose,
      retained_M='Actual starting beam reduces real boss120→80→40→0 and retypes owner0 to defeatedGoomba6/state35 at21054. Controller then walks into raised exit2241/Y128 until900guard; no game death.',
      runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
