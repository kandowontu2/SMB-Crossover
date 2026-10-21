"""Durable full-roster base milestone and still-open source/performance work."""
from pathlib import Path
import datetime,hashlib,json,os,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 out=V/'root-current49-progress-hf.json';assert not out.exists()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';c=read(cp)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==a['sha256']
 pins={'Ryu_root':'root49-ryu-h-root-review-gv.json','Ryu_source_support':'root49-ryu-h-support-gu.json','Rush_root':'root49-rush-root-review-gw/review.json','Water_filter_root':'root49-water-filter-root-review-hg.json','retention_and_Ryu_allocation':'root49-retention-and-ryu-motion-allocation-gx.json','repair_allowances':'root49-repair-successor-allocations-gz.json'}
 expected={'Ryu_root':'072c4dc9fa6340cb8d5554a88e45b5a587e28aad3aba78c1a20a9f3c356e6ac8','Ryu_source_support':'f8dc07f745921d8b01ab6752934c2f470db7c9271402087b8ceae718b433e85c','Rush_root':'df51f8ba94286d7d5fada42430a498a72aad79fbd3de2f43ab90a5eee7e9c1af','Water_filter_root':'a866a32e0bb1c917f614620d773139308dc3d8e46636d8e765463c07ceba7642','retention_and_Ryu_allocation':'d212766240c9672948f0b80cb0283f7c7aae2ef0aa229faabb61a3a5fe96c3f1','repair_allowances':'580c56ee5459a8d3956ed0e68752ad5b1a8a6041a0aa7dd8f84b8758d31b9612'}
 for k,n in pins.items():assert sha(V/n)==expected[k]
 beforeindex=V/'root49-goal-coverage-gv.json';assert sha(beforeindex)=='eeb8546e792e6bd87a93cc488669745b6e9a223ab1307a4f2d35be5f75c99a8e';j=read(beforeindex)
 assert len(j['roster'])==14 and j['current_H_actual_MMC3_admitted_identity_count']==14
 total=sum((z.get('hardware')or z.get('actual_hardware'))['actual_DMA']for r in j['roster']for z in r['current_H_independently_admitted_base_routes']);assert total==289401
 j.update(prior_index_sha256=sha(beforeindex),private_review_pins={k:dict(path=pins[k],sha256=expected[k])for k in ['Rush_root','Water_filter_root']},actual_H_DMA_total=total,goal_complete=False)
 index=V/'root49-goal-coverage-hf.json';assert not index.exists();index.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
 qa=R/'docs/qa/easy-hard-legacy-v49.md';assert sha(qa)=='1b7879869d244a245f63c56ce489e2205e3bacd4ec0ebad69a63e84630ad3b3e'
 backup=V/'root49-QA-before-hf.md';assert not backup.exists();backup.write_bytes(qa.read_bytes())
 addition='''

Root GS/GU/GV/HF: all14 actual H Easy/MMC3 base identities now independently
clear through2-2, with289401 decoded actualDMA snapshots. Ryu23098frames,
zero deaths,2-3entry23074 plus25 controlled frames X40to77. All11 G/H streams
and endpointRAM are literal.167 fresh inputs produce118 ground launches
(113terrain,4platform,1spring),46wall launches,2Down+A drops and1rejection.
42wall launches have current source cached contact;4 remain legacy fallback,
an explicit source geometry gap. Eight positive14..16px motion flags remain:
specialist unchangedH passive replay identifies exact native bank10 LeftClamp
STA atA2F5, opposite cached source climb side. Private narrow repair underway;
this base clear does not establish glitchless or complete2.02 source behavior.

Root GW independently rehashes frozen Rush mechanics470source/16artifacts/
889receipts and reexecutes all143 native fullcall pairs and560 source edges,
plus exact relocated-return lifetime controls. Land SFX remains a separate
private successor; no main install. HUD overflow repair likewise remains
private, with original offset100 versus84 capacity proof retained and material
mixed-queue foreground cost still unresolved. Native discovery is not yet a
bothmapper/fullroute acceptance.

Root GY/HA/HC/HD/HB/HG: privateI successor J changes47 bytes in the old50B
enemy-candidate scan on each mapper, preserving all RAM and outside-span PCs.
It hoists only the unchanged native offscreen rejection.18048 compiled scan
cases and18 unchanged native mechanics/geometry/OAM/foreign groups pass.
Twelve H/I/J profiles require actual native target eligibility; all attain
full8 shield orbit and expansion. Matched offscreen samples save4995(M3) or
4831(M5) cycles per8-ball update,32 samples peridentity/map. Genuine visible
enemy expansion remains about11.5Kto11.8K weapon cycles and is still laggy.
GQ/GT predecessors counted active actors without native offscreen admission,
so their full8 active-target windows do not establish visible-contact stress.
Skipped-consumer scratch liveness, further visible-target optimization and
full combined validation/adoption remain open. All candidate builds remain
uninstalled; installed source458/generated11/primary8 are again literalH.

The user's retained-lossless/raise-cap instruction now has a100GB working
cap,143GB free at allocation. All original inventory66/intrinsic/upgrade/
acquisition/ammo/icon/SFX/lifecycle/mode,1-1 variants/enemies/items and final
real audio/video requirements remain active. Only four retained H base movies
exist; no fullgoal/source-perfect/final-release claim is made.
'''
 temp=qa.with_name(qa.name+'.hf.tmp');assert not temp.exists();temp.write_bytes(qa.read_bytes()+addition.replace('\n','\r\n').encode('utf-8'));os.replace(temp,qa)
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used<100000000000
 prior=V/'root-current49-progress-gp.json';p=read(prior)
 p.update(status='PROGRESS_ALL14_H_BASE_ROUTES_RYU_HUD_LAND_AND_VISIBLE_WATER_FIXES_ACTIVE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_handoff_sha256=sha(prior),coverage_index_sha256=sha(index),QA_sha256=sha(qa),actual_H_base_identities=14,actual_H_DMA_total=total,root_Ryu_review_sha256=expected['Ryu_root'],root_Rush_review_sha256=expected['Rush_root'],root_Water_filter_review_sha256=expected['Water_filter_root'],private_J_installed=False,private_Rush_installed=False,workspace_bytes=used,workspace_cap=100000000000,retention_authority_sha256=expected['retention_and_Ryu_allocation'],repair_allocation_sha256=expected['repair_allowances'],root_native_handles=[],root_closed_this_turn={'72476':0,'97663':0,'78812':0,'92331':0,'77494':'Root-owned quadratic verifier stopped; unchanged source/artifacts and raw log retained, HA linear successor passed','59066':0,'31269':0,'74466':0,'66576':0},goal_status='active',current_turn_classification='progress',blocked=False,accepted_release=False,goal_complete=False)
 p['specialists']={'link_simon_ryu':'G frozen AL and actualH GS admitted; new GX private agent49-ryu-motion-h-a owns native LeftClamp/source-climb repair. H passive whole11+acceptedJSONL+endpoint literal; actual eight native writers bound. Samebank21B gate plan (+6) fits M5 SAMUS exactly; no main install. Inclusive2.4GB/100Mreserve, private200MB/50Mreserve.','samus_contra_s2':'Rush mechanics frozen R/root GW admitted component. Private LandV layout-y PASS; AA native28413 last owner report, normal/pause/world already pass and43 actualAudioUpdate calls reexecute exact.300MB/100Mreserve private, inclusive1.5GB/100Mreserve. Source Land55B existing literalasset, six frame records, new52B aliases inside old512B slab padding. Main unchanged.','mario_luigi_scrooge_s2':'HUDJ check-j bothmaps/boot192cases PASS. M actual scene guidance last owner report live96455; original K route and L observer failures retained. Pending initialization fixed. Mixed status1977..6407vs573/574 still performance concern; paired/deferred producer design being considered.330MB/50Mreserve. Main unchanged.'}
 p['remaining']=['Finish and independently root-review Ryu native opposite-side climb clamp, Rush Land audio/lifecycle and HUD bounded overflow repair/foreground cost.','Further optimize real visible-enemy Water Shield; J exact-scan/native checks and scoped offscreen savings pass, but skipped-consumer scratch liveness/source/mixed-state review remains before adoption.','Compose reviewed audio/Water/Arm/Rush/Land/HUD/Ryu changes; validate both mappers and install a new explicit checkpoint. Old H routes remain H, never retag.','Complete every intrinsic/special/alternate/upgrade/source/acquisition/ammo/icon/SFX/lifecycle/mode requirement, original1-1 variants/everyenemy/item.','Thorough remaining populated lag reduction and final real audio/video all14 identities; retain all lossless and negative evidence under raised100GB cap.']
 out.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(progress_sha256=sha(out),coverage_sha256=sha(index),QA_sha256=sha(qa),workspace_bytes=used,actual_H_DMA=total)))
if __name__=='__main__':main()
