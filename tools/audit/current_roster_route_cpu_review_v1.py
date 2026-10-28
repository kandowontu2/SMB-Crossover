"""Read only the35 tracker-selected route traces; no capture/native/product work."""
from pathlib import Path
import csv,gzip,hashlib,json,math,statistics,subprocess
ROOT=Path(__file__).resolve().parents[2]
TRACKER=ROOT/'docs/qa/current-roster-progress-2026-10-27.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
THRESHOLD=29781

def stats(rows):
 a=sorted(r['foregroundCycles']for r in rows)
 return dict(n=len(a),median=statistics.median(a)if a else None,p95=a[math.ceil(len(a)*.95)-1]if a else None,maximum=max(a)if a else None,recorded_foreground_over29781=sum(x>THRESHOLD for x in a))

def main():
 tracker_bytes=TRACKER.read_bytes();tracker=json.loads(tracker_bytes)
 wanted={v['native_result_sha256']:(r['identity'],mode,v)for r in tracker['rows']if r['identity']not in['twinbee','pentarou']for mode in['easy','hard']if(v:=r.get(mode,{})).get('native_result_sha256')}
 assert len(wanted)==35
 # Exactly one directory level, result.json only; no recursive workspace walk.
 candidates={}
 for d in(ROOT/'build/verification').iterdir():
  p=d/'result.json'
  if d.is_dir()and p.is_file():
   h=sha(p)
   if h in wanted:candidates.setdefault(h,[]).append(d)
 assert set(candidates)==set(wanted)
 name='tools/audit/current_roster_compact_11_v1.lua';historical={}
 for commit in subprocess.check_output(['git','log','-12','--format=%H','--',name],cwd=ROOT).decode().splitlines():
  data=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT);historical[hashlib.sha256(data).hexdigest()]=(commit,data.decode())
 required=["if activeLoop and kind=='NMI' then activeLoop.interrupt=activeLoop.interrupt+s['cpu.cycleCount']-q.start end",
  "if activeLoop and kind=='IRQ' and not nmiSaved then activeLoop.interrupt=activeLoop.interrupt+s['cpu.cycleCount']-q.start end",
  "hook(C.hooks.loop,function(s)check(activeLoop==nil,'No nested foreground GameLoop');activeLoop={sp=s['cpu.sp'],start=s['cpu.cycleCount'],interrupt=0}end)",
  "loops=loops+1;lastCycles=s['cpu.cycleCount']-a.start;lastInterrupt=a.interrupt;activeLoop=nil",
  'lastCycles,lastInterrupt,lastCycles-lastInterrupt']
 rows=[];bindings={str(TRACKER):hashlib.sha256(tracker_bytes).hexdigest(),str(Path(__file__)):sha(__file__)};versions={};histogram={}
 for h,(identity,mode,known)in wanted.items():
  d=sorted(candidates[h])[0];result=json.loads((d/'result.json').read_text());ready=json.loads((d/'ready.json').read_text());launch=json.loads((d/'launch.json').read_text())
  assert result['passed']and result['identity']==identity and result['ROM_sha256']==known['native_ROM_sha256']and result['actual_mode']==int(mode=='hard')
  assert not launch.get('changed_inputs')and launch.get('settings_before')==launch.get('settings_after')
  rb=ready['bindings'];module=[value for path,value in rb.items()if path.replace('\\','/').endswith('/'+name)]
  assert len(module)==1 and module[0]in historical
  commit,source=historical[module[0]];assert all(s in source for s in required),'Genuine historical counter/ISR formula changed'
  versions[module[0]]=dict(git_commit=commit,timing_fragments_sha256=hashlib.sha256('\n'.join(required).encode()).hexdigest(),exact_fragments_verified=True)
  t=d/'trace.csv';t=t if t.exists()else d/'trace.csv.gz';op=gzip.open if t.suffix=='.gz'else open
  with op(t,'rt',newline='')as f:raw=[{k:int(v)for k,v in r.items()}for r in csv.DictReader(f)]
  observed={};repeated=0
  for r in raw:
   assert r['foregroundCycles']==r['loopCycles']-r['interruptCycles']and r['foregroundCycles']>=0
   n=r['loops']
   if n==0:continue
   if n in observed:
    assert tuple(r[k]for k in['loopCycles','interruptCycles','foregroundCycles'])==tuple(observed[n][k]for k in['loopCycles','interruptCycles','foregroundCycles']);repeated+=1
   else:observed[n]=r
  assert max(observed)==result['completed_loops']
  def active(r):return r['world']==0 and r['level']==0 and r['engine']==8 and r['mode']==1 and r['task']==3 and r['yHigh']==1
  active_rows=[r for r in observed.values()if active(r)]
  # Do not silently label engine8 stationary refill/pause as ordinary motion.
  # These exact fields are not in the route CSV. Exclude the pickup zone and
  # a conservative64-observed-Main neighborhood of every power change.
  changed={n for n,r in observed.items()if n-1 in observed and r['power']!=observed[n-1]['power']}
  moving=[];walking=[]
  for n,r in observed.items():
   prev=observed.get(n-1);nxt=observed.get(n+1)
   if not(prev and nxt and active(prev)and active(r)and active(nxt)):continue
   if not(480<=r['x']<=3000 and 0<r['x']-prev['x']<=8 and prev['power']==r['power']==nxt['power']):continue
   if any(abs(n-c)<=64 for c in changed):continue
   moving.append(r)
   if prev['state']==r['state']==0:walking.append(r)
   if r['foregroundCycles']>THRESHOLD:histogram[str(r['x']//128*128)]=histogram.get(str(r['x']//128*128),0)+1
  top=lambda rs:[dict(r)for r in sorted(rs,key=lambda r:r['foregroundCycles'],reverse=True)[:3]]
  row=dict(identity=identity,mode=mode,ROM_sha256=result['ROM_sha256'],folder=str(d.relative_to(ROOT)),native_result_sha256=h,trace_sha256=sha(t),trace_rows=len(raw),sampled_completed_Main_IDs=len(observed),unobserved_completed_Main_IDs=result['completed_loops']-len(observed),duplicate_endframe_rows=repeated,all_completed_sample_stats=stats(list(observed.values())),active_engine8_stats=stats(active_rows),conservative_moving_stats=stats(moving),ground_moving_stats=stats(walking),top_moving_samples=top(moving),top_ground_moving_samples=top(walking),top_active_samples=top(active_rows),historical_producer_sha256=module[0])
  rows.append(row)
  for p in[t,d/'result.json',d/'ready.json',d/'launch.json']:bindings[str(p)]=sha(p)
 timing=ROOT/'build/verification/bill-enemy-timing9ea-ready-v1/bill-timing.csv'
 with timing.open(newline='')as f:detail=[{k:int(v)for k,v in r.items()}for r in csv.DictReader(f)]
 assert len(detail)==61 and all(r['timer']==r['powerup']==r['refill']==r['advanced_shots']==r['other_shots']==0 for r in detail)
 deltas=[b['cpu_cycle']-a['cpu_cycle']for a,b in zip(detail,detail[1:])];assert set(deltas)=={29780,29781}
 summary=ROOT/'build/verification/bill-enemy-timing9ea-ready-v1/bill-timing-summary.json';data=json.loads(summary.read_text())
 for p in[timing,summary,ROOT/'docs/qa/bill-enemy-native-timing-2026-10-27.txt',ROOT/'tools/audit/current_bill_passive_timing_v1.lua',ROOT/'src/game.s',ROOT/'src/object.s',ROOT/'src/tmnt_core.s',ROOT/'src/tmnt_equipment_draw.s',ROOT/'src/samus_weapons.s',ROOT/'src/roster_weapons.s']:bindings[str(p)]=sha(p)
 bill=dict(ROM_sha256='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e',window=[3500,3560],rows=61,all_timer_powerup_refill_zero=True,all_basic_shots_only=True,Main_completed_calls=sum(r['GameLoop_calls']for r in detail),Main_max_actual_CPU=max(r['GameLoop_max']for r in detail),Main_completed_CPU=sum(r['GameLoop_inclusive']for r in detail),enemy_completed_calls=sum(r['EnemiesAndLoopsCore_calls']for r in detail),enemy_inclusive_CPU=sum(r['EnemiesAndLoopsCore_inclusive']for r in detail),enemy_exclusive_CPU=sum(r['EnemiesAndLoopsCore_exclusive']for r in detail),parser_calls=sum(r['AreaParserTaskHandler_calls']for r in detail),parser_CPU=sum(r['AreaParserTaskHandler_inclusive']for r in detail),frame_cpu_delta_range=[min(deltas),max(deltas)],limits='Closed-completion buckets only; one open Main and one open EnemyCore at cutoff, warmup exists in aggregates, nested inclusive/exclusive must not be added. See existing finite report; no newly fabricated per-call actor IDs/resources.')
 proof=dict(passed=True,read_only=True,native_launched=False,tracker_sha256=hashlib.sha256(tracker_bytes).hexdigest(),tracker_route_rows=35,scope_selection='Initial35 identity whitelist; tracker advanced36 when ROOT finishedTwinBee during this audit. Newly completedTwinBee and pendingPentarou intentionally excluded; cardinality negative retained.',rows=rows,historical_timing_producers=versions,observed_NTSC_frame_cpu_upper_threshold=THRESHOLD,frame_budget_basis='Actual pinned native61-row Bill window has60 same-PPU-phase CPU differences29780/29781, mean29780.5. Use conservative integer29781.',moving_overbudget_histogram128_worldpixels=histogram,bill_independently_timed_window=bill,
  definitions=dict(dedup='First endFrame observation of each monotonically completed Main ID; repeated last duration never counted again. Missing earlier IDs when multipleMain complete before a sampled endFrame remain unobserved.',duration='Route foregroundCycles = start-to-pre-RTS elapsed minus nonnested IRQ/NMI hook body time. It retains hardware entry7+RTI6 for each interrupt, and excludes final Main RTS6. It is a recorded foreground proxy, not exact pure Main CPU. Bill passive timing includes complete interrupt entry/exit and Main return; its39494 maximum is actual disjoint foreground CPU.',normal='Conservative moving sample: adjacent observed IDs both sides, active world0/level0/engine8/task3/OperMode1/Ypage1; positive worldX advance1..8, x480..3000, same power, exclude64-Main neighborhood of power changes. Ground subset also has previous/current Player_State0.',unlogged='Route CSV mode is OperMode, NOT difficulty: actual difficulty taken from native result. TimerControl/InvRefill/pause/shot pool/enemy IDs/actual input consumed atMain return are not in route CSV. EndFrame position may reflect work from an in-progress nextMain. Moving subset reduces known special phases but cannot certify every remaining sample free of unlogged states.',interpretation='No FPS, cadence, all-frame performance or current-ROM retag from wall/Main counts or threshold counts. Sub-frame Main may still miss publication after ISR/world work. Different identities/modes/ROMs/controllers are observational, not a matched performance comparison.'),bindings=bindings)
 out=ROOT/'build/current_roster_route_cpu_review_v1.json';assert not out.exists();put(out,proof)
 report=ROOT/'docs/qa/current-roster-route-cpu-2026-10-28.txt';assert not report.exists()
 lines=['Existing native full-route CPU audit, 2026-10-28','',f'35 tracker-selected actual result hashes; trackerSHA {proof["tracker_sha256"]}. Read-only: no native, game/default/settings edits, source/runtime copies, capture decoding or frame files. Only bounded one-level build/verification/result.json lookup plus its35 known trace.csv(.gz) files. Historical results retain exact ROM/mode; no fresh current326942 performance claim.','',
 'Duration and scope','Deduplicated completed Main IDs, keeping first endFrame observation. Repeated last-cycle rows are not new work; unobserved IDs when several calls complete between endFrames stay missing. The route foreground field subtracts ISR bodies but retains13-cycle hardware entry/RTI boundary per interrupt and omits final Main RTS6. It is not exact pure Main CPU. The independent Bill profiler correctly includes those boundaries. The actual same-phase native Bill timestamps give29780/29781 cycles per frame; threshold29781 is conservative. No FPS or missed-NMI count follows from these sampled durations.','',
 'Ordinary-motion candidate filter: active1-1 engine8/task3/OperMode1/Ypage1; consecutive observed IDs on both sides, positiveX advance1..8, x480..3000, unchanged power, outside64 Main IDs of observed power changes. Grounded subset requires previous/current state0. CSV lacks TimerControl/refill/pause/actual shot/actor state and may contain in-flight nextMain coordinates, so those are explicit limits, not silently filled zeroes. Difficulty comes from native actual_mode; CSV mode is OperMode. Guest transformations use engine9 and are separated; engine8 refill cannot be perfectly classified without extra fields.','',
 'Identity  mode ROM       movingN median p95   maximum >29781  groundN groundP95 groundMax']
 for r in rows:
  s=r['conservative_moving_stats'];g=r['ground_moving_stats'];lines.append(f"{r['identity']:12} {r['mode']:4} {r['ROM_sha256'][:8]} {s['n']:5} {str(s['median']):>7} {str(s['p95']):>6} {str(s['maximum']):>7} {s['recorded_foreground_over29781']:6} {g['n']:7} {str(g['p95']):>9} {str(g['maximum']):>9}")
 lines+=['','Concrete observations / source leads',
  'Contra remains a broad ordinary-gameplay cost problem after the adopted early-cache optimization. BillHard9ea and LanceHard4a have moving medians near28–29k and p95 above34k. Exact witnesses/grounded samples are in the JSON; do not equate retained A/B mask with an actual weapon birth. The independent same9ea Bill61-frame window logs timer/powerup/refill0, only3–4 basic shots,1–3 active enemy slots, and max complete Main39494 true CPU cycles. This exceeds the whole frame budget by9713 cycles before any unrelated outside-Main work. That concrete ordinary case rules out explaining all apparent lag as intentional movement freezes.',
  'Existing Bill child attribution makes a shared engine lead actionable: strict window EnemyCore234 completions/159728 inclusive CPU,143207 exclusive after terrain/contact children. Parser10 calls18832 CPU (max4467) is bursty but smaller. GameCore visits all6 slots; inactive paths enter ProcLoopCommand, active RunNormalEnemies includes graphics, bbox, terrain, pair/player collision and movement. Smallest next passive refinement is existing static Bill observer + EnemyGraphicsEngine, EnemyMovementSubs and ProcLoopCommand spans, rather than inventing a family/audio rewrite. The aggregate EnemyCore remainder is not all movement or Goomba work, and source does not prove each actual actor ID.',
  'SamusHard8487 has substantial ordinary-motion spikes despite lower median. SamusWeapons already gates empty/noB cache work; live beams still bridge into native block/enemy collision, and bombs add block/enemy/boost work. Trace has no beam/bomb/upgrade state, so projectile or wave blame is not proven. Shared world/enemy/drawing plus that live projectile path are concrete spans to separate using the existing bounded static pattern if ROOT later measures.',
  'All four turtle routes have lower moving p95, with rare large32–35k recorded spikes. Their normal sub-frame Main does not prove smooth publication: NMI/audio/CHR and scheduling consume additional frame budget. TnDrawEquipment already has guarded empty scans/current native actor loops; do not re-propose that optimization from old held code. Source-ground Down+attack intentionally selects zero horizontal velocity, but these traces lack TnAttack and cannot classify every pause as that mechanic. No new turtle music/renderer regression claim follows.',
  'Many identities have their highest motion costs near world1870–1970; the128px histogram is retained. This cross-family location pattern plus actual Bill enemy profiling supports shared enemy/background/render work as a priority, but the traces do not bind enemy IDs or prove the common cause. Sophia and Bass also show large ordinary costs and deserve attention; different modes/controllers/ROMs prevent controlled ranking claims.',
  'Native successful route scope and selected visual review are inherited unchanged. No product optimization or new native packet was prepared. Existing Bill censored Main/EnemyCore and warmup limits remain: do not add nested inclusive totals, assign completion-bucket costs to every PPU frame, or divide these totals into FPS.','',
  f'Compact evidence: build/current_roster_route_cpu_review_v1.json SHA {sha(out)}.',f'Owned tool: tools/audit/current_roster_route_cpu_review_v1.py SHA {sha(__file__)}.']
 report.write_text('\n'.join(lines)+'\n',newline='\n');print(out,sha(out));print(report,sha(report))
 for r in rows:
  if r['identity']in['samus','bill','lance','leonardo','raphael','michelangelo','donatello','sophia','bass']:print(r['identity'],r['conservative_moving_stats'],r['ground_moving_stats'])
if __name__=='__main__':main()
