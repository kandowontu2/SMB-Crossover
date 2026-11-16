"""Exact7fb one grounded Up episode; no stage change or game-code changes."""
from pathlib import Path
CAPTURED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from unittest.mock import patch
from types import SimpleNamespace
import inspect,json
import current_prince_hidden_point67_ace_1115 as Current
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_hidden_ground_up_aligned_7fb_1115 as Factory

def run(image):
    C=Current.C;pin=C.digest(image);assert pin in(C.PIN,C.CANDIDATE)
    parent=C.inverse(image)if pin==C.CANDIDATE else image;raw,_=C.proposal(parent)
    assert pin!=C.CANDIDATE or raw==image
    cold=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=Current.cold))
    source=inspect.getsource(Previous.run)
    a="first_BBC1=receipt['new_candidate_readback'],terminal=";assert source.count(a)==1
    source=source.replace(a,"first_BBC1=receipt['new_candidate_readback'],point67_readback=receipt['point67_readback'],terminal=",1)
    space=dict(Previous.__dict__,Factory=Factory,Cold=cold);exec(compile(source,str(Path(__file__))+':one-grounded-Up','exec'),space)
    q=space['run'](raw,'oneup',8);assert q['actual_CPU_ROM_SHA256']==C.CANDIDATE
    q['captured_input_SHA256']=pin;q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Aligned Up source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(CAPTURED)
    s=q['natural_stock'];keys=('start','head_position','request','minimum_y','landing','head_queries','action_admissions','born','mature','collector','collected','credit','completed_at_main_return')
    print('SUMMARY '+json.dumps(dict(passed=q['passed'],reason=q['reason'],metadata=q['metadata'],receipt=q['receipt_SHA256'],terminal=q['terminal'],**{k:s.get(k)for k in keys}),separators=(',',':')),flush=True)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
