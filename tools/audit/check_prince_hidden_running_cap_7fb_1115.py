"""One bounded ordinary running-cap 1UP policy, actual strict candidate CPU."""
from pathlib import Path
CAPTURED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from types import SimpleNamespace
from unittest.mock import patch
import json
import current_prince_hidden_point67_ace_1115 as Current
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_hidden_running_cap_7fb_1115 as Factory

def run(image):
    C=Current.C;pin=C.digest(image)
    assert pin in(C.PIN,C.CANDIDATE),'Exact ACE or its strict point candidate required'
    parent=C.inverse(image)if pin==C.CANDIDATE else image
    raw,composition=C.proposal(parent);assert pin!=C.CANDIDATE or raw==image
    cold=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=Current.cold))
    runner=Current.Previous.Old.clone(Previous.run,dict(Factory=Factory,Cold=cold))
    q=runner(raw,'oneup',8);assert q['actual_CPU_ROM_SHA256']==C.CANDIDATE
    q['captured_input_SHA256']=pin;q['owning_parent_SHA256']=C.PIN
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Running cap source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(CAPTURED)
    stock=q['natural_stock']
    print('SUMMARY '+json.dumps(dict(passed=q['passed'],reason=q['reason'],metadata=q['metadata'],receipt=q['receipt_SHA256'],
        running_request=stock.get('running_request'),running_admission=stock.get('running_admission'),
        running_support=stock.get('running_support'),minimum_y=stock.get('minimum_y'),
        running_landing=stock.get('running_landing'),head_queries=stock.get('head_queries'),
        born=stock.get('born'),mature=stock.get('mature'),collected=stock.get('collected'),credit=stock.get('credit'),
        completed_at_main_return=stock.get('completed_at_main_return'),terminal=q['terminal']),separators=(',',':')),flush=True)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
