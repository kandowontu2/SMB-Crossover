"""Freeze strict menu-event replay failure and compare every remaining log."""
from pathlib import Path
from itertools import zip_longest
import csv,hashlib,json

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'mm-proto-postdma-native-ready-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=P/'replay-negative-v1';out.mkdir(exist_ok=False)
    route=P/'native/megaman-easy';direct=P/'native/megaman-easy-direct'
    assert json.loads((P/'exit.json').read_text())['exit']==1
    assert not(P/'native/proto-easy').exists()and not(direct/'proof.json').exists()
    assert 'AssertionError: events.csv'in(P/'native/megaman-easy-replay-host.log').read_text()
    for q in[route,direct]:assert 'Mesen exit: 0'in(q/'host.log').read_text()
    first=json.loads((route/'result.json').read_text());second=json.loads((direct/'result.json').read_text())
    assert first==second and first['cleared']and first['deaths']==0 and first['frames']==5175
    csv_comparisons={}
    names=['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv','completed-loop-motion.csv','chr-commit.csv']
    for name in names:
        x,y=(route/name).read_bytes(),(direct/name).read_bytes()
        csv_comparisons[name]=dict(byte_exact=x==y,discovery_sha256=sha(route/name),replay_sha256=sha(direct/name),discovery_bytes=len(x),replay_bytes=len(y))
        assert(x==y)==(name!='events.csv'),name
    x,y=[list(csv.DictReader((q/'events.csv').open()))for q in[route,direct]]
    missing=x[:3]
    assert x[3:]==y and [(int(r['frame']),r['event'],int(r['value']))for r in missing]==[(204,'sfx-0104',1),(205,'sfx-0104',1),(205,'sfx-0104',1)]
    stage=first['stage_entries']['0-0'];assert stage==371
    suffix_x=[r for r in x if int(r['frame'])>=stage];suffix_y=[r for r in y if int(r['frame'])>=stage]
    assert suffix_x==suffix_y
    jsonl={}
    for name in['shot-events.jsonl','shot-epochs.jsonl','shot-guards.jsonl']:
        count=0
        with(route/name).open()as left,(direct/name).open()as right:
            for a,b in zip_longest(left,right):
                assert a is not None and b is not None and json.loads(a)==json.loads(b),(name,count)
                count+=1
        jsonl[name]=dict(ordered_semantically_exact=True,rows=count,discovery_sha256=sha(route/name),replay_sha256=sha(direct/name))
    json_checks={}
    for name in['chr-audit-summary.json','chr-commit.json','completed-loop-motion.json','stomp-summary.json','mode-readback.json','shot-observer.json','result.json']:
        assert json.loads((route/name).read_text())==json.loads((direct/name).read_text()),name
        json_checks[name]=dict(semantically_exact=True,discovery_sha256=sha(route/name),replay_sha256=sha(direct/name))
    observer=json.loads((route/'shot-observer.json').read_text());assert observer['passed']and observer['DMAs']==3390 and observer['publications']==2851
    index=list(csv.DictReader((direct/'direct-frame-index.csv').open()))
    assert len(index)==4975 and[int(r['frame'])for r in index]==list(range(200,5175))
    assert[int(r['ppuFrame'])for r in index]==list(range(200,5175))
    # Verify the retained PNG hashes; RGB/raw/gzip equality had already passed
    # in the pinned capture control flow before its later events.csv assertion.
    for row in index:assert sha(direct/'frames'/f"{int(row['frame']):06d}.png")==row['PNG_sha256']
    source=(route/'harness.lua').read_text()
    assert 'selectionDone=true;return{a=true}'in source
    assert 'if done or not selectionDone or v==0 then return end'in source
    assert 'if input then' in source and "if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then selectionDone=true end"in source
    report='''STRICT REPLAY FAILURE RETAINED -- TWO SUCCESSFUL NATIVE EXECUTIONS
Exact b0c152fa. MegaEasy discovery and its fixed-input direct replay both
complete1-1 atframe5175 with0deaths. The frozen capture checker still FAILS
events.csv; noProto or retry ran. This packet does NOT change that criterion,
delete event rows, write a passing direct/proof.json or accept the candidate.

Literal difference: discovery contains three queue-write log rows at204/205
(sfx-0104,value1), before stage entry371; replay omits these log observations.
Every later event row is exact in order/value. The active-gameplay suffix
frame>=371 is exactly identical offline. The unlogged replay menu queue
values themselves are not invented or inferred as captured observations.

Cause in frozen runner.py:70, menu() sets local selectionDone=true when it
returns the confirmA controller input. runner.py:80 replaces the old frame
guard with 'not selectionDone' in the SFX logger. Discovery calls menu();
fixed replay uses its recorded-input branch and never calls that function.
runner.py:79 adds a second selectionDone initializer at actual engine8;
thus replay's logger starts at371, while discovery's starts at204.
Actual generated harness.lua bindings are:120(menu flag),126..137(fixed
input branch),140(logger gate),146(actual active-game initializer).
These are observer-local values, not NES RAM writes; both input streams
and CPU-cycle/game traces are byte-exact. No new guard or logger fix is made.

All10 other original CSV files are byte-exact. Allthree ordered JSONL streams
and seven JSON result/guard summaries compare semantically exact offline,
including actual live slot/age, every source/publication/physical OAM image,
NMI/IRQ/bank/5SMC/stack evidence. Both observer summaries pass3390DMAs,
2851publications,3536NMI+IRQ checks; these remain finite candidate-only runs.

The direct capture retained4975frames200..5174, full rawARGB and lossless
gzip. Every indexed PNG hash is freshly verified. The pinned capture reached
the later event comparison only AFTER its actualRGB/PNG/raw/gzip checks
passed; that preceding integrity statement follows the retained source/control
flow and does not turn the failed strict replay into a pass. Full original
capture outputs, both negative attempts, allfalse receipts remain untouched.

ROOT separately reports seven one-frame vertical menu wraps despite its
programmed guards; overall visual acceptance is false. This packet does not
qualify or repair the menu, body pixels, physical shot fairness, Proto or
matched performance. The source five-construction bound remains distinct
from actual publication/visibility. No adoption/installation/native retry.
'''
    (out/'report.txt').write_text(report)
    catalog={str(p):sha(p)for p in P.rglob('*')if p.is_file()and not p.is_relative_to(out)}
    catalog[str(out/'report.txt')]=sha(out/'report.txt');catalog[str(Path(__file__))]=sha(__file__)
    (out/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    result=dict(passed=False,strict_replay_failure_preserved=True,overall_visual_acceptance=False,ROM_sha256='b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99',launches=2,Proto_runs=0,retry_runs=0,worker_released=True,native_discovery_and_replay_engine_results=first,strict_failure='events.csv',menu_SFX_log_rows_present_only_in_discovery=missing,replay_values_unlogged=True,active_gameplay_suffix_frame=stage,active_gameplay_event_rows=len(suffix_x),active_gameplay_event_suffix_exact=True,remaining_CSV=csv_comparisons,ordered_JSONL=jsonl,JSON=json_checks,observer=observer,direct_frames=4975,all_frame_ids_exact=True,all_indexed_PNG_hashes_freshly_verified=True,prior_capture_RGB_raw_gzip_checks_passed_before_logged_assertion=True,source_lines=dict(runner=str(P/'runner.py'),menu_local_flag=70,logger_gate_rewrite=80,engine8_flag_initializer=79,generated_harness=str(route/'harness.lua'),actual_menu_flag=120,actual_fixed_branch_start=126,actual_logger_gate=140,actual_engine8_initializer=146),no_passing_direct_proof_written=True,native_readiness_sha256=sha(P/'readiness.json'),grant_sha256=sha(P/'ROOT-grant.json'),catalog_files=len(catalog),catalog_sha256=sha(out/'catalog.json'),report_sha256=sha(out/'report.txt'),checker_sha256=sha(__file__),limits='Strictfalse and global menuvisualfalse retained. Offline suffix equality does not replace full replay or prove unlogged menuSFX, wholebodyRGB/physicalshotfairness/Proto/matchednoharm. No game/source/observer/native changes.')
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(strict_replay_passed=False,active_gameplay_suffix_exact=True,exact_other_CSV=10,exact_ordered_JSONL=3,exact_JSON=7,direct_frames=4975,catalog_files=len(catalog),proof_sha256=sha(out/'proof.json')),indent=2))


if __name__=='__main__':main()
