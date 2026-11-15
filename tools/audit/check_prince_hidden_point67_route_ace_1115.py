"""Actual new packet plus unchanged ordinary cap/A route, source CPU only."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import current_prince_hidden_point67_ace_1115 as Current
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_hidden_point67_ace_1115 as Factory

def run(parent):
    C=Current.C;raw,composition=C.proposal(parent)
    cold=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=Current.cold))
    runner=Current.Previous.Old.clone(Previous.run,dict(Factory=Factory,Cold=cold))
    q=runner(raw,'oneup',8);stock=q['natural_stock']
    assert q['actual_CPU_ROM_SHA256']==C.CANDIDATE and stock['point67_readback']['bytes']==67
    assert stock['point67_hidden']and stock['point67_materials']
    assert all(p['A']==0 and p['classified_B36D']==0 for p in stock['point67_hidden'])
    assert all(p['A']!=20 and p['Wall']==0 for p in stock['point67_materials'])
    assert not stock.get('point67_backtrack'),'Same hidden cell must not cause the old C427 backtrack'
    q.update(hidden_false_wall_gate_passed=True,natural_item_route_passed=q['passed'],composition=composition)
    q['point67_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Point route source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
