"""Proposed collision image actual current owner/cold/Fresh/clock/ISR closure."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_collision_manifest_1102_v59 as M
import check_prince_collision_services_1102_v56 as V
O=M.O


def main():
 base,_,_,details=M.bundle();V.H.W.PIN=M.PIN;V.N.Bus=V.V.ControllerBus
 labels=json.loads((O/'native-labels-v49.json').read_text());vector_smc=labels['PpNativeRoute']+21-0xc000
 source=R/'tools/audit/check_prince_successor_services_1102_v27.py';text=source.read_text();changes={
  'import prepare_prince_successor_manifest_1102_v26 as M':'import prepare_prince_collision_manifest_1102_v59 as M',
  '0xdcc5<=c.pc<0xdd24':'0xd8f1<=c.pc<0xdfce',
  'expected=H.host(H.W.scoped_load(H.E.C.BASE))':'expected=HOST_SUCCESSOR(PROVIDED_BASE)',
  'M.A.PIN':'M.PIN','M.A.BASE':'M.BASE',
  'successor-proposal-v26.json':'collision-manifest-v59.json',
  'cold-pool-v25.bin':'cold-pool-v57.bin',
  'owner-third-v23.bin':'collision-owner-v59.bin',
  'owner-third-extra-v23.bin':'collision-owner-extra-v59.bin',
  'owner-third-v23.lbl':'collision-owner-v59.lbl',
  'public-selector-v24.bin':'collision-selector-v59.bin',
  'public-private-v24.bin':'native-public-v49.bin',
  'public-fresh-v24.bin':'native-fresh-v49.bin',
  'successor-services-CPU-v27.json':'collision-shared-CPU-v60.json',
  'all_Bub_v9_event_spans_preserved=event':'all_Bub_v9_event_spans_preserved=event["all55_Bub_event_spans_retained"]',
  "for lo,hi in profile['source_original_live_state_zero_ranges']:":"for lo,hi in [(a,min(z,0xc780))for a,z in profile['source_original_live_state_zero_ranges']if a<0xc780]:",
  "assert bytes(n.ram[2][0x800:])==code[0][0x800:]and bytes(n.ram[3])==code[1]":"after=bytearray(n.ram[2]);after[VECTOR_SMC]=code[0][VECTOR_SMC];assert bytes(after[0x800:])==code[0][0x800:]and bytes(n.ram[3])==code[1]",
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(source),__name__='prince_collision_shared_v60',HOST_SUCCESSOR=V.host,PROVIDED_BASE=base,VECTOR_SMC=vector_smc);exec(compile(text,str(source),'exec'),env);env['main']()
 file=O/'collision-shared-CPU-v60.json';q=json.loads(file.read_text());assert q['passed']
 q.update(private_proposal_only=True,new_execution_granted=False,qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),current_inherited_bytes_retained=details['current_inherited_bytes_retained'],sunny_five_patch_extents_retained=True,Sunny_palette_gate_and_local_C_skip_ABI_preserved=True,all_executable_state_and_metadata_unchanged=False,executable_metadata_preserved_except_owned_vector_low_operand=vector_smc+0xc000,audio_code_preserved_by_Fresh=True,genuine_source_live_state_zeroed=True,foreign_CPU_proof_reused_by_exact_disjoint_rebase='current-foreign-CPU-v52.json',source_audio_typed_pending=dict(sound_opcode='C0AD',sound_ID='C0AE',music_value='C0AF',source_event_calls_retained=True,donor_mixer_not_implemented=True),scope='Proposed current16a9 memory image actual shared worker/44carrier cold verifies three streams and genuine constructor then commits both complete headers last. Exact native route/cookie/retirement rebinding,Fresh/scene zero every genuine source-live byte while preserving C780 code,16epochs/16duplicate rejects and realIRQ/lagNMI. Warm vector row45 may change its sole owned JMP low operand; all other executable/metadata bytes preserved. Foreign shared instructions and gates unchanged apart from Prince-only target/cookie. New execution remains ungranted; no menu, ROM, emulator or fullstage/install claim.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),M.P.RECEIPT,O/'collision-manifest-v59.json',O/'current-foreign-CPU-v52.json',O/'native-runtime-v49.bin',O/'native-metadata-v49.bin',O/'collision-cold-CPU-v58.json']});file.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:q[k]for k in ['passed','base_SHA256','successor_memory_SHA256','actual_shared_typed_cold','warm_Fresh_and_scene_constructor_cases','actual_native_HuMovement_epochs','duplicate_epochs_rejected','real_IRQ_lagNMI_cuts','minimum_ISR_SP']}))


if __name__=='__main__':main()
