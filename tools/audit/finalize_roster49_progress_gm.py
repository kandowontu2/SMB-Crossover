"""Pin current source identity and scope two physical-event review findings."""
from pathlib import Path
import csv,datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
c=json.loads(cp.read_text())
for n,h in c['source_hashes'].items():assert sha(R/n)==h
for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
for b in c['builds']:
 for a in b['artifacts'].values():assert sha(R/a['path'])==a['sha256']
d=R/'build/roster-through-2-2/root49-h-samus-fixed-gj-2-v0-mmc3'
window={n:[z for z in csv.DictReader((d/n).open(newline=''))if 7955<=int(z['frame'])<=7961]for n in ['trace.csv','render.csv']}
render={int(z['frame']):z for z in window['render.csv']}
assert all(render[f]['dmaCount']=='0'and render[f]['lagNmi']=='1'for f in [7958,7959])
assert render[7957]['dmaCount']==render[7960]['dmaCount']=='1'
review=V/'root49-samus-h-root-review-gk.json';j=json.loads(review.read_text());unknown=j['hardware_event_review']['audio_events_needing_priority_or_audible_review'];assert len(unknown)==4240
add=V/'root49-samus-h-root-review-gk-addendum.json';assert not add.exists()
add.write_text(json.dumps(dict(status='PHYSICAL_REVIEW_QUALIFICATIONS_RETAINED',root_review_sha256=sha(review),source_458_generated11_primary8_main_rehashed=True,motion=dict(frames=[7958,7959],raw_position_delta=[[65,24],[-63,-24]],window=window,observation='Both flagged samples occur on lag/no-DMA frames between actual DMA7957 and7960. No OAM image commits at either flagged sample. Camera advances only2 then0, not65/-63. This does not establish a visible64px teleport. Exact temporary-position writer is not captured and remains unclassified; no source-perfect or pixel-movie claim.'),audio=dict(unconfirmed_queue_events=4240,first_two=unknown[:2],observation='Generic sound queue events lack audited voice ownership despite physical audio writes. This is not a measured silence or missing-SFX determination; waveform/source/cue priority review remains required.'),limits='All root GK flags stay in their original report. No flags are removed and no unresolved writer/SFX source claim is promoted.',goal_complete=False),indent=2)+'\n',encoding='utf-8')
sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
used=workspace_bytes(R);assert used<80000000000
prior=V/'root-current49-progress-gk.json';assert sha(prior)=='3b44e94dc47da2537e8d1b438b2b03144c87f886e7f8c78d2d17c3b26823467e'
p=json.loads(prior.read_text());p.update(status='PROGRESS_TWELVE_H_BASE_IDENTITIES_REHASHED_WITH_OPEN_SOURCE_AND_LAG_WORK',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_handoff_sha256=sha(prior),physical_review_addendum_sha256=sha(add),checkpoint_H_sha256=sha(cp),source_458_generated11_primary8_main_rehashed=True,workspace_bytes=used,root_native_handles=[],goal_complete=False)
out=V/'root-current49-progress-gm.json';assert not out.exists();out.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(progress_sha256=sha(out),addendum_sha256=sha(add),workspace_bytes=used)))
