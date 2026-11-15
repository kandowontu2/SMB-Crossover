"""Compile/API/old-control identity for three RAM pictures; no fake PNGs."""
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import json
import replay_bub_three_images_40a_1115 as F

if __name__=='__main__':
    raw=F.ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Three-image metadata attempted output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):q=F.metadata(raw)
    q.update(passed=True,actual_rendered_PNGs=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
