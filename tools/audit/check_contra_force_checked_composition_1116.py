"""Frozen source-only current checked-resolver composition; no CPU/native."""
from pathlib import Path
from unittest.mock import patch
import json
import compose_contra_force_checked_resolver_1116 as C


def run(parent):
    candidate,q=C.proposal(parent);assert C.inverse(candidate)==parent
    rejects=[]
    def reject(label,raw,fn):
        try:fn(raw)
        except AssertionError:rejects.append(label)
        else:raise AssertionError(('Strict input rejection missing',label))
    reject('parent truncated',parent[:-1],C.proposal)
    reject('reference6a3 is not owning91dc',C.reference(parent),C.proposal)
    for at,label in((0,'header'),(1989648+0x100,'protectedBTpayload'),(2006032+0x100,'protectedCFpayload'),(716848,'ownedspan')):
        raw=bytearray(parent);raw[at]^=1;reject('dirty parent '+label,bytes(raw),C.proposal)
        raw=bytearray(candidate);raw[at]^=1;reject('dirty inverse '+label,bytes(raw),C.inverse)
    reject('parent is not candidate',parent,C.inverse)
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Portable inverse attempted Nightly read'
        return reader(path)
    reader=Path.read_bytes
    C.proposal.cache_clear();C.reference.cache_clear();C.lease.cache_clear()
    with patch.object(Path,'read_bytes',read):
        assert C.inverse(candidate)==parent and C.proposal(C.inverse(candidate))[0]==candidate
        with patch.object(Path,'read_bytes',lambda p:candidate if p.resolve()==C.ROM.resolve()else read(p)):
            assert C.load_current_image()==candidate
    q.update(strict_rejections=rejects,portable_inverse_Nightly_read_forbidden=True,
        postinstallation_candidate_loader_roundtrip=True,all_files_and_Mesen_trapped=True,no_CPU_executed=True)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    return q


if __name__=='__main__':
    parent=C.load_current_image();assert C.H(parent)==C.PIN
    def deny(*a,**kw):raise AssertionError('Composition check attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
