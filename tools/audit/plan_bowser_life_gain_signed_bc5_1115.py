"""Detached signed-counter successor; unsigned0->FF negative stays frozen."""
from pathlib import Path
from hashlib import sha256
import inspect,json
from unittest.mock import patch
import plan_bowser_life_gain_bc5_1115 as Previous

R,PIN,Current,NesMPU=Previous.R,Previous.PIN,Previous.Current,Previous.NesMPU
digest=Previous.digest
PREVIOUS_SHA='a4ba9a3f30a51a7f77b5910920e35d11368d3a79ee8547d6fb87b093666fecb8'

def proposal(raw):
    assert digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    b,before,_,row=Previous.proposal(raw);row=dict(row);new=bytearray(row['new'])
    assert new[28:30]==bytes.fromhex('9006')
    new[28]=0x30;row['new']=bytes(new)
    after=before[:row['start']-0xa000]+row['new']+before[row['end']-0xa000:]
    return b,before,after,row

def inspect_plan(raw):
    namespace=dict(Previous.__dict__);namespace['proposal']=proposal
    exec(compile(inspect.getsource(Previous.inspect_plan),__file__+':detached-views','exec'),namespace)
    q=namespace['inspect_plan'](raw)
    q['semantics']='Valid same-player modular life delta0 returns unchanged; native small positive INC deltas update saved life; negative DEC (including0->FF) enters original Construct'
    q['scope']='Detached signed-counter repair; no source-game overlay or ROM composition'
    q['retained_unsigned_proposal']='BCC would misclassify actual last-life0->FF death; frozen previous plan is not eligible for mounting'
    return q

if __name__=='__main__':
    raw=Current.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Detached signed plan attempted output/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=inspect_plan(raw)
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
