"""Freeze metadata-only6c69 menu rebind and source/static readiness, no launch."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SHA='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','source-ready','preparation','static','parent-final','environment-ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(a.source_ready)=='9225b3bafce11ac542d6d10725d7e2ca99757bf586d908ff469af943f045722f'
 sr=json.loads(a.source_ready.read_text());assert sr['passed']and sr['source_CPU_only']and sr['candidate_ROM_sha256']==SHA
 files={a.source_ready.resolve()}
 for f,q in sr['files'].items():assert sha(f)==q['sha256'];files.add(Path(f).resolve())
 for name,h in json.loads((a.candidate/'source-manifest.json').read_text()).items():
  f=a.candidate/'source'/name;assert sha(f)==h;files.add(f.resolve())
 old=json.loads((a.parent_final/'proof.json').read_text());assert old['passed']and old['current_menu_all6native_components_passed']
 files.update((a.parent_final/n).resolve()for n in ['proof.json','manifest.json'])
 z=json.loads((a.preparation/'menu/preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256']and sha(script.with_name('candidate.nes'))==SHA
 assert z['original_controller_all6guards_finalizer_order_exact_after_path_normalization']
 assert not(script.parent/'proof.json').exists()and not(script.parent/'lifecycle-proof.json').exists()
 for f,h in z['dependencies'].items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update(f.resolve()for f in a.preparation.rglob('*')if f.is_file())
 st=json.loads((a.static/'proof.json').read_text());assert st['passed']and not st['native_run']and st['ROM_sha256']==SHA and st['script_sha256']==sha(script)
 files.update(f.resolve()for f in a.static.rglob('*')if f.is_file())
 for helper in ['parodius_visibility_menu4285_static_v1.py','parodius_visibility_hud_static_startup_v1.py','parodius_visibility_hud_cancel_observer_cpu_v1.py','parodius_visibility_menu_hint_observer_cpu_v3.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','check_nmi_vram_fast_cpu_v1.py','final_roll_items_prepare.py']:
  files.add((ROOT/'tools/audit'/helper).resolve())
 env=json.loads((a.environment_ready/'environment.json').read_text());envdir=a.output/'environment';envdir.mkdir()
 for name in ['emulator','core','worker_settings','user_settings']:
  f=Path(env[name]);assert sha(f)==env[name+'_sha256'],'Actual runtime changed; require additive rebinding';files.add(f.resolve())
  if name.endswith('settings'):shutil.copy2(f,envdir/(name+'.json'))
 (a.output/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
 owned=[ROOT/'tools/audit'/n for n in ['parodius_visibility_menu6c69_prepare_v1.py','parodius_visibility_menu6c69_ready_v1.py','parodius_visibility_menu6c69_run_v1.py']]+[ROOT/'docs/qa/parodius-menu6c69-source-2026-10-26.txt']
 files.update(f.resolve()for f in owned);(a.output/'review-files.json').write_text(json.dumps({str(f):sha(f)for f in owned},indent=2)+'\n')
 files.update(f.resolve()for f in a.output.rglob('*')if f.is_file());manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,agent_visual_review=False,goal_complete=False,ROM_sha256=SHA,
        profiles=[dict(kind='menu',limit=1800,actual_mode_required=0,actual_variant_required=1,packet=str((a.preparation/'menu').resolve()),preparation_sha256=sha(a.preparation/'menu/preparation.json'),script_sha256=sha(script))],
        padding_source_ready_sha256=sha(a.source_ready),parent_passed4285_menu_final_sha256=sha(a.parent_final/'proof.json'),static_source_proof_sha256=sha(a.static/'proof.json'),
        original_controller_all6guards_bodyrecords_finalizer_order_exact=True,ROM_delta_3bytes_only=True,public_RAM_label_file_exact=True,
        required_native_components=['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json'],
        environment=env,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(owned[-1]),review_files_sha256=sha(a.output/'review-files.json'),
        stable_command='python -B tools/audit/parodius_visibility_menu6c69_run_v1.py --ready "'+a.output.as_posix()+'" --profile menu --native-grant',
        limits='SOURCE ONLY, exactsame focusedmenu1800 requires explicit newgrant. No sourceoptimization/controller/guard/body/art change, no launch/retry/death/area/Hardmatrix/adoption. OriginalareaFALSE/6missingoutputs/naturalBuffer2limitation and historical4285deadline negative stay separate. No globaltiming/wholegoal claim.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=q['manifest_sha256'],bindings=len(manifest),script_sha256=sha(script),report_sha256=q['report_sha256']),indent=2))


if __name__=='__main__':main()
