"""Strict private e418 ordinary four-pipe replay; no game-state writes."""
from hashlib import sha256
import json
import compose_prince_body_world_1114 as C
import replay_prince_earned_current_1114 as Earned
from check_ff_stdout_controller_source_1110 import LuaRuntime

PIN='e4185311a7031c88570467dc99225ee42baad7c4931b5cfa1d57d37e7720dd08'
LUA_SHA='91535e9cb89eb6379a74d1b40a35a45e31e0cc38ea6c15134fc4e4f4f9a644dc'


def controller(raw):
    assert C.digest(raw)==PIN,'Expected exact private e418, not current Downloads'
    parent=C.inverse(raw);typed=C.normalize_parent(parent,kind=C.parent_kind(parent))
    text=Earned.controller(typed.reference421)
    old="          switch('third-park',65)";assert text.count(old)==1
    text=text.replace(old,"          switch('third-running-approach',1)",1)
    old='pad=201  -- Original Up+Right+A+B pipe-approach fallback.'
    assert text.count(old)==1;text=text.replace(old,'pad=8  -- Ordinary original Up throughout the pipe approach.',1)
    old='pad=age<55 and 8 or 201';assert text.count(old)==1;text=text.replace(old,'pad=8',1)
    # The inherited full-stage finish is unreachable in this four-cap scope,
    # but retain no fallback chord in that shared text either.
    assert text.count('pad=201')==1;text=text.replace('pad=201','pad=8',1)
    old="  if progress=='third-park' and s.action~=0 and s.action~=1 and s.action~=10 then"
    new="""  if progress=='third-running-approach' then
    if s.x>=744 and s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0 then
      late.third_running_request=s;switch('third-running-takeoff',129)
    end
  elseif progress=='third-running-takeoff' and s.action==4 then
    late.third_running_admission=s;switch('third-running-flight',1)
  elseif progress=='third-running-flight' then
    if s.x>=897 and s.pose==15 and s.mode==0 and s.lock==0 then
      late.fourth_practical_stand=s;switch('fourth-practical-up',8)
    elseif s.mode==2 or s.mode==6 then
      switch('fourth-practical-up',8)
    end
  elseif progress=='fourth-practical-up' then
    local left,right=capFeet(s,912,144)
    if left or right then
      late.fourth_practical_cap=s
      assert(read(@STAR@)==0 and read(@POWER@)==1,'Genuine mushroom form without Star')
      final=s;finish(true,'Four real native pipe caps through ordinary jump and Up');return
    end
  elseif progress=='third-park' and s.action~=0 and s.action~=1 and s.action~=10 then"""
    bundle=Earned.Frozen.W.Symbols.bundle()
    new=new.replace('@STAR@',str(Earned.Frozen.W.address(bundle,'StarInvincibleTimer'))).replace('@POWER@',str(Earned.Frozen.W.address(bundle,'PlayerStatus')))
    assert text.count(old)==1;text=text.replace(old,new,1)
    assert text.count(Earned.PIN)==1;text=text.replace(Earned.PIN,PIN,1)
    old=typed.reference421[C.Build.Old.Packet.COOKIE:C.Build.Old.Packet.COOKIE+16].hex()
    new=raw[C.Build.Old.Packet.COOKIE:C.Build.Old.Packet.COOKIE+16].hex()
    assert text.count(old)==1;text=text.replace(old,new,1)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','takeScreenshot'))
    LuaRuntime().compile(text)
    if LUA_SHA:assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),
        required_native_variant=3,ordinary_controls_only=True,four_caps_not_full_stage=True,
        current_Downloads_replacement=False,gameplay_seeds=0,outputs=0,Mesen=False)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--current-bt-f11',action='store_true');args=parser.parse_args()
    if args.current_bt_f11:import current_prince_body_research_f11_1114 as Current
    else:import current_prince_body_research_input_1114 as Current
    current=Current.load(Earned.ROM);raw,_=C.proposal(current.reference1daca)
    print(json.dumps(dict(**metadata(raw),public_input=current.metadata()),separators=(',',':')),flush=True)
