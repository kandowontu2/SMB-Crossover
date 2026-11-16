"""Same paired ISR smoke, Mini owner reload reached by genuinely earned F."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_mini_sonic_owner_irq_9826_1116 as Previous
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

C=Previous.C
BASE_SHA='5b45a8d7920ea6632e54f5c3763127b25f84173417a10993f1e78dd7ea7384bb'

def run(parent):
    assert C.H(Path(Previous.__file__).read_bytes())==BASE_SHA
    old='        mini,mini_opening=F.Current.cold(raw,True)'
    new='''        openings=[];family=F.family()
        def cold(image,key):m,q=F.Current.cold(image,True);openings.append(q);return m
        with patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):route=Model.run(raw,'mini',5100)
        assert route['passed'];mini_opening=dict(cold=openings,genuine_earnedF_two_shot_source_receipt=route['source_receipt_SHA256'])'''
    assert Previous.TAIL.count(old)==1
    tail=Previous.TAIL.replace(old,new,1)
    prefix=inspect.getsource(Previous.Previous.run).split('    class CPU(base):',1)[0]
    env=dict(Previous.Previous.__dict__,F=Previous.F,C=C,N=Previous.N,W=Previous.W,Sonic=Previous.Sonic,Runner=Runner,Model=Model,__file__=__file__)
    exec(compile(prefix+tail,'<actual9826 earnedMini/sharedowner pairedIRQ>','exec'),env);q=env['run'](parent)
    q['retained_neutral_only_coverage_negative']=dict(checker_SHA256=BASE_SHA,job=52562,
        reason='Both Sonic43 cuts matched actual parent ISR/continuation; unpowered neutralMini41 never reaches the powered weapon owner reload. Coverage assertion failed, no ISR discrepancy.')
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**kw):raise AssertionError('Combined earned IRQ source attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny):q=run(C.ROM.read_bytes())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
