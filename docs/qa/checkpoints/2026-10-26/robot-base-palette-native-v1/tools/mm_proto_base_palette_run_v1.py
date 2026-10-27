"""One exact separately granted six-case base-cache native profile."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json
import subprocess

B=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/robot-base-palette-candidate-v2/ready-v1')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native-grant',action='store_true');a=p.parse_args();assert a.native_grant
    assert sha(B/'ROOT-grant.json')=='da3b20b09e8e83119f1eb68fce4cf5c92710651c52b160730fd0ab515caf1739'
    expected='d48e101f291439971146878107832bab23bdbc1fc534c2138ef9460e5406bb0d'
    assert sha(B/'readiness.json')==expected
    grant=json.loads((B/'ROOT-grant.json').read_text());assert grant['readiness_sha256']==expected
    assert not(B/'launch-binding-v1.json').exists(),'No retries'
    bindings=json.loads((B/'bindings.json').read_text())
    for f,h in bindings.items():assert sha(f)==h,f
    command=json.loads((B/'command.json').read_text())
    put(B/'launch-binding-v1.json',dict(UTC=datetime.now(timezone.utc).isoformat(),explicit_ROOT_grant=True,
        grant_sha256=sha(B/'ROOT-grant.json'),readiness_sha256=expected,checked_bindings=len(bindings),
        command_sha256=sha(B/'command.json'),command=command,maximum_launches=1,attempt=1,no_retry=True,tool_sha256=sha(__file__)))
    with(B/'launch-host-v1.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    summary=B/'native/native-mm-weapon-profile.json';passed=r.returncode==0 and summary.exists()
    if passed:
        z=json.loads(summary.read_text());passed=z['passed']and z['actual_mode_readback']==1 and len(z['cases'])==6
    put(B/'launch-outcome-v1.json',dict(returncode=r.returncode,passed=bool(passed),attempt=1,no_retry=True,
        native_worker_released=True,summary_sha256=sha(summary)if summary.exists()else None))
    print((B/'launch-outcome-v1.json').read_text());return r.returncode


if __name__=='__main__':raise SystemExit(main())
