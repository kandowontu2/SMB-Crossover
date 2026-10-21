"""Root execution of frozen passive O under the later user-authorized cap."""
from pathlib import Path
import hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/agent49n-bill-late-contact-observer-o'
OWN=ROOT/'build/verification/root49n-bill-late-contact-o-admission-a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OWN.exists()
    policy=ROOT/'build/verification/root-workspace-storage-policy-50gb-a.json'
    assert sha(policy)=='564e723e5d8f248ac4b9cdf5db57b434e30ae06d806dcffd5668862220d1dc80'
    cap=json.loads(policy.read_text())['cap_bytes'];assert cap==50_000_000_000
    assert sha(PACKET/'freeze.json')=='aea80d63f91bcb09fe1dfceb4ea409b0bffb8e10e936c0bf46330ec3debb2f2e'
    OWN.mkdir()
    # Keep the old packet/30GB guard immutable; its complete host gate still runs.
    with (OWN/'host-preflight.log').open('wb')as f:
        gate=subprocess.run([sys.executable,str(PACKET/'preflight.py')],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    assert gate.returncode==0,str(OWN/'host-preflight.log')
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);reserve=50_000_000;other_active_future=0
    assert used+reserve+other_active_future<cap
    prep=json.loads((PACKET/'preparation.json').read_text())
    command=[sys.executable,str(ROOT/'tools/playthroughs/roster_run.py'),
        '--character','3','--mapper','mmc3','--rom',prep['target_ROM']['rom']['path'],
        '--replay',prep['reference_inputs']['path'],'--policy',str(PACKET/'policy.lua'),
        '--tag','root49n-bill-late-contact-observe-o','--frames','13500','--timeout','240',
        '--workspace-cap-gb','50']
    admission={'status':'PASS_FRESH_ROOT_50GB_POLICY_ADMISSION_BEFORE_NATIVE',
        'script_sha256':sha(Path(__file__)),'policy_sha256':sha(policy),
        'packet_freeze_sha256':sha(PACKET/'freeze.json'),'host_preflight_exit':0,
        'workspace_bytes':used,'cap_bytes':cap,'own_future_reserve_bytes':reserve,
        'other_root_native_CPU_jobs_live':False,'other_future_reserve_bytes':other_active_future,
        'command':command,'old_packet_30GB_guard_unchanged':True,
        'scope':'Full literal Bill N passive replay. Native death is expected, no tactic/runtime change.'}
    (OWN/'admission.json').write_text(json.dumps(admission,indent=2)+'\n')
    with (OWN/'native.log').open('wb')as f:
        native=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    (OWN/'native-exit.json').write_text(json.dumps({'native_exit':native.returncode,'expected_native_exit':1})+'\n')
    assert native.returncode==1,str(OWN/'native.log')
    review=OWN/'review.json'
    with (OWN/'host-check.log').open('wb')as f:
        checked=subprocess.run([sys.executable,str(PACKET/'check.py'),'--out',str(review)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    assert checked.returncode==0,str(OWN/'host-check.log')
    print(json.dumps({'review':str(review),'sha256':sha(review),'status':json.loads(review.read_text())['status']}))


if __name__=='__main__':main()
