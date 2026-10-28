"""Read-only reconciliation of one successful44204 Bill drawing profile."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import math
import statistics
import sys

R = Path(__file__).resolve().parents[2]
B = R / 'build'
P = B / 'verification/bill-drawing-timing44204-ready-v1'
PARENT = B / 'verification/bill-landing-candidate326-hard-ready-v1'
OUT = B / 'bill_drawing_timing44204_review.json'
REPORT = R / 'docs/qa/bill-drawing-timing-2026-10-28.txt'
sys.path.insert(0, str(R / 'tools/audit'))
import bill_early_cache_cpu_v1 as H


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    assert not OUT.exists() and not REPORT.exists(), 'Preserve completed review'
    ready = read(P/'ready.json')
    assert sha(P/'ready.json') == '9019d34a8ee392fb4091d546243a18c8e7607d3878e9f1801312e0b9bea965e0'
    assert len(ready['bindings']) == 42
    for path, expected in ready['bindings'].items():assert sha(path) == expected, path
    result, launch = read(P/'result.json'), read(P/'launch.json')
    assert result['passed'] and result['ROM_sha256'] == '44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a'
    assert (result['frames'],result['polls'],result['completed_loops'],result['full_frames'],result['real_1_2_control_updates']) == (5992,5991,5058,5107,25)
    assert launch['exit_code'] == 0 and launch['changed_inputs'] == []
    assert launch['settings_before'] == launch['settings_after']
    matching = {}
    for name in ('inputs.csv','trace.csv','result.json','captures-index.jsonl','captures.nesppuv1'):
        digest = sha(P/name)
        assert digest == sha(PARENT/name), ('Original same-ROM successful run differs', name)
        matching[name] = digest
    summary = read(P/'bill-timing-summary.json')
    assert summary['timing_observation_complete'] and summary['open_interrupts'] == 0
    assert summary['first_frame'] == 3443 and summary['last_frame'] == summary['frames'] == 3503
    data = [{k:int(v) for k,v in q.items()} for q in csv.DictReader((P/'bill-timing.csv').open(newline=''))]
    assert len(data) == 61 and [q['endframe_count'] for q in data] == list(range(3443,3504))
    assert all(q['endframe_count'] == q['ppu_frame'] and q['ppu_line'] == 240 and q['ppu_dot'] == 0 for q in data)
    intervals = {b['cpu_cycle']-a['cpu_cycle'] for a,b in zip(data,data[1:])}
    assert intervals == {29780,29781}
    raw = (P/'bill-timing.csv').read_bytes()
    assert summary['csv_rows'] == 62 and len(raw)-summary['csv_bytes'] == raw.count(b'\r\n') == 62
    totals = {}
    for name, a in summary['aggregate'].items():
        t = {k:sum(q[name+'_'+k] for q in data) for k in ('calls','inclusive','exclusive','prewindow')}
        t['max'] = max(q[name+'_max'] for q in data)
        t['warmup'] = {k:a[k]-t[k] for k in ('calls','inclusive','exclusive')}
        assert all(v >= 0 for v in t['warmup'].values())
        assert t['exclusive'] <= t['inclusive']
        assert sum(a['callers'].values()) == sum(a['interrupt_depths'].values()) == a['calls']
        t['mean_inclusive_per_own_complete_call'] = t['inclusive']/t['calls']
        t['mean_exclusive_per_own_complete_call'] = t['exclusive']/t['calls']
        totals[name] = t
    main_costs = []
    for q in data:
        assert q['GameLoop_calls'] in (0,1,2)
        if q['GameLoop_calls']:main_costs.append(q['GameLoop_max'])
        if q['GameLoop_calls'] == 2:main_costs.append(q['GameLoop_inclusive']-q['GameLoop_max'])
    assert len(main_costs) == 40 and sum(main_costs) == totals['GameLoop']['inclusive'] == 1138820
    assert totals['PlayerGfxHandler']['calls'] == 39 and totals['PlayerGfxHandler']['inclusive'] == 65477
    assert totals['PlayerGfxHandler']['warmup'] == dict(calls=1,inclusive=1563,exclusive=1563)
    assert totals['DrawMetasprite']['calls'] == 75 and totals['DrawMetasprite']['inclusive'] == 49424
    assert totals['DrawMetasprite']['exclusive'] == 24523
    assert totals['DrawMetasprite']['warmup'] == dict(calls=3,inclusive=2243,exclusive=1121)
    assert [(q['name'],q['frame']) for q in summary['open_spans_censored']] == [('GameLoop',3503),('PlayerGfxHandler',3503)]
    fg = sum(t['exclusive'] for n,t in totals.items() if n != 'AudioUpdate')
    agg_fg = sum(t['exclusive'] for n,t in summary['aggregate'].items() if n != 'AudioUpdate')
    assert fg == 1136640 and agg_fg == 1154125
    assert fg-totals['GameLoop']['inclusive'] == -2180 and agg_fg-fg == 17485
    states = {k:dict(sorted(collections.Counter(q[k] for q in data).items())) for k in
              ('state','weapon','ordinary_shots','advanced_shots','other_shots','enemy_slots','timer','powerup','refill')}
    assert all(q['timer'] == q['powerup'] == q['refill'] == q['weapon'] == q['advanced_shots'] == q['other_shots'] == 0 for q in data)
    ranking = sorted([dict(name=n,**t) for n,t in totals.items() if n != 'AudioUpdate'],key=lambda q:-q['exclusive'])
    b = H.scoped_load(B/'bill_inert_pool.nes')
    start = H.address(b,'RosterGraphics::WalkDivide')-2
    finish = H.address(b,'RosterGraphics::WalkReady')
    at = H.location(b,'RosterGraphics::WalkDivide')-2
    code = list(b['raw'][at:at+finish-start])
    assert code == [0xa2,0,0xc9,7,0x90,6,0xe9,7,0xe8,0x4c,0x0a,0xa2,0x8a,0xc9,3,0x90,5,0xe9,3,0x4c,0x15,0xa2]
    math_costs = []
    for clock in range(256):
        q = H.setup(b,enemies=0)
        q.m.page(1,22)
        q.set('CurrentBank',22|128)
        c = H.NesMPU(memory=q.m,pc=start)
        c.a,c.x,c.y,c.p,c.sp = clock,0x89,0xab,0x20,0xfd
        while c.pc != finish:c.step()
        assert c.a == (clock//7)%3 == (clock%21)//7 and c.y == 0xab and c.sp == 0xfd
        math_costs.append(c.processorCycles)
    assert (min(math_costs),max(math_costs)) == (14,518)
    proposal = dict(source_owner='RosterGraphics standing/walking path, physical22:$A208..$A21D',
        compiled_bytes=code,old_arithmetic_typed_inputs=256,old_arithmetic_cycles=[14,518],
        identity_for_all256='floor(clock/7) mod3 == floor((clock mod21)/7)',
        possible_small_experiment='Replace the repeated divide7/mod3 with a bounded mod21/classification implementation; do not skip pose updates or original stores.',
        native_call_input_RgClock_or_pose_logged=False,measured_native_saving=None,
        proof_needs='Fresh assembled net whole PlayerGfx/RosterGraphics AXYP/SP/application/OAM/CHR/bank comparisons for all256 clocks, incoming flags, both Bill/Lance variants/modes and other reachable families; retain returned X/flags unless whole genuine caller proves overwrite. Check real footprint and cold-path regressions. No LUT/free-space or universal improvement assumed.')
    artifacts = {str(p):sha(p) for p in [P/'ready.json',P/'launch.json',P/'result.json',P/'profile-config.json',
        P/'prepare-controls.json',P/'bill-timing.csv',P/'bill-timing-summary.json',PARENT/'ready.json',
        B/'bill_inert_pool.nes',(B/'bill_inert_pool.nes').with_suffix('.dbg'),Path(__file__),
        R/'src/roster.s',R/'src/game.s',R/'src/player.s',R/'src/metasprite_engine.s',
        B/'bill_early_cache_timing_full.lua',Path(H.__file__)]}
    proof = dict(passed_read_only_arithmetic=True,native_route_pass=True,ROM_sha256=result['ROM_sha256'],
        native_counts=dict(wall=5992,Main=5058,DMAs=result['completed_DMAS'],PPU=5107,control12=25),
        unchanged_binding_count=42,same_ROM_successful_parent_files_byte_exact=matching,
        capture_decodes=0,new_images=0,timing_frames=[3443,3503],actual_data_rows=61,
        table_totals=totals,foreground_exclusive_ranking=ranking,
        measured_Main=dict(calls=40,total=sum(main_costs),mean=statistics.mean(main_costs),
            median=statistics.median(main_costs),p95_nearest_rank=sorted(main_costs)[math.ceil(.95*len(main_costs))-1],
            maximum=max(main_costs),Main_CPU_alone_above29781=sum(v>29781 for v in main_costs)),
        boundary=dict(first_Main_prewindow=1,open_spans_censored=summary['open_spans_censored'],open_interrupts=0,
            completed_table_foreground_exclusives=fg,closed_Main_inclusive=1138820,difference=-2180,
            aggregate_foreground_exclusives=agg_fg,warmup_foreground_exclusives=17485,
            rule='Different completion cohorts. Do not divide all descendants by40 or sum nested inclusive totals. Open lastMain/Gfx and warmup orphan/descendant accounting prevent exact reallocation to one closedMain/DrawAll cohort without serial IDs.'),
        ISR_DMA={k:sum(q[k] for q in data) for k in ('nmi_closed','nmi_elapsed','irq_closed','irq_elapsed','dmas','lag_counter_delta')},
        state_samples=states,new_DrawMetasprite_closed_child_CPU=49424-24523,
        actual_DrawMetasprite_aggregate_callsite_counts=summary['aggregate']['DrawMetasprite']['callers'],
        source_proposal=proposal,artifact_hashes=artifacts,
        limits='44204 historical ROM only; no canonical change/native launch. Selected window differs from prior3263500..3560; prior Main313583/DrawAll130852 residuals are not matched baselines. Source arithmetic lead is not a new implementation or native saving. No per-call EnemyID/RgClock/pose and no FPS claim; only endFrame sample workload. NMI gross includes nestedIRQ; AudioCPU excludes interrupts. Inherited summary prose3560 is stale, actual fields3443..3503 govern.')
    OUT.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    REPORT.write_text(f'''Bill44204 drawing timing, 2026-10-28

Actual strict native route PASS5992wall/5058Main/3878DMAs/5107wholePPU/25controlled1-2. All42bindings/settings unchanged. Inputs, complete trace, result, capture index and lossless container are byte-exact the prior same-ROM success by whole-file hashes. No capture was decoded or new image extracted. This is44204 historical evidence, independent of any later HUD/product adoption.

Window3443..3503 contains61actualPPU rows, x1888..1938. EndFrame samples:41air/20ground, ordinary shots4/3/2 on47/12/2 rows, enemy slots2/1/3 on18/10/33 rows; timer/powerup/refill/selectedspecial/advanced/other shots allzero. These are sampled counts, not per-call poses or EnemyIDs.40completed Main calls total1,138,820 foregroundCPU: mean28,470.5, median29,607, nearest-rankp9536,956, max38,803;18 Main-alone durations exceed29,781cycles. This excludes IRQ/NMI from each function and is not FPS, a matched-work gain or proof that every long Main misses display.

New PlayerGfxHandler:39table completions/65,477cycles (mean1,678.897/call,max1,994); one extra warmup call1,563cycles, and final PlayerGfxHandler is censored inside final openMain at3503. It now exposes a real cost formerly inside directMain, but adding it to Main's248,143exclusive and comparing with old326's313,583 would mix cohorts and different workloads.

New wholeDrawMetasprite:75table completions/49,424inclusive/24,523exclusive (659.0/327.0 per owncall). The24,901difference is measured descendantCPU in those completed calls, already counted in their inclusive total. Three extra warmup calls2,243inclusive/1,121exclusive are outside the table. InnerMetaspriteRenderLoop separately has220table completions/59,673cycles across many emitters, so its total must not be treated as exactly the child set of the75wholeDrawMetasprite calls. Aggregate DrawMetasprite caller counts are9/46world-order calls and23player calls; these include warmup, and no per-call object/pose was recorded.

DrawAll's own completed22calls total205,519inclusive/93,577exclusive (9,341.8/4,253.5 per owncall). WholeDrawMetasprite setup explains a portion of its old inner-loop-only residue; no exact cross-cohort reallocation/old-window speed delta is claimed. Current table foreground exclusive ranking: directMain248,143; EnemyCore99,813; DrawAll93,577; PlayerCtrl82,326; RosterWeapons79,031; BulletBlocks70,949; PlayerGfx65,477; innerRender59,673; background collision54,615; bullet-enemy44,892. DirectMain remains the largest unprobed owner.

Accounting: first closedMain began beforewindow; finalMain andPlayerGfx remain open. Alltable foreground exclusives sum1,136,640 versus1,138,820closedMaininclusive (difference-2,180). Including warmup adds17,485exclusive to1,154,125, now15,305aboveclosedMain. These are completion buckets/censored descendants, not missing CPU or additive per-frame integrals. NMI61gross288,819 includes nestedIRQ61/7,320; do NOTadd these ISR totals. Audio61complete calls252,738CPU are already within NMI elapsed and exclude IRQ.22DMAs and39skip-counter increments are separate observations.

ONE finite source lead: RosterGraphics physical22:A208..A21D repeatedly computes floor(RgClock/7)mod3 for walking. Existing compiled arithmetic measured14..518cycles over all256typed inputs; floor((clock mod21)/7) is algebraically identical for all256. A small source-faithful mod21/classification experiment could remove repeated subtraction without pose/event/store omissions. Actual per-call RgClock/pose were not logged, so no window/call saving is claimed. Need real assembly/footprint and fullcaller AXYP/SP/state/OAM/CHR/bank/foreign controls, especially quotientX/flags liveness and any short-path regression, before any product change. This does not resolve the6k/directMain residual or establish60Hz.

Exact receipt: {OUT}
SHA256 {sha(OUT)}
Only owned new reviewer: tools/audit/bill_drawing_timing44204_review_v1.py (hash in receipt). This report plus the compact receipt may be published; raw/ROM/container/settings stay external existing inputs. No source/candidate/canonical edits or native launch.
''',newline='\n')
    print(json.dumps(dict(receipt=str(OUT),receipt_sha256=sha(OUT),report=str(REPORT),
        report_sha256=sha(REPORT),reviewer_sha256=sha(Path(__file__)),native_pass=True,new_images=0)))


if __name__ == '__main__':main()
