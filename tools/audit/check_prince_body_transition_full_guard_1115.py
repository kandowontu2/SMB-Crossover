"""Actual16a complete-Main ordinary full-stage guard-control experiment."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_body_transition_candidate_1115 as Candidate
import replay_prince_body_transition_full_guard_1115 as Replay

C,N=Candidate.C,Candidate.N


def run(parent):
    raw,_=C.proposal(parent);text=Replay.controller(raw);metadata=Replay.metadata(raw)
    print(json.dumps(dict(event='strict16a-full-guard-metadata',**metadata),separators=(',',':')),flush=True)
    m,opening=Candidate.cold(raw);complete=Candidate.Frames.frame;loads=json.loads;receipts=[];ticks=0;helpers=[]
    def capture(*args,**kwargs):
        value=loads(*args,**kwargs)
        if isinstance(value,dict)and'later_route'in value:receipts.append(value)
        return value
    def frame(model,*args,**kwargs):
        nonlocal ticks
        result=complete(model,whole_pass=True);ticks+=1
        if ticks%500==0:
            print(json.dumps(dict(event='actual16a-full-guard',Main=ticks,x=N.get(model,'Player_X_Position')+256*N.get(model,'Player_PageLoc'),
                y=N.get(model,'Player_Y_Position'),hp=model.ram[2][0x6cf],sword=model.ram[2][0x6ee],guard=model.ram[2][0x6e0],action=model.ram[2][0x616]),separators=(',',':')),flush=True)
        if not helpers:
            for slot in range(6):
                if N.get(model,'Enemy_Flag',slot)and N.get(model,'Enemy_ID',slot)==28:
                    helpers.append(dict(Main=ticks,slot=slot,left=N.get(model,'Enemy_X_Position',slot)+256*N.get(model,'Enemy_PageLoc',slot),
                        y=N.get(model,'Enemy_Y_Position',slot),player_x=N.get(model,'Player_X_Position')+256*N.get(model,'Player_PageLoc'),
                        scope='Presence only, not an assistance or support witness'))
        return result
    with patch.object(Candidate.Game,'controller',lambda image:text),patch.object(Candidate.Game.json,'loads',capture),patch.object(Candidate.Game.Frames,'frame',frame):
        proof=Candidate.Game.route(m,raw,8500)
    assert len(receipts)==1;receipt=receipts[0];proof.pop('events',None);proof.pop('sword_trace',None)
    if isinstance(proof.get('flower'),dict):proof['flower']={k:v for k,v in proof['flower'].items()if k!='trace'}
    if proof['passed']:
        assert proof['reason']=='Prince earned-sword full1-1 and25 living grounded completed Main returns in1-2'
        assert receipt['grounded_1_2_completed_returns']>=25 and receipt['Main_entries']==receipt['Main_returns']and not receipt['Main_pending']
    q=dict(passed=proof['passed'],metadata=metadata,opening=opening,proof=proof,
        actual_Main_witness={key:receipt.get(key)for key in('Main_entries','Main_returns','Main_pending','grounded_1_2_completed_returns')},
        actual_transition=receipt.get('later_route',{}).get('body_transition'),first_helper_presence=helpers,
        actual_readback=receipt.get('new_candidate_readback'),actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),
        source_array_mounts=0,source_frames_return_complete_Main=True,no_gameplay_seeds=True,
        native_qualified=False,installed=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Full guard source experiment attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
