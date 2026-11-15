"""Source qualify the scoped actual-coordinate Bub close-defence controls."""
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import argparse,json
import replay_bub_flower_close_defence_40a_1115 as F

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1),default=0);a=p.parse_args()
    raw=F.ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Close-defence source attempted output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):
        try:q=F.source_check(raw,a.identity)
        except AssertionError as e:
            assert len(e.args)==1 and isinstance(e.args[0],dict)and'receipt'in e.args[0]
            q=e.args[0]
    r=q.get('receipt')or{};receipt=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(dict(passed=q['passed'],ROM_SHA256=F.PIN,identity=a.identity,
        controller_SHA256=q['controller_SHA256'],source_receipt_SHA256=receipt,
        Main=r.get('Main_updates'),moves=r.get('source_updates'),reason=r.get('reason'),
        flower=r.get('natural_flower'),terminal=r.get('terminal'),output_files=0),separators=(',',':')),flush=True)
    assert q['passed'],'Bub close-defence continuation remains source-unqualified'
