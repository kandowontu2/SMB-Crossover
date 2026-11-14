"""Strict current421, normal-input first/second-pipe usability observations.

This is a diagnostic controller, not a traversal qualification or a game fix.
The frozen successful first-pipe navigation is retained. The second-pipe
approach then brakes at an explicit world coordinate and holds normal input.
"""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import prince_cold_packet_1111 as Packet
import current_smb2_hidden_input_1114 as Current
import check_ff_white_mushroom_current_1110 as W
from check_ff_stdout_controller_source_1110 import LuaRuntime

R=Packet.R
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN=Current.HIDDEN
FROZEN=R/'tools/playthroughs/prince_original_first_pipe_stdout_1110.lua'
FROZEN_SHA='e9b45ae96c00ee55b456200f346ab2e4f22c78013a0820e98910ecddcc6dc65e'


@lru_cache(maxsize=1)
def authenticate(raw):
    assert isinstance(raw,bytes) and sha256(raw).hexdigest()==PIN
    q=Current.normalize(raw,kind='hidden-421')
    packet=Packet.extract(raw)
    assert packet==Packet.extract(q.postbg)
    assert raw[Packet.COOKIE:Packet.COOKIE+16]==q.postbg[Packet.COOKIE:Packet.COOKIE+16]
    return dict(ROM_SHA256=PIN,postbg_SHA256=sha256(q.postbg).hexdigest(),
        Prince_packet_exact_vs_12397=True,cookie=raw[Packet.COOKIE:Packet.COOKIE+16].hex(),
        decoded_SHA256=[sha256(p).hexdigest()for p in packet[1]],
        all_176_current_fixes_preserved=True,outputs=0)


def controller(raw,*,brake=572,pad=8,hold=180,target=2,approach='brake'):
    q=authenticate(raw)
    assert target in(1,2)and approach in('brake','contact','prefix')
    assert 390<=brake<=594 and pad in(8,9,136,137) and 80<=hold<=300
    assert sha256(FROZEN.read_bytes()).hexdigest()==FROZEN_SHA
    text=FROZEN.read_text(encoding='utf-8')
    def once(a,b):
        nonlocal text
        assert text.count(a)==1,a
        text=text.replace(a,b,1)
    once("local cookie = 'a726021676a00802119275ac7f48cce7'",f"local cookie = '{q['cookie']}'")
    once("local variant = tonumber(os.getenv('SMB_TEST_VARIANT') or '0')",
         "local variant = 3\nassert(rom=='"+PIN+"','Explicit current421 Prince observation')")
    once('emu.setInput({right=pad&1~=0,','emu.setInput({right=pad&1~=0,left=pad&2~=0,')
    lo=text.index('local function laterTick(s)\n')
    hi=text.index('local function tick()\n',lo)
    diagnostic=r'''
local probe={brake=@BRAKE@,held_pad=@PAD@,hold_commits=@HOLD@,target=@TARGET@,approach='@APPROACH@',samples={},walls={},hang=false,top=false}
late.usability=probe
local function probeState(s)
 s.source_x=source(0x60f)+256*source(0x610)
 s.source_y=source(0x611)+256*source(0x612)
 s.cached_x=source(0x4db)+256*source(0x4dc)
 s.old_native_x=source(0xa7)+256*source(0xa8)
 s.wall_timer=read(@WALL@);s.source_pad=source(0x40a)
 s.query_x=source(0x1369,3)+256*source(0x136a,3)
 s.query_y=source(0x136b,3);s.query_raw=source(0x136d,3)
 s.sword=source(0x6ee)
 return s
end
local function probeTick(s)
 local age=commits-changedAt
 if progress=='later-approach' or progress=='usability-approach' then
  probe.front=math.max(probe.front or s.x,s.x)
  if not probe.last_x or probe.last_x~=s.x then probe.last_x=s.x;probe.last_advance=commits end
  local atWall=s.x>=probe.target*160+273 and read(@WALL@)>0
  local stopped=commits-(probe.last_advance or commits)>=64
  if probe.approach=='prefix' then
   final=probeState(s);finish(true,'Actual first-pipe source prefix checkpoint');return
  elseif(probe.approach=='brake'and s.x>=probe.brake)or(probe.approach=='contact'and(atWall or stopped))then
   probe.release=probeState(s);probe.contact=atWall;probe.stalled=stopped;switch('usability-settle',0)
  end
 elseif progress=='usability-settle' and idle(s) and floor(s) then
  probe.stand=probeState(s);switch('usability-held',probe.held_pad)
 elseif progress=='usability-held' then
  probe.hang=probe.hang or s.mode==2 or s.mode==6
  probe.top=probe.top or (s.y<=(@TOP@-31)and support(s)and s.x+13>=@LEFT@)
  if age%4==0 and #probe.samples<76 then probe.samples[#probe.samples+1]=probeState(s)end
  if age>=probe.hold_commits then
   final=probeState(s);probe.terminal=final
   finish(true,'Bounded ordinary pipe usability observation')
  end
 end
end
local function laterTick(s)probeTick(s)end
emu.addMemoryCallback(guarded(function()
 if progress:sub(1,10)~='usability-'and progress~='later-approach'then return end
 local map=emu.convertAddress(@WALLPC@)
 if not map or map.memType~=emu.memType.nesPrgRom or map.address~=@WALLAT@ then return end
 local s=probeState(state());s.side=read(3)
 s.body={read(0x658),read(0x659),read(0x65a),read(0x65b)}
 s.cap_left=@LEFT@;s.cap_top=@TOP@;s.cap=tile(@LEFT@,@TOP@);s.air=tile(@LEFT@,@TOP@-1)
 if #probe.walls<12 then probe.walls[#probe.walls+1]=s end
end),emu.callbackType.exec,@WALLPC@)

'''
    b=W.Symbols.bundle();wall=W.location(b,'SamusStopAtWallBanked')
    replacements={'@BRAKE@':brake,'@PAD@':pad,'@HOLD@':hold,'@TARGET@':target,
        '@APPROACH@':approach,'@WALL@':W.address(b,'SideCollisionTimer'),
        '@WALLPC@':W.address(b,'SamusStopAtWallBanked'),'@WALLAT@':wall-16,
        '@LEFT@':448 if target==1 else 608,'@TOP@':176 if target==1 else 160}
    for a,z in replacements.items():diagnostic=diagnostic.replace(a,str(z))
    text=text[:lo]+diagnostic+text[hi:]
    once('  if firstPipe then\n',"  if progress:sub(1,10)=='usability-'then probeTick(s);return end\n  if firstPipe then\n")
    if target==1:
        once("    elseif s.x>=400 then\n      switch('pipe-settle',0)","    elseif s.x>=400 then\n      switch('usability-approach',1)")
        once("if s.x>=400 then switch('pipe-settle',0) else switch('approach',1) end",
             "if s.x>=400 then switch('usability-approach',1) else switch('approach',1) end")
    assert not any(s in text for s in('emu.write','emu.setState','io.open','emu.takeScreenshot'))
    LuaRuntime().compile(text)
    return text


def metadata(raw,**kwargs):
    text=controller(raw,**kwargs)
    return dict(authenticate(raw),Lua_SHA256=sha256(text.encode()).hexdigest(),
        normal_inputs_only=True,diagnostic_not_stage_clear=True,Mesen=False,**kwargs)


if __name__=='__main__':
    print(json.dumps(metadata(ROM.read_bytes()),separators=(',',':')))
