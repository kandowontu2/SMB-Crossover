"""Separate16a full route: ordinary B held through late opponent admission."""
from functools import lru_cache
from hashlib import sha256
import replay_prince_body_transition_1115 as Frozen

PIN=Frozen.PIN


@lru_cache(maxsize=1)
def controller(raw):
    text=Frozen.controller(raw,scope='opposed-loss')
    assert sha256(text.encode()).hexdigest()=='ae355c1948d71dd7d0611b63958debe8dff045b837968da54be6291e39bbc55e'
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old;text=text.replace(old,new,1)
    change('  if transition.movement and now.active==1 and now.sword==2 and now.marker==0 and s.x>=1800 and s.y==176 and s.hp>0 then',
        '  if not transition.readmitted and transition.movement and now.active==1 and now.sword==2 and now.marker==0 and s.x>=1800 and s.y==176 and s.hp>0 then')
    change("    transition.readmitted=now;final=s\n    finish(true,'Prince four caps and opposed sword loss, sheath, movement and re-admission; not full stage')\n    return",
        '    transition.readmitted=now')
    old='        and(not target or math.abs(x-s.x)<math.abs(target.x-s.x))then target={slot=slot,x=x,y=y}end'
    change(old,'        and(s.x<1800 or slot==(s.guard_uid&127))\n'+old)
    change('    if s.pose==171 and not episode.parried then pad=64\n    elseif s.action==62 then episode.parried=true',
        '''    if s.x>=1800 and not episode.parried then
      if s.action==62 then episode.parried=true else pad=64 end
    elseif s.pose==171 and not episode.parried then pad=64
    elseif s.action==62 then episode.parried=true''')
    assert not any(token in text for token in('emu.write','emu.setState','io.open','saveState','loadState','pad=201','or 201'))
    Frozen.Full.LuaRuntime().compile(text)
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),required_native_variant=3,
        controls='Only late x>=1800 actual-UID target and ordinary B held through draw before parry/approach/A',
        no_game_byte_changes=True,gameplay_seeds=0,source_full_route_pending=True,native_qualified=False,outputs=0,Mesen=False)
