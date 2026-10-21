"""Durable full-scope coverage and handoff after the Samus axis repair."""
from pathlib import Path
import csv,datetime,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
QA='''
Root continuation CG installs provisional working G, the Samus head/side-axis
repair. Actual F replay V is quarantined after29,923: an upward jump beside
coral incorrectly separated Y171 to185, then the left-wall clamp advanced
sixteen pixels per update. A passive exact-tape replay identifies the native
head and wall writers; the original minimal regression fails on both F
mappers. The diagnosis is `root49-samus-f-coral-defect-review-bp.json`.

G checks each nonempty head sample against the previous Q8.16 head position
before admitting a ceiling, following pinned2.02 HitTester.checkLastHitPoints.
Walking coin checks, the three head samples and actual brick/reward origins
remain. This does not claim complete original corner-axis equivalence. Both
mappers pass48 coral-side jump arenas,432 head-displacement arenas,150 Easy
head and240 wall arenas,75 debris origins,19 question rewards and a complete
mushroom rise; the existing power-up animation and swimming fixtures also
pass. The corrected wall observer binds actual physical-bank/eight-byte
hooks: its obsolete CurrentBank==1 check missed fixed-bank effects while the
rare head handler mapped bank9. Legacy brick expectations explicitly select
Easy; the original default-Hard failures are preserved. Shared fixtures have
not silently been rewritten to make them pass.

The compiled axis leaf also passes5,070 independent Q16 geometry components
per mapper. Empty complete-head outputs match F outside stack call bytes and
use no mapper writes; measured extra cost is10 walking/32 rising instruction
cycles. This replaces the first private candidate's unconditional banked
sample. The99-byte cold leaf fits both mappers; only the original184-byte
head procedure and the appended cold gap differ in ROM (204 changed bytes).
Baselines are literal F and all old external function/RAM addresses remain.
The twelve native regressions are pinned by
`root49-samus-head-axis-g6-check-bx/review.json`, SHA256
`cc64372af948d3ea2f8bb00d15c8ebf4412ef04305c29660ae41a03671d8f941`.

Working G checkpoint SHA256 is
`feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0`.
Both installed boot/control/floor smokes pass; the476-file F backup is
verified. This remains provisional: replaying the old F V physical tape on G
dies at4,199 in1-1 after position/cadence divergence at2,324, so it does not
demonstrate the underwater repair in an ordinary full route. Fresh G routes
and retained final videos remain required. Frozen D/F proofs retain their
original identities.

Root independently admits Bill and Lance F/Easy/MMC3:34,401/33,254 frames,
all six stages, zero deaths and25 actual2-3 controls X40 to70 each. The frozen
3,311-file/34-packet review preserves30 negatives and rechecks all21 trace
fields, native telemetry, supports and actual256-byte DMA snapshots.
`root49-lance-f-full-review-ca.json` SHA256 is
`82a5739180507824f70ce918e5df7111100b1c3dfeeb0f09eab3c0387faadaad`.
Sophia's earlier independently verified F proof remains separate.
Mega Man and Bass now have independently root-reviewed D/Easy/MMC3 proofs:
28,951/30,281 frames, zero deaths, with real subsequent-stage control.
Bass's full57-file raw/241-receipt/21-file closure rehash and20,943 actual DMA
decodes are in `root49-bass-d-full-review-cd.json`, SHA256
`8e69318409d58fed9d56eee444696652a218a2fd019589ff0050d97c215a2017`.
These are base routes, not complete arsenal/source-geometry/media admission.

Additional Samus F progress legitimately clears five stages and enters2-2;
the later coral displacement is invalid traversal evidence. Both-map Hard
components separately verify first Ice freeze without damage, second real
Ice thaw/damage, frozen-platform contact and authored Screw protection;
forced-roll missile ammo recovery, weapon-slot OAM and authored sound channel
restoration retain their explicit arena/ownership limits. The strengthened
shared passive fixture is the only adopted test change outside G's runtime
source catalog. Actual-route lag and interrupt-exclusive1-2 CPU scopes are
measured, with audio, drawing and enemy work still significant; no broad lag
solution or complete weapon profile is claimed.

The full-scope index is now `root49-goal-coverage-cf.json`. All14 identities,
66 inventory entries, both original1-1 route variants, every enemy/item,
remaining abilities/lag work and retained final recordings remain required.
No full-suite-green claim replaces the original73 failures/stock-Mario
comparison. The user's explicit lossless-retention/cap-raise answer supersedes
the old30GB limit; the bounded internal global cap is80GB, with all previous
allocation receipts and negatives retained. No full-goal completion is claimed.
'''
def main():
 out=V/'root-current49-progress-cg.json';index=V/'root49-goal-coverage-cf.json'
 assert not out.exists()and not index.exists()
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';g=json.loads(cp.read_text())
 assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0'
 for n,h in g['source_hashes'].items():assert sha(R/n)==sha(Path(g['source_directory'])/n)==h,n
 for n,h in g['generated11'].items():assert sha(R/'build/generated'/n)==h,n
 for b in g['builds']:
  for q in b['artifacts'].values():assert sha(R/q['path'])==sha(R/q['frozen_path'])==q['sha256']
 old=V/'root49-goal-coverage-bo.json';assert sha(old)=='0223b43ede1e6982c89c0e316eff40cb98d800f737f5350fd65fe9272fb78628';j=json.loads(old.read_text())
 j['checkpoints']['G']=dict(path=str(cp.relative_to(R)),sha256=sha(cp),ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in g['builds']})
 images={h:(rev,mapper)for rev,c in j['checkpoints'].items()for mapper,h in c['ROMs'].items()};clears={}
 for p in(R/'build/roster-through-2-2').glob('*/manifest.json'):
  m=json.loads(p.read_text());which=images.get(m.get('rom_sha256'))
  if not which or not m.get('verified_through_2_2'):continue
  assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and m['result']['cleared']and m['result']['all_six_stages']and not m['result']['deaths']
  key=(m['config']['character'],m['config'].get('variant',0));clears.setdefault(key,[]).append(dict(revision=which[0],mapper=which[1],manifest=str(p.relative_to(R)),sha256=sha(p),frames=m['result']['frames'],recorded=m['config']['record']))
 for q in j['roster']:
  q['pinned_full_clear_candidates']=clears.get((q['character'],q['variant']),[])
  for rev in ['F','G']:q[f'current_working_{rev}_full_clear_candidates']=[z for z in q['pinned_full_clear_candidates']if z['revision']==rev]
  q['actual_working_revision']='G'
  assert not any(q[n]for n in ['base_moves_and_power_tiers_complete','all_specials_upgrades_complete','final_recording_complete','overall_complete'])
 assert len(j['roster'])==14 and sum(len(q['inventory_2_02'])for q in j['roster'])==66
 samus=next(q for q in j['roster']if q['character']==2)
 samus['additional_current_F_progress']['newer_V_quarantined']='Confirmed native head/side classification defect, BP diagnosis and BR baseline bothmaps. F V after29923 remains invalid.'
 samus['provisional_working_G_repair']=dict(checkpoint_sha256=sha(cp),native_regression_sha256=sha(V/'root49-samus-head-axis-g6-check-bx/review.json'),CPU_component_sha256=sha(V/'root49-samus-head-axis-g6/axis-cpu-bz.json'),installed_smoke_sha256=sha(V/'root49-samus-axis-adoption-cb/review.json'),ordinary_corral_repair_demonstrated=False,full_clear=False)
 refs=['root49-lance-f-full-review-ca.json','root49-megaman-d-full-review-bc.json','root49-bass-d-full-review-cd.json','root49-samus-f-progress-review-bc.json','root49-samus-f-later-review-bg.json','root49-samus-f-coral-defect-review-bp.json','root49-current-f-samus-coral-regression-br/baseline-results.json','root49-samus-head-axis-g6-check-bx/review.json','root49-samus-head-axis-g6/axis-cpu-bz.json','root49-samus-axis-adoption-cb/review.json','root49-samus-g6-coral-replay-by/native-result.json','root49-samus-f-real-lag-profile-bd.json','root49-samus-f-exclusive-profile-review-bl.json','root49-global-allocation-bm.json']
 references={n:dict(sha256=sha(V/n),bytes=(V/n).stat().st_size)for n in refs}
 j.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),root_review_references=references,working_revision='G',completion_scope='G installed component-verified Samus repair, no ordinary G full route yet. Frozen F Bill/Lance/Sophia and frozen D MM/Bass independently root-admitted with original limits. All14 identities/66 inventory entries and all original route/media requirements remain open.',goal_complete=False)
 index.write_text(json.dumps(j,indent=2)+'\n')
 qa=R/'docs/qa/easy-hard-legacy-v49.md';qa_before=sha(qa);assert qa_before=='63f02dfb5a51a551321aaae4dadd4a7592d7aa9be50c2d5eb767316635a1cacd'
 qa.write_text(qa.read_text()+QA)
 sys_path=R/'tools/playthroughs';import sys;sys.path.insert(0,str(sys_path));from roster_run import workspace_bytes
 handoff=dict(status='PROGRESS_SAMUS_AXIS_REPAIR_INSTALLED_AND_ADDITIONAL_F_D_COMPLETE_PROOFS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),prior_handoff_sha256=sha(V/'root-current49-progress-ba.json'),current_goal_turn_classification='progress',working_checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),shared_main_rehashed=dict(sources=458,generated=11,artifacts=8),references=references,full_scope_index=dict(path=str(index.relative_to(R)),sha256=sha(index)),QA=dict(path=str(qa.relative_to(R)),before_sha256=qa_before,sha256=sha(qa)),
  completed=['Installed provisional Samus previous-head/coral-axis fix, bothmappers, recoverable476-file F backup, literalbaseline builds and two-ROM-span delta.', 'Bothmap12 native regression groups pass:48coral/432head/150head+240wall/reward/mushroomrise, powerup/swimming;10,140 compiledsource-axis decisions and exact emptyhead ABI outside stack.', 'Independent root admissions: F Bill+Lance plus retained F Sophia; D MegaMan+Bass. Original geometry/arsenal/media/mapper/revision limits retained.','Source-correct Ice passive test and other F seeded components independently rehashed; real lag/exclusive CPU profile measured, broadoptimization still open.'],
  negative_scope={'F_V':'29923 head side/ceiling defect +16px successive wall clamps; traversal invalid; source-repaired component tests, ordinary currentG traversal still pending.','G6_old_F_tape':'4199 death in1-1, first actual position divergence2324 after changedNmiSkipped cadence; does not reachcoral, no G route claim.','G5_coral_observer':'Empty Probe shared whole-head Done RTS, so observer sampled temporary shiftedX. G6 uses its own empty RTS; wholehead native semantics rechecked.','legacy_fixtures':'Original Hard legacy-brick assertions and A-bank-only effect observer failures retained; private explicitEasy/actualphysicalhook corrections pass bothF/G without weakening effects.','host_preflight':'G initialorder/G3 unresolved.res/G4 off-by-one pad and CPUfixedcycle reviewer negatives retained; no mainmutation fromthosefailedpreflights.'},
  root_live_native_handles=[],root_native_handles_closed={'88816':0,'98558':0,'50140':0,'55781':0,'25360':0,'43000':0,'12855':0,'2864':0,'88824':1},
  specialists={'link_simon_ryu':'FrozenF Link five stages/2-2 progress, latestAF25605fishcontact; approved1.3GB/100MBreserve/global80, nextAG actualsupported fulljump. MainG successor not retagged.','mario_luigi_scrooge_s2':'Bill/LanceFMMC3 AKfrozen and rootadmitted. ALFMMC5 oldD transferterminal12944death1-2, additiveownerreviewpending. No current ownednative aslastreported.','samus_contra_s2':'D MM+Bass CG/CHfrozen and rootadmitted. Followupassigned newG MM/Bass phase650MB/100MBreserve/global80, bothmaps/arsenal/media stillrequired.'},
  budget=dict(workspace_bytes=workspace_bytes(R),global_cap_bytes=80000000000,authority_sha256=sha(V/'root49-global-allocation-bm.json'),lossless_and_negatives_retained=True),
  next_required=['Fresh ordinary G Samus controller discovery through coral and2-2; retain all earlier F/D proof scopes.','Complete currentG roster and remaining66-entry arsenal acquisition/effects, original1-1 shortcut/nonshortcut/everyenemy/item obligations.','Use measured Audio/Enemies/Draw/Weapons hotspots to optimize unresolvedlag, verify meaningful output/ABI/ISR equivalence.','Record and inspect final real audio/video for every identity, retain lossless; no final recordings this continuation.'],blocked=False,accepted_release=False,goal_complete=False)
 out.write_text(json.dumps(handoff,indent=2)+'\n');print('CURRENT_PROGRESS',sha(out),'INDEX',sha(index),'QA',sha(qa),flush=True)
if __name__=='__main__':main()
