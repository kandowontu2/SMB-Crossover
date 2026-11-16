"""Same a2 sustained-ceiling/physical1UP gates with right-side ordinary route."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import check_sonic_ceiling_side_life_a2d9_1116 as Previous
import sonic_ceiling_life_right_policy_a2d9_1116 as Policy

F=Previous.F
PREVIOUS_SHA='aeca053af5c74e9747569f2c68a681c23df0e4d59e80d1b24eb2cff1a8d0320f'


def run(raw,form='sonic',limit=1200):
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    code=inspect.getsource(Previous.run);ns=dict(Previous.__dict__,Policy=Policy,__file__=__file__)
    exec(compile(code,'<same a2 natural observer with measured right-side route>','exec'),ns)
    result=ns['run'](raw,form,limit)
    result.update(retained_left_side_route_negative='6f07a47b2c0ddd703f920d56c7a8fa388a07691c624f2b1b462e67952edb4e0b',
        right_side_policy_module_SHA256=F.H(Path(Policy.__file__).read_bytes()),right_side_policy_SHA256=F.H(Policy.text().encode()))
    result['receipt_SHA256']=F.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Right-side1UP source controller attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.load_current_image(),a.form)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
