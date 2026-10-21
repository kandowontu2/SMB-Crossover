"""Cold-replay the complete real Sophia incident on the private body candidate."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-sophia-source-body-hs'
H=D/'ordinary-hu'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    meta=V/'agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('sophia_hu_meta',meta)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    im=m.Image(D/'source/build/smb-crossover-mmc3.nes')
    old=V/'root49-gq-sophia-route-gw'
    bind=json.loads((old/'binding.json').read_text())
    assert sha(old/'observer.lua')==bind['observer_sha256']
    assert sha(R/bind['base_policy']['path'])==bind['base_policy']['sha256']
    inputs=R/'build/roster-through-2-2/root49hg-sophia-live-11-v0-mmc3/inputs.csv'
    assert sha(inputs)=='4a22350204704da67065adf1d8a0bc4fa8ebdb7bdf03475aa8afbea0a1afdd79'
    names=['GameLoop','ExpandedMovement','EnemyToBGCollisionDet','PlayerEnemyCollision','FirebarCollision','InjurePlayer','ForceInjury','KillPlayer']
    hooks={n:im.hook(n)for n in names}
    H.mkdir()
    # The same read-only observer uses newly compiled physical banks/eight bytes.
    observer=H/'observer.lua';observer.write_bytes((old/'observer.lua').read_bytes())
    policy=H/'policy.lua'
    policy.write_text('SOPHIA_GQ_HOOKS='+m.lua(hooks)+'\nSOPHIA_GQ_BASE='+m.lua(str(R/bind['base_policy']['path']).replace('\\','/'))+'\nreturn dofile('+m.lua(observer.as_posix())+')\n')
    command=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','11','--mapper','mmc3',
        '--rom',str(im.path),'--tag','root49hu-sophia-body','--policy',str(policy),'--replay',str(inputs),
        '--frames','11129','--timeout','900','--workspace-cap-gb','60']
    record=dict(status='PREPARED_FULL_FIXED_REAL_INPUT_REPLAY',ROM=im.metadata(),hooks=hooks,
        input_sha256=sha(inputs),policy_sha256=sha(policy),observer_sha256=sha(observer),
        original_binding_sha256=sha(old/'binding.json'),script_sha256=sha(__file__),command=command,
        emulated_writes=False,state_loads=False,
        scope='Unchanged whole11128-poll controller tape, cold boot. A new timing/contact divergence is diagnostic, not assumed source regression or a fullclear.')
    (H/'binding.json').write_text(json.dumps(record,indent=2)+'\n')
    rc=subprocess.run(command,cwd=R).returncode
    (H/'host-result.json').write_text(json.dumps(dict(exit=rc),indent=2)+'\n')
    raise SystemExit(rc)


if __name__=='__main__':main()
