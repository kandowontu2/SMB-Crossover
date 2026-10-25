"""Fresh controller-only Bass retry; retains the original enemy-contact failure."""
from pathlib import Path
import hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=D/'current8ff-bass-retry-v1';assert not out.exists();out.mkdir()
    old=D/'current8ff-roster-v1/bass-hard/policy.lua';body=old.read_text()
    first,body=body.split('\n',1);assert first.startswith('dofile(')
    policy=out/'policy.lua';policy.write_text(first+'\nlocal original=(function()\n'+body+'''
end)()
return function(c)
 local b=original(c)
 -- The old route parked at1496 and allowed a live Goomba to walk into
 -- the muzzle. Cross the close-contact spot with a normal held jump.
 if c.world==0 and c.level==0 and c.x>=1472 and c.x<1590 then
  return{right=true,a=true,b=c.poll%24<12}
 end
 return b
end
''')
    rom=D/'mac-native-current529-v1/adoption-v1/candidate.nes'
    driver=D/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
    run=out/'discovery'
    with(out/'discovery-host.log').open('w')as log:
        result=subprocess.run([sys.executable,str(driver),'bass','--rom',str(rom),'--output',str(run),'--mapper','mmc5','--behavior','hard','--frames','18000','--capture','12','--policy',str(policy),'--chr-commit','--timeout','240'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    manifest=json.loads((run/'manifest.json').read_text())
    proof=dict(passed=result.returncode==0 and manifest['result']['cleared'],goal_complete=False,ROM_sha256=sha(rom),
               retained_failed_discovery=str(old.parent),retained_failed_manifest_sha256=sha(old.parent/'manifest.json'),
               controller_only_change=True,original_policy_sha256=sha(old),new_policy_sha256=sha(policy),native=manifest['result'],replay=None,
               scope='Adaptive controller retry across a point-blank Goomba contact. No game/source/physics patch or every-enemy/every-item claim.')
    if proof['passed']:
        with(out/'replay-host.log').open('w')as log:
            replay=subprocess.run([sys.executable,str(ROOT/'tools/audit/capture_direct_replay_ot.py'),'--rom',str(rom),'--route',str(run),'--output',str(out/'direct')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        q=json.loads((out/'direct/proof.json').read_text());proof['replay']=dict(passed=replay.returncode==0 and q['passed'],proof_sha256=sha(out/'direct/proof.json'),physical_frames=q['direct_frames'])
        proof['passed']&=proof['replay']['passed']
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
    return 0 if proof['passed']else 1


if __name__=='__main__':raise SystemExit(main())
