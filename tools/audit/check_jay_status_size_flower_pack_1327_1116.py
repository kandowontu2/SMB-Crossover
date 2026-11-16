"""Actual-source callback execution of the strict Flower native observer."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_jay_status_size_flower_1327_1116 as F
import check_jay_status_size_full11_1327_1116 as Driver

J=F.J
DRIVER_SHA='9a0e93bfbda2935a7b3eff764ef1c183fff3cf23b1a2a5915f4200122314f1c1'


def run(raw,limit=1800):
    assert J.H(Path(Driver.__file__).read_bytes())==DRIVER_SHA
    source=inspect.getsource(Driver.run).replace('full11','flower').replace('F.policy_text()','F.Source.text()')
    old="assert r['passed']and r['credit']['flag']and r['credit']['castle']and r['credit']['entrance']\n    assert r['motor']>=r['credit']['entrance']['motor']+25 and r['terminal']['lives']==2"
    new="assert r['passed']and r['target']and r['credit']['writer']and r['award']and r['brick']and r['attack']\n    assert r['motor']>=r['credit']['motor']+25 and r['terminal']['lives']==2 and r['terminal']['hp']>0"
    assert source.count(old)==1;source=source.replace(old,new)
    line="    ns=dict(Harness.__dict__,F=F,J=J,__file__=__file__)"
    assert source.count(line)==1
    source=source.replace(line,"    source=source.replace(\"('unknown-kind',raw,'flower')\",\"('unknown-kind',raw,'life')\")\n"+line)
    ns=dict(Driver.__dict__,F=F,J=J,__file__=__file__)
    exec(compile(source,'<1327 actual Flower observer callback transport>','exec'),ns)
    q=ns['run'](raw,limit)
    q.update(fullstage_regression=False,genuine_Flower_native_observer_qualified_in_source=True,
        shared_callback_driver_SHA256=DRIVER_SHA)
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=1800);a=p.parse_args();assert 100<=a.limit<=2400
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay1327 Flower native-pack source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
