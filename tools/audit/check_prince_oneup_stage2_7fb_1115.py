"""Actual2-1 ordinary controls after compiled level-select input unit."""
from pathlib import Path
CAPTURED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from types import SimpleNamespace
from unittest.mock import patch
import inspect,json
import prince_oneup_stage2_cold_7fb_1115 as Cold
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_oneup_stage2_7fb_1115 as Factory

def run(image):
    raw=Cold.prepare(image);cold=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=Cold.cold))
    source=inspect.getsource(Previous.run);a="first_BBC1=receipt['new_candidate_readback'],terminal=";assert source.count(a)==1
    source=source.replace(a,"first_BBC1=receipt['new_candidate_readback'],point67_readback=receipt['point67_readback'],terminal=",1)
    space=dict(Previous.__dict__,Cold=cold,Factory=Factory);exec(compile(source,str(Path(__file__))+':actual2-1-inputs','exec'),space)
    q=space['run'](raw,'oneup',8);assert q['actual_CPU_ROM_SHA256']==Cold.C.CANDIDATE
    q['receipt_SHA256']=Cold.C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Stage2 natural source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(CAPTURED)
    s=q['natural_stock'];keys=('platform_contact','platform_mount','platform_idle','platform_runway','jump_request','jump_admission','farbank','coin_revealed','coin_mount','coin_cap','head_queries','born','mature','collector','collected','credit','completed_at_main_return','stage2_actor_milestones','stage2_hp_writes')
    print('SUMMARY '+json.dumps(dict(passed=q['passed'],reason=q['reason'],metadata=q['metadata'],receipt=q['receipt_SHA256'],terminal=q['terminal'],**{k:s.get(k)for k in keys}),separators=(',',':')),flush=True)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
