"""Compile the passive picture facade; never fake or execute screenshots."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_celeste_flower_images_00bb_1116 as F
import check_smb1_alts_full11_1114 as Runner

if __name__=='__main__':
    raw=F.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Picture compile attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny):
        q=F.metadata(raw)
    sample={'passed':True,'existing':{'a':1},'visual':{'pictures':[]}}
    assert F.functional_receipt(sample)=={'passed':True,'existing':{'a':1}} and'visual'in sample
    q.update(passed=True,source_CPU_run=False,screenshot_executed=False,receipt_normalizer_removes_only_visual=True)
    q['receipt_SHA256']=F.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
