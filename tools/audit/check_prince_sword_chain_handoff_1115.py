"""Actual installed16a ordinary full route with a measured kill-handoff policy."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_prince_body_transition_full_guard_1115 as Base
import current_prince_body_transition_1115 as Current
import replay_prince_sword_chain_handoff_1115 as Factory


def run(raw):
    Current.normalize(raw,kind='prince-body-transition-16a')
    source=inspect.getsource(Base.run)
    old='raw,_=C.proposal(parent);text=Replay.controller(raw);metadata=Replay.metadata(raw)'
    new="raw=Current.normalize(parent,kind='prince-body-transition-16a').original;text=Replay.controller(raw);metadata=Replay.metadata(raw)"
    assert source.count(old)==1;source=source.replace(old,new,1)
    space=dict(Base.__dict__,Current=Current,Replay=Factory)
    exec(compile(source,str(Path(__file__))+':actual16a-chain-handoff','exec'),space)
    q=space['run'](raw)
    q.update(ordinary_kill_handoff_policy=True,no_new_game_bytes=True,
        interpretation='A source pass is not native or full-goal qualification; equal-facing F090 remains open')
    q['chain_handoff_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Chain-handoff source experiment attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
