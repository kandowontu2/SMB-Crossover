"""Actual16a full ordinary route, fresh-step decisions and real pipe cells."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_prince_body_transition_full_guard_1115 as Base
import current_prince_body_transition_1115 as Current
import replay_prince_full_fresh_step_1115 as Factory


def run(raw):
    Current.normalize(raw,kind='prince-body-transition-16a')
    source=inspect.getsource(Base.run)
    old='raw,_=C.proposal(parent);text=Replay.controller(raw);metadata=Replay.metadata(raw)'
    new="raw=Current.normalize(parent,kind='prince-body-transition-16a').original;text=Replay.controller(raw);metadata=Replay.metadata(raw)"
    assert source.count(old)==1;source=source.replace(old,new,1)
    old="actual_transition=receipt.get('later_route',{}).get('body_transition'),first_helper_presence=helpers,"
    new=old+"\n        late_pipe={k:receipt.get('later_route',{}).get(k)for k in('fresh_step_outcomes','careful_step_admissions','late_pipe_geometry','late_pipe_control')},"
    assert source.count(old)==1;source=source.replace(old,new,1)
    space=dict(Base.__dict__,Current=Current,Replay=Factory)
    exec(compile(source,str(Path(__file__))+':actual16a-fresh-step','exec'),space)
    q=space['run'](raw)
    q.update(no_new_game_bytes=True,scope='Actual compiled cold16a ordinary full route, fresh original control decisions; no gameplay seeds or array mounts')
    q['fresh_step_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Fresh-step source route attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
