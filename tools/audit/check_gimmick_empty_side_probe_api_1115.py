"""Strict new-candidate passive observer API/compile/authentication, no play."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_probe_current_1115 as F


if __name__=='__main__':
    actual=C.ROM.read_bytes();raw,proposal=C.current_proposal(actual)
    def forbid(*args,**kwargs):raise AssertionError('Side observer API attempted files/launch')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch('subprocess.Popen',forbid):
        q=F.bindings(raw);text=F.controller(raw)
        for name,hook in q['hooks'].items():
            at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes']),name
            if'bank'in hook:
                a=16+hook['bank']*8192;assert hook['bank_SHA256']==sha256(raw[a:a+8192]).hexdigest()
        result=dict(passed=True,metadata=F.metadata(raw),factory_SHA256=sha256(Path(F.__file__).read_bytes()).hexdigest(),
            hook_count=len(q['hooks']),new_hooks={k:v for k,v in q['hooks'].items()if k in('GmSideProbeEnter','GmSideProbeReturn','GmRawProbeReturn')},
            all_hook_bytes_bank_hashes_authenticated=True,gameplay_run=False,outputs=0,Mesen_run=False)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
