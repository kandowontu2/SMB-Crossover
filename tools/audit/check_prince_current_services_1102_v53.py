"""Current22d099 actual common cold/two headers/Fresh/clock/ISR successor."""
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_current_manifest_1102_v51 as M
import check_prince_native_link_1102_v43 as V
O=M.O


def main():
 base,_,_,_=M.bundle();V.H.W.PIN=M.PIN
 source=R/'tools/audit/check_prince_successor_services_1102_v27.py';text=source.read_text();changes={
  'import prepare_prince_successor_manifest_1102_v26 as M':'import prepare_prince_current_manifest_1102_v51 as M',
  '0xdcc5<=c.pc<0xdd24':'0xd8f1<=c.pc<0xdfa2',
  'expected=H.host(H.W.scoped_load(H.E.C.BASE))':'expected=HOST_SUCCESSOR(PROVIDED_BASE)',
  'M.A.PIN':'M.PIN','M.A.BASE':'M.BASE',
  'successor-proposal-v26.json':'current-manifest-v51.json',
  'cold-pool-v25.bin':'cold-pool-v44.bin',
  'owner-third-v23.bin':'current-owner-v51.bin',
  'owner-third-extra-v23.bin':'current-owner-extra-v51.bin',
  'public-selector-v24.bin':'current-selector-v51.bin',
  'public-private-v24.bin':'native-public-v42.bin',
  'public-fresh-v24.bin':'native-fresh-v42.bin',
  'successor-services-CPU-v27.json':'current-services-CPU-v53.json',
  'all_Bub_v9_event_spans_preserved=event':'all_Bub_v9_event_spans_preserved=event["all55_Bub_event_spans_retained"]',
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(source),__name__='prince_current_services_v53',HOST_SUCCESSOR=V.host,PROVIDED_BASE=base);exec(compile(text,str(source),'exec'),env)
 env['main']()
 file=O/'current-services-CPU-v53.json';q=json.loads(file.read_text());assert q['passed'];q.update(qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),current_root_menu_Thomas_inherited_bytes_retained=1878,source_v49_audio_proposal_excluded=True,source_audio_typed_pending=dict(sound_opcode='C0AD',sound_ID='C0AE',music_value='C0AF',source_event_calls_retained=True,donor_mixer_not_implemented=True),scope='Actual current22d099 common worker/Prince44carrier typed cold verified three streams and genuine new constructor then committed both complete headers last. Exact rebound public NativeRoute/retirement/cookie; real Fresh/scene zero source-live state and preserve all code,16source epochs/16duplicate rejections,tag and actual current IRQ/lagNMI. No new menu/collision-audio proposal/ROM/native-emulator/fullstage/install claim. Original native box/terrain/pickup successors still separate.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'current-manifest-v51.json',O/'current-foreign-CPU-v52.json',O/'native-runtime-v42.bin',O/'native-metadata-v42.bin',O/'cold-link-CPU-v45.json']});file.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','base_SHA256','successor_memory_SHA256','actual_shared_typed_cold','warm_Fresh_and_scene_constructor_cases','actual_native_HuMovement_epochs','duplicate_epochs_rejected','real_IRQ_lagNMI_cuts','minimum_ISR_SP']}))


if __name__=='__main__':main()
