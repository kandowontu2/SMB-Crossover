"""Execute one explicitly granted, frozen physical presentation preflight."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--expected-grant-sha256', required=True)
    a = p.parse_args()
    ready, grant = a.packet/'readiness.json', a.packet/'ROOT-grant.json'
    assert sha(grant) == a.expected_grant_sha256
    q, g = [json.loads(f.read_text(encoding='utf-8')) for f in [ready, grant]]
    assert g['native_grant_explicit'] and g['maximum_native_launches'] == 1
    assert g['readiness_sha256'] == sha(ready)
    assert g['launcher_sha256'] == sha(__file__)
    for path, h in {**q['bindings'], **g['qualification_bindings']}.items():
        assert sha(path) == h, path
    query = "@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"
    assert int(subprocess.check_output(['powershell', '-NoProfile', '-Command', query], text=True).strip()) < 2
    with (a.packet/'launch.json').open('x', encoding='utf-8') as f:
        json.dump(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       grant_sha256=sha(grant), readiness_sha256=sha(ready), command=q['command']), f, indent=2)
    with (a.packet/'native-host.log').open('x', encoding='utf-8') as f:
        z = subprocess.run(q['command'], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    result = json.loads((a.packet/'result.json').read_text(encoding='utf-8')) if (a.packet/'result.json').exists() else {}
    for n in ['user_settings', 'worker_settings']:
        assert sha(q['environment'][n]) == q['environment'][n+'_sha256'], n
    receipt = dict(passed=z.returncode == 0 and result.get('passed') is True, exit=z.returncode,
                   result=result, worker_released=True, launches=1, retries=0,
                   ROM_sha256=q['ROM_sha256'], grant_sha256=sha(grant), launcher_sha256=sha(__file__))
    (a.packet/'native-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
