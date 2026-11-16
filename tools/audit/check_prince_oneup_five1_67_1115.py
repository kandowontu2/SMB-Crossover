"""Actual current67 ordinary5-1 hidden1UP route, stdout only."""
from pathlib import Path
CAPTURED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from types import SimpleNamespace
from unittest.mock import patch
import inspect,json
import current_prince_oneup_five1_67_1115 as Current
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_oneup_five1_67_1115 as Factory

def run(raw):
    Current.prepare(raw);cold=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=Current.cold))
    source=inspect.getsource(Previous.run);a="first_BBC1=receipt['new_candidate_readback'],terminal=";assert source.count(a)==1
    source=source.replace(a,"first_BBC1=receipt['new_candidate_readback'],point67_readback=receipt.get('point67_readback'),terminal=",1)
    source=source.replace("4200 if mode=='oneup'else 6800","4800 if mode=='oneup'else 6800")
    space=dict(Previous.__dict__,Cold=cold,Factory=Factory);exec(compile(source,str(Path(__file__))+':actual-five1','exec'),space)
    q=space['run'](raw,'oneup',8);assert q['actual_CPU_ROM_SHA256']==Current.PIN
    if q['passed']:assert q['point67_readback']['bytes']==67 and q['first_BBC1']['bytes']==4193
    q['binding_only_reference_SHA256']=Current.Previous.REFERENCE;q['all57_Bub_changes_preserved']=True
    q['receipt_SHA256']=Current.C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Five1 source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(CAPTURED)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
