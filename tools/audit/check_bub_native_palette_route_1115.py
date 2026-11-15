"""Actual in-memory candidate natural source route, zero output files."""
import argparse,json
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import replay_bub_native_palette_current_1115 as F

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--identity',type=int,choices=(0,1),default=0)
    ap.add_argument('--stock',choices=('flower','oneup'),default='flower');ap.add_argument('--metadata',action='store_true');ap.add_argument('--all',action='store_true');a=ap.parse_args()
    raw,composition=F.C.proposal(F.ROM.read_bytes());assert F.C.proposal(F.C.inverse(raw))[0]==raw
    if a.metadata:print(json.dumps(F.metadata(raw),separators=(',',':')))
    else:
      for identity,stock in([(i,s)for i in(0,1)for s in('flower','oneup')]if a.all else[(a.identity,a.stock)]):
        def forbid(*args,**kw):raise AssertionError('Candidate source attempted output')
        with patch.object(Path,'write_text',forbid),patch.object(Path,'write_bytes',forbid):
            try:q=F.source_check(raw,identity,stock)
            except AssertionError as e:
                assert len(e.args)==1 and isinstance(e.args[0],dict)and'receipt'in e.args[0];q=e.args[0]
        r=q.get('receipt')or{}
        receipt=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        f=r.get('natural_flower')or{};s=r.get('natural_stock')or{}
        compact_f={k:f[k]for k in('phase','M_moves','F_moves','M_resume','actual_post_F_moves','retries','sixth_support')if k in f}
        compact_f['pickups']={name:{k:p[k]for k in('collector','grant','erase','setup','popup','cue','freeze','first_age','last_age')if k in p}for name,p in(f.get('pickups')or{}).items()}
        compact_s={k:s[k]for k in('phase','credit','collector','erase','setup','popup','born','mature','credit_moves')if k in s}
        print('RESULT '+json.dumps(dict(passed=q['passed'],composition=composition,identity=identity,stock=stock,
            Lua_SHA256=q['controller_SHA256'],receipt_SHA256=receipt,Main=r.get('Main_updates'),moves=r.get('source_updates'),
            flower=compact_f,stock_receipt=compact_s,terminal=r.get('terminal'),reason=r.get('reason'),output_files=0),separators=(',',':')),flush=True)
        assert q['passed'],'Candidate natural source remains unqualified'
