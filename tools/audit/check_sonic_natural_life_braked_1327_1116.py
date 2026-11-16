"""Actual swept-selector hidden60 witness from a braked ordinary jump."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import check_sonic_natural_life_probe_1327_1116 as Prior
import sonic_natural_life_braked_policy_1327_1116 as Policy

F=Prior.F
PRIOR_SHA='472bed468fac38e37f205e224d72a20ca507a718dd9cb40d9e95788e214a1857'


def run(raw,form='sonic',limit=900):
    assert F.H(Path(Prior.__file__).read_bytes())==PRIOR_SHA
    q=F.bindings(raw);k=q['kernel']
    assert k[0x1b26:0x1b39].hex()=='ad04c1c95ff070c960f06cc967f068c968f064'
    assert k[0x1b9d:0x1ba3].hex()=='a907d002a90a'
    source=inspect.getsource(Prior.run)
    assert source.count('(3,0xb842)')==1;source=source.replace('(3,0xb842)','(3,0xbb9d)')
    ns=dict(Prior.__dict__,Policy=Policy,__file__=__file__)
    exec(compile(source,'<actual1327 swept-selector/braked jump witness>','exec'),ns)
    out=ns['run'](raw,form,limit);r=out['first_actual_60_rejection']
    out.update(retained_moving_jump_negative='15444f151cab6d2f43284dd8549e53160f6fc22f88f312c50231ef96a60c1f9a',
        actual_swept_selector_PC=0xbb26,actual_reject_PC=0xbb9d,
        proper_upward60_observed=bool(r and r[0]['query']['axis']==1 and r[0]['query']['negative']==1 and r[0]['state']['vy']<0 and r[0]['requested_pad']&128),
        static_B842_not_claimed_as_reached=True)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');p.add_argument('--limit',type=int,default=900);a=p.parse_args()
    assert 100<=a.limit<=1200;raw=F.ROM.read_bytes();assert F.H(raw)==F.PIN
    def deny(*a,**kw):raise AssertionError('Braked Sonic source witness attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.form,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
