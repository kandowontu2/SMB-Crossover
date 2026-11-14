"""Frozen current1daca-derived first-pipe walk-to432 then ordinary Up.

Diagnostic first pipe only. No game writes, ability seeds or fallback chords.
"""
from hashlib import sha256
import json
import compose_prince_body_world_1114 as C
import replay_prince_pipe_direct_1114 as Legacy

PIN='e4185311a7031c88570467dc99225ee42baad7c4931b5cfa1d57d37e7720dd08'
LUA='89fa7b13680aead4009046de0f5e3ebc5584b54c76e3738dca116e67d3f64533'


def controller(raw):
    assert C.digest(raw)==PIN
    parent=C.inverse(raw);assert C.digest(parent)==C.DK.CANDIDATE
    typed=C.normalize_parent(parent,kind='dk-window7-1daca')
    text=Legacy.controller(typed.reference421,pad=9,hold=240)
    old=""" if progress=='later-approach' or progress=='usability-approach' then
  probe.release=probeState(s);probe.stand=probeState(s)
  switch('usability-held',probe.held_pad)
"""
    new=""" if progress=='later-approach' or progress=='usability-approach' then
  pad=1
  if s.x>=432 then
   probe.release=probeState(s);probe.stand=probeState(s)
   switch('usability-held',probe.held_pad)
  end
"""
    assert text.count(old)==1 and text.count('held_pad=9,')==1
    text=text.replace(old,new,1).replace('held_pad=9,','held_pad=8,',1)
    assert text.count(Legacy.PIN)>=1;text=text.replace(Legacy.PIN,PIN)
    packet=C.Build.Old.Packet;old_cookie=typed.reference421[packet.COOKIE:packet.COOKIE+16].hex()
    assert text.count(old_cookie)==1
    text=text.replace(old_cookie,raw[packet.COOKIE:packet.COOKIE+16].hex(),1)
    assert sha256(text.encode()).hexdigest()==LUA
    assert not any(q in text for q in('emu.write','emu.setState','io.open'))
    Legacy.LuaRuntime().compile(text)
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),variant=3,
        ordinary_walk_to_x=432,then_pad=8,hold_admitted_source_updates=240,
        first_pipe_diagnostic_only=True,full_stage_qualified=False,
        no_gameplay_seeds=True,controller_only=True,outputs=0,Mesen=False)


if __name__=='__main__':
    raw,_=C.proposal(C.Build.Old.F.ROM.read_bytes())
    print(json.dumps(metadata(raw),separators=(',',':')),flush=True)
