"""Explicit421 first-pipe approach with intuitive held direction/Up or jump.

Keep the frozen contact-trigger negative separate. Here Right+Up or Right+A
is held from the real X404 approach; no wall timer, braking, neutral interval
or idle admission is required. The preceding live-Goomba jump is unchanged.
"""
from hashlib import sha256
import json
from check_ff_stdout_controller_source_1110 import LuaRuntime
import replay_prince_pipe_usability_1114 as Frozen

ROM,PIN,authenticate=Frozen.ROM,Frozen.PIN,Frozen.authenticate


def controller(raw,*,pad=9,hold=240,target=1,brake=572,approach='direct'):
    assert pad in(9,129,137)and target==1 and 80<=hold<=300
    text=Frozen.controller(raw,target=1,pad=136,hold=hold,approach='contact')
    start=text.index(" if progress=='later-approach' or progress=='usability-approach' then\n")
    stop=text.index(" elseif progress=='usability-settle'",start)
    direct=""" if progress=='later-approach' or progress=='usability-approach' then
  probe.release=probeState(s);probe.stand=probeState(s)
  switch('usability-held',probe.held_pad)
"""
    text=text[:start]+direct+text[stop:]
    assert text.count('held_pad=136,')==1 and text.count("approach='contact',")==1
    text=text.replace('held_pad=136,',f'held_pad={pad},',1).replace("approach='contact',","approach='direct',",1)
    old=' s.sword=source(0x6ee)\n return s'
    assert text.count(old)==1
    text=text.replace(old,""" s.sword=source(0x6ee);s.native_status=read(0x759)
 s.body={read(0x658),read(0x659),read(0x65a),read(0x65b)}
 s.body_world={read(0x658)+s.scroll,read(0x659),read(0x65a)+s.scroll,read(0x65b)}
 s.projection_width=source(0x70f)
 return s""",1)
    assert not any(q in text for q in('emu.write','emu.setState','io.open'))
    LuaRuntime().compile(text)
    return text


def metadata(raw,**kwargs):
    text=controller(raw,**kwargs)
    return dict(authenticate(raw),Lua_SHA256=sha256(text.encode()).hexdigest(),
        pad=kwargs.get('pad',9),hold=kwargs.get('hold',240),target=1,approach='direct',
        controller_only=True,diagnostic_not_stage_clear=True,outputs=0,Mesen=False)


if __name__=='__main__':
    raw=ROM.read_bytes()
    for pad in(9,129,137):print(json.dumps(metadata(raw,pad=pad),separators=(',',':')),flush=True)
