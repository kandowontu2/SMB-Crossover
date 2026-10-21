"""Additive full-scope handoff: current G routes and private H audio work."""
from pathlib import Path
import csv,datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
rows=lambda p:list(csv.DictReader(Path(p).open(newline='')))
QA='''

Root continuation CV keeps the working build at G. Independent root review
`root49-current-route-review-cm.json` verifies Mario and Luigi on both MMC3
and MMC5 through six stages and25 subsequent2-3 controls, zero deaths. Their
routes remain small throughout, without injury; this is not a growth/fire/
Star or complete-specials proof. Two Mario takeoffs are explicitly native
corner catches, not certified terrain-top jumps. Independent fixed replays
match all21 trace and16 native fields; actual hardware/DMA and support checks
pass. Link's G/Easy/MMC3 fixed transfer completes27,058 frames, zero deaths,
25 subsequent controls X40 to62. All nine canonical streams literally match
the original F candidate/fixed pair, and the single10,240-byte G endpoint
matches F fixed. The root rehash covers1,915 F files and46 G files. No complete
Link accepted-ground-A log exists; no universal support, MMC5, source-perfect
or complete-arsenal claim follows. Root receipt SHA256:
`ed8e80955df544744f0b1cc704e2db34faceb22b4bc3b40e495e52b58718cfe9`.

Fresh ordinary G Samus controllers now legitimately pass the first four
stages. Two observed underground bomb encounters produce six native Goomba
defeat-state transitions, three per group. Fresh bridge controls pass Bowser
using the actual moving platform; this does not claim a Bowser kill. The
later2-1 pose guide loops over a shell and farms lives, then dies; a successor
leaves that loop and contacts an actual Green Koopa. Neither is a complete
route or underwater-coral repair proof. The original G bridge host postprocess
mistakenly read the prior F-attempt output directory; its retained report is
superseded by the explicitly tagged actual native manifest in CV. The second
bomb host encountered a missing-result key after an intentional controller
stall; that negative and the actual result-null manifest remain retained.
No runtime patch is inferred from those host/controller failures.

A private H candidate ports the existing MMC5 Metroid flag-scan replacement
to MMC3. It changes75 ROM bytes across five music banks; MMC5 and both
baseline ROMs stay literal G. Working sources and installed ROMs are unchanged.
Compiled checks cover65,536 mask/status combinations with an explicit oracle
for every removed scan RMW/stack write and no unexplained RAM/register/bank/
APU differences. Isolated execution from122 actual F audio-entry snapshots
saves a median1,470 instruction cycles per update (old median5,985; new
median4,531). This is not a whole-game frame-rate measurement. Six existing
native audio fixture groups pass on both mappers: short/long/wave envelopes,
pickup sounds and world effects with physical APU/MMC5 assertions. These are
authored fixtures with setup writes, not ordinary acquisition or final media.
Native interrupt composition and ordinary H traversal remain required before
adoption. Build/CPU/native receipts are under `root49-samus-audio-scan-h`.

The full-scope index is `root49-goal-coverage-cu.json`. All14 identities and
66 inventory entries, remaining routes/upgrades, original1-1 variants and
every enemy/item, lag work, and retained final audio/video are still required.
No original suite failures are erased and no final recordings were made in
this continuation. All negatives/lossless files are retained under the80GB
global allocation authorized after the user's explicit cap-raise answer.
'''
def main():
 out=V/'root-current49-progress-cv.json';index=V/'root49-goal-coverage-cu.json';assert not out.exists()and not index.exists()
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';c=read(cp);assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0'
 for n,h in c['source_hashes'].items():assert sha(R/n)==sha(Path(c['source_directory'])/n)==h,n
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==sha(R/a['frozen_path'])==a['sha256']
 expected={'root49-current-route-review-cm.json':'ed8e80955df544744f0b1cc704e2db34faceb22b4bc3b40e495e52b58718cfe9','root49-audio-isolated-cq/report.json':'d4557ba6645dda4371bb976102f0642ee0e14381ffc8d1d6895651a0f89c56f2','root49-samus-audio-scan-h/build-review.json':'b3c597eecd63eaaab3b15fad6e31766d8c051d2413a6e92536b49420b1a0e18b','root49-samus-audio-scan-h/cpu-review-ct.json':'70bcf833b77d9a3058b37f990c0f66a75df5203ae8bddc4a474fc26d9a86bcee','root49-samus-audio-scan-h/native-checks-cw/review.json':'4df4e939842df79229a730bbd1204f270de8edf76ad3a7cc4d639ffbeccf020d','root49-global-allocation-bm.json':'94233edf6ac368b4689bafd937fc5f7be3231c1137dc3aa002e76125827a79d3'}
 for n,h in expected.items():assert sha(V/n)==h,n
 attempts={};P=R/'build/roster-through-2-2';phase=V/'root49-current-g-samus-a'
 names=['pose-a','Fclock-ci','clock-b','clock-c','bombs-d','bombs-e','resume-f','boss-g','forward-h']
 for n in names:
  d=P/('root49-g-samus-'+n+'-2-v0-mmc3');m=read(d/'manifest.json');assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
  attempts[n]=dict(directory=str(d.relative_to(R)),manifest_sha256=sha(d/'manifest.json'),ROM=m['rom_sha256'],result=m.get('result'),last_trace=rows(d/'trace.csv')[-1])
  if n!='Fclock-ci':assert m['rom_sha256']=='151f3f6e8aa8753fce088c3f2ba6815df7290c1ec3b959018ca4717ae8f491cc'
 assert attempts['Fclock-ci']['ROM']=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
 prefix_checks=[]
 for new,old,n in [('bombs-d','clock-c',10600),('bombs-e','bombs-d',11950),('resume-f','bombs-e',12860),('boss-g','resume-f',22280),('forward-h','boss-g',24144)]:
  a=P/('root49-g-samus-'+new+'-2-v0-mmc3');b=P/('root49-g-samus-'+old+'-2-v0-mmc3')
  assert rows(a/'inputs.csv')[:n]==rows(b/'inputs.csv')[:n]and rows(a/'trace.csv')[:n]==rows(b/'trace.csv')[:n]
  prefix_checks.append(dict(new=new,parent=old,input_and_all21_trace_prefix_rows=n))
 kills={}
 for n in ['bombs-d','bombs-e']:
  d=P/('root49-g-samus-'+n+'-2-v0-mmc3');found={}
  for q in rows(d/'floor-bombs-d.csv'):
   for raw in q['actors'].split(';'):
    z=list(map(int,raw.split(':')))
    if z[1]and z[2]==6 and z[3]&32:found.setdefault(z[0],int(q['frame']))
  assert len(found)==3;kills[n]=found
 corrections=dict(second_bomb_host='E native intentionally stopped on pose-progress bound, result absent; postprocess KeyError retained. No game-death assertion.',bridge_postprocess=dict(retained_wrong_file=str((phase/'boss-g-cp/native-result.json').relative_to(R)),wrong_sha256=sha(phase/'boss-g-cp/native-result.json'),actual_manifest=attempts['boss-g'],reason='Copied postprocess directory referenced resume-f. Command tag and actual33039 native output establish boss-g result; no production change.'),reviewer_negatives=['Root CM initial assertion required verified flag on adaptive candidate; retained initial reviewer, fixed flag restricted to independent fixed replays.','CP expected-stage host preflight and CT initial Python syntax failure retained; no native or main effects.'],geometry_limit='G33039 ForceInjury ObjectOffset0 does not establish fatal actor; native boxes at that row are disjoint and X255. Caller/ownership attribution remains unresolved. H24192 owns rawGreenKoopa0/slot1 and native boxes overlap. AreaPointer future destination parsing alone is not corruption evidence.')
 (phase/'additive-native-review-cv.json').write_text(json.dumps(dict(attempts=attempts,prefix_checks=prefix_checks,observed_Goomba_defeats=kills,corrections=corrections,scope='Actual ordinary progress, no complete Samus route/coral or source-perfect claim.'),indent=2)+'\n')
 old=V/'root49-goal-coverage-cf.json';assert sha(old)=='83c51389d516277cec92b95367d386dbc938d0c0f149a5d097c66a1dbb46599f';j=read(old)
 images={h:(rev,mp)for rev,cp0 in j['checkpoints'].items()for mp,h in cp0['ROMs'].items()};candidates={}
 for p in P.glob('*/manifest.json'):
  m=read(p);which=images.get(m.get('rom_sha256'))
  if not which or not m.get('verified_through_2_2'):continue
  q=m['result'];assert q['cleared']and q['all_six_stages']and not q['deaths']and not m['memory_or_register_writes']and m['controller_only']and m['full_frame_audit']
  candidates.setdefault((m['config']['character'],m['config'].get('variant',0)),[]).append(dict(revision=which[0],mapper=which[1],manifest=str(p.relative_to(R)),sha256=sha(p),frames=q['frames'],recorded=m['config']['record']))
 for q in j['roster']:
  key=(q['character'],q['variant']);q['pinned_full_clear_candidates']=candidates.get(key,[])
  for rev in ['F','G']:q[f'current_working_{rev}_full_clear_candidates']=[z for z in q['pinned_full_clear_candidates']if z['revision']==rev]
  q['current_G_independently_admitted_base_route_mappers']=['mmc3','mmc5']if key in[(0,0),(8,0)]else['mmc3']if key==(4,0)else[]
  assert not any(q[n]for n in ['base_moves_and_power_tiers_complete','all_specials_upgrades_complete','final_recording_complete','overall_complete'])
 assert len(j['roster'])==14 and sum(len(q['inventory_2_02'])for q in j['roster'])==66
 j.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),new_root_review_references=expected,working_revision='G',private_H_installed=False,current_G_root_admitted_identity_count=3,current_G_root_admitted_identity_mapper_pairs=5,completion_scope='Current G Mario/Luigi bothmaps and LinkMMC3 base routes independently admitted. Samus fourstages progress only. Private H MMC3 audio scan passes compiled and6authored native groups, pending ISR/ordinary validation, not installed. All14/66 and original full route/media requirements remain open.',goal_complete=False)
 index.write_text(json.dumps(j,indent=2)+'\n')
 qa=R/'docs/qa/easy-hard-legacy-v49.md';before=sha(qa);assert before=='a5b7fa166727fe5855c968f3b57eaf1b7e229b84e580816d620796062c34a1a1';qa.write_text(qa.read_text()+QA)
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total<80000000000
 owned=sum(p.stat().st_size for p in phase.rglob('*')if p.is_file())+sum(p.stat().st_size for d in P.glob('root49-g-samus-*')for p in d.rglob('*')if p.is_file());hbytes=sum(p.stat().st_size for p in(V/'root49-samus-audio-scan-h').rglob('*')if p.is_file());assert owned<650000000 and hbytes<300000000
 refs={n:dict(sha256=h,bytes=(V/n).stat().st_size)for n,h in expected.items()}
 result=dict(status='PROGRESS_CURRENT_G_ROUTES_AND_PRIVATE_MMC3_AUDIO_OPTIMIZATION',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),prior_handoff_sha256=sha(V/'root-current49-progress-cg.json'),working_checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),shared_main_rehashed=dict(sources=458,generated=11,artifacts=8),references=refs,root_Samus_additive_review=dict(path=str((phase/'additive-native-review-cv.json').relative_to(R)),sha256=sha(phase/'additive-native-review-cv.json')),full_scope_index=dict(path=str(index.relative_to(R)),sha256=sha(index)),QA=dict(path=str(qa.relative_to(R)),before_sha256=before,sha256=sha(qa)),root_live_native_handles=[],root_handles_closed={'23093':1,'78083':0,'32789':1,'18154':1,'91000':0,'11669':1,'55993':0,'88239':0,'69232':0,'93093':0,'31352':0,'39276':0},specialists=dict(mario_luigi_scrooge_s2='G Mario/Luigi bothmaps J admitted. Scrooge Q actual firstlift ride/jump discovery live68069;650MB/100MBreserve, lastphase394MB. No root claim beyond admitted J.',link_simon_ryu='G LinkMMC3 admitted. Simon L1-3 combat live57804; Ryu D first/middle mushroom route preparation, latest383MB.650MB/100MBreserve. OldG/F proofs immutable.',samus_contra_s2='CurrentG MegaMan five stages/2-2 progress, U secondcap fish wait live79875, lastphase389MB. OldD MM/Bass proofs immutable, no currentG fullclear yet.650MB/100MBreserve.'),budget=dict(workspace_bytes_observed=total,global_cap_bytes=80000000000,allocation_sha256=expected['root49-global-allocation-bm.json'],root_G_phase_bytes=owned,root_G_phase_cap=650000000,private_H_phase_bytes=hbytes,private_H_phase_cap=300000000,all_lossless_and_negatives_retained=True),next_required=['Private H exact native ISR composition and ordinary traversal/audio checks before installation; keep G main and all current proofs stable meanwhile.','Fresh G Samus through2-1/2-2/coral, resolve actual33039 caller attribution without treating staleObjectOffset as collision ownership.','Finish currentG all14 routes, every66 inventory acquisition/special/upgrade effect and original1-1 variants/enemies/items.','Optimize unresolved weapons/renderer/enemy/audio lag and verify meaningful effects, then record and inspect final real audio/video for every identity, retain lossless.'],blocked=False,accepted_release=False,goal_complete=False)
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(handoff_sha256=sha(out),index_sha256=sha(index),QA_sha256=sha(qa),budget=result['budget'])))
if __name__=='__main__':main()
