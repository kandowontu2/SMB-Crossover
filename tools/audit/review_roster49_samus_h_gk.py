"""Root support, actual DMA and physical-event review of the full H Samus clear."""
from pathlib import Path
import collections,csv,datetime,hashlib,json,os,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-fixed-gj'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
rows=lambda p:list(csv.DictReader(Path(p).open(newline='')))
def main():
 out=V/'root49-samus-h-root-review-gk.json';assert not out.exists()
 z=read(J/'result.json');d=R/z['manifest'];d=d.parent;m=read(d/'manifest.json');assert sha(d/'manifest.json')=='e1597fca7dc0b7a266d7af5b4d237113c0415863530c092a8708adf3e0a3b55f'
 assert m['verified_through_2_2']and m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']and m['result']['frames']==32224
 source=R/'build/roster-through-2-2/root49-h-samus-ball-wait-gh-2-v0-mmc3'
 for n in ['inputs.csv','trace.csv','events.csv']:assert(d/n).read_bytes()==(source/n).read_bytes()
 accepted=[json.loads(s)for s in(d/'samus-accepted-native.jsonl').read_text().splitlines()]
 counts=collections.Counter();classified=[]
 for a in accepted:
  if a['event']!='AcceptedJump':continue
  assert a['state']==0 and a['raw']&128 and not a['previousAB']&128 and a['clearance']==128 and a['ball']==0
  solid=lambda t:t>0 and t not in [0x23,0x26,0xc2,0xc3]
  kind=None;owner=None
  if a['yHigh']==1 and a['y']%16==0 and any(solid(t)for t in [a['footL'],a['footR']]):kind='actual_native_terrain_top'
  else:
   for b in a['actors']:
    width=48 if b[8]in [5,6]else 32
    if b[1]and 36<=b[2]<=43 and b[7]==b[0]and b[6]==a['yHigh']==1 and a['y']+32==b[5]and a['x']+13>=b[4]and a['x']+2<b[4]+width:
     kind='actual_native_platform_owner';owner=b;break
   if kind is None:
    for b in a['actors']:
     if b[1]and b[2]==50 and 0<a['spring']<5 and b[6]==a['yHigh']==1 and a['y']+32==b[5]and a['x']+13>=b[4]and a['x']+2<b[4]+16:
      kind='actual_native_compressed_spring';owner=b;break
  assert kind is not None,('Unclassified actual accepted jump',a)
  counts[kind]+=1;classified.append(dict(frame=a['frame'],x=a['x'],y=a['y'],kind=kind,owner=owner,spring=a['spring'],springForce=a['springForce']))
 assert counts=={'actual_native_terrain_top':164,'actual_native_platform_owner':5,'actual_native_compressed_spring':1}
 spring=next(v for v in classified if v['kind']=='actual_native_compressed_spring');assert spring['frame']==26022 and spring['y']==152 and spring['owner'][5]==184 and spring['spring']==2
 trace=rows(d/'trace.csv');tail=trace[-25:];assert tail[0]['frame']=='32200'and tail[0]['x']=='40'and tail[-1]['x']=='70'and all((a['world'],a['level'],a['mode'],a['task'],a['engine'])==('1','2','1','3','8')for a in tail)
 raw=(d/'actual-2-3-ram.bin').read_bytes();assert len(raw)==10240
 sys.path.insert(0,str(R/'tools/audit'));from review_roster49_h_transfers_dl import hardware
 hw=hardware(d,32224)
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_review import review
 from roster_run import workspace_bytes
 flags=review(d)
 catalogue=J/'root-catalog-gk.json';assert not catalogue.exists();catalogue.write_text(json.dumps({str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()},indent=2)+'\n',encoding='utf-8')
 receipt=dict(status='PASS_ROOT_ACTUAL_H_SAMUS_COMPLETE_CONTROLLER_SUPPORT_DMA_WITH_PHYSICAL_FINDINGS_RETAINED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),manifest=str((d/'manifest.json').relative_to(R)),manifest_sha256=sha(d/'manifest.json'),identity=2,variant=0,mapper='mmc3',execution_revision='H',result=m['result'],hardware=hw,support=dict(counts=counts,classified=classified,unknown=[]),actual_2_3_endpoint_sha256=sha(d/'actual-2-3-ram.bin'),native_events=z['native_events'],hardware_event_review=flags,raw_catalogue_sha256=sha(catalogue),scope='Full independent whole ordinary H replay; actual170 accepted source jump inputs have current terrain/native actor support. Intrinsic Easy Morph is observed with its real5NESpx entry/exit displacement, not an assumed Hard crouch. NativeSpring indexed hook had0 calls; compressed-spring freshA support at26022 is the actual actor top184 and phase2, not a claim about that uncalled indexed routine. No final movie/source-SFX/full-equipment/mode/MMC5 claim.',goal_complete=False)
 out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 old=V/'root49-goal-coverage-gd.json';j=read(old);row=next(q for q in j['roster']if(q['character'],q['variant'])==(2,0));assert not row['current_H_independently_admitted_base_routes']
 row['current_H_independently_admitted_base_routes']=[dict(identity=2,variant=0,manifest=receipt['manifest'],manifest_sha256=receipt['manifest_sha256'],result=receipt['result'],hardware=hw,root_review_sha256=sha(out),physical_findings_in_root_review=True)]
 row['pinned_full_clear_candidates'].append(dict(revision='H',mapper='mmc3',manifest=receipt['manifest'],sha256=receipt['manifest_sha256'],frames=32224,recorded=False))
 j.update(prior_index_sha256=sha(old),current_H_actual_MMC3_admitted_identity_count=12,current_H_actual_native_mapper_pairs=12,latest_Samus_root_review_sha256=sha(out),goal_complete=False)
 assert sum(bool(q['current_H_independently_admitted_base_routes'])for q in j['roster'])==12
 j['completion_scope']='Twelve independently admitted actual H Easy/MMC3 base identities, full limitations and physical findings retained. G Simon independent full replay frozen, H/source-support transfer not yet admitted. Ryu currentG discovery still active. Four retained H base movies. All14/full arsenal/intrinsic/acquisition/mode/source/lag/final media requirements remain active. Private I/Arm/Rush/HUD candidates not installed.'
 index=V/'root49-goal-coverage-gk.json';assert not index.exists();index.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
 qa=R/'docs/qa/easy-hard-legacy-v49.md';before=sha(qa);assert before=='3b9965901bfd421a7e43795cc86ba7e7159c513b0714770928843467d46ba6f7'
 backup=V/'root49-QA-before-gk.md';assert not backup.exists();backup.write_bytes(qa.read_bytes())
 extra=f'\r\n\r\nRoot GK admits actual H Samus independent32224/32223/all6/zero deaths,\r\n25 responsive2-3 controls X40 to70. Whole input/trace/events repeat discovery\r\nliterally. All170 actual source accepted jumps classify164 terrain/five\r\nnative platform owners/one compressed spring26022, actor top184/phase2.\r\nThe indexedSpring hook had zero calls and is not claimed as exercised.\r\nIntrinsic Easy Morph and its5NESpx displacement are observed; the prior GF\r\nstanding-only host assertion and GG B-bomb-lift bound remain observer/control\r\nnegatives. GH used a clearly scoped tail observer; GJ observes the full replay.\r\nActual DMA decoded independently: {hw["actual_DMA"]}. Twelve H base identities\r\nare admitted; all physical findings and equipment/source/movie limits remain.\r\nRoot GE independently reexecutes all180 frozen Arm native fullcaller pairs\r\nand rehashes470 source files/16 artifacts/451 raw receipts. Arm/I remain\r\nprivate; Rush source and confirmed HUD queue overflow repairs are in progress.\r\n'
 temp=qa.with_name(qa.name+'.gk.tmp');assert not temp.exists();temp.write_bytes(qa.read_bytes()+extra.encode('utf-8'));os.replace(temp,qa)
 used=workspace_bytes(R);assert used<80000000000
 progress=V/'root-current49-progress-gk.json';assert not progress.exists();progress.write_text(json.dumps(dict(status='PROGRESS_TWELVE_H_BASE_IDENTITIES_ARM_ROOT_VERIFIED_RUSH_HUD_REPAIRS_ACTIVE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_handoff_sha256=sha(V/'root-current49-progress-gd.json'),root_Samus_review_sha256=sha(out),coverage_index_sha256=sha(index),QA_sha256=sha(qa),working_revision='H',actual_H_base_identities=12,actual_H_DMA_total=219009+hw['actual_DMA'],private_I_installed=False,private_Arm_installed=False,private_Arm_root_review_sha256=sha(V/'root49-arm-root-review-ge/review.json'),frozen_G_Simon='simon-az-proof freeze1cdde2d88edd63643da8f8b3926a826fb0dc5d733239a779721d021fbc6b65b1; independent root/source-support/H transfer remains pending.',specialists=dict(mario_luigi_scrooge_s2='Confirmed offset100>84 HUD queue capacity, repeatedcoin/score. Private bank11 coalescer + no-room handling being designed, GI220MB/50MBreserve. Prior435-file Pit/Rygar immutable.',samus_contra_s2='Rush sourceC fourbuilds/layout; E native source/caller batch98181 lastreported live. GA inclusive1.5GB; private250MB/100MBreserve. New8B GUEST+250SPECIAL_ROSTER; Arm87 leaves79M3 free. MM6NSF37 Land bounce SFX source gap retained.',link_simon_ryu='SimonAZ complete frozenG, RyuAG high/lowfish native discovery lastreported live27919; GB2.2GB/100MBreserve. No main edits.'),root_native_handles=[],root_closed_this_turn={'61563':0,'27804':0,'44506':0,'73443':0,'15215':0,'39522':0,'88429':0,'5154':0,'77387':0,'46060':0,'80090':0},remaining=['Current build Simon/Ryu proofs with actual accepted source support.','Finish and root-review Rush and HUD overflow fixes; compose with reviewed audio/Water/Arm, validate/adopt without retagging old routes.','Complete every intrinsic/special/alternate/upgrade/source/acquisition/ammo/icon/SFX/lifecycle/mode requirement, original1-1 variants/everyenemy/item.','Thorough populated-level lag reduction and final real audio/video all14 identities; retain lossless and all failures.'],workspace_bytes=used,workspace_cap=80000000000,all_lossless_and_negatives_retained=True,goal_status='active',current_turn_classification='progress',blocked=False,accepted_release=False,goal_complete=False),indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(root_review_sha256=sha(out),index_sha256=sha(index),progress_sha256=sha(progress),QA_sha256=sha(qa),hardware=hw,workspace_bytes=used)))
if __name__=='__main__':main()
