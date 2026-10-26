"""Freeze one separate UNRUN current4285 all-variant menu smoke for review."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SHA='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['composition-ready','preparation','static','historical-final','area-final','environment-ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(a.composition_ready)=='9609d87ad0545251fd19408baa6994ce09cd788f79f734ae336c1983e80d7749'
 comp=json.loads(a.composition_ready.read_text());files={a.composition_ready.resolve()}
 for f,h in comp['all_frozen_bindings'].items():assert sha(f)==h;files.add(Path(f).resolve())
 old=json.loads((a.historical_final/'proof.json').read_text());assert old['passed']and old['ROM_sha256']=='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
 area=json.loads((a.area_final/'proof.json').read_text());assert not area['passed']and area['original_aggregate_false_and_6missing_files_preserved']
 files.update((d/n).resolve()for d in [a.historical_final,a.area_final]for n in ['proof.json','manifest.json'])
 z=json.loads((a.preparation/'menu/preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256']and sha(script.with_name('candidate.nes'))==SHA
 assert z['all_original_menu_controller_and_guard_tail_exact_after_path_normalization']
 assert not(script.parent/'proof.json').exists()and not(script.parent/'lifecycle-proof.json').exists()
 for f,h in z['dependencies'].items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update(f.resolve()for f in a.preparation.rglob('*')if f.is_file())
 st=json.loads((a.static/'proof.json').read_text());assert st['passed']and not st['native_run']and st['ROM_sha256']==SHA and st['script_sha256']==sha(script)
 files.update(f.resolve()for f in a.static.rglob('*')if f.is_file())
 env=json.loads((a.environment_ready/'environment.json').read_text());envdir=a.output/'environment';envdir.mkdir()
 for name in ['emulator','core','worker_settings','user_settings']:
  f=Path(env[name]);assert sha(f)==env[name+'_sha256'],'Actual runtime changed; require additive rebinding';files.add(f.resolve())
  if name.endswith('settings'):shutil.copy2(f,envdir/(name+'.json'))
 (a.output/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
 owned=[ROOT/'tools/audit'/n for n in ['parodius_visibility_menu4285_prepare_v1.py','parodius_visibility_menu4285_static_v1.py','parodius_visibility_menu4285_ready_v1.py','parodius_visibility_menu4285_run_v1.py']]
 owned += [ROOT/'docs/qa/parodius-menu4285-source-2026-10-26.txt'];files.update(f.resolve()for f in owned)
 (a.output/'review-files.json').write_text(json.dumps({str(f):sha(f)for f in owned},indent=2)+'\n')
 files.update(f.resolve()for f in a.output.rglob('*')if f.is_file());manifest={str(f):sha(f)for f in sorted(files,key=str)}
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,agent_visual_review=False,goal_complete=False,ROM_sha256=SHA,
        profiles=[dict(kind='menu',limit=1800,actual_mode_required=0,actual_variant_required=1,packet=str((a.preparation/'menu').resolve()),preparation_sha256=sha(a.preparation/'menu/preparation.json'),script_sha256=sha(script))],
        composition_ready_sha256=sha(a.composition_ready),static_source_proof_sha256=sha(a.static/'proof.json'),
        historical5354_menu_final_sha256=sha(a.historical_final/'proof.json'),separate_area_false_final_sha256=sha(a.area_final/'proof.json'),
        required_native_components=['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json'],
        environment=env,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(owned[-1]),review_files_sha256=sha(a.output/'review-files.json'),
        stable_command='python -B tools/audit/parodius_visibility_menu4285_run_v1.py --ready "'+a.output.as_posix()+'" --profile menu --native-grant',
        limits='SOURCE ONLY, one separate UNRUN focusedmenu1800 requires explicit newgrant. No area retry/death/Hard/automaticretry/adoption or globalcoverage. OriginalareaFALSE/6missingoutputs/naturalBuffer2limitation remain untouched. Originalmenu5guards/controllers preserved exactly; addedactualpairfinalizer precedesstop.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),bindings=len(manifest),manifest_sha256=q['manifest_sha256'],script_sha256=sha(script),report_sha256=q['report_sha256']),indent=2))


if __name__=='__main__':main()
