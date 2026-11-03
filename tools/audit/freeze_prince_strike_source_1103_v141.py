"""Compact successor source/proofs after immutable115; exclude ROM/captures."""
from pathlib import Path
import json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_cold_1103_v131 as C
O=C.O;sha=lambda p:C.M.M.sha(p.read_bytes())


def main():
 sources=['measure_prince_deferred_strike_1102_v116.py','check_prince_deferred_strike_1102_v117.py','diagnose_prince_deferred_strike_1102_v118.py','audit_prince_native_drop_policy_1102_v119.py','measure_prince_owned_drop_ack_1102_v120.py','check_prince_owned_drop_ack_1102_v121.py','measure_prince_owned_drop_ack_1102_v122.py','check_prince_owned_drop_ack_1102_v123.py','check_prince_strike_lifetime_1102_v125.py','check_prince_strike_lifetime_1102_v126.py','check_prince_strike_nested_irq_1102_v127.py','check_prince_strike_nested_irq_1103_v128.py','prepare_prince_strike_cold_1103_v129.py','prepare_prince_strike_manifest_1103_v130.py','check_prince_strike_cold_1103_v131.py','check_prince_strike_foreign_1103_v132.py','check_prince_strike_respawn_1103_v133.py','check_prince_strike_actual_1103_v134.py','check_prince_strike_lifecycle_isr_1103_v135.py','check_prince_strike_actual_nested_1103_v136.py','prepare_prince_frontend_1103_v137.py','check_prince_strike_native_ingress_1103_v138.py','prepare_prince_first_native_1103_v139.py','prince_first_native_1103_v139.lua','emit_prince_private_1103_v140.py']
 live=[R/'tools/audit'/n for n in sources]+[R/'docs/qa/prince-strike-native-1103-v141.md',Path(__file__)]
 positives=['native-drop-policy-CPU-v119.json','deferred-strike-CPU-v123.json','strike-lifetime-CPU-v126.json','post-return-nested-IRQ-CPU-v128.json','cold-link-storage-v129.json','strike-manifest-v130.json','current-shared-cold-CPU-v131.json','current-foreign-hot-CPU-v132.json','post-return-respawn-CPU-v133.json','actual-strike-CPU-v134.json','current-game-loop-ISR-CPU-v135.json','post-return-nested-IRQ-CPU-v136.json','frontend-proposal-v137.json','current-native-ingress-CPU-v138.json','candidate-v140.json']
 for n in positives:
  q=json.loads((O/n).read_text());assert q['passed'],n;C.M.M.validate(q)
 negatives=['deferred-strike-negative-v117.json','deferred-strike-diagnostic-v118.json','strike-lifetime-negative-v125.json','strike-nested-IRQ-negative-v127.json','strike-shared-cold-negative-v131.json']
 measurements=['deferred-strike-measurement-v116.json','deferred-strike-measurement-v120.json','deferred-strike-measurement-v122.json']
 components=['native-labels-v122.json','native-runtime-v122.bin','native-metadata-v122.bin','native-state-v122.bin','cold-pool-v129.bin','cold-worker-v129.s','cold-worker-v129.cfg','cold-worker-v129.lbl','cold-worker-v129.bin','post-owner-v130.s','post-owner-v130.cfg','post-owner-v130.lbl','post-owner-v130.bin','post-owner-extra-v130.bin','post-selector-v130.s','post-selector-v130.cfg','post-selector-v130.lbl','post-selector-v130.bin']
 components += [f'native-{n}-v122.{suffix}'for n in ['services','battle','proxy','public','policies','audio','small']for suffix in ['s','bin']]
 components += [f'native-{n}-v129.lzdict'for n in ['runtime','metadata','state_code']]
 grants=[R/'docs/qa/allocations/prince-current-frontend-1103-v105.json']
 files=live+grants+[O/n for n in positives+negatives+measurements+components]
 for mode in ['controls','contact-death']:
  files += [O/f'native-first-{mode}-v139'/n for n in ['controller.lua','run.py','ready.json']]
 assert len(files)==len(set(files))and all(p.is_file()for p in files)
 previous=O/'current-source-v115.zip';assert sha(previous)=='50052ec19203fc81506b4e74cf0d594429da8e62850b6b22d008954d73c211d5'
 archive=O/'strike-source-v141.zip';assert not archive.exists(),'Do not overwrite frozen source'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 with zipfile.ZipFile(archive)as z:
  assert len(z.namelist())==len(files)
  for p in files:assert C.M.M.sha(z.read(p.relative_to(R).as_posix()))==sha(p)
 manifest=C.image()[1];frontend=json.loads((O/'frontend-proposal-v137.json').read_text());own=[p for p in O.rglob('*')if p.is_file()]
 q=dict(passed=True,frozen=True,private_native_candidate_only=True,installed=False,native_emulator=False,native_ready_for_root_probe=True,ROM_SHA256=frontend['expected_memory_only_SHA256'],parent_ROM_SHA256=C.M.PIN,component_memory_SHA256=manifest['expected_memory_only_SHA256'],archive=archive.relative_to(R).as_posix(),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,archive_members=len(files),source_files_to_commit=[p.relative_to(R).as_posix()for p in live],members={p.relative_to(R).as_posix():dict(SHA256=sha(p),bytes=p.stat().st_size)for p in files},prior_frozen_dependency=dict(durable_root='docs/qa/checkpoints/2026-11-03/prince-current-v115',archive_SHA256=sha(previous),not_copied_or_expanded=True),active_output=O.relative_to(R).as_posix(),active_output_files=len(own),active_output_bytes=sum(p.stat().st_size for p in own),remaining='Root native menu/hardware/controls/contact/death, naturally earned sword/strike, original movement/ledge crossing and1-1; original audio mapping unfinished. No helper added. No nightly installation by helper.')
 assert q['active_output_files']<1000 and q['active_output_bytes']<256000000
 (O/'strike-checkpoint-v141.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['members','source_files_to_commit']}))


if __name__=='__main__':main()
