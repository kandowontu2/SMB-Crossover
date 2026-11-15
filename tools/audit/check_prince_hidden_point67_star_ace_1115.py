"""Actual point candidate real Star route; inherited fixed return completion."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import inspect,json
import current_prince_hidden_point67_ace_1115 as Current
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_hidden_point67_star_ace_1115 as Factory

def run(parent):
    C=Current.C;raw,composition=C.proposal(parent)
    cold=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=Current.cold))
    source=inspect.getsource(Previous.run)
    old="first_BBC1=receipt['new_candidate_readback'],terminal=";assert source.count(old)==1
    source=source.replace(old,"first_BBC1=receipt['new_candidate_readback'],point67_readback=receipt['point67_readback'],terminal=",1)
    space=dict(Previous.__dict__,Factory=Factory,Cold=cold)
    exec(compile(source,str(Path(__file__))+':actual-candidate-Star','exec'),space)
    q=space['run'](raw,'star',8)
    assert q['passed']and q['point67_readback']['bytes']==67 and q['actual_CPU_ROM_SHA256']==C.CANDIDATE
    q['composition']=composition;q['point67_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Point Star source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print('SUMMARY '+json.dumps({k:q[k]for k in('passed','metadata','Main_returns','Main_entries','terminal','point67_readback','point67_receipt_SHA256')},separators=(',',':')),flush=True)
    print(json.dumps(q,separators=(',',':')),flush=True)
