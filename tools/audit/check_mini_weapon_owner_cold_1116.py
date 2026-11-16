"""Exact composer/inverse/unchanged Mini packet and actual owning cold16."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_mini_weapon_owner_twoshot_1116 as F

if __name__=='__main__':
    parent=F.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Mini owner cold attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw,composition=F.C.proposal(parent);_,cold=F.Current.cold(raw,True);meta=F.metadata(raw)
        old=F.Previous.controller(parent).split('\n',1)[1];new=F.controller(raw).split('\n',1)[1];assert old==new
        rejects=[]
        for label,bad in(('parent',parent),('truncated',raw[:-1]),('unowned',raw[:16+8192]+bytes((raw[16+8192]^1,))+raw[17+8192:])):
            try:F.controller(bad)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(label)
    q=dict(passed=True,composition=composition,cold=cold,metadata=meta,body_byte_identical=True,rejects=rejects,outputs=0,Mesen=False)
    q['receipt_SHA256']=F.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
