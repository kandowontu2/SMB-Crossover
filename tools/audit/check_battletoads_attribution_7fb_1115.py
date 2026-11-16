"""Minimal typed7fb transfer proof and actual current CPU callback replay."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_battletoads_attribution_7fb_1115 as P
import check_battletoads_idle_native_profile_1115 as Driver

C,F=P.C,P.F


def strict(raw):
    original=Path.read_bytes;rejects=[]
    def read(path):
        assert path.resolve()!=P.ROM.resolve(),'Current facade reread mutable Nightly'
        return original(path)
    with patch.object(Path,'read_bytes',read):
        old=P.reference(raw);q=P.metadata(raw)
        assert P.controller(raw).split('\n',1)[1]==P.Prior.controller(old).split('\n',1)[1]
        try:P.Prior.controller(raw)
        except AssertionError:rejects.append('frozen_ACE_API_rejects7fb')
        else:raise AssertionError('Frozen ACE API widened')
        for label,bad in(('oldACE',old),('parent174fa',C.inverse(old)),('unknown',bytes(len(raw))),('truncated',raw[:-1])):
            try:P.controller(bad)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Wrong current input accepted',label))
        for at in(90000,535471,653512,765868,792489,1989648):
            bad=bytearray(raw);bad[at]^=1
            try:P.controller(bytes(bad))
            except AssertionError:rejects.append('dirty@'+str(at))
            else:raise AssertionError(('Dirty current input accepted',at))
    q.update(rejections=rejects,mutable_Nightly_rereads=0,compiled_LF=True)
    return q


def callbacks(raw):
    assert C.digest(Path(Driver.__file__).read_bytes())=='168b2e55e74ac154049a2e9df82784df08c435a2f58fd7981924c49a023c910f'
    scope=dict(Driver.__dict__,P=P,Base=P.Model,W=P.W,N=P.N,Frames=P.Model.Frames)
    exec(compile(inspect.getsource(Driver.run),str(Path(__file__))+':actual7fb-callbacks','exec'),scope)
    q=scope['run'](raw);a=q['profile']['attribution']
    assert a['entries']==a['returns']and not a['unacknowledged']
    assert q['profile']['service_entries']==q['profile']['service_returns']
    assert q['profile']['service_entries']==dict(BtCheck=240,WfResolve=240)
    assert a['entries']['NMI_regular:AudioUpdate']==80 and len(q['profile']['rows'])<=32
    q.update(actual_current7fb_executed=True,old_ACE_body_and_code_transfer_exact=True,
        original_ACE_vector_proof_retained='40ce494b1cf08a71fc91d0e4c3a670eaf4a5290ea817266e0d6aec96d10af524',
        hardware_timing_or_natural_catchup_not_claimed=True)
    return q


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('strict','callbacks'));a=ap.parse_args()
    raw=P.load_current_image()
    def deny(*args,**kw):raise AssertionError('Attribution binding attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=(strict if a.mode=='strict'else callbacks)(raw)
    q.update(mode=a.mode,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
