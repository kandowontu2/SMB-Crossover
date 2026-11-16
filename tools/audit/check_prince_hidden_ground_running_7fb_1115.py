"""One bounded actual7fb ground-jump policy; preserve all earlier negatives."""
from pathlib import Path
CAPTURED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from unittest.mock import patch
from types import SimpleNamespace
import json
import current_prince_hidden_point67_ace_1115 as Current
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_hidden_ground_running_7fb_1115 as Factory

def run(image):
    C=Current.C;pin=C.digest(image);assert pin in(C.PIN,C.CANDIDATE)
    parent=C.inverse(image)if pin==C.CANDIDATE else image;raw,_=C.proposal(parent)
    assert pin!=C.CANDIDATE or image==raw
    cold=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=Current.cold))
    runner=Current.Previous.Old.clone(Previous.run,dict(Factory=Factory,Cold=cold))
    q=runner(raw,'oneup',8);assert q['actual_CPU_ROM_SHA256']==C.CANDIDATE
    q['captured_input_SHA256']=pin;q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Ground1UP source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(CAPTURED)
    stock=q['natural_stock'];keys=('ground_drop','ground_ready','running_request','running_admission','minimum_y','ground_landing','head_queries','born','mature','collected','credit','completed_at_main_return')
    print('SUMMARY '+json.dumps(dict(passed=q['passed'],reason=q['reason'],metadata=q['metadata'],receipt=q['receipt_SHA256'],terminal=q['terminal'],**{k:stock.get(k)for k in keys}),separators=(',',':')),flush=True)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
