"""Actual-CPU fullstage production-Lua callback qualification, no native run."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_sonic_ceiling_full11_a2d9_1116 as Factory
import check_sonic_hidden_native_callback_f7c9_1116 as Previous

F=Factory.F
PREVIOUS_SHA='76442c0f0362192ef95cbefbc9a80b00892c702622c7927f916bc14f4e9108b1'


def functions():
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    ns=dict(Previous.__dict__,F=F,Factory=Factory,__file__=__file__)
    for name in('compile_pack','run'):
        s=inspect.getsource(getattr(Previous,name))
        if name=='run':
            a="assert receipt['pending']==0 and receipt['terminal']['lives']==3 and receipt['terminal']['rings']==5"
            b="assert receipt['pending']==0 and receipt['terminal']['lives']==2 and receipt['full_1_1']and receipt['grounded_1_2_original_updates']>=25"
            assert s.count(a)==1;s=s.replace(a,b)
            a="assert receipt['collected'][0]['boxes']and receipt['collected'][0]['item']['state']==6"
            b="assert receipt['native_flag']and receipt['native_castle']and receipt['native_entrance'];assert receipt['terminal']['level']==1 and receipt['terminal']['y']==176"
            assert s.count(a)==1;s=s.replace(a,b).replace('actual f7 CPU','actual a2 CPU')
        exec(compile(s,'<actuala2 fullstage native observer source>','exec'),ns)
    return ns


def compile_pack(raw):return functions()['compile_pack'](raw)


def run(raw,form='sonic',limit=5500):
    out=functions()['run'](raw,form,limit);out['retained_stage_controller_only']=True
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compile',action='store_true');p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Fullstage native-source callback test attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=compile_pack(F.load_current_image())if a.compile else run(F.load_current_image(),a.form)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
