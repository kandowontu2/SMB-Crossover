"""Freeze finite4285 natural-area source readiness; no native grant or launch."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SHA='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','composition-ready','preparation','cpu','static','environment-ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(a.candidate/'candidate.nes')==SHA
 comp=json.loads(a.composition_ready.read_text());assert sha(a.composition_ready)=='9609d87ad0545251fd19408baa6994ce09cd788f79f734ae336c1983e80d7749'
 # Composition's actual frozen ledger is independently rehashed here.
 files=set()
 for f,h in comp['all_frozen_bindings'].items():assert sha(f)==h;files.add(Path(f).resolve())
 files.add(a.composition_ready.resolve())
 receipts={}
 for d in [a.cpu,a.static]:
  z=json.loads((d/'proof.json').read_text());assert z['passed']and not z['native_run']and z['ROM_sha256']==SHA
  receipts[d.name]=dict(path=str((d/'proof.json').resolve()),sha256=sha(d/'proof.json'))
  files.update(f.resolve()for f in d.rglob('*')if f.is_file())
 z=json.loads((a.preparation/'area/preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256']and sha(script.with_name('candidate.nes'))==SHA
 assert not(script.parent/'proof.json').exists()and not(script.parent/'lifecycle-proof.json').exists()
 for f,h in z['dependencies'].items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update(f.resolve()for f in a.preparation.rglob('*')if f.is_file())
 base=a.output.parent
 for n in ['parodius-area-controller4285-cpu-v1','parodius-area4285-static-v1']:files.update(f.resolve()for f in(base/n).rglob('*')if f.is_file())
 env=json.loads((a.environment_ready/'environment.json').read_text());envdir=a.output/'environment';envdir.mkdir()
 for name in ['emulator','core','worker_settings','user_settings']:
  f=Path(env[name]);assert sha(f)==env[name+'_sha256'],'Actual runtime changed; require additive rebinding'
  files.add(f.resolve())
  if name.endswith('settings'):shutil.copy2(f,envdir/(name+'.json'))
 (a.output/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
 names=['parodius_visibility_area_controller_v2.lua','parodius_visibility_area_controller_v3.lua',
        'parodius_visibility_hud_transition_v2.lua','parodius_visibility_hud_transition_v3.lua',
        'parodius_visibility_area_controller_cpu_v2.py','parodius_visibility_area_controller_cpu_v3.py',
        'parodius_visibility_hud_lease_native_v2.lua','parodius_visibility_area4285_prepare_v1.py',
        'parodius_visibility_area4285_static_v1.py','parodius_visibility_area4285_static_v2.py',
        'parodius_visibility_area4285_ready_v1.py','parodius_visibility_area4285_run_v1.py']
 owned=[ROOT/'tools/audit'/n for n in names]+[ROOT/'docs/qa/parodius-area-controller-source-2026-10-26.txt']
 files.update(f.resolve()for f in owned);(a.output/'review-files.json').write_text(json.dumps({str(f):sha(f)for f in owned},indent=2)+'\n')
 files.update(f.resolve()for f in a.output.rglob('*')if f.is_file());manifest={str(f):sha(f)for f in sorted(files,key=str)}
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,
        composition_ready_sha256=sha(a.composition_ready),profiles=[dict(kind='area',limit=2600,actual_mode_required=0,actual_variant_required=1,
        packet=str((a.preparation/'area').resolve()),preparation_sha256=sha(a.preparation/'area/preparation.json'),script_sha256=sha(script))],
        receipts=receipts,required_native_components=['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json'],
        environment=env,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),
        report_sha256=sha(owned[-1]),review_files_sha256=sha(a.output/'review-files.json'),tool_sha256=sha(Path(__file__)),
        stable_command='python -B tools/audit/parodius_visibility_area4285_run_v1.py --ready "'+a.output.as_posix()+'" --profile area --native-grant',
        limits='SOURCE ONLY. One natural2600 area/Buffer2 profile is UNRUN and requires fresh explicit native grant. No queue/actor/position/resource/RNG/outcome writes; pendingBuffer2hold remains mandatory, not inferred reachable. Original F35 aggregateFALSE and every earlier failure remain immutable. No retry/body/Hard/DMC/globaltiming/adoption verdict.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=q['manifest_sha256'],bindings=len(manifest),script_sha256=sha(script),report_sha256=q['report_sha256']),indent=2))


if __name__=='__main__':main()
