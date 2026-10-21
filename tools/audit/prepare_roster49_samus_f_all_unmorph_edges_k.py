"""Apply the demonstrated grounded Up-edge controller rule to later bomb fights."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
POLICY=r'''local base=dofile(BASE)
local age,done=0,false
local f=assert(io.open(ROSTER_CONFIG.out..'unmorph-k.csv','w'));f:write('frame,x,y,state,ball,previous,mask\n')
return function(c)
 if done then return base(c)end
 age=age+1;assert(age<100,'Bounded actual post-combat Up edge')
 local b={}
 if c.r('SmBall')==0 and c.grounded then done=true
 elseif age>4 and c.grounded and c.r('SmPreviousDirections')&8==0 then b.up=true end
 f:write(table.concat({c.frame,c.x,c.y,c.state,c.r('SmBall'),c.r('SmPreviousDirections'),b.up and 8 or 0},',')..'\n');f:flush()
 return b
end
'''
def main():
    out=H/'preparation-k.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-j-2-v0-mmc3'
    trace=list(csv.DictReader((parent/'trace.csv').open()));pose=next(z for z in trace if z['frame']=='12600')
    assert pose['x']=='1725'and pose['y']=='176'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-12600-k.csv';prefix.write_text('\n'.join(lines[:12601])+'\n')
    base=(H/'policy-h.lua').read_text();needle="elseif phase=='exit'then\n  b.up=true"
    assert base.count(needle)==1
    fixed=H/'actor-policy-k.lua';fixed.write_text(base.replace(needle,"elseif phase=='exit'then\n  b.up=c.grounded and c.r('SmPreviousDirections')&8==0").replace('actor-bombs-h.csv','actor-bombs-k.csv'))
    policy=H/'policy-k.lua';policy.write_text(POLICY.replace('BASE',json.dumps(fixed.as_posix())))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-k-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-j.py').read_text().replace('native-j.log','native-k.log').replace('native-result-j.json','native-result-k.json').replace('allocation-j.json','allocation-k.json').replace('preparation-j-run.json','preparation-k-run.json').replace('policy-j.lua','policy-k.lua').replace('prefix-11600-j.csv','prefix-12600-k.csv').replace('root49-f-samus-route-j','root49-f-samus-route-k')
    (H/'run-k.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_GROUNDED_UP_EDGE_FOR_EACH_LATER_BOMB_EXIT',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),actor_policy_sha256=sha(fixed),runner_sha256=sha(H/'run-k.py'),actual_prefix_pose=pose,
      retained_J='Ordinary planted-bomb retreat clears both1464 encounter Goombas, exits at11910 and advances to1725. Later generic controller repeats the already diagnosed held-Up-after-apex error; its550 guard remains unchanged.',
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
