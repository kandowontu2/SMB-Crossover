"""Ordinary attack held through a real completed sword-kill handoff."""
from functools import lru_cache
from hashlib import sha256
import replay_prince_body_transition_full_guard_1115 as Frozen

PIN=Frozen.PIN
FROZEN_LUA='f5823b8c9d1cf1923289edf07985e9dc9c53dbd878f2341158d0b2a2ce5b69b5'


@lru_cache(maxsize=1)
def controller(raw):
    text=Frozen.controller(raw);assert sha256(text.encode()).hexdigest()==FROZEN_LUA
    old='  if source(0x6ee)==2 then'
    new='''  if earnedStage.sword_pause and source(0x6ee)==1 and source(0x6de)==85 and s.action==58 then
    -- The real original attack just defeated the imported guard. Keep the
    -- ordinary attack button through a possible nearby replacement actor;
    -- do not insert the old neutral release before its automatic draw.
    pad=128;changedAt=commits
    return
  end
'''+old
    assert text.count(old)==1;text=text.replace(old,new,1)
    Frozen.Frozen.Full.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','saveState','loadState'))
    return text


def metadata(raw):
    q=Frozen.metadata(raw)
    q.update(Lua_SHA256=sha256(controller(raw).encode()).hexdigest(),
        controls='Only actual marker85/Sword1/action58 kill handoff retains ordinary A instead of eight-update neutral release',
        frozen_failed_parent_Lua_SHA256=FROZEN_LUA,original_FE67_attack_semantics=True)
    return q
