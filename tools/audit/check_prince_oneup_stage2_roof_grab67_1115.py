"""Actual67 higher-roof ordinary held-grab source replay, no outputs."""
from pathlib import Path
from unittest.mock import patch
from types import FunctionType
import json
import check_prince_oneup_stage2_grab67_1115 as Previous
import replay_prince_oneup_stage2_roof_grab67_1115 as Factory

def run(raw):
    run_base=Previous.Previous.run
    return FunctionType(run_base.__code__,dict(run_base.__globals__,Factory=Factory))(raw)

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Higher-roof source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(Previous.Previous.CAPTURED)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
