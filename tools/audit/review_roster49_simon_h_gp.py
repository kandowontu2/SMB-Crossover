"""Root actual H Simon full route/support/DMA admission, preserving all qualifiers."""
from pathlib import Path
import collections,csv,datetime,hashlib,json,os,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-simon-g-review-h-transfer-gn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 out=V/'root49-simon-h-root-review-gp.json';assert not out.exists()
 z=read(J/'result.json');assert z['status']=='PASS_ACTUAL_H_SIMON_FULL_FIXED_NATIVE_SUPPORT_REVIEW_PENDING'
 d=(R/z['manifest']).parent;m=read(d/'manifest.json');assert sha(d/'manifest.json')=='d73ab13d931a878a8cd3fb4ae3502c9e5908f39dee481a00d098312d68a2abdd'
 assert m['verified_through_2_2']and m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']and m['result']['frames']==28793 and m['result']['deaths']==0
 assert len(z['streams_literal'])==11 and all(z['streams_literal'].values())and z['endpoint_raw_literal']
 support=V/'root49-simon-h-support-go.json';assert sha(support)=='dbd4dc76f91cb2c62f39f3030898d27a87f3a9ad4e0a042c0e2fc1ece40ece80';s=read(support)
 assert s['counts']=={'actual_native_terrain_top':146,'actual_source_available_secondary_air_jump':75,'actual_native_platform_owner':5}and not s['unknown']
 events=[json.loads(t)for t in(d/'simon-accepted-native.jsonl').read_text().splitlines()];used={t['input_cycle']for t in s['details']}
 rejected=[t for t in events if t['event']=='FreshInput'and t['cycle']not in used];assert len(rejected)==6 and all(t['state']!=0 and t['airAvailable']==0 for t in rejected)
 spring=[t for t in events if t['event']=='SpringEntry'];assert len(spring)==1
 sys.path.insert(0,str(R/'tools/audit'));from review_roster49_h_transfers_dl import hardware
 hw=hardware(d,28793);assert hw['actual_DMA']==25537
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_review import review
 from roster_run import workspace_bytes
 flags=review(d)
 trace=list(csv.DictReader((d/'trace.csv').open(newline='')));tail=trace[-25:];assert tail[0]['frame']=='28769'and tail[0]['x']=='40'and tail[-1]['x']=='70'and all((q['world'],q['level'],q['mode'],q['task'],q['engine'])==('1','2','1','3','8')for q in tail)
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';c=read(cp)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==a['sha256']
 catalogue=J/'root-catalog-gp.json';assert not catalogue.exists();catalogue.write_text(json.dumps({str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()},indent=2)+'\n',encoding='utf-8')
 receipt=dict(status='PASS_ROOT_ACTUAL_H_SIMON_FULL_CONTROLLER_SOURCE_SUPPORT_AND_DMA',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),manifest=str((d/'manifest.json').relative_to(R)),manifest_sha256=sha(d/'manifest.json'),identity=5,variant=0,mapper='mmc3',execution_revision='H',result=m['result'],hardware=hw,source_support_sha256=sha(support),source_counts=s['counts'],secondary_above_viewport=s['secondary_above_viewport'],six_actual_unavailable_air_rejections=rejected,one_native_spring_entry=spring,hardware_event_review=flags,catalogue_sha256=sha(catalogue),whole_11_G_H_streams_and_endpoint_RAM_literal=True,source_458_generated11_primary8_main_rehashed=True,limits=['Actual H/Easy/MMC3 base route and source jump acceptance/support only. Ground146/platform5 and75 real available-secondary consumes; six unavailable air inputs reject. Above-viewport air jumps are not misclassified as ground launches.','Original source geometry/enemy/animation/SFX adaptations and all frozenG qualifications retained. Single native Spring entry is observed; no unlogged downstream index/cost claim.','No final real movie or complete equipment/acquisition/power tier/Hard/MMC5/waveform/source-perfect claim. Physical/audio candidates remain in full event review.'],goal_complete=False)
 out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 old=V/'root49-goal-coverage-gk.json';j=read(old);row=next(q for q in j['roster']if(q['character'],q['variant'])==(5,0));assert not row['current_H_independently_admitted_base_routes']
 row['current_H_independently_admitted_base_routes']=[dict(identity=5,variant=0,manifest=receipt['manifest'],manifest_sha256=receipt['manifest_sha256'],result=receipt['result'],hardware=hw,root_review_sha256=sha(out),source_support_sha256=sha(support))]
 row['pinned_full_clear_candidates'].append(dict(revision='H',mapper='mmc3',manifest=receipt['manifest'],sha256=receipt['manifest_sha256'],frames=28793,recorded=False));row['current_G_independently_admitted_base_route_mappers']=['mmc3']
 j.update(prior_index_sha256=sha(old),current_H_actual_MMC3_admitted_identity_count=13,current_H_actual_native_mapper_pairs=13,current_G_root_admitted_identity_count=7,current_G_root_admitted_identity_mapper_pairs=9,latest_Simon_root_review_sha256=sha(out),goal_complete=False)
 assert sum(bool(q['current_H_independently_admitted_base_routes'])for q in j['roster'])==13
 j['completion_scope']='Thirteen independently admitted actual H Easy/MMC3 base identities; all original physical/source/equipment limitations retained. G Simon777-file proof independently rehashed and separately executed H with11 streams/endpointRAM literal plus actual source acceptance/support. Ryu remains incomplete. Four retained H base movies. Full14/equipment/source/modes/acquisition/1-1variants/populated-lag/final real media scope remains active; private I/Arm/Rush/HUD not installed.'
 index=V/'root49-goal-coverage-gp.json';assert not index.exists();index.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
 qa=R/'docs/qa/easy-hard-legacy-v49.md';before=sha(qa);assert before=='2ff5e9d9d6177f49f731411ce3a0ede069a07cb1e7f6ad5dd5c6fe0baa2cc962'
 backup=V/'root49-QA-before-gp.md';assert not backup.exists();backup.write_bytes(qa.read_bytes())
 extra='\r\n\r\nRoot GN/GO/GP rehashes frozen777-file G Simon and separately executes actualH\r\n28793/28792/all6/zero deaths/25 responsive2-3 controls X40 to70. All11\r\noriginal streams and full endpoint RAM are literalG/H. New exact native\r\nsource hooks pair226 consumed launches with actual prior fresh inputs:\r\n146 terrain,five liveplatform owners,75 genuine available-secondary consumes.\r\nSix unavailable-air inputs reject; above-viewport secondary jumps remain\r\nsource-valid. One nativeSpring entry is observed, without a downstream-index\r\nclaim. All25,537 actualDMA snapshots independently decode. InstalledH now\r\nhas13 base identities/269,485 actualDMA snapshots; Ryu remains incomplete.\r\nSource geometry, equipment, mode, SFX/waveform and final movie obligations\r\nremain open. Private audio/Water/Arm/Rush/HUD work has not been installed.\r\n'
 temp=qa.with_name(qa.name+'.gp.tmp');assert not temp.exists();temp.write_bytes(qa.read_bytes()+extra.encode('utf-8'));os.replace(temp,qa)
 usedbytes=workspace_bytes(R);assert usedbytes<80000000000
 prior=V/'root-current49-progress-gm.json';p=read(prior);p.update(status='PROGRESS_THIRTEEN_H_BASE_IDENTITIES_RYU_AND_SOURCE_FIXES_ACTIVE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_handoff_sha256=sha(prior),coverage_index_sha256=sha(index),QA_sha256=sha(qa),actual_H_base_identities=13,actual_H_DMA_total=269485,root_Simon_review_sha256=sha(out),source_support_sha256=sha(support),root_native_handles=[],workspace_bytes=usedbytes,frozen_G_Simon='Root GN/GO/GP rehashed and independently executed actual H; all11 original streams and endpoint RAM literal, full actual source support.',goal_complete=False)
 progress=V/'root-current49-progress-gp.json';assert not progress.exists();progress.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(root_review_sha256=sha(out),index_sha256=sha(index),progress_sha256=sha(progress),QA_sha256=sha(qa),hardware=hw,above_viewport_secondary=s['secondary_above_viewport'],workspace_bytes=usedbytes)))
if __name__=='__main__':main()
