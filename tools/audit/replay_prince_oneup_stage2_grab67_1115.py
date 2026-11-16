"""Retain A during real stair jumps for the authenticated donor grab gate."""
from functools import lru_cache
from pathlib import Path
import re
import replay_prince_oneup_stage2_stair_A67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='da0d52974a877a200f69d80a3241a83319635fdd6362c0514af1c4aa17cf1466'
    # Original fall-contact explicitly requires held A or B ($040A & C0).
    # The preceding policy released A at admission and therefore never
    # requested this intended grab. Authenticate its actual owning bytes.
    labels=dict((name,int(at,16))for at,name in re.findall(r'^al ([\da-fA-F]+) \.?(\S+)$',
        (C.R/'build/prince-actor-1101-v1/contact-core.lbl').read_text(),re.M))
    pc=labels['PpN_7_F89B'];part=C.Packet.extract(raw)[1][0]
    assert part[pc-0xa000:pc-0xa000+5]==bytes.fromhex('ad0ac429c0')
    old=" elseif stock.phase=='two1-stair-air'then\n  pad=s.x<400 and 1 or 0"
    new=""" elseif stock.phase=='two1-stair-air'then
  local j=stock.stair_jumps[#stock.stair_jumps]
  if s.mode==2 or s.mode==6 or s.action==9 or s.action==10 then j.hang=j.hang or s end
  pad=j.hang and 8 or 129
  if j.hang and s.action==10 and idle(s)and s.y<=96 then j.cap=s;stockPhase('two1-stair-cap-release',0);return end"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    old=" elseif stock.phase=='coin-ledge-approach'then"
    new=""" elseif stock.phase=='two1-stair-cap-release'then
  pad=0
  if idle(s)and s.action==0 then
   stock.stair_cap_idle=s;stockPhase('approach',0)
  end
  assert(age<180,'Actual original stair-hoist release to idle')
 elseif stock.phase=='coin-ledge-approach'then"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        original_F89B_held_A_or_B_grab_gate_authenticated=True,
        standing_A3_then_held_RightA_then_Up_only_after_real_hang=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        actual_current67_CPU=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
