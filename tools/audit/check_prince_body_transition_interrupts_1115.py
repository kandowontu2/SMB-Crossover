"""Frozen paired-ISR assertions on real16a decode and ordinary execution."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import inspect,json
import check_prince_transition_interrupt_pairs_1115 as Frozen
import check_prince_body_transition_candidate_1115 as Candidate
import replay_prince_body_transition_1115 as Replay
import current_prince_body_transition_1115 as Current

C,N,W=Candidate.C,Candidate.N,Candidate.W
PIN='3ce63530ea873a399c14cdc2cef887580086b68601f689e5bc1111ec6b1d979a'


def actual_run(raw,*,full,limit,frame_observer):
    assert full and C.digest(raw)==C.CANDIDATE
    m,opening=Candidate.cold(raw);text=Replay.controller(raw,scope='opposed-loss')
    actual=Candidate.Frames.frame;ticks=0;cold_class=type(m)
    class CheckpointReached(Exception):pass
    def frame(model,*args,**kwargs):
        nonlocal ticks
        result=actual(model,whole_pass=True);ticks+=1
        if ticks%500==0:print(json.dumps(dict(event='actual16a-paired-ISR',Main=ticks,**Frozen.Model.state(model)),separators=(',',':')),flush=True)
        if frame_observer(model,ticks):raise CheckpointReached()
        return result
    checkpoint=False
    try:
        with patch.object(Candidate.Game,'controller',lambda image:text),patch.object(Candidate.Game.Frames,'frame',frame):
            proof=Candidate.Game.route(m,raw,limit)
    except CheckpointReached:proof=dict(passed=False,scope='Declared real16a checkpoint, not a full clear');checkpoint=True
    finally:m.__class__=cold_class
    q=dict(passed=checkpoint,checkpoint_reached=checkpoint,full_route_completed=False,opening=opening,
        controller_SHA256=sha256(text.encode()).hexdigest(),terminal=Frozen.Model.state(m),actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),
        source_array_mounts=0,logical_Main=ticks,scope='Actual16a packet and ordinary frozen inputs; reached checkpoint only',outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


def run(parent):
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==PIN
    raw,_=C.proposal(parent);Current.normalize(raw,kind='prince-body-transition-16a')
    model=SimpleNamespace(N=N,W=W,Current=C.Plan.Current,Research=Frozen.Model.Research,state=Frozen.Model.state,run=actual_run)
    source=inspect.getsource(Frozen.run)
    old="current=Model.Current.normalize(raw,kind='prince-graphics-590')"
    new="current=Current.normalize(raw,kind='prince-body-transition-16a')"
    assert source.count(old)==1;source=source.replace(old,new,1)
    space=dict(Frozen.__dict__,Model=model,Current=Current)
    exec(compile(source,str(Path(__file__))+':strict16a-paired','exec'),space)
    q=space['run'](raw)
    q.update(frozen_paired_assertion_source_SHA256=PIN,new_input_boundary='Explicit16a only, portable inverse to590; no frozen API widening',
        actual_new_encoded_ROM=True,all_previous_paired_assertions_retained=True)
    q['actual16a_ISR_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Actual16a source ISR proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
