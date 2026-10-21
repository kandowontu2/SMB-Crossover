"""Validate passive timing domains and rank the actual measured CPU work."""
from pathlib import Path
import collections,csv,hashlib,json,statistics
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-exclusive-profile-bj';P=R/'build/roster-through-2-2/root49-f-samus-exclusive-bj-2-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def summary(a):
    x=sorted(z['exclusive_cycles']for z in a)
    return dict(calls=len(a),exclusive_median=statistics.median(x),exclusive_p95=x[int((len(x)-1)*.95)],exclusive_max=x[-1],exclusive_total=sum(x),
      elapsed_total=sum(z['cycles']for z in a),actual_child_interrupt_cycles=sum(z['interrupted_cycles']for z in a),return_contexts=dict(collections.Counter(str(z['entry_ISR_depth'])for z in a)),
      exact_RAM_continuation_returns=sum(z['return_bank']==-1 for z in a))
def main():
    out=V/'root49-samus-f-exclusive-profile-review-bl.json';assert not out.exists()
    pre=json.loads((H/'preparation.json').read_text());native=json.loads((H/'native-result.json').read_text())
    assert sha(H/'preparation.json')==native['preparation_sha256']and sha(H/'native.log')==native['native_log_sha256']
    assert sha(P/'manifest.json')==native['manifest_sha256']
    for n,h in pre['dependencies'].items():assert sha(R/n)==h,n
    assert sha(H/'policy.lua')==pre['policy_sha256']and sha(H/'profile-actual-ram-return.lua')==pre['private_helper_sha256']
    m=json.loads((P/'manifest.json').read_text());assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
    assert m['result']['failure']=='frame limit'and m['result']['frames']==14850 and not m['verified_through_2_2']
    assert m['rom_sha256']==sha(P/'smb-crossover-mmc3.nes')=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
    a=rows(P/'trace.csv');parent=R/'build/roster-through-2-2/root49-f-samus-route-s-2-v0-mmc3';assert a==rows(parent/'trace.csv')[:14850]
    assert rows(P/'inputs.csv')==rows(parent/'inputs.csv')[:14849]
    data=[json.loads(s)for s in(P/'ordinary-profile.jsonl').read_text().splitlines()];groups=collections.defaultdict(list)
    for z in data:
        assert 12500<=z['frame']<14800 and z['return_frame']<=14830
        assert z['exclusive_cycles']==z['cycles']-z['interrupted_cycles']and 0<z['exclusive_cycles']<=z['cycles']
        assert z['return_sp']==(z['entry_sp']+2)%256 and z['world']==0 and z['level']==1
        assert z['entry_ISR_depth']in [0,1]
        if z['nmi']==z['irq']==0:assert z['interrupted_cycles']==0
        assert z['return_bank']>=0 or z['return_bank']==-1
        groups[z['name']].append(z)
    summaries={n:summary(z)for n,z in groups.items()};ranked=sorted(summaries,key=lambda n:-summaries[n]['exclusive_total'])
    assert len(groups['GameLoop'])==1529 and len(groups['AudioUpdate'])==1750
    assert summaries['GameLoop']['actual_child_interrupt_cycles']>0 and summaries['AudioUpdate']['actual_child_interrupt_cycles']>0
    r=dict(status='PASS_ACTUAL_F_SAMUS_ORDINARY_EXCLUSIVE_CPU_PROFILE',script_sha256=sha(__file__),native_result_sha256=sha(H/'native-result.json'),preparation_sha256=sha(H/'preparation.json'),
      superseded_review_sha256=sha(V/'root49-samus-f-exclusive-profile-review-bk.json'),reviewer_correction='BL directly asserts SP/world/level and actual ISR context; original BK ternary-precedence reviewer remains retained. Runtime call/return guards and all measured data unchanged.',
      manifest_sha256=sha(P/'manifest.json'),profile_sha256=sha(P/'ordinary-profile.jsonl'),physical_trace_and_input_prefix_exact_rows=[14850,14849],sample_frame_range=[12500,14800],
      measured_calls=len(data),summaries=summaries,ranked_by_inclusive_subtree_work=ranked,actual_F_RAM_farcall_continuation=pre['ram_return'],method=pre['exclusive_method'],
      unobserved_scope_names=[n for n in pre['hooks']if n not in groups and n not in ['NMI','IRQ','NMI_END','IRQ_END']],
      limitations=['Each function total includes its nested foreground callees; do not add parent and child totals or interpret ranking as disjoint percentages.',
        'Window is one ordinary Easy MMC3 underground scene; different weapons, enemies, mappers and water require their own samples.',
        'Native1 at14850 is the deliberately bounded frame-limit endpoint, not a profile failure or full route.',
        'BE CLI rejection and BF ROM-only caller assumption remain retained negatives. BH established exact RAM continuation before this fully interrupt-subtracted sample.',
        'This measures current CPU cost; no new ROM optimization or all-lag-fixed claim follows.'],
      performance_optimization_complete=False,production_ROM_changed=False,goal_complete=False)
    out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],sha(out));print(json.dumps({n:summaries[n]for n in ranked[:8]}))
if __name__=='__main__':main()
