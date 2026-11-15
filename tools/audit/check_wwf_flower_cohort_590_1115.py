"""Independent current590 per-role source M/F transactions, zero outputs."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json,time
import explore_wwf_natural_flower_590_1115 as F

SOURCE='de035643e747c8bde10c77c28afe12eddbd6e17422c4b793ebcbb01ca21a26e5'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',nargs='+',choices=F.IDENTITIES,required=True);a=p.parse_args()
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==SOURCE
    raw=F.Images.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    def deny(*args,**kwargs):raise AssertionError('Cohort source attempted output/Mesen')
    failures=[]
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        for key in a.identity:
            start=time.monotonic();q=F.explore(raw,key,limit=4200)
            summary=dict(identity=key,passed=q['passed'],ROM_SHA256=F.PIN,
                receipt_SHA256=q['receipt_SHA256'],source_Main=q['source_Main'],final=q['final'],
                items=q['items'],failure=q['failure'],seconds=round(time.monotonic()-start,2),
                all6_cookie_SHA256=q['all6_cookie_SHA256'],gameplay_seeds=0,outputs=0,Mesen_run=False)
            if not q['passed']:summary.update(events=q['events'],recent=q['recent'],jump_inputs=q['jump_inputs']);failures.append(key)
            print('RESULT '+json.dumps(summary,separators=(',',':')),flush=True)
    assert not failures,('Natural per-role M/F remains source-unqualified',failures)
