"""Freeze finite HUD-only lifecycle readiness; never launch an emulator."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SHA='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','source-proof','emulator','user-settings','output']:p.add_argument('--'+n,type=Path,required=True)
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
 for n in ['parodius_visibility_hud_lifecycle_ready_v2.py','parodius_visibility_hud_lifecycle_run_v1.py','parodius_visibility_hud_lifecycle_source_v4.py','parodius_visibility_hud_lifecycle_prepare_v2.py','parodius_visibility_hud_lifecycle_bridge_v2.lua','parodius_visibility_hud_lifecycle_v3.lua','parodius_visibility_hud_static_startup_v1.py','final_roll_items_prepare.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py']:
  files.add((ROOT/'tools/audit'/n).resolve())
 report=ROOT/'docs/qa/parodius-hud-lifecycle-readiness-2026-10-25.txt';files.add(report.resolve())
 for f in [a.emulator,a.emulator.parent/'MesenCore.dll',settings,a.user_settings]:files.add(f.resolve())
 files.update(f.resolve()for f in envdir.iterdir());files.add((a.output/'environment.json').resolve())
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,profiles=z['profiles'],preparation_sha256=sha(a.preparation/'proof.json'),source_cpu_sha256=sha(a.source_proof/'proof.json'),environment=environment,manifest_count=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),tool_sha256=sha(Path(__file__)),scope='HUD-only literal original Parodius body. Three bounded natural-input OctopusEasy lifecycle proposals: menu1800, death1800, area5000. New init observer extends inactive owners; original live engine8 guard file is byte-exact. Fresh/old generation labels, complete256B snapshots and original completed DMA guard retained. Display-off carry is not visible or new-generation proof. All native outcome/reachability/Buffer2 overlap remains unrun; stop on first failure and await review. No production changes or Mesen launch.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=q['manifest_sha256'],bindings=len(manifest),profiles=q['profiles']),indent=2))


if __name__=='__main__':main()
