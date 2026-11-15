"""Independent Bob actual-current natural Flower source case; zero outputs."""
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import json
import replay_bob_flower_close_defence_40a_1115 as F

if __name__=='__main__':
    raw=F.ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Bob close-defence source attempted output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):
        try:q=F.source_check(raw,1)
        except AssertionError as e:
            assert len(e.args)==1 and isinstance(e.args[0],dict)and'receipt'in e.args[0]
            q=e.args[0]
    r=q.get('receipt')or{};receipt=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(dict(passed=q['passed'],ROM_SHA256=F.PIN,identity=1,
        controller_SHA256=q['controller_SHA256'],source_receipt_SHA256=receipt,
        Main=r.get('Main_updates'),moves=r.get('source_updates'),reason=r.get('reason'),
        flower=r.get('natural_flower'),terminal=r.get('terminal'),output_files=0),separators=(',',':')),flush=True)
    assert q['passed'],'Bob close-defence continuation remains source-unqualified'
