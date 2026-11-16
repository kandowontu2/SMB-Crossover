"""Actual owningbc5 ordinary running-roof1UP experiment, zero outputs."""
from pathlib import Path
CAPTURED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from types import FunctionType
from unittest.mock import patch
import json
import current_prince_oneup_bc5_1115 as Current
import check_prince_oneup_stage2_stair67_1115 as Previous
import replay_prince_oneup_roof_running_bc5_1115 as Factory

def run(raw):
    q=FunctionType(Previous.run.__code__,dict(Previous.run.__globals__,Factory=Factory,Current=Current))(raw)
    q['all106_HotNew_changes_preserved']=True;q['binding_reference67_only']=True
    q['receipt_SHA256']=Current.C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Running roof source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(CAPTURED)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
