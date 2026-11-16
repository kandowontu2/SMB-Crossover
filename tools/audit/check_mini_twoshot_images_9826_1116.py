"""Compile/restoration only; do not simulate or execute screenshots."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_mini_twoshot_images_9826_1116 as F

if __name__=='__main__':
    def deny(*a,**kw):raise AssertionError('Picture compile attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw,_=F.C.proposal(F.ROM.read_bytes());q=F.metadata(raw)
    sample={'passed':True,'visual':{'pictures':[]},'functional':{'a':1}}
    assert F.functional_receipt(sample)=={'passed':True,'functional':{'a':1}}and'visual'in sample
    q.update(passed=True,receipt_normalizer_only_removes_visual=True)
    q['receipt_SHA256']=F.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
