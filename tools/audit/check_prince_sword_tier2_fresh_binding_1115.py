"""Strict candidate/parent negatives and inverse without mutable nightly reads."""
from pathlib import Path
from unittest.mock import patch
import json
import compose_prince_sword_tier2_fresh_1115 as C

def run(parent):
    raw,info=C.proposal(parent);reader=Path.read_bytes
    def read(path,*a,**k):
        assert path.resolve()!=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').resolve(),'Mutable nightly reread'
        return reader(path,*a,**k)
    C.inverse.cache_clear()
    with patch.object(Path,'read_bytes',read):assert C.inverse(raw)==parent and C.proposal(C.inverse(raw))[0]==raw
    negatives=[]
    for name,fn,image in(('parent_as_candidate',C.inverse,parent),('candidate_as_parent',C.proposal,raw),
        ('truncated_parent',C.proposal,parent[:-1]),('truncated_candidate',C.inverse,raw[:-1]),
        ('dirty_parent',C.proposal,parent[:100]+bytes([parent[100]^1])+parent[101:]),
        ('dirty_candidate',C.inverse,raw[:100]+bytes([raw[100]^1])+raw[101:])):
        try:fn(image)
        except AssertionError:negatives.append(name)
        else:raise AssertionError('Unknown input accepted')
    q=dict(passed=True,composition=info,portable_inverse_exact_parent=True,mutable_nightly_rereads=0,
        strict_input_negatives=negatives,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Binding source gate attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
