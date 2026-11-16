"""Current Celeste owner qualification before any long natural route."""
from pathlib import Path
from unittest.mock import patch
import json
import current_celeste_stock_00bb_1116 as C

if __name__=='__main__':
    raw=C.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Celeste cold attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):m,q=C.cold(raw,report=True)
    q.update(passed=True,facade_SHA256=C.digest(Path(C.__file__).read_bytes()));q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
