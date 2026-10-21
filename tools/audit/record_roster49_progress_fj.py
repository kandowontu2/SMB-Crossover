"""Preserve the whole roster/equipment/media goal with actual H and private I evidence."""
from pathlib import Path
import csv,datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def main():
 out=V/'root-current49-progress-fj.json';index=V/'root49-goal-coverage-fj.json';assert not out.exists()and not index.exists()
 prior=V/'root-current49-progress-eb.json';assert sha(prior)=='5c85fe668ef521862bd78df672af46bc19d60e132668ca3d736bb814b288ea2e'
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';c=read(cp);S=Path(c['source_directory'])
 for n,h in c['source_hashes'].items():assert sha(R/n)==sha(S/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==sha(S/'build/generated'/n)==h
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==sha(R/a['frozen_path'])==a['sha256']
 refs={'root49-scrooge-h-root-review-em.json':'550b431525fd3e012007012e6bdbcc287caee99d09121a06a9a5fff9cdc544a1','root49-bass-g-review-h-transfer-fc/review.json':'7675e0f41a9ac31a971154d1b02bb4c2ff9da437dd86e5b99dc44c38d4fe8880','root49-audio-root-review-ff.json':'ef7728b70378f7d56a6361b8b994fdd22d9f8f258710125c9838b64e8b349361','root49-water-cache-root-review-fe.json':'8d2d339ad9c11b14e1d056daa3e918da9ffb622ab262312c4bf1e58573b06c18','root49-water-cache-root-review-fe-addendum.json':'60552502d9260b06fe4a04fe4d956aa56b0b33af0ce2a6816ead25f100eb3847','root49-lag-combined-i/build-review.json':'55c241370c34437410747a9762d3a11c4c7f52bb5d50e1e45a067360cff9ddbe','root49-lag-combined-native-fl/review.json':'d9d52efa096168e5ce2402e5a8a977515e699f2a47ce85a81528a0605b801a91','agent49-megaman-bass-current-g-a/arsenal-freeze-by.json':'3f3e3e4b74d55c859a1c743026f4575d56176c7ca3b3c97e0ff922d092d32f97','agent49-megaman-bass-current-g-a/arsenal-coverage-bw.json':'a60c2cef622188c4c09a6d1424cd7a00db7efccfc0b2227582603622031fbe3d','specialist-mario-luigi-scrooge-current-g-a/coverage-ao.json':'2e9fba82aefc7f5c01922e6e6c40f82a8e9dedff9abbb6b749690452492744b6','root49-pit-rygar-h-allocation-fg.json':'337d7322bb0ce4e80a9a4e3cd8f4e72d19a8b62e1b296598c76a2ab1ce7091f0','root49-megaman-bass-arm-allocation-fm.json':'15ff18a2805594db17e49077c61d77c753d2c8356b8e559f57adae28dd18a8ab','root49-lsr-g-allocation-ez.json':'908348ee9a7dbfd6b42d9e149c4b858ff09ff55deda7c8d345ecbc654280114d','root49-mls-h-audio-allocation-eo.json':'f952abfdb1a62f5430345816cf0a1cdb8a8d76eaf3c2c57e76aa8cee429f601a','root49-mls-h-audio-allocation-eo-addendum.json':'5d57d351761ed77804e3fcacfa27c94f60eb5b06d3e777c271fcd8df00702185'}
 for n,h in refs.items():assert sha(V/n)==h,n
 for stem in ['root49-lag-combined-native-fl']:
  d=V/stem;z=read(d/'review.json');assert len(z['groups'])==18 and all(q['exit']==0 for q in z['groups'])
  assert sha(d/'preparation.json')==z['preparation_sha256']
  for n,h in read(d/'preparation.json')['dependencies'].items():assert sha(R/n)==h
  for q in z['groups']:
   for n,a in q['files'].items():assert sha(d/n)==a['sha256']and(d/n).stat().st_size==a['bytes']
 old=V/'root49-goal-coverage-eb.json';assert sha(old)=='b3584f3f2fad67d04d9ccc8ef107e5046f607febb72de1ae0834040838c19b02';j=read(old)
 sc=read(V/'root49-scrooge-h-root-review-em.json');ba=read(V/'root49-bass-g-review-h-transfer-fc/review.json')
 additions=[dict(identity=12,variant=0,manifest=sc['manifest'],manifest_sha256=sc['manifest_sha256'],result=sc['result'],hardware=sc['hardware'],root_review_sha256=refs['root49-scrooge-h-root-review-em.json']),dict(identity=9,variant=0,manifest=ba['H_manifest'],manifest_sha256=ba['H_manifest_sha256'],result=ba['result'],hardware=ba['hardware'],root_review_sha256=refs['root49-bass-g-review-h-transfer-fc/review.json'])]
 for q in j['roster']:
  key=q['character'],q['variant']
  for z in additions:
   if (z['identity'],z['variant'])==key:
    q['current_H_independently_admitted_base_routes'].append(z)
    q['pinned_full_clear_candidates'].append(dict(revision='H',mapper='mmc3',manifest=z['manifest'],sha256=z['manifest_sha256'],frames=z['result']['frames'],recorded=False))
    q['current_G_independently_admitted_base_route_mappers']=['mmc3']
  assert not any(q[n]for n in ['base_moves_and_power_tiers_complete','all_specials_upgrades_complete','final_recording_complete','overall_complete'])
 assert len(j['roster'])==14 and sum(len(q['inventory_2_02'])for q in j['roster'])==66
 assert sum(bool(q['current_H_independently_admitted_base_routes'])for q in j['roster'])==9
 candidate=R/'build/roster-through-2-2/specialist-h-pr-pit-c-6-v0-mmc3/manifest.json';assert sha(candidate)=='d8c98d94740740f90f239e49f75b4025cf11b407c7aff9ec5cfc7769ed0fe292';cm=read(candidate);assert cm['result']['cleared']and cm['result']['frames']==25750 and not cm['full_frame_audit']
 j['roster'][next(i for i,q in enumerate(j['roster'])if q['character']==6)]['current_H_discovery_candidate']=dict(manifest=str(candidate.relative_to(R)),sha256=sha(candidate),frames=25750,full_hardware_proof_pending=True,root_admitted=False)
 j.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),current_H_actual_MMC3_admitted_identity_count=9,current_H_actual_native_mapper_pairs=9,current_G_root_admitted_identity_count=6,current_G_root_admitted_identity_mapper_pairs=8,working_revision='H',private_I_installed=False,new_root_review_references=refs,private_I=dict(build_review_sha256=refs['root49-lag-combined-i/build-review.json'],native_18_groups_sha256=refs['root49-lag-combined-native-fl/review.json'],current_H_routes_transferred=False,adopted=False),extended_equipment_requirements=dict(MegaMan=11,Bass=9,audit=refs['agent49-megaman-bass-current-g-a/arsenal-coverage-bw.json'],note='66 inventory IDs already include automatic MM Charge10. Intrinsic busters/movement, replacement/passive/lifecycle and mode requirements remain in addition; do not reduce scope to66 selectable items.'),completion_scope='Current installedH has nine independently admitted actualEasy/MMC3 base identities and two explicit priorG literalMMC5 links; four retained H base recordings. New Pit H discovery clear is not admitted until full independent hardware/support review. Private combinedI has scoped audio, exact math/ABI and18 native fixture groups but is not installed and has no current-route transfer. All14 routes, every intrinsic/special/weapon/upgrade/acquisition/mode/source/SFX requirement, original1-1 variants/enemies/items, thorough populated lag and final all-roster media remain incomplete.',goal_complete=False)
 index.write_text(json.dumps(j,indent=2)+'\n')
 attempts={}
 for tag,ident in [('pit-guided-el',6),('rygar-guided-el',7),('samus-flame-eh',2),('samus-bowser-en',2),('samus-bowser-er',2),('samus-bowser-et',2),('samus-resume-ex',2),('samus-water-fd',2),('samus-water-fh',2),('pit-combat-eu',6),('rygar-combat-eu',7),('pit-followup-fa',6),('rygar-followup-fa',7)]:
  d=R/'build/roster-through-2-2'/f'root49-h-{tag}-{ident}-v0-mmc3';m=read(d/'manifest.json');assert m['rom_sha256']=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'and m['controller_only']and not m['memory_or_register_writes']
  t=list(csv.DictReader((d/'trace.csv').open()));attempts[tag]=dict(manifest=str((d/'manifest.json').relative_to(R)),sha256=sha(d/'manifest.json'),result=m.get('result'),last_trace=t[-1],discovery_only=True)
 qa=R/'docs/qa/easy-hard-legacy-v49.md';before=sha(qa);assert before=='8db3749c71de096ef466fa1763801478bb004898ca5ca895ec41f9a45cf61dc8'
 qa.write_text(qa.read_text()+'''

Root continuation FJ keeps installed main at immutable H. Scrooge and Bass
now have actual H full fixed replays, independently rehashed with full physical
OAM decoding. Scrooge clears21,742 frames and Bass29,543, both zero deaths
with25 responsive native2-3 rows. Eleven Scrooge and14 Bass streams match
their separately reviewed G proofs literally. The H total is now nine
identities and177,948 independently decoded actual DMA snapshots. All original
corner/platform/spring/source/power/audio limitations remain. There are still
four retained H base movies, not final recordings for the entire roster.

Actual H Samus now clears five stages. A late supported jump from the moving
castle platform at2188 passes Bowser; the earlier jump bonked the real ceiling
and the stationary wait was carried into his rising body. The old guide's
future AreaPointer rejection and recomputing past an already active fallback
were controller defects. One observer is used in the successor, retaining the
old duplicate-log negative. Real supported coral jumps now reach2-2 X2097;
the remaining failure is a native fish contact on descent. No source-disjoint
claim is inferred from that inclusive collision. Pit has a new25,750-frame H
discovery clear; independent full hardware/support replay is still pending.
Rygar passed the first low-ceiling pit using an actual1274 edge takeoff and
later reached a second Goomba. The three identities are not yet root-admitted.

The original H authored WaterShield checks retain two MMC5 max-cycle failures,
6113/6114 versus the existing6100 bound. Private cache proposal EQ/ES moves
the vector-key guard into its sole caller, removing only a redundant JSR/RTS
on cache hits. It saves12 cycles per reused ball, typically84 per expansion
update. Both baselines, foreign addresses and RAM ABI stay unchanged. Root EW
checks10,240 compiled cases, exact remaining ordered writes/registers/liveRAM,
with only the two individually identified dead call-stack cells excepted.
Eighteen unchanged native groups cover exact signed orbit, nonuniform expansion
and lifetime, world/Y wrap, source-left reveal, terrain corners, OAM, Bass
specials and MegaMan special armor. These are explicitly authored arenas.
MMC5 expansion max falls to6029/6030 and actual DMA is60/62; MMC3 still has
18/62 or21/62 missed expansion opportunities. FE's original prose20 is corrected
to21 in its additive receipt; raw attached metrics were always21. Serious
populated-level lag is not solved by this small optimization.

Root independently reruns the frozen private H MegaMan audio verifier:1167
pinned files,44,428 foreign symbols,16,008 compiled lifecycle calls,200 actual
native calls with195 child IRQs and1936 exact native instruction clocks pass.
Observed same-entry savings are362..516 cycles. Only the owned MMC3 audio
closure changes; MMC5 is literal H. A local copy of py65's cycle table repairs
its CE/DEC-absolute3-cycle entry to the native6-cycle value; shared dependencies
are untouched. The old H controller tape's private timing/death negative is
retained and never promoted to a route clear. Private combined I now builds
as the exact disjoint union:1508 MMC3 bytes,149 MMC5 bytes, both baselines
literal H. Its18 combined native groups pass. It remains private, with no
adoption, full ordinary-route transfer or final-media claim.

The new equipment audit distinguishes11 MegaMan and9 Bass equipment nodes,
including intrinsic Busters, automatic Charge and passive/replacement Balancer.
The existing66-ID index already includes Charge10; it never covered all
intrinsic/mode/refill/animation/SFX/lifecycle requirements by itself. Historical
170 subsystem passes and six retained failures remain historical. Source
review identifies Super Arm's wrong payment time (native lift versus source
throw), and source-valid low-energy Rush behavior requiring focused witnesses.
Private Arm correction is authorized in its own measured phase; main remains H.
All prior captures, lossless masters, negatives and receipts remain retained.
The later raised-storage authorization supersedes the original30GB request;
the measured working ceiling remains80GB.
''')
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used<80000000000
 result=dict(status='PROGRESS_H_NINE_BASE_ROUTES_PRIVATE_I_LAG_VALIDATION_AND_EQUIPMENT_GAPS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),prior_handoff_sha256=sha(prior),working_checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),main_rehashed=dict(sources=458,generated=11,artifacts=8),references=refs,index=dict(path=str(index.relative_to(R)),sha256=sha(index)),QA=dict(path=str(qa.relative_to(R)),prior_sha256=before,sha256=sha(qa)),root_actual_H_attempts=attempts,root_owned_native_handles_all_terminal=['59219','24400','6847','2067','98360','7093','48750','64560','61400','55358','34863','57088','80763','5307','90082','77688','45027','70995','60868'],root_live_native_handles=[],specialists=dict(mario_luigi_scrooge_s2='New separate500MB currentH Pit/Rygar phase; Pit C actual discoveryclear25750, next independent fixed/support proof. Frozen prior MLS/audio remains read-only.',samus_contra_s2='Bass BU/rootFC actualH complete; frozen20-node arsenal audit; private H SuperArm timing correction approved in200MB phase/50MB reserve and1.35GB inclusive/100MB reserve, no main edits.',link_simon_ryu='FrozenG Simon/Ryu ordinary routes, lastreported SimonAP actualroofedpit passed;1.8GB cap/100MB reserve. No full root-admitted clear yet.'),budget=dict(global_observed=used,global_cap=80000000000,all_prior_negatives_lossless_retained=True,MLS_prior_cap=1050000000,MLS_prior_reserve=100000000,new_Pit_Rygar_cap=500000000,new_Pit_Rygar_reserve=100000000,MM_Bass_inclusive_cap=1350000000,MM_Bass_inclusive_reserve=100000000,Arm_private_cap=200000000,Arm_private_reserve=50000000,LSR_cap=1800000000,LSR_reserve=100000000),next_required=['Independently review/freeze actualH Pit fixed/support packet; finish H Rygar/Samus and frozenG Simon/Ryu plus actual current-build transfers.','Finish source-backed Arm correction and witness low-energy Rush leads; full14/everyequipment acquisition→attack→contact→ammo→icon→SFX/mode/lifecycle remains required.','Profile populated WaterShield and inner collision/vector/draw work. Combined I passes authored bounds but MMC3 expansion still misses18/62 and21/62 hardware opportunities.','Review actual private I ordinary route timing and adoption only with full evidence; all current H proofs remain H.','Finish original1-1 shortcut/nonshortcut/everyenemy/item coverage and all-character final real audio/video with lossless retention.'],goal_status='active',previous_substantive_goal_turn_classification='progress: installedH/seven actualroutes/four realmovies/native profile; intervening acknowledgments did not alter authority',current_goal_turn_classification='progress: two additional actualH admitted routes, newSamus/Pit/Rygar native progress, root audio verification, private water and combinedI runtime changes with18 native groups each, full source equipment gap audit and new correction work',blocked=False,accepted_release=False,goal_complete=False)
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=sha(out),index_sha256=sha(index),QA_sha256=sha(qa),workspace_bytes=used)))
if __name__=='__main__':main()
