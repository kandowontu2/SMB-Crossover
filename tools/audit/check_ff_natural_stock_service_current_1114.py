"""Execute realae66 bytes with the strict independent FF stock adapter."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_ff_natural_stock_service_current_1114 as Factory
import check_ff_natural_oneup_current_1114 as Source
import check_ff_oneup_classes_after_credit_1114 as LifeReceipt
import check_ff_natural_star_current_1114 as StarReceipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',nargs='+',choices=Factory.IDENTITIES,default=['white-life','black-life','thief-life']);a=p.parse_args()
    raw=Factory.ROM.read_bytes();results=[]
    def forbid(*args,**kwargs):raise RuntimeError('FF current service source checker attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',Factory):
        for key in a.identity:
            q=Source.run(raw,key)
            row=StarReceipt.compact(q)if key.endswith('-star')else LifeReceipt.compact(q)
            results.append(dict(identity=key,passed=q['passed'],source_receipt_SHA256=q['source_receipt_SHA256']))
            print(json.dumps(dict(class_result=row),separators=(',',':')),flush=True)
            assert q['passed'],f'{key} actual-current FF stock route remains unqualified'
    print(json.dumps(dict(passed=True,ROM_SHA256=Factory.PIN,results=results,captured_current_bytes=True,
        fresh_cold_per_identity=True,outputs=0,Mesen_run=False),separators=(',',':')),flush=True)
