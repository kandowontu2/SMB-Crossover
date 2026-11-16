"""Actual a2 fullstage regression using unchanged frozen stage controls."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import current_sonic_ceiling_complete_a2d9_1116 as F
import check_sonic_hidden_full11_f7c9_1116 as Previous

PREVIOUS_SHA='3e19563d65124a443ec4f13117afa4d6bdb41e9b02ae04215e17ae5ac1909a36'


def run(raw,form='sonic',limit=5500):
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    ns=dict(Previous.__dict__,F=F,__file__=__file__)
    code=inspect.getsource(Previous.run)
    edits=(('complete=False;fault=None;grounded=0;ctx={}','complete=False;fault=None;grounded=0;last_motor=0;ctx={}'),
        ('nonlocal complete,grounded','nonlocal complete,grounded,last_motor'),
        ("s=state();assert N.get(m,'SelectedCharacter')", "s=state();progressed=s['motor']>last_motor;last_motor=s['motor'];assert N.get(m,'SelectedCharacter')"),
        ("if s['yhigh']==1 and s['y']==176 and s['state']==0 and s['source_flags']&8:grounded+=1",
         "if s['yhigh']==1 and s['y']==176 and s['state']==0 and s['source_flags']&8:\n                if progressed:grounded+=1"))
    for a,b in edits:assert code.count(a)==1,(a,code.count(a));code=code.replace(a,b)
    exec(compile(code,'<actuala2 complete ceiling fullstage>','exec'),ns)
    out=ns['run'](raw,form,limit);out['frozen_f7_stage_checker_SHA256']=PREVIOUS_SHA
    out['grounded_counter_requires_actual_original_C1_this_Main']=True
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Newa2 stage source regression attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.load_current_image(),a.form)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
