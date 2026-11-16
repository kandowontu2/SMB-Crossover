"""Actual67 oneup route after measured early enemy clearance, no state seeds."""
from pathlib import Path
CAPTURED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from types import SimpleNamespace
from unittest.mock import patch
import inspect,json
import current_prince_oneup_67e3_1115 as Current
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_oneup_stage2_actor67_1115 as Factory

def run(raw):
    Current.prepare(raw);cold=SimpleNamespace(**dict(Previous.Cold.__dict__,cold=Current.cold))
    source=inspect.getsource(Previous.run);a="first_BBC1=receipt['new_candidate_readback'],terminal=";assert source.count(a)==1
    source=source.replace(a,"first_BBC1=receipt['new_candidate_readback'],point67_readback=receipt.get('point67_readback'),terminal=",1)
    space=dict(Previous.__dict__,Cold=cold,Factory=Factory);exec(compile(source,str(Path(__file__))+':actual-passed-left-actor','exec'),space)
    q=space['run'](raw,'oneup',8);assert q['actual_CPU_ROM_SHA256']==Current.PIN
    if q['passed']:assert q['point67_readback']['bytes']==67 and q['first_BBC1']['bytes']==4193
    q['binding_only_reference_SHA256']=Current.REFERENCE;q['all57_Bub_changes_preserved']=True
    q['receipt_SHA256']=Current.C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Stage2 actor source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(CAPTURED)
    s=q['natural_stock'];keys=('platform_contact','platform_mount','platform_idle','platform_runway','jump_request','jump_admission','farbank','coin_revealed','coin_mount','coin_cap','head_queries','born','mature','collector','collected','credit','completed_at_main_return','stage2_actor_milestones','stage2_hp_writes','stage2_up_states')
    print('SUMMARY '+json.dumps(dict(passed=q['passed'],reason=q['reason'],metadata=q['metadata'],receipt=q['receipt_SHA256'],terminal=q['terminal'],**{k:s.get(k)for k in keys}),separators=(',',':')),flush=True)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
