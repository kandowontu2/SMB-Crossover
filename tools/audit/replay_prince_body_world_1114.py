"""Explicit fitted Prince controllers; frozen parent factories stay strict."""
from functools import lru_cache
from hashlib import sha256
import json
import compose_prince_body_world_1114 as C
import replay_prince_pipe_direct_1114 as Direct
import replay_prince_pipe_usability_1114 as Contact
import check_prince_pit_foot_context_1114 as Pits

ROM=Contact.ROM


@lru_cache(maxsize=2)
def authenticate(raw):
    parent=C.inverse(raw);typed=C.normalize_parent(parent,kind=C.parent_kind(parent))
    assert C.proposal(parent)[0]==raw
    legacy=Contact.authenticate(typed.reference421)
    return typed,dict(legacy,ROM_SHA256=C.digest(raw),parent_SHA256=C.digest(parent),
        cookie=raw[C.Build.Old.Packet.COOKIE:C.Build.Old.Packet.COOKIE+16].hex(),
        fitted_Prince_grant=C.GRANT_SHA,actual_DK_three_operands_preserved=True,
        controller_only=True,outputs=0,Mesen=False)


def controller(raw,*,mode='direct',pad=9,hold=240,edge=432):
    typed,info=authenticate(raw)
    assert mode in('direct','contact','pits','edge','pits-intuitive','earned')
    if mode in('direct','edge'):
        assert pad in((8,129)if mode=='edge'else(1,9,129))
        text=Direct.controller(typed.reference421,pad=9 if pad in(1,8)else pad,hold=hold)
        if pad in(1,8):
            assert text.count('held_pad=9,')==1;text=text.replace('held_pad=9,',f'held_pad={pad},',1)
        if mode=='edge':
            assert edge in(420,424,428,432,434)
            before=""" if progress=='later-approach' or progress=='usability-approach' then
  probe.release=probeState(s);probe.stand=probeState(s)
  switch('usability-held',probe.held_pad)
"""
            after=f""" if progress=='later-approach' or progress=='usability-approach' then
  pad=1
  if s.x>={edge} then
   probe.release=probeState(s);probe.stand=probeState(s)
   switch('usability-held',probe.held_pad)
  end
"""
            assert text.count(before)==1;text=text.replace(before,after,1)
    elif mode=='contact':text=Contact.controller(typed.reference421,target=1,pad=8,hold=180,approach='contact')
    elif mode=='earned':
        import replay_prince_earned_current_1114 as Earned
        text=Earned.controller(typed.reference421)
    else:
        text=Pits.controller(typed.reference421)
        if mode=='pits-intuitive':
            old="""  elseif progress=='pipe-settle' and s.pose==15 and s.mode==0 and s.lock==0 then
    assert(s.facing==255 and s.x>=390 and s.x<448 and floor(s),'Real idle stance before first pipe')
    switch('pipe-up',8)
"""
            new="""  elseif progress=='pipe-settle' then
    if s.x>=432 then switch('pipe-up',8)else pad=1 end
"""
            assert text.count(old)==1;text=text.replace(old,new,1)
            assert text.count('pad=201  -- Original Up+Right+A+B pipe-approach fallback.')==1
            text=text.replace('pad=201  -- Original Up+Right+A+B pipe-approach fallback.','pad=8  -- Ordinary Up at the real pipe approach; no fallback chord.',1)
            assert text.count('brake=577')==1 and text.count('brake=690')==1
            text=text.replace('brake=577','brake=592',1).replace('brake=690','brake=720',1)
            assert text.count('pad=age<55 and 8 or 201')==1
            text=text.replace('pad=age<55 and 8 or 201','pad=8',1)
    assert text.count(Contact.PIN)>=1
    text=text.replace(Contact.PIN,C.digest(raw))
    cookie=typed.reference421[C.Build.Old.Packet.COOKIE:C.Build.Old.Packet.COOKIE+16].hex()
    assert text.count(cookie)==1;text=text.replace(cookie,info['cookie'],1)
    assert not any(s in text for s in('emu.write','emu.setState','io.open'))
    Contact.LuaRuntime().compile(text)
    return text


def metadata(raw,**kwargs):
    _,info=authenticate(raw);text=controller(raw,**kwargs)
    return dict(info,Lua_SHA256=sha256(text.encode()).hexdigest(),mode=kwargs.get('mode','direct'),
        pad=kwargs.get('pad',9),diagnostic_not_stage_clear=True)


if __name__=='__main__':
    raw,_=C.proposal(ROM.read_bytes())
    for pad in(1,9,129):print(json.dumps(metadata(raw,pad=pad),separators=(',',':')),flush=True)
