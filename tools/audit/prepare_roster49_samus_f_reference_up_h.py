"""Advance the reference controller after an already completed Up action."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'preparation-h.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-f-samus-route-g-2-v0-mmc3'
    rows=list(csv.DictReader((parent/'unmorph-edge-g.csv').open()))
    assert rows[-1]['phase']=='done'and rows[-1]['ball']=='0'and rows[-1]['frame']=='10015'
    trace=list(csv.DictReader((parent/'trace.csv').open()));pose=next(z for z in trace if z['frame']=='10770')
    assert pose['x']=='1020'and pose['y']=='176'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-10770-h.csv';prefix.write_text('\n'.join(lines[:10771])+'\n')
    ref=(H/'reference-policy-b.lua').read_text();needle='if mask==0 and c.grounded and c.vx==0 then idleFloor=best+1;cursor=idleFloor end'
    assert ref.count(needle)==1
    ref=ref.replace(needle,needle+"\n  if mask==8 and c.grounded and c.r('SmBall')==0 and c.r('SmCrouch')==0 then idleFloor=best+1;cursor=idleFloor end")
    reference=H/'reference-policy-h.lua';reference.write_text(ref)
    policy=H/'policy-h.lua';policy.write_text((H/'policy-f.lua').read_text().replace('reference-policy-b.lua','reference-policy-h.lua').replace('actor-bombs-f.csv','actor-bombs-h.csv'))
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-h-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-f.py').read_text().replace('native-f.log','native-h.log').replace('native-result-f.json','native-result-h.json').replace('allocation-f.json','allocation-h.json').replace('preparation-f-run.json','preparation-h-run.json').replace('policy-f.lua','policy-h.lua').replace('prefix-9540-f.csv','prefix-10770-h.csv').replace('root49-f-samus-route-f','root49-f-samus-route-h')
    (H/'run-h.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_CURRENT_FORM_COMPLETED_UP_REFERENCE_ADVANCE',script_sha256=sha(__file__),parent_manifest_sha256=sha(parent/'manifest.json'),
      unmorph_trace_sha256=sha(parent/'unmorph-edge-g.csv'),prefix_sha256=sha(prefix),reference_sha256=sha(reference),policy_sha256=sha(policy),runner_sha256=sha(H/'run-h.py'),actual_prefix_pose=pose,
      retained_G='Real Up release then press exits Morph Ball and lands upright at10015. Later generic reference controller stalls on a completed Up action at1020; no runtime failure inferred.',
      G_hook_qualification='The SamusCanStand last-byte hook includes its trailing Offsets table and was not a return witness. Only the guarded entry hook attained. Actual unseeded SmBall and pose transitions prove exit; no return-ABI claim.',
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
