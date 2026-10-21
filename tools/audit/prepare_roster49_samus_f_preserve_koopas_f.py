"""Retain the executed Koopa solution; bomb the subsequent Goomba wave."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'preparation-f.json';assert not out.exists()
    e=R/'build/roster-through-2-2/root49-f-samus-route-e-2-v0-mmc3'
    em=json.loads((e/'manifest.json').read_text());assert em['result']['frames']==9457 and em['result']['failure']=='death'
    a=list(csv.DictReader((e/'actual-injury-b.csv').open()))
    owner=[z for z in a if z['event']=='InjurePlayer'and z['slot']==z['owner']][-1]
    assert owner['slot']=='2'and owner['id']=='0'and int(owner['ex'])<int(owner['playerX'])
    parent=R/'build/roster-through-2-2/root49-f-samus-route-c-2-v0-mmc3'
    t=list(csv.DictReader((parent/'trace.csv').open()));pose=next(z for z in t if z['frame']=='9540')
    assert pose['x']=='829'and pose['y']=='176'and pose['state']=='0'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=H/'prefix-9540-f.csv';prefix.write_text('\n'.join(lines[:9541])+'\n')
    policy=H/'policy-f.lua';s=(H/'policy-e.lua').read_text().replace('actor-bombs-e.csv','actor-bombs-f.csv')
    # The earlier real C jump/shoot sequence already resolves both Koopas.
    # Do not replace it with a stationary pincer fight; preserve that input.
    policy.write_text(s)
    pre=json.loads((H/'preparation-a.json').read_text());pre.update(policy_sha256=sha(policy),prefix_sha256=sha(prefix))
    (H/'preparation-f-run.json').write_text(json.dumps(pre,indent=2)+'\n')
    runner=(H/'run-e.py').read_text().replace('native-e.log','native-f.log').replace('native-result-e.json','native-result-f.json').replace('allocation-e.json','allocation-f.json').replace('preparation-e-run.json','preparation-f-run.json').replace('policy-e.lua','policy-f.lua').replace('prefix-9180-e.csv','prefix-9540-f.csv').replace('root49-f-samus-route-e','root49-f-samus-route-f')
    (H/'run-f.py').write_text(runner)
    out.write_text(json.dumps(dict(status='PREPARED_PRESERVED_REAL_KOOPA_PREFIX_AND_NEXT_BOMB_WAVE',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),runner_sha256=sha(H/'run-f.py'),actual_prefix_pose=pose,
      retained_E=dict(manifest_sha256=sha(e/'manifest.json'),actual_fatal_owner=owner,reason='A Koopa approached from behind while E watched only the front. No bomb had reached fuse58. Preserve the demonstrated C Koopa solution before proposing later bomb combat.'),
      runtime_changed=False,emulated_writes=False,goal_complete=False),indent=2)+'\n')
    print('PREPARED',sha(out),flush=True)
if __name__=='__main__':main()
