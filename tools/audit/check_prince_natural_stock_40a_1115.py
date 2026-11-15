"""Actual current40a ordinary natural stock-item source input experiment."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_prince_natural_stock_40a_1115 as Factory
import check_prince_sword_tier2_fresh_cold_1115 as Cold

N,Game,Frames=Cold.N,Cold.Game,Cold.Frames

def run(raw,mode='oneup',jump=8):
    text=Factory.controller(raw,mode,jump);metadata=Factory.metadata(raw,mode,jump)
    print(json.dumps(dict(event='natural-stock-metadata',**metadata),separators=(',',':')),flush=True)
    m,opening=Cold.cold(raw);receipts=[];loads=json.loads;actual=Frames.frame;ticks=0
    def capture(*a,**k):
        q=loads(*a,**k)
        if isinstance(q,dict)and'natural_stock'in q:receipts.append(q)
        return q
    def frame(model,*a,**k):
        nonlocal ticks
        result=actual(model,whole_pass=True);ticks+=1
        if ticks%500==0:print(json.dumps(dict(event='natural-stock-source',Main=ticks,mode=mode,state=Cold.Previous.state(model)),separators=(',',':')),flush=True)
        return result
    with patch.object(Game,'controller',lambda image:text),patch.object(Game.json,'loads',capture),patch.object(Game.Frames,'frame',frame):
        proof=Game.route(m,raw,4200 if mode=='oneup'else 6800)
    assert len(receipts)==1;receipt=receipts[0]
    q=dict(passed=proof['passed'],metadata=metadata,opening=opening,reason=receipt['reason'],phase=receipt['phase'],
        natural_stock=receipt['natural_stock'],Main_returns=receipt['Main_returns'],Main_entries=receipt['Main_entries'],
        first_BBC1=receipt['new_candidate_readback'],terminal=receipt['terminal'],logical_Main=ticks,
        actual_CPU_ROM_SHA256=Factory.C.digest(m.bundle['raw']),source_only=True,no_gameplay_seeds=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=Factory.C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('oneup','star'),default='oneup');p.add_argument('--jump',type=int,choices=(8,128),default=8);a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Natural stock route attempted output or native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),a.mode,a.jump)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
