"""Actualbc5 ordinary original fall-grip successor, zero outputs."""
from pathlib import Path
from types import FunctionType
from unittest.mock import patch
import json
import check_prince_oneup_roof_running_bc5_1115 as Previous
import replay_prince_oneup_roof_fall_grip_bc5_1115 as Factory

def run(raw):
    return FunctionType(Previous.run.__code__,dict(Previous.run.__globals__,Factory=Factory))(raw)

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Original fall-grip source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(Previous.CAPTURED)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
