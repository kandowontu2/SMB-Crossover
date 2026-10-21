"""Re-anchor controller proposals to the actual later pipe pose, not a stale early one."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'preparation-p.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-o-2-v0-mmc3';m=json.loads((parent/'manifest.json').read_text());assert m.get('result')is None
    pose=next(z for z in csv.DictReader((parent/'trace.csv').open())if z['frame']=='24680')
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-24680-p.csv';prefix.write_text('\n'.join(lines[:24681])+'\n')
    ref=(H/'reference-policy-h.lua').read_text();needle=" assert(score<2000,'Bounded actual Samus pose/reference distance')";assert ref.count(needle)==1
    addition=""" -- A completed long combat can leave the local proposal window behind.
 -- Re-anchor only controller guidance within this actual stage/area and48px.
 if score>400 then
  local chosen=best
  for i=idleFloor,#ref do
   local q=ref[i]
   if math.abs(q[6]-c.x)<=48 then
    local d=distance(c,q)
    if d<score-100 then chosen,score=i,d end
   end
  end
  if chosen~=best then best=chosen;idleFloor=math.max(idleFloor,best-3);still=0 end
 end
"""
    ref=ref.replace(needle,addition+needle).replace('controller-reference-a.csv','controller-reference-p.csv')
    rp=H/'reference-policy-p.lua';rp.write_text(ref)
    policy=H/'policy-p.lua';policy.write_text((H/'actor-policy-l.lua').read_text().replace('reference-policy-h.lua','reference-policy-p.lua').replace('actor-bombs-l.csv','actor-bombs-p.csv'))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-p-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-o.py').read_text().replace('native-o.log','native-p.log').replace('native-result-o.json','native-result-p.json').replace('allocation-o.json','allocation-p.json').replace('preparation-o-run.json','preparation-p-run.json').replace('policy-o.lua','policy-p.lua').replace('prefix-24350-o.csv','prefix-24680-p.csv').replace('root49-f-samus-route-o','root49-f-samus-route-p').replace('650000000','800000000')
    (H/'run-p.py').write_text(runner)
    allocation=dict(old_cap=650000000,new_cap=800000000,final_reserve=100000000,actual_phase_bytes=470399541,global_cap=70000000000,
      basis='Actual470.4MB +60MB next discovery +60MB independent fixed +100MB reserve exceeds650MB. Retain old receipts; future P and full-proof guard use800MB.')
    (H/'allocation-extension-p.json').write_text(json.dumps(allocation,indent=2)+'\n')
    out.write_text(json.dumps(dict(status='PREPARED_ACTUAL_POSE_REANCHORED_ORDINARY_CONTROLS',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      prefix_sha256=sha(prefix),policy_sha256=sha(policy),reference_sha256=sha(rp),runner_sha256=sha(H/'run-p.py'),actual_prefix_pose=pose,allocation=allocation,
      retained_O='Actual second beam defeats Piranha0 after safe stationary repeated jump fire. Later retained local reference remains atq20807 while actualX1828 and score1994; guard prevents another proposal. Re-anchor proposals to the actual later pose with original2000distance bound retained.',
      runtime_changed=False,emulated_writes=False,state_loads=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
