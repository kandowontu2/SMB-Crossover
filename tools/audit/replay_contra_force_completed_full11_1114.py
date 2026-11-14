"""CF controller successor: decisions only after completed worker/Main snapshots."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_contra_force_grounded_full11_1114 as Grounded
import replay_contra_force_iron_full11_1114 as Iron

PIN,ROM,R,W,N=Grounded.PIN,Grounded.ROM,Grounded.R,Grounded.W,Grounded.N
Frozen,POLICY,IDENTITIES=Grounded.Frozen,Grounded.POLICY,Grounded.IDENTITIES
normalize,bindings=Grounded.normalize,Grounded.bindings
GROUND_SOURCE='0d55648f367bfec47f5b272eb4eeff3efcfe86787b112a92dae7a3422c7bcd14'
IRON_SOURCE='67e90e1ea8cf217e47b759fc4f8ddc8cf3fae92ad744daf69a0e14321b31b296'
LUA_SHA={'burns':'94b3056b7752a0b3d781a1ea5b06c496259e96fadbfb19fd0e51a05eb77c431f',
    'smith':'275665478a4d84e7482d300b029dfa334dba4df274499da2cf1ab0bcf528a0f9',
    'iron':'876048a6dc066ef7420c72be6aa5a7424617cae86aeccd3421d8471c1b962247',
    'beans':'1e6af4ca5c7c39acb218d727ad8387886017bc0a5e346775c81efc69741515d4'}


@lru_cache(maxsize=4)
def controller(raw,key):
    assert sha256(Path(Grounded.__file__).read_bytes()).hexdigest()==GROUND_SOURCE
    assert sha256(Path(Iron.__file__).read_bytes()).hexdigest()==IRON_SOURCE
    previous=Iron if key=='iron'else Grounded
    text=previous.controller(raw,key)
    def once(old,new):
        nonlocal text
        assert text.count(old)==1,old
        text=text.replace(old,new,1)
    once('update=cfCalls,heldA=lastA,','update=cfCompletedSource and cfCompletedSource.worker or 0,heldA=lastA,')
    once(' if cfDecisionUpdate==cfCalls then return cfButtons end',
         ' if pendingReturn or not cfCompletedSource or cfCompletedSource.Main~=updates then return cfButtons end\n local completed=cfCompletedSource.worker\n if cfDecisionUpdate==completed then return cfButtons end')
    once(' cfDecisionUpdate,cfButtons=cfCalls,b',' cfDecisionUpdate,cfButtons=completed,b')
    Frozen.LuaRuntime().compile(text)
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key):
    previous=Iron if key=='iron'else Grounded
    q=previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_controller_Lua_SHA256=previous.LUA_SHA[key],
        decisions_and_phase_clock_use_completed_CF_snapshot_not_entry_count=True,
        previous_buttons_retained_through_busy_Main_input_polls=True,
        original_CF_ground_snapshot_cookie_and_whole_Main_guards_retained=True,
        gameplay_physics_and_original_projectiles_unchanged=True)
    return q
