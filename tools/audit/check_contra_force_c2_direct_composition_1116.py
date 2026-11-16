"""Strict661/284 composition/inverse contract; executes no CPU."""
from pathlib import Path
from unittest.mock import patch
import json
import compose_contra_force_checked_c2_direct_1116 as C


def run(parent):
    image,q=C.proposal(parent);assert C.inverse(image)==parent
    failures=[]
    def reject(label,raw,fn):
        try:fn(raw)
        except AssertionError:failures.append(label)
        else:raise AssertionError(('Missing strict rejection',label))
    reject('old44b is reference only',C.Base.proposal(parent)[0],C.proposal)
    reject('6a3 is reference only',C.reference(parent),C.proposal)
    reject('truncated parent',parent[:-1],C.proposal)
    reject('parent is not candidate',parent,C.inverse)
    for at,label in((0,'header'),(2022304,'protected old401'),(2022305,'new tail'),(573351,'guard helper'),
                   (642966,'new cookie'),(C.Base.BT.CACHE+128,'protected BT'),(2006200,'unowned CF payload')):
        raw=bytearray(parent);raw[at]^=1;reject('dirty parent '+label,bytes(raw),C.proposal)
        raw=bytearray(image);raw[at]^=1;reject('dirty inverse '+label,bytes(raw),C.inverse)
    C.proposal.cache_clear();C.lease.cache_clear()
    C.Base.proposal.cache_clear();C.Base.reference.cache_clear();C.Base.lease.cache_clear()
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Portable inverse attempted live Nightly read'
        return reader(path)
    with patch.object(Path,'read_bytes',read):assert C.inverse(image)==parent and C.proposal(parent)[0]==image
    with patch.object(Path,'read_bytes',lambda p:image if p.resolve()==C.ROM.resolve()else read(p)):
        assert C.load_current_image()==image
    q.update(strict_rejections=failures,portable_inverse_caches_cleared_and_live_Nightly_forbidden=True,
        postinstallation_loader_accepts_only_exact_newcandidate=True,no_CPU_executed=True)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    parent=C.load_current_image();assert C.H(parent)==C.PIN
    def deny(*a,**kw):raise AssertionError('Composition checker attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
