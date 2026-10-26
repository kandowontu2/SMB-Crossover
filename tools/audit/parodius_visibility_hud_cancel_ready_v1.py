"""Freeze private source/CPU candidate and one UNRUN death fixture for review."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SHA='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','preparation','negative-final','environment-ready','output','checkpoint']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert not a.checkpoint.exists();a.checkpoint.mkdir(parents=True)
 base=a.output.parent;folders=['parodius-hud-cancel-cpu-v2','parodius-hud-cancel-interrupt-cpu-v2','parodius-hud-cancel-gateway-cpu-v1','parodius-hud-cancel-lifecycle-cpu-v1','parodius-hud-cancel-extent-cpu-v1','parodius-hud-cancel-observer-cpu-v1','parodius-hud-cancel-lease-cpu-v1']
 files=set();receipts={}
 for name in folders:
  folder=base/name;z=json.loads((folder/'proof.json').read_text());assert z['passed']and not z['native_run']
  bound=z.get('ROM_sha256',z.get('candidate_ROM_sha256'));assert bound==SHA or name.endswith('lease-cpu-v1')
  receipts[name]=dict(path=str(folder/'proof.json'),sha256=sha(folder/'proof.json'),cases=z['cases']if'cases'in z else None)
  files.update(f.resolve()for f in folder.rglob('*')if f.is_file());dest=a.checkpoint/'cpu';dest.mkdir(exist_ok=True);shutil.copy2(folder/'proof.json',dest/(name+'.json'))
 negative=json.loads((a.negative_final/'proof.json').read_text());assert not negative['passed']and negative['worker_released']
 for f,h in json.loads((a.negative_final/'manifest.json').read_text()).items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update(f.resolve()for f in a.negative_final.iterdir()if f.is_file())
 files.update(f.resolve()for f in a.candidate.rglob('*')if f.is_file());files.update(f.resolve()for f in a.preparation.rglob('*')if f.is_file())
 build=json.loads((a.candidate/'proof.json').read_text());assert build['candidate_ROM_sha256']==SHA and build['delta_bytes']==293 and build['CHR_exact']
 for n,h in build['changed_source'].items():
  f=a.candidate/'source'/n;assert sha(f)==h;dest=a.checkpoint/'proposal'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
 shutil.copy2(a.candidate/'sourcepatch.patch',a.checkpoint/'sourcepatch.patch');shutil.copy2(a.candidate/'proof.json',a.checkpoint/'source-build-proof.json')
 prep=a.preparation/'death';z=json.loads((prep/'preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256']and sha(script.with_name('candidate.nes'))==SHA
 assert not(script.parent/'proof.json').exists()and not(script.parent/'lifecycle-proof.json').exists()
 for f,h in z['dependencies'].items():assert sha(f)==h;files.add(Path(f).resolve())
 builds=base/'parodius-hud-cancel-builds-v1';files.update(f.resolve()for f in builds.rglob('*')if f.is_file())
 for mapper in ['mmc3','mmc5']:assert(builds/('parent-'+mapper+'.nes')).read_bytes()==(builds/('candidate-'+mapper+'.nes')).read_bytes()
 for n in ['parodius-hud-cancel-cpu-v1','parodius-hud-cancel-interrupt-cpu-v1']:files.update(f.resolve()for f in(base/n).rglob('*')if f.is_file())
 env=json.loads((a.environment_ready/'environment.json').read_text());envdir=a.output/'environment';envdir.mkdir()
 for n in ['emulator','core','worker_settings','user_settings']:
  f=Path(env[n]);assert sha(f)==env[n+'_sha256'];files.add(f.resolve())
  if n.endswith('settings'):shutil.copy2(f,envdir/(n+'.json'))
 (a.output/'environment.json').write_text(json.dumps(env,indent=2)+'\n');files.update(f.resolve()for f in a.output.rglob('*')if f.is_file())
 names=['parodius_visibility_hud_cancel_candidate_v1.py','parodius_visibility_hud_cancel_cpu_v1.py','parodius_visibility_hud_cancel_cpu_v2.py','parodius_visibility_hud_cancel_interrupt_cpu_v1.py','parodius_visibility_hud_cancel_interrupt_cpu_v2.py','parodius_visibility_hud_cancel_gateway_cpu_v1.py','parodius_visibility_hud_cancel_lifecycle_cpu_v1.py','parodius_visibility_hud_cancel_extent_cpu_v1.py','parodius_visibility_hud_cancel_observer_cpu_v1.py','parodius_visibility_hud_cancel_prepare_v1.py','parodius_visibility_hud_cancel_ready_v1.py','parodius_visibility_hud_cancel_run_v1.py','parodius_visibility_hud_lease_cpu_v1.py','parodius_visibility_hud_lease_native_v1.lua','parodius_visibility_death_native_negative_v1.py','parodius_visibility_death_native_freeze_v1.py','parodius_visibility_death_observer_cpu_v1.py','parodius_visibility_death_observer_prepare_v1.py','parodius_visibility_death_observer_ready_v1.py','parodius_visibility_death_records_cpu_v1.py','parodius_visibility_death_records_cpu_v2.py','parodius_visibility_area_controller_cpu_v1.py','parodius_visibility_hud_static_observer_v2.lua']
 toolfiles=[ROOT/'tools/audit'/n for n in names];files.update(f.resolve()for f in toolfiles)
 toolfiles += [ROOT/'docs/qa'/n for n in ['parodius-death-observer-source-2026-10-26.txt','parodius-death-restart-hud-hold-2026-10-26.txt','parodius-hud-cancellation-source-2026-10-26.txt']]
 report=ROOT/'docs/qa/parodius-hud-cancellation-source-2026-10-26.txt';files.update(f.resolve()for f in toolfiles)
 (a.checkpoint/'review-files.json').write_text(json.dumps({str(f.resolve()):sha(f)for f in toolfiles},indent=2)+'\n')
 (a.checkpoint/'README.txt').write_text('SOURCE ONLY - HELD FOR NATIVE QUALIFICATION\n\nPrivateF35 HUD cancellation/font repair on immutable5354.293ROMbytes, all72281parent addresses/CHR exact. Production remains50b5.\nOriginal5354 death/restart native failure813 is false; actual515/813 glyph corruption and all raw receipts remain external.\nThis checkpoint contains only changed private source, patch, small source/CPU receipts and the bounded ROOT review-file list. No game-source adoption, binaries, captures or settings.\nReadiness external: '+a.output.as_posix()+'\nOne UNRUN numericEasy0/Octopus1 death2200 profile only; no grant/reservation inferred. No area profile.\n',encoding='utf-8')
 local={f.relative_to(a.checkpoint).as_posix():sha(f)for f in a.checkpoint.rglob('*')if f.is_file()};(a.checkpoint/'manifest.json').write_text(json.dumps(local,indent=2)+'\n');files.update(f.resolve()for f in a.checkpoint.rglob('*')if f.is_file())
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,parent_ROM_sha256=build['parent_ROM_sha256'],
        profiles=[dict(kind='death',limit=2200,actual_mode_required=0,actual_variant_required=1,packet=str(prep.resolve()),preparation_sha256=sha(prep/'preparation.json'),script_sha256=sha(script))],
        receipts=receipts,required_native_components=['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json'],
        original_negative_final_sha256=sha(a.negative_final/'proof.json'),delta_bytes=293,all72281parent_addresses_and_CHR_exact=True,
        environment=env,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),checkpoint_manifest_sha256=sha(a.checkpoint/'manifest.json'),
        tool_sha256=sha(Path(__file__)),runner_sha256=sha(ROOT/'tools/audit/parodius_visibility_hud_cancel_run_v1.py'),
        stable_command='python -B tools/audit/parodius_visibility_hud_cancel_run_v1.py --ready "'+a.output.as_posix()+'" --profile death --native-grant',
        limits='SOURCE-ONLY readiness. One unchanged-controller death2200 native fixture requires a fresh explicit grant. No retry/area/native timing/globalDMC/visibility/adoption verdict. Original failed5354 receipts and menu success remain separate. Runtime user8a439 and worker627cd conditions freshly verified without settings mutation.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=q['manifest_sha256'],bindings=len(manifest),script_sha256=sha(script),report_sha256=sha(report),checkpoint_manifest_sha256=q['checkpoint_manifest_sha256']),indent=2))


if __name__=='__main__':main()
