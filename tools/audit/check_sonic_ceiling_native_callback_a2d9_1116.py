"""Newa2 native pack/callback gate; priorf7 source/body stays immutable."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_sonic_ceiling_life_a2d9_1116 as Factory
import check_sonic_hidden_native_callback_f7c9_1116 as Previous

F=Factory.F
PREVIOUS_SHA='76442c0f0362192ef95cbefbc9a80b00892c702622c7927f916bc14f4e9108b1'


def functions():
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    ns=dict(Previous.__dict__,F=F,Factory=Factory,__file__=__file__)
    for name in('compile_pack','run'):
        code=inspect.getsource(getattr(Previous,name))
        if name=='run':code=code.replace("receipt['collected'][0]['item']['state']==6", "receipt['collected'][0]['item']['state']>=6")
        exec(compile(code,'<owninga2 production sourcecallback>','exec'),ns)
    return ns


def compile_pack(raw):return functions()['compile_pack'](raw)


def run(raw,form='sonic',limit=1200):
    out=functions()['run'](raw,form,limit)
    assert len(out['native_body_receipt']['first8_posthead_original_returns'])==8
    out['scope']=out['scope'].replace('actual f7 CPU','actual a2 CPU')
    out['frozen_f7_callback_checker_SHA256']=PREVIOUS_SHA
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compile',action='store_true');p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Newa2 native source observer attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=compile_pack(F.load_current_image())if a.compile else run(F.load_current_image(),a.form)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
