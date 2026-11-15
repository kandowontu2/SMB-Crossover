"""Matched ordinary free controls after genuine Flower; no state seeds."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_transition_model_1115 as Model

N,Frames=Model.N,Model.Frames


def episode(model,report,ticks):
    # The real pickup sets C6EE and supplies its original action91. Ordinary
    # neutral input lets that action finish before testing free buttons.
    prefix=Model.state(model);settle=[]
    for step in range(180):
        s=Model.state(model)
        if s['guard']or s['uid']:break
        if s['pose']==15 and s['action']==0 and model.ram[2][0x618]==0 and model.ram[2][0x6c0]==0:break
        model.controller_pad=0;Frames.frame(model,whole_pass=True)
        if step%20==0:settle.append(dict(Main=step+1,**Model.state(model)))
    ready=Model.state(model);cases=[]
    for name in('idle','B','A','Down','B_then_A','B_and_Down'):
        m=N.fork(model);last=None;trace=[];admitted=None
        for update in range(80):
            bits=0
            if name=='B':bits=64
            elif name=='A'and update<2:bits=128
            elif name=='Down'and update<2:bits=4
            elif name=='B_then_A':bits=64 if update<40 else 128 if update<42 else 0
            elif name=='B_and_Down'and update<2:bits=68
            m.controller_pad=bits;Frames.frame(m,whole_pass=True);s=Model.state(m)
            key=tuple(s[k]for k in('sword','marker','guard','uid','action','pose','x','y','hp'))
            if key!=last:trace.append(dict(Main=update+1,pad=bits,**s));last=key
            if s['guard']or s['uid']:admitted=update+1;break
            assert s['hp']>0 and s['lives']==2
        cases.append(dict(buttons=name,actual_Main=update+1,re_admitted_at=admitted,
            actions=sorted({r['action']for r in trace}),sword_states=sorted({r['sword']for r in trace}),
            terminal=Model.state(m),trace=trace[:2]+trace[-4:]if len(trace)>6 else trace,
            full_trace_SHA256=sha256(json.dumps(trace,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    return dict(actual_earned_prefix=prefix,prefix_Main=ticks,ordinary_neutral_settle=settle,ready=ready,cases=cases,
        no_health_actor_terrain_position_ability_seeds=True,scope='Actual earned Flower/no-opponent descendant; raw native button names only')


def run(raw):
    records=[]
    for transition in(False,True):
        def stop(m,tick):
            s=Model.state(m)
            return s['sword']==1 and s['guard']==0 and s['uid']==0 and s['hp']>0 and N.get(m,'GameEngineSubroutine')==8
        q=Model.run(raw,full=True,limit=4000,transition=transition,frame_observer=stop,after_route=episode)
        assert q['checkpoint_reached']and not q['full_route_completed']
        records.append(dict(transition219=transition,checkpoint=q['terminal'],component=q['after_route_component'],
            actual_CPU_ROM_SHA256=q['actual_CPU_ROM_SHA256'],model_only_mounts=q['model_only_mounts'],source_receipt=q['receipt_SHA256']))
    q=dict(passed=True,matched_actual_parent_and_transition_models=records,gameplay_seeds=0,outputs=0,Mesen=False,
        full_stage_qualified=False,scope='Matched source-only earned free-control characterization; action outcomes reported rather than assumed')
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Free-control source component attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
