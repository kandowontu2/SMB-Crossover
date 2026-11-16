"""New ordinary controls after retaineda2 pickup-then-pit route negative."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import check_sonic_ceiling_natural_life_a2d9_1116 as Previous
import sonic_ceiling_life_side_policy_a2d9_1116 as Policy

F=Previous.F
PREVIOUS_SHA='4a7e4ee954fe54275522d74f512e38cc079f3f81f6028c68c872a61d7cccf164'


def run(raw,form='sonic',limit=1200):
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    source=inspect.getsource(Previous.run)
    old="ns=dict(Previous.__dict__,F=F,F_SHA=F_SHA,__file__=__file__)"
    new="ns=dict(Previous.__dict__,F=F,F_SHA=F_SHA,Policy=_Policy,POLICY_SHA=F.H(Path(_Policy.__file__).read_bytes()),__file__=__file__)"
    assert source.count(old)==1;source=source.replace(old,new)
    ns=dict(Previous.__dict__,_Policy=Policy,__file__=__file__)
    exec(compile(source,'<same a2 observer with ordinary beside-block approach and braking>','exec'),ns)
    result=ns['run'](raw,form,limit)
    result.update(retained_pickup_then_pit_control_negative='ce488b7072cd2b129f79a004ef1f03f3d231fb4cca27f53d8e0a89f0331e5c2f',
        controls_only=True,new_policy_module_SHA256=F.H(Path(Policy.__file__).read_bytes()),new_policy_SHA256=F.H(Policy.text().encode()))
    result['receipt_SHA256']=F.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Side1UP source controller attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.load_current_image(),a.form)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
