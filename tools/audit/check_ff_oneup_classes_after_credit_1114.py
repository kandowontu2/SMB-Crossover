"""Independent class checks with captured571 and actual post-credit entries."""
import argparse
import json
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

import replay_ff_natural_oneup_after_credit_1114 as Factory
import check_ff_natural_oneup_current_1114 as Source


def compact(q):
    r=q['receipt'];s=r.get('stock_oneup',{});c=s.get('credit',{})
    return dict(passed=q['passed'],identity=q['identity'],metadata=q['metadata'],
        source_receipt_SHA256=q['source_receipt_SHA256'],seconds=q['seconds'],
        source_scheduler_passes=q['source_scheduler_passes'],
        reason=r.get('reason'),completed_Main=r.get('completed_Main'),
        actual_FF_calls=r.get('calls',{}).get('CurrentFFWorker'),
        born=s.get('born'),mature=s.get('mature'),collector=s.get('collector'),
        credit=c,actual_entry_count=s.get('actual_FF_entries'),
        strictly_post_credit_actual_entries=s.get('resume'),terminal=r.get('terminal'),
        gameplay_seeds=q['gameplay_seeds'],Mesen_run=q['Mesen_run'],outputs=q['outputs'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',nargs='+',choices=Factory.IDENTITIES,
        default=['white-life','black-life','thief-life']);a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    assert sha256(raw).hexdigest()==Factory.PIN
    assert sha256(Path(Factory.__file__).read_bytes()).hexdigest()=='d381a25808eed711635aa06db08ad5503a5a1832ca10045050b6585384fba3a4'
    assert sha256(Path(Source.__file__).read_bytes()).hexdigest()=='0d62e98840b139e58be0b85a547d5c2a61d9e52716ead7f923a3884915cbdc58'
    def forbid(*args,**kwargs):raise RuntimeError('FF class source check attempted files/Mesen')
    results=[]
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',Factory):
        for key in a.identity:
            q=Source.run(raw,key);row=compact(q);results.append(row)
            print(json.dumps(dict(class_result=row),separators=(',',':')),flush=True)
            assert q['passed'],f'{key} actual post-credit endpoint remains unqualified'
    print(json.dumps(dict(passed=True,captured_ROM_SHA256=sha256(raw).hexdigest(),
        identities=a.identity,source_receipts=[q['source_receipt_SHA256']for q in results],
        fresh_cold_per_identity=True,mutable_nightly_rereads=0,outputs=0,Mesen_run=False),separators=(',',':')),flush=True)
