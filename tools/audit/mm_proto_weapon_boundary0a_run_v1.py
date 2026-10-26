"""Execute the explicitly granted two frozen profiles once, stopping at failure."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D/'mm-proto-weapon-boundary0a-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-grant', action='store_true')
    a = p.parse_args()
    assert a.native_grant, 'Separate explicit ROOT grant required'
    assert sha(B/'ready-v1/readiness.json') == 'b1532dd21bd9dfd422409dfd6a30574e3c8d2fff1c7576caac9701caf77d263f'
    for name, expected in json.loads((B/'ready-v1/bindings.json').read_text()).items():
        assert sha(name) == expected, name
    result = []
    for folder, expected in [
        ('mega-hard-ready-v2', 'b9dc0b9a94f2aec94a155085e7e1698cfa12f783cde9935352d5749c82fbdfd1'),
        ('proto-hard-ready-v1', '369045f48eed80482b971f1bf155bafd121323c567ac9616007be87c26530469')]:
        root = B/folder
        assert sha(root/'readiness.json') == expected
        assert not (root/'launch-binding-v1.json').exists(), 'No retry'
        command = json.loads((root/'command.json').read_text())
        put(root/'launch-binding-v1.json', dict(UTC=datetime.now(timezone.utc).isoformat(),
            grant='Explicit ROOT collaboration NEW_TASK: Mega once; only if pass Proto once. Maximum2 sequential launches/one worker; stopfirstfailure; no retry.',
            native_grant_explicit=True, maximum_launches_for_profile=1, attempt=1,
            readiness_sha256=expected, command_sha256=sha(root/'command.json'),
            aggregate_readiness_sha256=sha(B/'ready-v1/readiness.json'),
            unchanged_recorded_command=True, command=command, coordinator_sha256=sha(__file__)))
        print('Launching '+folder, flush=True)
        with (root/'launch-host-v1.log').open('w') as log:
            run = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        summary = root/'native/native-mm-weapon-profile.json'
        passed = run.returncode == 0 and summary.exists()
        if passed:
            data = json.loads(summary.read_text())
            passed = data['passed'] and data['actual_mode_readback'] == 1 and len(data['cases']) == 6
        row = dict(profile=folder, returncode=run.returncode, passed=bool(passed),
                   attempt=1, no_retry=True, worker_released=True,
                   summary_sha256=sha(summary) if summary.exists() else None)
        put(root/'launch-outcome-v1.json', row)
        result.append(row)
        print(json.dumps(row), flush=True)
        if not passed:
            break
    proof = dict(passed=len(result) == 2 and all(x['passed'] for x in result),
                 launches=len(result), maximum_workers=1, native_workers_released=True,
                 rows=result, graphics_reviewed=False, no_adoption=True)
    put(B/'native-execution-v1.json', proof)
    return 0 if proof['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
