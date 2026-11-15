"""Source-qualify strict571 per-class genuine M/F/Star controllers."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_ff_natural_star_current_1114 as Factory
import check_ff_natural_oneup_current_1114 as Previous


def compact(q):
    r=q['receipt'];s=r.get('stock_star',{})
    def player(p):
        return {k:p.get(k)for k in('updates','completed','frame','x','y','engine','state','power','earned','charges','lives','star','active','timer','life_lease')}
    def event(e):
        if not e:return None
        return dict(player=player(e.get('player',{})),actor=e.get('actor'),score=e.get('score'),
            player_box=e.get('player_box'),item_box=e.get('item_box'))
    c=s.get('collected',{})
    return dict(passed=q['passed'],identity=q['identity'],metadata=q['metadata'],
        source_receipt_SHA256=q['source_receipt_SHA256'],seconds=q['seconds'],
        completed_Main=r.get('completed_Main'),actual_FF_entries=r.get('calls',{}).get('CurrentFFWorker'),
        reason=r.get('reason'),mushroom={k:r.get('mushroom',{}).get(k)for k in('ticks','collected')},
        flower={k:r.get('flower',{}).get(k)for k in('ticks','collected')},
        born=event(s.get('born')),mature=event(s.get('mature')),collector=event(s.get('collector')),
        collected=dict(after=player(c.get('after',{})),cue=c.get('cue'),music=c.get('music'),actual_FF_entries=c.get('actual_FF_entries')),
        final_score=s.get('final_score'),score_awarded=event(s.get('score_awarded')),
        strictly_post_collector_entries=s.get('resume'),terminal=player(r.get('terminal',{})),
        gameplay_seeds=q['gameplay_seeds'],Mesen_run=q['Mesen_run'],outputs=q['outputs'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,default='fighter-star');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('FF Star source checker attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        q=Previous.run(raw,a.identity)
    print(json.dumps(compact(q),separators=(',',':')),flush=True)
    assert q['passed'],'FF real Star continuation remains unqualified'
