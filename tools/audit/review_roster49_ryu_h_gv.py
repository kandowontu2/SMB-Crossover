"""Root admission of actual H Ryu route and physical/source admission evidence."""
from pathlib import Path
import collections,csv,datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-ryu-g-review-h-transfer-gs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 out=V/'root49-ryu-h-root-review-gv.json';assert not out.exists()
 z=read(J/'result.json');assert z['status']=='PASS_ACTUAL_H_RYU_FULL_FIXED_NATIVE_SUPPORT_REVIEW_PENDING'
 d=(R/z['manifest']).parent;m=read(d/'manifest.json');assert sha(d/'manifest.json')=='e875416d25c40b67d58e00453416222e82a49934093b17ebd4b228c3e435a8e9'
 assert m['verified_through_2_2']and m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']and m['result']['frames']==23098 and m['result']['deaths']==0
 assert len(z['streams_literal'])==11 and all(z['streams_literal'].values())and z['endpoint_raw_literal']
 support=V/'root49-ryu-h-support-gu.json';assert sha(support)=='f8dc07f745921d8b01ab6752934c2f470db7c9271402087b8ceae718b433e85c';s=read(support)
 assert s['counts']=={'actual_native_terrain_top':113,'actual_source_cached_terrain_wall_jump':42,'actual_native_platform_owner':4,'actual_source_down_A_wall_drop':2,'actual_legacy_wall_fallback_jump':4,'actual_native_compressed_spring':1}and not s['unknown']
 assert len(s['rejected_fresh_inputs'])==1 and s['rejected_fresh_inputs'][0]['state']==2 and s['rejected_fresh_inputs'][0]['wall']==0
 events=[json.loads(t)for t in(d/'ryu-accepted-native.jsonl').read_text().splitlines()];counts=collections.Counter(q['event']for q in events)
 assert counts['FreshInput']==167 and counts['AcceptedLaunch']==164 and counts['GroundLaunch']==118 and counts['WallAttempt']==48 and counts['WallDrop']==2 and counts['SpringEntry']==1
 sys.path.insert(0,str(R/'tools/audit'));from review_roster49_h_transfers_dl import hardware
 hw=hardware(d,23098);assert hw['actual_DMA']==19916
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_review import review
 flags=review(d)
 trace=list(csv.DictReader((d/'trace.csv').open(newline='')));tail=trace[-25:]
 assert tail[0]['frame']=='23074'and tail[0]['x']=='40'and tail[-1]['x']=='77'and all((q['world'],q['level'],q['mode'],q['task'],q['engine'])==('1','2','1','3','8')for q in tail)
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';c=read(cp)
 assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==a['sha256']
 catalogue=J/'root-catalog-gv.json';assert not catalogue.exists()
 catalogue.write_text(json.dumps({str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()},indent=2)+'\n',encoding='utf-8')
 receipt=dict(status='PASS_ROOT_ACTUAL_H_RYU_FULL_CONTROLLER_NATIVE_ADMISSIONS_AND_DMA_WITH_SOURCE_LIMITS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),manifest=z['manifest'],manifest_sha256=sha(d/'manifest.json'),identity=10,variant=0,mapper='mmc3',execution_revision='H',result=m['result'],hardware=hw,source_support_sha256=sha(support),source_counts=s['counts'],rejected_fresh_inputs=s['rejected_fresh_inputs'],source_event_counts=dict(counts),hardware_event_review=flags,catalogue_sha256=sha(catalogue),whole_11_G_H_streams_and_endpoint_RAM_literal=True,source_458_generated11_primary8_main_rehashed=True,limits=s['limits']+['Four legacy wall-fallback admissions are retained as an explicit source geometry gap. They do not invalidate the actual controller clear, and do not establish2.02 source perfection.','All original G frozen-packet qualifications retained. No final movie, full equipment/acquisition/modes/1-1 variants/waveform proof. Every event candidate remains in the physical review.'],goal_complete=False)
 out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 old=V/'root49-goal-coverage-gp.json';j=read(old);row=next(q for q in j['roster']if(q['character'],q['variant'])==(10,0));assert not row['current_H_independently_admitted_base_routes']
 row['current_H_independently_admitted_base_routes']=[dict(identity=10,variant=0,manifest=receipt['manifest'],manifest_sha256=receipt['manifest_sha256'],result=receipt['result'],hardware=hw,root_review_sha256=sha(out),source_support_sha256=sha(support))]
 row['pinned_full_clear_candidates'].append(dict(revision='H',mapper='mmc3',manifest=receipt['manifest'],sha256=receipt['manifest_sha256'],frames=23098,recorded=False))
 row['current_G_independently_admitted_base_route_mappers']=['mmc3']
 j.update(prior_index_sha256=sha(old),current_H_actual_MMC3_admitted_identity_count=14,current_H_actual_native_mapper_pairs=14,current_G_root_admitted_identity_count=8,current_G_root_admitted_identity_mapper_pairs=10,latest_Ryu_root_review_sha256=sha(out),goal_complete=False)
 assert sum(bool(q['current_H_independently_admitted_base_routes'])for q in j['roster'])==14
 j['completion_scope']='All14 identities independently admitted actual H Easy/MMC3 base routes through2-2. This is not the full goal: every66 inventory item, intrinsic/upgraded attacks, power tiers, acquisition, Hard/MMC5, original1-1variants/enemies/items, source geometry/SFX, populated lag and all final recordings remain active. Four retained H base movies only. Private I/Arm/Rush/HUD remain uninstalled.'
 index=V/'root49-goal-coverage-gv.json';assert not index.exists();index.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(review_sha256=sha(out),index_sha256=sha(index),hardware=hw,source_counts=s['counts'],event_review_keys=list(flags))))
if __name__=='__main__':main()
