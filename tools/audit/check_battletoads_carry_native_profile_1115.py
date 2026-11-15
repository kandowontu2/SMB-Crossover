"""Zero-output strict ACE profiler bindings and genuine callback acknowledgement."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_battletoads_carry_native_profile_1115 as P
import check_battletoads_idle_native_profile_1115 as Previous

C,F,Model=P.C,P.F,P.Model
DRIVER_SHA='168b2e55e74ac154049a2e9df82784df08c435a2f58fd7981924c49a023c910f'


def strict(raw):
    original=Path.read_bytes;rejects=[]
    def reader(path):
        assert path.resolve()!=C.ROM.resolve(),'Profiler reread mutable Downloads'
        return original(path)
    with patch.object(Path,'read_bytes',reader):
        q=P.metadata(raw)
        for label,bad in(('parent174fa',C.inverse(raw)),('a90',P.reference(raw)),('unknown',bytes(len(raw))),('truncated',raw[:-1])):
            try:P.controller(bad)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Wrong profiler input accepted',label))
        for at in(90000,653512,716848,792489,765868,1501131,535471):
            bad=bytearray(raw);bad[at]^=1
            try:P.controller(bytes(bad))
            except AssertionError:rejects.append('dirty@'+str(at))
            else:raise AssertionError(('Dirty profiler accepted',at))
    q.update(rejections=rejects,portable_current_inverse_binding=True,mutable_Downloads_reads_after_load=0,
        no_game_bytes_changed=True,compiled_LF_Lua=True)
    return q


def callbacks(raw):
    assert C.digest(Path(Previous.__file__).read_bytes())==DRIVER_SHA
    scope=dict(Previous.__dict__,P=P,Base=Model,W=Model.W,N=Model.N,Frames=Model.Frames)
    exec(compile(inspect.getsource(Previous.run),str(Path(__file__))+':frozen-callback-driver','exec'),scope)
    q=scope['run'](raw);profile=q['profile']
    assert profile['unacknowledged_services']==0
    assert profile['service_entries']==profile['service_returns']
    assert profile['service_entries']['WfResolve']==profile['service_entries']['BtCheck']==240,profile['service_entries']
    for phase,count in(('idle',48),('walk',32)):
        for name in('WfResolve','BtCheck'):assert profile['groups'][phase+':'+name]['calls']==3*count
        if phase+':HuResolve'in profile['groups']:assert profile['groups'][phase+':HuResolve']['calls']%count==0
    q.update(actual_current_ACE_code=True,all_service_returns_acknowledged=True,
        frozen_callback_driver_SHA256=DRIVER_SHA,hardware_cadence_not_claimed=True)
    return q


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('strict','callbacks'));a=ap.parse_args()
    raw=P.load_current_image()
    def deny(*args,**kw):raise AssertionError('Profiler attempted output or native launch')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q=(strict if a.mode=='strict'else callbacks)(raw)
    q.update(mode=a.mode,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
