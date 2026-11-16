"""Actual67 held-grab ordinary control successor, zero outputs."""
from pathlib import Path
from unittest.mock import patch
from types import FunctionType
import json
import check_prince_oneup_stage2_stair_A67_1115 as Previous
import replay_prince_oneup_stage2_grab67_1115 as Factory

def run(raw):
    space=dict(Previous.run.__globals__,Factory=Factory)
    return FunctionType(Previous.run.__code__,space)(raw)

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Stage2 grab source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(Previous.CAPTURED)
    s=q['natural_stock']
    keys=('stair_contact','stair_geometry','stair_jumps','stair_cap_idle','farbank','head_position','request','actual_head_pad','coin_revealed','coin_mount','coin_cap','head_queries','born','mature','collector','collected','credit','completed_at_main_return','stage2_hp_writes')
    print('SUMMARY '+json.dumps(dict(passed=q['passed'],reason=q['reason'],metadata=q['metadata'],receipt=q['receipt_SHA256'],terminal=q['terminal'],**{k:s.get(k)for k in keys}),separators=(',',':')),flush=True)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
