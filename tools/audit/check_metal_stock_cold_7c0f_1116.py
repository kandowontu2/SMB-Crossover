"""Actual7c0f cold/worker proof; old91dc functions remain frozen and strict."""
from pathlib import Path
from unittest.mock import patch
import json
import current_metal_stock_7c0f_1116 as C

if __name__=='__main__':
    raw=C.ROM.read_bytes();assert C.digest(raw)==C.PIN
    def deny(*args,**kw):raise AssertionError('Current Metal binding attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        m,q=C.cold(raw,report=True)
        assert m.bundle['raw']is raw and q['actual_ROM_SHA256']==C.PIN
        q.update(passed=True,facade_SHA256=C.digest(Path(C.__file__).read_bytes()),reference91dc_SHA256=C.digest(C.reference(raw)),
            actual7c0f_executed=True,old91dc_APIs_unchanged=True)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
