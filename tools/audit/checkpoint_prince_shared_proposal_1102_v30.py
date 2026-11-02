"""Compact review checkpoint of qualified private shared/runtime proposal."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/prince-actor-1101-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 receipts=[O/name for name in ['shared-frame-CPU-v22.json','shared-frame-consumers-v22.json','cold-successor-v25.json','successor-services-CPU-v27.json','successor-foreign-CPU-v28.json']]
 for p in receipts:
  q=json.loads(p.read_text());assert q['passed']
  for rel,digest in q.get('bindings',{}).items():assert sha(R/rel)==digest,('Stale proof',p.name,rel)
 frozen=json.loads((O/'native-binding-source-v3-manifest.json').read_text());archive=O/'native-binding-source-v3.zip';assert sha(archive)==frozen['SHA256']
 with zipfile.ZipFile(archive)as z:
  original_sources=frozen['explicit_commit_files']
  for rel in original_sources:assert (R/rel).read_bytes()==z.read(rel),('Frozen36 source changed',rel)
 names=['measure_prince_dispatch_funding_1102_v21.py','measure_prince_shared_frame_1102_v22.py','check_prince_shared_frame_1102_v22.py','check_prince_frame_consumers_1102_v22.py','record_prince_frame_failure_1102_v22.py','measure_prince_owner_routes_1102_v23.py','prepare_prince_public_routes_1102_v24.py','prepare_prince_cold_successor_1102_v25.py','prepare_prince_successor_manifest_1102_v26.py','check_prince_successor_services_1102_v27.py','check_prince_successor_foreign_1102_v28.py','audit_prince_palette_health_1102_v29.py','checkpoint_prince_shared_proposal_1102_v30.py']
 sources=[R/'tools/audit'/n for n in names]+[R/'docs/qa/prince-shared-proposal-1102-v30.md']
 generated=[O/n for n in ['dispatch-factor-measurement-v21.json','dispatch-factor-v21.s','shared-frame-v22.s','shared-frame-v22.cfg','shared-frame-v22.bin','shared-selector-v22.bin','shared-foreign-v22.bin','shared-frame-v22.lbl','shared-frame-measurement-v22.json','frame-negative-v22.json','owner-third-v23.s','owner-third-v23.cfg','owner-third-v23.bin','owner-third-extra-v23.bin','owner-third-v23.lbl','owner-routes-measurement-v23.json','public-private-v24.s','public-private-v24.cfg','public-private-v24.bin','public-fresh-v24.bin','public-private-v24.lbl','public-selector-v24.s','public-selector-v24.cfg','public-selector-v24.bin','public-selector-v24.lbl','public-router-v24.s','public-router-v24.cfg','public-router-v24.bin','public-router-tail-v24.bin','public-scene-v24.s','public-scene-v24.cfg','public-scene-v24.bin','public-foreign-v24.bin','public-routes-measurement-v24.json','native-storage-v25.json','cold-worker-v25.s','cold-worker-v25.cfg','cold-worker-v25.bin','cold-worker-v25.lbl','cold-decoder-v25.s','cold-decoder-v25.cfg','cold-decoder-v25.bin','cold-decoder-v25.lbl','cold-worker-layout-v25.json','successor-proposal-v26.json','palette-health-authority-v29.json']]
 packet=O/'shared-proposal-source-v30.zip';members=sorted(set(sources+generated+receipts))
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,9)as z:
  for p in members:
   if p.name=='successor-proposal-v26.json':
    # Keep the complete preimage manifest live for review. The compact source
    # checkpoint retains its exact digest and every carrier span/hash, without
    # embedding old/new CHR art as hexadecimal payloads inside JSON.
    layout=json.loads(p.read_text());layout['full_manifest_SHA256']=sha(p);layout['carrier_hex_omitted_from_source_checkpoint']=True
    for row in layout['patches']:
     if 'physical_CHR'in row:row.pop('old_hex');row.pop('new_hex')
    z.writestr('receipts/successor-layout-v26.json',json.dumps(layout,indent=2)+'\n')
   else:z.write(p,p.relative_to(R).as_posix())
 manifest=json.loads((O/'successor-proposal-v26.json').read_text());taskfiles=[p for p in O.rglob('*')if p.is_file()]
 q=dict(passed=True,status='PRIVATE_CPU_QUALIFIED_SHARED_PROPOSAL_NO_GRANT',ROM_written=False,shared_sources_written=False,installed=False,base_SHA256=manifest['base_SHA256'],expected_memory_successor_SHA256=manifest['expected_memory_only_successor_SHA256'],source_checkpoint=packet.relative_to(R).as_posix(),source_checkpoint_SHA256=sha(packet),source_checkpoint_bytes=packet.stat().st_size,checkpoint_members=len(members),explicit_source_commit_files=[p.relative_to(R).as_posix()for p in sources],all36_previous_frozen_sources_and_archive_unchanged=True,all_bound_receipts_current=True,active_output=O.relative_to(R).as_posix(),active_output_bytes=sum(p.stat().st_size for p in taskfiles),active_output_files=len(taskfiles),physical_pool=dict(pages=43,used=44029,capacity=44032,spare=3),shared_resident=dict(source_factor141=141,manager_extra=92,public_selector_growth=21,remaining=28),new_predicate_domains=dict(selector_raw37_38_39_only=True,public_native_roster_raw0_39=True,tag_C09E='Existing Source SavedY, source world STY before LDY and456 real ISR cuts; old geometry grant remains mandatory.',warm_packet='C200..C235 source-dead original OAM retained by warm reset; cold code still zeroed before live.'),qualified=['6000 fixed public transport cases and964 real ISR cuts; earlier53B receipt rejected and retained.','5850 exact613b foreign rows/AXYP/fullSMC/native/private/maps,128 bad header bytes,768 actual raw256×3cookie cases.','Actual common worker/typed3stream cold/Ctor/two full header publication,7278020CPU/28650PPUreads.','Fresh/scene4cases,16original phase epochs+16duplicate rejection,25SavedY write/read pairs,456 real source public ISR cuts.'],remaining=['Root shared/source-tag review and formal grants before any ROM composition or menu admission.','Bind original palette/native collision profile/health/hurt/combat to concrete original predicates.','Native menu/scene/death/control/camera/original ability first-pipe tests under sole root Mesen queue.','Full1-1 source route or native platform helpers only after real original-ability crossing failure.'],source_policy_progress='Natural original palette1 hues27/16/20 captured;6DC is background flash countdown. Original hit reaction/armed admission still being recovered; no cooldown invented.',helpers='None placed or claimed.',scope='Compact source/readers/CPU proposal, no ROM/DBG/assets/captures in checkpoint. Every cumulative613b and55B Bubv9 event change is retained. Latest installedf5c remains independent and unchanged.')
 q['scope']='Compact source/readers/CPU proposal, no ROM/DBG/assets/captures in checkpoint. Every cumulative613b and55B Bubv9 event change is retained. Installed613b is the parent-delivered baseline; this Prince successor remains private and unwritten.'
 (O/'shared-proposal-qualified-v30.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
