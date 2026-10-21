"""Preserve full14/66 scope while recording installed H, real routes and movies."""
from pathlib import Path
import csv,datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def main():
 out=V/'root-current49-progress-eb.json';index=V/'root49-goal-coverage-eb.json';assert not out.exists()and not index.exists()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';c=read(cp);S=Path(c['source_directory'])
 for n,h in c['source_hashes'].items():assert sha(R/n)==sha(S/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==sha(S/'build/generated'/n)==h
 assert(len(c['source_hashes']),len(c['generated11']))==(458,11)
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==sha(R/a['frozen_path'])==a['sha256']
 refs={'root49-samus-audio-adoption-dd/review.json':'6317c78ac227f4a2c22103090a261e1eb1fc3ff24f6e2bcd749e421445e008e8','root49-samus-audio-scan-h/native-irq-cz/cpu-native-review-db.json':'fa7464b1ff17fb6d4f5dc0a8e823e00ee031f5dc013e8ed3cfb7e99e953dff3e','root49-samus-audio-scan-h/scan-irq-components-dc.json':'7d2fbd007f7883b6018f0e1c92041ae2ea6db199781481fa762e619a14d8ab98','root49-megaman-g-full-review-df.json':'676f12af4a21437cfbfccc22c18db38b00265babe58ee0ab0d0cec7561d4c656','root49-h-route-root-review-dl.json':'5b64c4e044d51ea5f97e27ebb10082f3bd991c804c8203058e64c359774d9b4d','root49-h-three-root-review-dw.json':'ca408ec4e1f78037bbccbba58c54123740f72e9e3bfbe6172fdb0f6c4de11c35','root49-h-media-root-review-dz.json':'bf1c093e7c81f96e49f8f63db6cff5f144281f423e9eef14eb6ff9ca5d43bbfd','root49-megaman-h-profile-ds/review-du.json':'83f678f9658dffdb1a562619608fe03ad55adc611b20e79895b883c4797f5972','root49-global-allocation-bm.json':'94233edf6ac368b4689bafd937fc5f7be3231c1137dc3aa002e76125827a79d3','root49-mls-g-allocation-du.json':'92577ceb62fb692c62eddb5955eb30443e868983b09aa04c95cd0f9c454ef4cd','root49-megaman-bass-g-allocation-dq.json':'af5611e6909d63366b5cb954560a0cafd2a5bc70a629a89cc6ac393dcacb0b35','root49-lsr-g-allocation-dx.json':'24c65768b05b99a47d941f74a59c495c75b910e4d21d9c1630a900fd5116aa79'}
 for n,h in refs.items():assert sha(V/n)==h,n
 dl=read(V/'root49-h-route-root-review-dl.json');dw=read(V/'root49-h-three-root-review-dw.json');media=read(V/'root49-h-media-root-review-dz.json');actual=dl['accepted_actual_H']+dw['actual_H'];assert len(actual)==7
 old=V/'root49-goal-coverage-cu.json';assert sha(old)=='334d028adff42c96607c12fee16f937633c207c1300213fbd1d0d6508add5984';j=read(old)
 j['checkpoints']['H']=dict(path=str(cp.relative_to(R)),sha256=sha(cp),ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in c['builds']})
 assert len(j['roster'])==14 and sum(len(q['inventory_2_02'])for q in j['roster'])==66
 for q in j['roster']:
  key=q['character'],q['variant'];found=[a for a in actual if(a['identity'],a.get('variant',0))==key]
  q['current_H_independently_admitted_base_routes']=found
  q['current_H_binary_identity_prior_G_MMC5_links']=[a for a in dl['exact_ROM_links']if a['identity']==q['character']and q['variant']==0]
  q['current_G_independently_admitted_base_route_mappers']=['mmc3','mmc5']if key in[(0,0),(8,0)]else['mmc3']if key in[(1,0),(4,0)]else[]
  for a in found:
   m=read(R/a['manifest']);q['pinned_full_clear_candidates'].append(dict(revision='H',mapper='mmc3',manifest=a['manifest'],sha256=a['manifest_sha256'],frames=a['result']['frames'],recorded=False))
  q['retained_H_base_route_recordings']=[a for a in media['recordings']if a['character'].replace('megaman','Mega Man').lower()==q['name'].lower()]
  assert not any(q[n]for n in['base_moves_and_power_tiers_complete','all_specials_upgrades_complete','final_recording_complete','overall_complete'])
 j.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),working_revision='H',private_H_installed=True,H_installed=True,current_G_root_admitted_identity_count=4,current_G_root_admitted_identity_mapper_pairs=6,current_H_actual_MMC3_admitted_identity_count=7,current_H_actual_native_mapper_pairs=7,current_H_additional_literal_G_MMC5_links=2,retained_H_base_recording_count=4,new_root_review_references=refs,completion_scope='Installed H. Seven actual H/Easy/MMC3 base routes independently admitted; two explicit literal-binary prior G MMC5 links for Mario/Luigi. Four actual H base movies retain native186parts and93,975 decodedlosslessframes. All14/66, missing routes, actual acquisition/upgrade/SFX/behavior fidelity, original1-1 variants/everyenemy/item, further lag and complete final movies remain open.',goal_complete=False)
 index.write_text(json.dumps(j,indent=2)+'\n')
 attempts={};P=R/'build/roster-through-2-2'
 for name in['ground-dh','source-dj','pose-dn','stairs-dp','platform-dr','platform-dt','platform-dv','firebar-dy']:
  d=P/('root49-h-samus-'+name+'-2-v0-mmc3');m=read(d/'manifest.json');assert m['rom_sha256']==j['checkpoints']['H']['ROMs']['mmc3']and m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
  with(d/'trace.csv').open(newline='')as f:t=list(csv.DictReader(f))
  attempts[name]=dict(manifest=str((d/'manifest.json').relative_to(R)),sha256=sha(d/'manifest.json'),result=m.get('result'),last_trace=t[-1])
 qa=R/'docs/qa/easy-hard-legacy-v49.md';before=sha(qa);assert before=='0cc1abe37cfafe9fe22eae38cdfd0c36d7e5c0b47a3e2b406e3e59a781b74f71'
 qa.write_text(qa.read_text()+'''

Root continuation EB installs the H MMC3 Samus audio scan optimization. The
frozen H checkpoint is `roster-audit-v49-samus-audio-scan-h`; all458 build
sources,11 generated inputs and8 primary artifacts match installed main.
H changes75 MMC3 ROM bytes; MMC5 and baseline ROMs stay literal G. The earlier
private-H/pending-adoption paragraphs remain historical. Native validation
now includes560 complete AudioUpdate calls with258 actual child IRQs and
233,997 ordered writes exactly reproduced against full10,240-byte RAM and
register/bank/cycle endpoints. No native IRQ occurred inside the changed scan;
5,544 authored boundary injections separately cover the changed instructions.
The installed boot/swimming/power-up checks pass on both mappers. The isolated
median1,470-cycle saving remains a call-level measurement, not total FPS.

Independent root H reviews DL and DW admit seven actual Easy/MMC3 full base
routes: Mario, Luigi, Mega Man, Link, Bill, Lance and Sophia. All six stages
clear with zero deaths and actual control in2-3. All nine canonical input,
gameplay and physical hardware streams literally match their previously
reviewed G/F routes; all137,092 actual DMA snapshots are independently decoded.
Mario/Luigi MMC5 additionally have explicit literal full-ROM identity links to
their prior G executions. Those links are not fabricated fresh H sessions.
Every original source/support/power-tier limitation remains in force.

Four H base-route movies now exist for Mario, Luigi, Link and Mega Man. The
186 native ZMBV parts and continuous PCM recordings, verified lossless MKV
masters and playable MP4 copies are all retained. Root review DZ rehashes752
files and independently checks PCM identity. Automated scans decode all93,975
lossless frames; these runs have no HUD split, CHR-lag, sudden-motion, vertical
shift, black-flash or illegal-stomp flags. Selected contact sheets and menu
samples were inspected. This is not manual inspection of every frame or
every source waveform. Link321 and MegaMan2727 queued sound observations have
physical writes but lack the generic owner-bit evidence; native remapping,
priority and audible correctness remain follow-up work, not waived failures.
Mario/Luigi's observed events all have voice and physical-write evidence.

The export tool now accepts the caller's raised storage allowance instead of
rejecting any value above30GB. Real four-movie exports validate the80GB path.
The frame reviewer prefers a hash-verified lossless master and requires the
exact expected frame count. All prior captures, negatives and receipts remain.

Actual H Mega Man underground profiling covers46,191 calls with all nine
native prefix streams unchanged. Median main GameLoop cost is20,018 cycles;
its95th percentile is28,623. AudioUpdate runs in NMI, median7,125.5 cycles,
and drawing costs median6,754 when performed. MegaManWeapons95th percentile
is6,129 cycles. Parent/child function totals overlap and must not be added.
This identifies remaining music/enemy/drawing/weapon work; it is not a claim
that overall lag or WaterShield is solved. The initial host's all-scopes-main
assertion is retained; the corrected review explicitly separates NMI audio.

New ordinary H Samus play clears the first three stages. The successful first
underground lift crossing walks to the actual32/48px platform edge before
launching, avoiding the earlier overhead sibling. Castle lower-bar timing is
still in discovery. The unchanged old G physical input tape diverges in pose
at H frame1203 after the audio timing improvement; copying its physical frame
schedule is not a physics equivalence proof. G native producer capture remains
G,18,497 actual movement entries with literal G input/trace prefix. Retained
host/controller negatives include the frame-limit label, large-platform flag
being actor-slot rather than zero, and nearest-pose/platform/phase failures.
No production collision patch is inferred from these controller failures.

The full-scope index is `root49-goal-coverage-eb.json`. All14 identities and66
inventory entries, every special/upgrade/acquisition, original1-1 shortcut and
nonshortcut/everyenemy/item requests, remaining lag work and complete final
recordings stay required. The original73 suite failures and stock comparison
are not erased. Global allowance remains80GB under the user's explicit
lossless-retention/cap-raise answer, superseding the old30GB goal text. Current
specialist caps are MLS1GB, MegaMan/Bass1GB and LSR1.4GB, each100MB reserve.
''')
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used<80000000000
 result=dict(status='PROGRESS_INSTALLED_H_SEVEN_BASE_ROUTES_FOUR_REAL_RETAINED_MOVIES_AND_LAG_PROFILE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),prior_handoff_sha256=sha(V/'root-current49-progress-cv.json'),working_checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),shared_main_rehashed=dict(sources=458,generated=11,artifacts=8),references=refs,index=dict(path=str(index.relative_to(R)),sha256=sha(index)),QA=dict(path=str(qa.relative_to(R)),prior_sha256=before,sha256=sha(qa)),root_H_Samus_attempts=attempts,root_verified_native_handles_closed=['24844','92149','63194','20916','18595','23556','57667','43780','34176','79806','35853','3513','72165','61302','45938','14697','41791'],root_live_handle_at_record='28691 (EA lowerbar controller; poll same handle, do not restart on observation timeout)',specialists=dict(mario_luigi_scrooge_s2='Frozen G Scrooge water continuation, latestAH host66473. Mario/Luigi G proofs unchanged; full tier/special gap audit next after Scrooge fixed proof.',samus_contra_s2='Frozen G Bass five-stage/water final-bank progression, latestBA host84202; exact epoch joins replace manual guards. G MegaMan frozen/root-admitted; no Bass G full proof yet.',link_simon_ryu='Frozen G Simon water secondBlooper/Ryu2-1 progression; latestreported natives terminal, prospective controls pending;1.4GB cap. Link G/H proofs unchanged.'),budget=dict(global_observed=used,cap=80000000000,all_prior_negatives_lossless_retained=True,authority=refs['root49-global-allocation-bm.json'],MLS_cap=1000000000,MM_Bass_cap=1000000000,LSR_cap=1400000000,each_specialist_reserve=100000000),host_negatives='Preserved original scripts/receipts; corrected actual runtime epochs, frame-limit label and NMI audio classification in additive reports. No native rerun merely for an observation timeout.',next_required=['Poll live EA actual H Samus handle28691; continue real1-4/2-1/2-2 using actual hazards/support.','Finish ordinary current-build Pit/Rygar and remaining specialist routes; retain original revision identities and full independent replay proofs.','Complete all66 acquisition/special/alternate/upgrade effects and Easy/Hard/source/SFX checks, including specialized Link/MegaMan sound ownership/audible review.','Optimize measured remaining weapons/audio/enemy/drawing lag, including actual WaterShield/spread stress; preserve intended behavior.','Finish and inspect final real audio/video for every identity, retaining lossless; complete original1-1 shortcut/nonshortcut/enemy/item coverage.'],goal_status='active',previous_goal_turn_classification='progress (H installation/native validation and G MegaMan root admission); immediate user acknowledgment did not change task authority',current_goal_turn_classification='progress (seven actual current H proofs, four verified real recordings, export/reviewer fixes, native profile and actual new Samus traversal evidence)',blocked=False,accepted_release=False,goal_complete=False)
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(handoff_sha256=sha(out),index_sha256=sha(index),QA_sha256=sha(qa),workspace_bytes=used)),flush=True)
if __name__=='__main__':main()
