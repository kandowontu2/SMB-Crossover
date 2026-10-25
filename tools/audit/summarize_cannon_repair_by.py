from pathlib import Path
import collections,csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/cannon-repair-by';assert not O.exists();O.mkdir()
sys.path.insert(0,str(R/'tools/playthroughs'));import roster_review
def rows(p):
 with p.open(newline='')as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def labels(p):return {z.split()[2][1:]:int(z.split()[1],16)for z in p.read_text().splitlines()if z.startswith('al ')}
source=R/'build/roster-through-2-2/cannon-bv-bill-3-v0-mmc3'
results=[]
for tag,mapper in [('cannon-bx-before','mmc3'),('cannon-bx-after','mmc3'),('cannon-bx-after-mmc5','mmc5')]:
 P=R/'build/roster-through-2-2'/f'{tag}-3-v0-{mapper}'
 m=json.loads((P/'manifest.json').read_text());L=labels(P/f'smb-crossover-{mapper}.lbl')
 timers=rows(P/'cannon-timer-writes.csv')
 dry=[z for z in timers if int(z['area'])!=0]
 wrongly_cleared=[z for z in dry if int(z['old'])>0 and int(z['new'])==0 and L['ProcessWhirlpools']<=int(z['pc'])<L['WhirlpoolActivate']]
 births=[z for z in dry if int(z['new'])==14 and int(z['slot'])==0]
 frames=[int(z['frame'])for z in births]
 countdown=[z for z in dry if int(z['old'])==int(z['new'])+1]
 actors=[z for z in rows(P/'actors.csv')if int(z['id'])==0x33 and 0<int(z['flag'])<128 and int(z['state'])==1]
 byframe=collections.defaultdict(list)
 for z in actors:byframe[int(z['frame'])].append(z)
 if tag!='cannon-bx-before':assert not wrongly_cleared and len(countdown)>=14
 else:
  assert wrongly_cleared
  assert(P/'trace.csv').read_bytes()==b''.join((source/'trace.csv').read_bytes().splitlines(keepends=True)[:2201])
 assert(P/'inputs.csv').read_bytes()==b''.join((source/'inputs.csv').read_bytes().splitlines(keepends=True)[:2200])
 review=None;lossless=None
 if(P/'playthrough-lossless.mkv').exists():
  proof=P/'playthrough-lossless.verification/report.json';lossless=json.loads(proof.read_text());assert lossless['result']=='passed-exact-rgb-and-pcm'
  assert m['recording_metadata']['passed']and m['recording_metadata']['video_frames']==2199
  review=roster_review.review(P)
 out=dict(tag=tag,mapper=mapper,ROM_sha256=m['rom_sha256'],input_prefix_literal=True,
  old_trace_literal_to_discovery=tag=='cannon-bx-before',wrong_dry_cooldown_clears=len(wrongly_cleared),
  wrong_clear_first=wrongly_cleared[:2],cannon0_attempts=len(births),attempt_frames=frames,
  min_attempt_interval=min((b-a for a,b in zip(frames,frames[1:])),default=None),
  native_countdown_writes=len(countdown),live_cannon_bill_rows=len(actors),max_simultaneous_native_cannon_bills=max(map(len,byframe.values()),default=0),
  result=m['result'],native_lossless_AV=bool(lossless),delivery_frame_count=m.get('recording_metadata',{}).get('video_frames'),
  review_flags={k:len(review[k])for k in('motion_candidates','split_timing_candidates','video_vertical_shift_candidates','video_background_flash_candidates')}if review else None,
  classification='Bounded explicit-cheat diagnosis, level5-2 and invincibility selected with ordinary controls; not a final route. Multiple spaced native Bills remain allowed.')
 results.append(out)
for z in results:print(z['tag'],z['wrong_dry_cooldown_clears'],z['cannon0_attempts'],z['min_attempt_interval'],z['native_countdown_writes'],flush=True)
report=dict(passed=True,runs=results,goal_complete=False)
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
