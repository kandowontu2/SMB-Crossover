"""One frozen two-identity discovery/replay cohort; no retries."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,datetime
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
p=json.loads((r/'readiness.json').read_text());g=json.loads((r/'ROOT-grant.json').read_text())
assert g['readiness_sha256']==sha(r/'readiness.json') and g['maximum_native_launches']==4
assert p['selected_cases']==['megaman:easy','proto:easy'] and p['maximum_owned_workers']==1 and p['no_retry']
assert not(r/'launch-binding.json').exists()
bindings=json.loads((r/'bindings.json').read_text())
for name,h in bindings.items():assert sha(name)==h,name
assert shutil.disk_usage(r).free>=p['minimum_free_bytes']
live=int(subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"],text=True).strip())
assert live<2,'Global two-native-worker cap'
cmd=json.loads((r/'command.json').read_text())
assert sha(r/'command.json')==p['command_sha256']
(r/'launch-binding.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ready_sha256=sha(r/'readiness.json'),grant_sha256=sha(r/'ROOT-grant.json'),bindings_verified=len(bindings),command=cmd,maximum_native_launches=4,maximum_owned_workers=1,maximum_global_workers=2,no_retry=True),indent=2)+'\n')
with(r/'host.log').open('x')as log:z=subprocess.run(cmd,cwd=p['workspace'],stdout=log,stderr=subprocess.STDOUT)
unchanged=[]
for name,h in bindings.items():
 if sha(name)!=h:unchanged.append(name)
f=r/'native/proof.json';native=json.loads(f.read_text())if f.exists()else{}
rows=native.get('runs',[])
passed=bool(z.returncode==0 and not unchanged and native.get('passed') and len(rows)==2 and[(q['identity'],q['mode'])for q in rows]==[('megaman','easy'),('proto','easy')]and all(q['passed']and q['replay']['passed']for q in rows))
proof=dict(passed=passed,ROM_sha256=p['ROM_sha256'],coordinator_exit=z.returncode,dependencies_unchanged=not unchanged,changed_inputs=unchanged,coordinator_proof_sha256=sha(f)if f.exists()else None,completed_identity_results=len(rows),maximum_native_launches=4,no_retry=True,worker_released=True,scope='Two controller-only1-1 discoveries and independent direct replays on exactce635. Not the remaining35 roster identities, every powerup, waveform or release qualification.')
(r/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof));raise SystemExit(0 if passed else 1)
