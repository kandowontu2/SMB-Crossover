"""Actual captured40a fresh-A hidden1UP source route, zero output files."""
from pathlib import Path
# Root may deliver a separate character while this historical exact40a job
# runs. Capture the sole installed input once, before heavier module imports.
CAPTURED_RAW=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from unittest.mock import patch
import json
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_hidden_mount_fresh_A_40a_1115 as Factory

if __name__=='__main__':
    receipts=[];loads=json.loads
    def capture(*a,**k):
        q=loads(*a,**k)
        if isinstance(q,dict)and'natural_stock'in q:receipts.append(q)
        return q
    def deny(*a,**k):raise AssertionError('Fresh A route attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny),patch.object(Previous,'Factory',Factory),patch.object(Previous.Game.json,'loads',capture):
        q=Previous.run(CAPTURED_RAW,'oneup',8)
    assert len(receipts)==1
    q['base_receipt_SHA256']=q.pop('receipt_SHA256');q['inherited_injuries']=receipts[0].get('injuries',[])
    q['receipt_SHA256']=Factory.C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
