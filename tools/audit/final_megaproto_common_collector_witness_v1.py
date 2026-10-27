"""Ordered actual case witnesses replace only the reset emptyChecked flag check."""
from pathlib import Path
import json

def ordered_case_witnesses(out,cfg,summary):
    return interpret_events([json.loads(s)for s in(Path(out)/'events.jsonl').open()],cfg,summary)

def interpret_events(events,cfg,summary):
    assert len(cfg['cases'])==len(summary['cases'])==14
    assert[q['q']['name']for q in summary['cases']]==[q['name']for q in cfg['cases']]
    records=[]
    for case,c in enumerate(cfg['cases'],1):
        es=[q for q in events if q['case']==case]
        phases=[q for q in es if q['kind']=='gallery-phase'and q['phase']!='next']
        assert[q['phase']for q in phases]==['select','hud','setup-funded','funded','setup-empty','empty','setup-pool','pool','clear-after-pool']
        assert all(b['update']>a['update']and b['wall']>a['wall']for a,b in zip(phases,phases[1:]))
        phase={q['phase']:q for q in phases};funded=[q for q in es if q['phase']=='funded']
        assert any(q['kind']=='actual-source-contact'for q in funded)
        zero=[q for q in funded if q['kind']=='actual-funded-debit-zero'];assert zero and all(q['data']['item']==c['item']and q['data']['after']==0 and q['data']['before']==q['data']['cost']for q in zero)
        assert[q['data']['kind']for q in es if q['kind']=='isolated-native-boundary-component-reset']==['funded','empty','pool']
        empty=phase['empty'];end=phase['setup-pool'];assert end['update']-empty['update']==25
        for q in[empty,end]:
            d=q['data'];assert d['selected']==c['item']and d['ammo']==0 and d['held']==0 and d['kick']!=1 and len(d['shots'])==10 and all(s['type']==0 for s in d['shots'])
        empty_events=[q for q in es if q['phase']=='empty'];assert not any(q['kind']=='actual-special-spawn'for q in empty_events)
        debits=[q for q in empty_events if q['kind']=='actual-source-spend'];assert not any(q['data']['accepted']for q in debits)
        if c['item']==1:
            assert not debits
            gate='ARM source minimum8 gate, unchanged native postassert block51 guard, no debit/emission.'
        else:
            assert len(debits)==1;d=debits[0]['data'];assert d['item']==c['item']and d['cost']==c['source_cost']and d['before']==d['after']==0 and d['accepted']is False
            gate='Actual selected source exact-cost rejected InventorySpend before0/after0.'
        captures=[q for q in events if q['kind']=='ppu-frame-captured'and q['data']['name'].startswith(c['name']+'-')]
        refusal=[q for q in captures if q['data']['name']==c['name']+'-exhaust-refusal'];assert len(refusal)==1 and refusal[0]['update']==end['update']and refusal[0]['wall']>end['wall']
        for suffix in['natural-cleanup','selection-cleanup']:assert any(q['data']['name']==c['name']+'-'+suffix for q in captures)
        pool=phase['pool']['data'];assert pool['selected']==c['item']and pool['ammo']==112 and len(pool['shots'])==10 and all(s['type']==10 for s in pool['shots'])
        witnesses=[q for q in es if q['kind']in['actual-full-pool-special','actual-full-pool-refusal']];assert len(witnesses)==1;pw=witnesses[0]
        special=c['item']in[1,5];expected_cost={1:0,5:4,7:16}.get(c['item'],0)
        assert pw['kind']==('actual-full-pool-special'if special else'actual-full-pool-refusal')and pw['data']['cost']==expected_cost and pw['phase']=='pool'
        if not special:assert pw['data']['count']==10
        assert phase['clear-after-pool']['update']-phase['pool']['update']<15
        cleanup=[q for q in events if q['case']==case+1 and q['kind']=='gallery-phase'and q['phase']=='next'];assert len(cleanup)==1;cleanup=cleanup[0];d=cleanup['data'];assert cleanup['update']>phase['clear-after-pool']['update']and cleanup['update']-phase['clear-after-pool']['update']<30
        assert d['selected']!=c['item']and d['held']==0 and len(d['shots'])==10 and all(s['type']==0 for s in d['shots'])
        assert d['kick']==0 or d['kick']==2 and d['selected']!=5 and d['slide']!=0
        raw=summary['cases'][case-1]['emptyChecked']
        records.append(dict(case=case,name=c['name'],raw_terminal_emptyChecked=raw,raw_field_unchanged=True,actual_refusal_passed=True,empty_entry_update=empty['update'],empty_exit_update=end['update'],source_gate=gate,rejected_debits=debits,postassert_refusal_capture=refusal[0],pool_witness=pw,selection_cleanup=cleanup))
    return dict(passed=True,actual_ordered_cases=14,raw_summary_unchanged=True,records=records,scope='Only the terminal reset emptyChecked metadata predicate is replaced by actual ordered typed witnesses. No resource/flag/outcome mutation, missing refusal accepted, acquisition or global visual/timing claim.')
