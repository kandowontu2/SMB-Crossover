"""Ordinary actual174fa Star source controller; stdout only."""
import argparse,json
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import replay_bub_star_174fa_1115 as F

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--identity',type=int,choices=(0,1),default=0);a=ap.parse_args()
    raw,actual=F.load_current()
    def forbid(*args,**kw):raise AssertionError('Star source attempted file output')
    with patch.object(Path,'write_text',forbid),patch.object(Path,'write_bytes',forbid):
        try:q=F.source_check(raw,a.identity)
        except AssertionError as e:
            assert len(e.args)==1 and isinstance(e.args[0],dict)and'receipt'in e.args[0];q=e.args[0]
    r=q.get('receipt')or{};star=r.get('natural_star')or{}
    digest=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(dict(passed=q['passed'],input_SHA256=actual,executed_SHA256=F.PIN,identity=a.identity,
        Lua_SHA256=q['controller_SHA256'],receipt_SHA256=digest,Main=r.get('Main_updates'),moves=r.get('source_updates'),
        star=star,terminal=r.get('terminal'),reason=r.get('reason'),output_files=0),separators=(',',':')),flush=True)
    assert q['passed'],'Natural Star remains source-unqualified'
