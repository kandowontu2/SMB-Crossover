"""Execute one separately granted metadata-only diagnostic, with no retries."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json
import subprocess

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',type=Path,required=True)
    p.add_argument('--expected-grant-sha256',required=True)
    p.add_argument('--native-grant',action='store_true');a=p.parse_args();assert a.native_grant
    b=a.packet.resolve();g=b/'ROOT-grant.json'
    assert sha(g)==a.expected_grant_sha256
    grant=json.loads(g.read_text());ready=json.loads((b/'readiness.json').read_text())
    assert grant['readiness_sha256']==sha(b/'readiness.json')
    assert ready['maximum_native_launches']==ready['maximum_workers']==1 and ready['no_retry']
    assert not(b/'launch-binding-v1.json').exists(),'No retries'
    bindings=json.loads((b/'bindings.json').read_text())
    for f,h in bindings.items():assert sha(f)==h,f
    command=json.loads((b/'command.json').read_text())
    assert sha(b/'command.json')==ready['command_sha256']
    put(b/'launch-binding-v1.json',dict(UTC=datetime.now(timezone.utc).isoformat(),explicit_ROOT_grant=True,
        grant_sha256=sha(g),readiness_sha256=sha(b/'readiness.json'),checked_bindings=len(bindings),
        attempt=1,no_retry=True,command=command,command_sha256=sha(b/'command.json'),tool_sha256=sha(__file__)))
    with(b/'launch-host-v1.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    fail=b/'native/first-failure.json'
    put(b/'launch-outcome-v1.json',dict(returncode=r.returncode,attempt=1,no_retry=True,
        diagnostic_only=True,native_worker_released=True,first_failure_sha256=sha(fail)if fail.exists()else None,
        strict_profile_pass=r.returncode==0))
    print((b/'launch-outcome-v1.json').read_text());return r.returncode


if __name__=='__main__':raise SystemExit(main())
