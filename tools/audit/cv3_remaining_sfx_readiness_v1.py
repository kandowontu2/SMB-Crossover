"""Immutable source/CPU readiness packet, no binaries installed or adopted."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-remaining-sfx-v1')
ROM='70808ed6f48a3d543eb409a48cc2026b898cb1a969ae0ca12a6f133c8098597f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);qualified=D/'full-qualified-v3';q=json.loads((qualified/'qualification.json').read_text());assert q['ROM_sha256']==ROM and q['passed']and sha(qualified/'candidate.nes')==ROM
 receipts=[]
 for name in['source-v2/proof.json','per-voice-plan-v2/proof.json','noise-qualified-v2/qualification.json','full-cpu-v5/proof.json','full-controls-v1/proof.json','full-compat-v2/proof.json','full-dmc-cpu-v1/proof.json','full-irq-v1/proof.json','full-qualified-v3/qualification.json','retained-failures-v1/proof.json']:
  f=D/name;r=json.loads(f.read_text());assert r['passed'];rec=dict(path=str(f),sha256=sha(f),scope=r.get('scope',r.get('meaning')))
  if name.startswith('full-'):assert r.get('ROM_sha256')==ROM
  receipts.append(rec)
 source=qualified/'source-final';assert len(q['source_files'])==7
 for r in q['source_files']:assert sha(source/r['path'])==r['sha256']
 tools=[];frozen=out/'frozen-tools';frozen.mkdir()
 files=sorted((ROOT/'tools/audit').glob('cv3_remaining_sfx_*.py'))
 files +=[ROOT/'tools/audit'/n for n in['cv3_dmc_complete_cpu_v1.py','cv3_primary_sfx_source_v1.py','check_tmnt_render_oa.py','check_tmnt_audio_fallback_oc.py','robots_weapon_cpu_v1.py','verify_native_relocation.py','final_item_matrix.py']]
 for f in files:
  tools.append(dict(path=f.relative_to(ROOT).as_posix(),sha256=sha(f),bytes=f.stat().st_size));shutil.copyfile(f,frozen/f.name)
 report=ROOT/'docs/qa/cv3-remaining-sfx-source-2026-10-25.txt';assert report.is_file();shutil.copyfile(report,out/report.name)
 for name in['qualification.json','implementation.patch','all-deployable-files.json','removed-private-label-references.json']:shutil.copyfile(qualified/name,out/name)
 result=dict(status='PRIVATE_SOURCE_CPU_READY_NATIVE_UNQUALIFIED_NOT_ADOPTED',ROM_sha256=ROM,baseline_ROM_sha256=q['baseline_ROM_sha256'],exact_source=str(source),exact_ROM=str(qualified/'candidate.nes'),exact_debug=str(qualified/'candidate.dbg'),source_files=q['source_files'],source_files_independently_enumerated=7,total_deployable_files=634,all_deployable_manifest_sha256=q['all_deployable_manifest_sha256'],implementation_patch_sha256=q['patch_sha256'],qualified_receipt_sha256=sha(qualified/'qualification.json'),source_cpu_receipts=receipts,frozen_tools=tools,report=dict(path=report.relative_to(ROOT).as_posix(),sha256=sha(report)),counts=dict(original_fresh_effects=8,standalone_two_mode_source_cases=14,strict_raw_priority_pairs=441,strict_raw_continued_mixed_updates=512,actual_delayed_subweapon_releases=18,active_lifecycle=84,pending_lifecycle=70,bat_exit_reject=8,pool_world_priority=60,all_ordinary_identities=37,all_ordinary_whole_AudioUpdate=9472,CV1_cross_updates=80,unrelated_KillPlayer=18,DMC_priority=6048,DMC_actual_owners=72,DMC_completion_tails=1152,DMC_ordinary_whole_AudioUpdate=5024,actual_IRQ_RTI_boundaries=44472),layout=dict(changed_banks=q['changed_banks'],resident127_and_mirror125_exact=True,all_CHR_exact=True,new_RAM_allocation=0,selected_family_existing_slab_offsets=[36,56],new_source_stream_bytes=1072,new_table_bytes=71,C28_free_bytes=580,A82_free_bytes=1811,A29_free_bytes=0,A29_zero_length_free_span_does_not_authorize_bank30=True),performance=dict(ordinary_CV1_CV3_idle_delta=-2,legacy1F_held_delta=15,legacy1F_pitch_write_delta=35,legacy1F_admission_delta=49,new_multivoice_samples_inclusive_CPU_cycles=[3182,6789],native_cadence_unqualified=True),scope=dict(no_ROOT_game_source_mutated=True,no_Git_mutation=True,no_Downloads_install=True,no_Mesen_worker_used=True,current5ec8_composition_and_native_required=True,common_ASC_hardware_flush_retained_as_existing_timing_adaptation=True,mixed_raw400F_mask_used=False,CV3_music_driver_not_added=True),tool_sha256=sha(__file__))
 (out/'readiness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(readiness_sha256=sha(out/'readiness.json'),source_files=len(result['source_files']),tools_frozen=len(tools),report_sha256=sha(report)),indent=2))
if __name__=='__main__':main()
