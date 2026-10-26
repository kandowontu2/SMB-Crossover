"""Freeze bounded menu hint proposal/readiness; never launch an emulator."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','source-proof','emulator','user-settings','candidate','cpu','initial-cpu','build-controls','old-profile','negative','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.preparation/'proof.json').read_text());cpu=json.loads((a.source_proof/'proof.json').read_text());assert z['ROM_sha256']==cpu['ROM_sha256']==SHA and cpu['passed'] and not cpu['native_run']
 envdir=a.output/'environment';envdir.mkdir();settings=a.emulator.parent/'settings.json'
 for f,n in [(a.user_settings,'user-settings-current.json'),(settings,'worker-settings-current.json')]:shutil.copy2(f,envdir/n);assert sha(f)==sha(envdir/n)
 cfg=json.loads(settings.read_text(encoding='utf-8-sig'));user=json.loads(a.user_settings.read_text(encoding='utf-8-sig'))
 keys=['Region','DisableSprites','DisableBackground','RemoveSpriteLimit','AdaptiveSpriteLimit','RandomizeMapperPowerOnState','RandomizeCpuPpuAlignment','RamPowerOnState','PpuExtraScanlinesBeforeNmi','PpuExtraScanlinesAfterNmi']
 conditions={k:cfg['Nes'][k]for k in keys};conditions['RunAheadFrames']=cfg['Emulation']['RunAheadFrames']
 assert conditions['RunAheadFrames']==0 and all(conditions[k]==0 for k in ['PpuExtraScanlinesBeforeNmi','PpuExtraScanlinesAfterNmi'])
 assert all(conditions[k]is False for k in ['DisableSprites','DisableBackground','RemoveSpriteLimit','AdaptiveSpriteLimit','RandomizeMapperPowerOnState','RandomizeCpuPpuAlignment'])
 options=['--doNotSaveSettings','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false','--nes.removeSpriteLimit=false']
 environment=dict(emulator=str(a.emulator),emulator_sha256=sha(a.emulator),core=str(a.emulator.parent/'MesenCore.dll'),core_sha256=sha(a.emulator.parent/'MesenCore.dll'),worker_settings=str(settings),worker_settings_sha256=sha(settings),user_settings=str(a.user_settings),user_settings_sha256=sha(a.user_settings),effective_worker_conditions=conditions,deterministic_command_overrides=options,settings_untouched=True,limits='Fresh actual user settings copy and effective portable-worker settings bound independently. User current settings differ from historical snapshots; no old bytes or invented diff claimed. No extra scanlines, runahead0, hardware8sprites/adaptiveoff. RAM Random in persisted worker settings is overridden toAllZeros by the original command.')
 (a.output/'environment.json').write_text(json.dumps(environment,indent=2)+'\n')
 files=set(f.resolve()for f in a.preparation.rglob('*')if f.is_file());files.update(f.resolve()for f in a.source_proof.rglob('*')if f.is_file())
 for profile in z['profiles']:
  q=json.loads((Path(profile['packet'])/'preparation.json').read_text());assert sha(q['script'])==q['script_sha256']
  for f,digest in q['dependencies'].items():assert sha(f)==digest;files.add(Path(f).resolve())
  out=Path(q['script']).parent;config=json.loads((out/'config.json').read_text());assert config['mode']==0 and config['variant']==1
  assert not(out/'proof.json').exists()and not(out/'native-result.json').exists(),'Source-only unrun fixtures'
 for n in ['parodius_visibility_menu_hint_ready_v2.py','parodius_visibility_menu_hint_run_v2.py','parodius_visibility_menu_hint_candidate_v2.py','parodius_visibility_menu_hint_cpu_v2.py','parodius_visibility_menu_initial_hint_cpu_v3.py','parodius_visibility_guarded_build_controls_v1.py','parodius_visibility_menu_hint_observer_cpu_v2.py','parodius_visibility_menu_hint_prepare_v2.py','parodius_visibility_hud_lifecycle_bridge_v3.lua','parodius_visibility_hud_lifecycle_v3.lua','parodius_visibility_hud_static_startup_v1.py','final_roll_items_prepare.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py']:
  files.add((ROOT/'tools/audit'/n).resolve())
 report=ROOT/'docs/qa/parodius-menu-initial-hint-proposal-2026-10-25.txt';files.add(report.resolve())
 assert len(z['profiles'])==1 and z['profiles'][0]['kind']=='menu'
 proposal=json.loads((a.candidate/'proof.json').read_text());component=json.loads((a.cpu/'proof.json').read_text());initial=json.loads((a.initial_cpu/'proof.json').read_text());build=json.loads((a.build_controls/'proof.json').read_text())
 assert proposal['candidate_ROM_sha256']==component['candidate_ROM_sha256']==initial['candidate_ROM_sha256']==build['ROM_sha256']==SHA and component['passed'] and initial['passed'] and build['passed']
 for base in [a.candidate,a.cpu,a.initial_cpu,a.build_controls]:
  files.update(f.resolve()for f in base.iterdir()if f.is_file())
 old=json.loads((a.old_profile/'preparation.json').read_text());new=json.loads((Path(z['profiles'][0]['packet'])/'preparation.json').read_text());oldscript=Path(old['script']);newscript=Path(new['script']);oldroot=a.old_profile.parent.as_posix();newroot=a.preparation.as_posix();oldSHA=proposal['parent_ROM_sha256']
 normalize=lambda text,root:text.replace(root,'FROZEN_PREPARATION').replace(oldSHA,SHA)
 assert normalize(oldscript.read_text(),oldroot)==normalize(newscript.read_text(),newroot),'Original observer/controller tail must be exact after ROM metadata/isolated paths'
 for f in(a.old_profile/'controller').iterdir():
  if f.is_file():assert normalize(f.read_text(),oldroot)==normalize((Path(z['profiles'][0]['packet'])/'controller'/f.name).read_text(),newroot)
 files.update(f.resolve()for f in a.negative.iterdir()if f.is_file())
 equivalence=dict(parent_script_sha256=sha(oldscript),candidate_script_sha256=sha(newscript),same_complete_script_after_ROM_hash_and_path_normalization=True,controller_harness_policy_stream_exact=True,original_static_guard_sha256=sha(ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua'),diagnostic_bridge_sha256=sha(ROOT/'tools/audit/parodius_visibility_hud_lifecycle_bridge_v3.lua'),original_negative_sha256=sha(a.negative/'proof.json'))
 (a.output/'source-equivalence.json').write_text(json.dumps(equivalence,indent=2)+'\n');files.add((a.output/'source-equivalence.json').resolve())
 for f in [a.emulator,a.emulator.parent/'MesenCore.dll',settings,a.user_settings]:files.add(f.resolve())
 files.update(f.resolve()for f in envdir.iterdir());files.add((a.output/'environment.json').resolve())
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,parent_ROM_sha256=oldSHA,profiles=z['profiles'],preparation_sha256=sha(a.preparation/'proof.json'),source_cpu_sha256=sha(a.source_proof/'proof.json'),proposal_sha256=sha(a.candidate/'proof.json'),full_caller_CPU_sha256=sha(a.cpu/'proof.json'),initial_PPU_interrupt_CPU_sha256=sha(a.initial_cpu/'proof.json'),build_controls_sha256=sha(a.build_controls/'proof.json'),environment=environment,source_equivalence=equivalence,manifest_count=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),tool_sha256=sha(Path(__file__)),scope='ONE unrun same-controller menu1800 initial-owner strict proposal.84newbytes vs636f only66; all original init/live/diagnostic guards exact. CPU329PPU/interrupt +257live/fallback +observer14 +canonical/flagoff pass, no native deadline/pixels/lifecycle verdict. Only proven blanked/private initialship owner moves20sourcehinttiles toforeground; live636f Select-only reuse remains. No new grant/launch/death/area/body/adoption.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=q['manifest_sha256'],bindings=len(manifest),profiles=q['profiles']),indent=2))


if __name__=='__main__':main()
