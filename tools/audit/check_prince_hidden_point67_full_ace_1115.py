"""Actual candidate E161 full route, real earned Flower and public lifecycle."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import current_prince_hidden_point67_ace_1115 as Current
import replay_prince_hidden_point67_full_ace_1115 as Replay
import check_prince_sword_tier2_earned_1115 as Earned
import check_prince_full_reload_budget_1115 as Budget

C,N,W,Game,Frames=Current.C,Current.N,Current.W,Current.Game,Current.Frames
BASE_CPU=N.NesMPU

def actual(raw):
    text=Replay.controller(raw);metadata=Replay.metadata(raw)
    print(json.dumps(dict(event='point67-full-metadata',**metadata),separators=(',',':')),flush=True)
    m,opening=Current.cold(raw);actual_frame=Frames.frame;ticks=0;receipts=[];loads=json.loads;components=None
    def capture(*a,**k):
        q=loads(*a,**k)
        if isinstance(q,dict)and 'Main_returns'in q:receipts.append(q)
        return q
    def frame(model,*a,**k):
        nonlocal ticks,components
        result=actual_frame(model,whole_pass=True);ticks+=1
        if components is None and model is m and N.get(m,'PlayerStatus')==2 and m.ram[2][0x6ee]==1:
            with patch.object(N,'NesMPU',BASE_CPU):components=Earned.earned_components(m,actual_frame,raw)
        if ticks%1000==0:print(json.dumps(dict(event='point67-full-source',Main=ticks,state=Earned.state(m)),separators=(',',':')),flush=True)
        return result
    with patch.object(Game,'controller',lambda image:text),patch.object(Game.json,'loads',capture),patch.object(Game.Frames,'frame',frame):
        proof=Game.route(m,raw,10200)
    if not proof['passed']:
        print(json.dumps(dict(event='point67-full-negative',proof={k:v for k,v in proof.items()if k not in('events','flower','sword_trace')},terminal=Earned.state(m),Main=ticks),separators=(',',':')),flush=True)
    assert proof['passed']and len(receipts)==1 and components
    receipt=receipts[0];assert receipt['point67_readback']['bytes']==67
    assert receipt['new_candidate_readback']['bytes']==4193
    q=dict(passed=True,metadata=metadata,opening=opening,proof=proof,earned_components=components,
        actual_Main_witness={k:receipt.get(k)for k in('Main_entries','Main_returns','Main_pending','grounded_1_2_completed_returns')},
        point67_readback=receipt['point67_readback'],first_BBC1=receipt['new_candidate_readback'],
        persistent_sword=receipt['persistent_sword'],terminal=Earned.state(m),complete_Main_calls=ticks,
        actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),source_array_mounts=0,outputs=0,Mesen=False)
    return q

def run(parent):
    raw,composition=C.proposal(parent);source=inspect.getsource(Budget.run)
    old="current=CurrentCheck.Current.normalize(raw,kind='prince-current-gimmick-7a80')";assert source.count(old)==1
    source=source.replace(old,'assert C.digest(raw)==C.CANDIDATE',1)
    old="with patch.object(Frames,'frame',frame):q=CurrentCheck.run(raw,full=True)";assert source.count(old)==1
    source=source.replace(old,"with patch.object(Frames,'frame',frame):q=actual(raw)",1)
    space=dict(Budget.__dict__,C=C,actual=actual);exec(compile(source,str(Path(__file__))+':same-authenticated-cold-budget','exec'),space)
    q=space['run'](raw);q['composition']=composition
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Point full source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
