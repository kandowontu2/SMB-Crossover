"""Separate exact32bf Flower policy: guarded ascending second-pipe admission.

Retains the frozen native acquisition/growth/reward/grounded observer and all
original physics. Default compiles only; --source-prefix is linked CPU only.
Root alone may use --run in the existing two-file slot, restored in memory.
"""
import argparse,json
from pathlib import Path
from unittest.mock import patch
import run_dkjr_flower_native_1123 as Frozen

S,H=Frozen.Source,Frozen.H
CANDIDATE=S.CANDIDATE
FROZEN_SHA='adc1832d2c9fc9d4b44d1779d9f604a853e25585a53e9292e9a5aedbb4d2281a'
NATIVE_SHA='24515082b3e248ebb8cecb189b4c0383c7bf527e299f023367647bcb84d90301'

POLICY=r'''
local pipe2Guard={phase='position',defenses=0}
FF.pipe2_guard=pipe2Guard
local function pipe2Actors()
 local out={}
 for i=0,5 do if read(0x10+i)~=0 then
  out[#out+1]={slot=i,id=read(0x17+i),state=read(0x1f+i),x=pos(0x76,0x5d,i),y=read(0xbe+i),
   flag=read(0x10+i),box=read(0x646+i),direction=read(0x46+i),speed=read(0x58+i)}
 end end
 return out
end
local function pipe2View()
 return {Main=updates,frame=frame,x=x(),y=read(0xbd),camera=camera(),phase=phase,index=index,
  guard_phase=pipe2Guard.phase,pad=bits,held=ram(2,0x14),sample=ram(2,0x15),source=ram(2,0x6b),prior=ram(2,0x6c),
  source_y=ram(2,0x210),source_x=ram(2,0x213),origin=ram(2,0x76),fall_limit=ram(2,0x7b),
  native_state=read(0x1e),hurt=ram(2,0x68),power=read(0x75b),lives=read(0x75f),
  up=currentTop(560),down=currentTop(624),actors=pipe2Actors()}
end
local function pipe2Tail()
 if FF.mushroom.complete and x()>=480 and x()<=720 then
  local q=FF.pipe2_tail or{};FF.pipe2_tail=q;q[#q+1]=pipe2View();if #q>12 then table.remove(q,1)end
  if index==2 and x()>=608 and x()<=640 and read(0xbd)==128 and ram(2,0x6b)==1 then
   pipe2Guard.actual_roof=pipe2Guard.actual_roof or pipe2View()
  end
 end
end
local function pipe2Set(name,top)
 pipe2Guard.phase=name;pipe2Guard.since=updates
 remember('guarded-pipe2-'..name,top);events[#events].actors=pipe2Actors()
end
local function pipe2Policy()
 local g=pipe2Guard
 if g.done or index~=2 or phase~='approach'and not g.started then return nil end
 if not g.started then
  assert(phase=='approach'and x()>=512 and x()<=524,'Ordinary first-pipe floor handoff')
  g.started=updates;g.initial=pipe2View()
 end
 assert(updates-g.started<650,'Finite guarded second-pipe entry')
 assert(FF.mushroom.complete and read(0x75b)==1 and read(0x75f)==2 and ram(2,0x68)==0 and ram(2,0x6b)~=5,
  'Earned Mushroom and original health retained at second pipe')
 local player,y=x(),read(0xbd);local top=currentTop(560)
 assert(top,'Original X560 lift admitted')
 local previous=g.lastTop;g.lastTop=top;g.maximum=math.max(g.maximum or top,top);g.minimum=math.min(g.minimum or top,top)
 if top>=208 then g.seen_low=true end
 local floor=ram(2,0x6b)==1 and ram(2,0x6c)==1 and read(0x1e)==0 and y==176 and ram(2,0x210)==191
 local released=(ram(2,0x14)|ram(2,0x15))&128==0
 if g.phase=='position'or g.phase=='wait-low-rise'then
  assert(player>=512 and player<=540,'Wait outside X560 lift collision footprint')
  assert(groundTile(player)~=0,'Authored solid floor before second pipe')
  if not floor then
   assert(g.defense_hold,'Only an actual defensive jump leaves this waiting floor')
   return updates<g.defense_hold and 128 or 0
  end
  for _,a in ipairs(pipe2Actors())do
   local dx=a.x-player
   if(a.id==2 or a.id==6)and a.state&32==0 and a.y>=172 and dx>=8 and dx<=30
    and released and updates>=(g.defense_rearm or 0)then
    g.defenses=g.defenses+1;assert(g.defenses<=3,'Bounded observed floor-enemy defense')
    g.defense_hold=updates+8;g.defense_rearm=updates+47
    g.last_defense={before=pipe2View(),enemy=a};return 128
   end
  end
  if player<538 then return 1 elseif player>539 then return 2 end
  if g.phase=='position'then pipe2Set('wait-low-rise',top)end
  if floor and released and g.seen_low and previous and top<previous and top>=206 and top<=210 then
   g.takeoff=pipe2View();g.hold=updates+8;pipe2Set('board-rising',top);return 129
  end
  return 0
 end
 assert(g.phase=='board-rising','Known second-pipe guarded phase')
 assert(updates-g.takeoff.Main<110,'Bounded ordinary ascending-lift jump')
 if ram(2,0x6b)==3 and ram(2,0x14)&128~=0 then g.accepted=g.accepted or pipe2View()end
 local ride=ram(2,0x6b)==1 and ram(2,0x6c)==1 and y<176 and y+32==top and ram(2,0x210)==y+15
 if ride then g.capture=g.capture or pipe2View()end
 if g.capture and ride and released and updates-g.takeoff.Main>=12 then
  assert(top<=206 and y<176,'Committed above-floor original carry')
  hold=0;rearm=updates;priorTop[560]=top;phase='rise';g.done=true;g.handoff=pipe2View()
  remember('guarded-pipe2-native-rise',top);events[#events].actors=pipe2Actors();return nil
 end
 return 1|(updates<g.hold and 128 or 0)
end
'''

WRITE_WITNESS=r'''
if emu.callbackType.write then
 emu.addMemoryCallback(guarded('guarded pipe2 source-state writer',function(_,value)
  if value~=5 or not playing or read(0x6002)~=40 or FF.source5_write then return end
  local m=emu.convertAddress(0xc06b)
  if not m or m.memType~=emu.memType.nesWorkRam or m.address~=2*8192+0x6b then return end
  local c=emu.getState();local pc=c['cpu.pc'];local p=emu.convertAddress(pc)
  FF.source5_write=pipe2View();FF.source5_write.writer_pc=pc
  FF.source5_write.writer_map=p and{kind=p.memType,address=p.address}
  FF.source5_write.writer_near={};for at=pc-5,pc+3 do FF.source5_write.writer_near[#FF.source5_write.writer_near+1]=read(at)end
 end),emu.callbackType.write,0xc06b)
end
'''

PREFIX_END=r'''
emu.addEventCallback(guarded('linked guarded pipe2 endpoint',function()
 if playing and pipe2Guard.done and index==3 and x()>=660 and x()<=665 and read(0xbd)==176
  and ram(2,0x6b)==1 and ram(2,0x6c)==1 and read(0x1e)==0 then
  assert(pipe2Guard.capture and pipe2Guard.actual_roof and FF.mushroom.complete and read(0x75b)==1
   and read(0x75f)==2 and ram(2,0x68)==0,'Natural Mushroom,real second-pipe roof and safe authored far floor')
  finish(false,'Source-only guarded second-pipe prefix completed')
 end
end),emu.eventType.endFrame)
'''


def controller(raw,*,source_prefix=False):
    assert H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    base=Frozen.controller(raw);assert H(base.encode())==Frozen.NATIVE_SHA
    text=S.Check.Replay.one(base,'local function drive()\n',POLICY+'\nlocal function drive()\n')
    marker=' local flowerBits=flowerPolicy();if flowerBits~=nil then bits=flowerBits;return end\n'
    replacement=' local pipe2Bits=pipe2Policy();if pipe2Bits~=nil then bits=pipe2Bits;return end\n'+marker
    text=S.Check.Replay.one(text,marker,replacement)
    old="FF.returns=FF.returns+1;assert(ffHealthy(),'Healthy ordinary Easy1-1 original work')"
    new="FF.returns=FF.returns+1;pipe2Tail();assert(ffHealthy(),'Healthy ordinary Easy1-1 original work')"
    text=S.Check.Replay.one(text,old,new)
    text=text+WRITE_WITNESS
    restored=text[:-len(WRITE_WITNESS)]
    for a,b in ((new,old),(replacement,marker),(POLICY+'\nlocal function drive()\n','local function drive()\n')):
        restored=S.Check.Replay.one(restored,a,b)
    assert restored==base and H(restored.encode())==Frozen.NATIVE_SHA
    if source_prefix:text=text+PREFIX_END
    S.Check.LuaRuntime().compile(text)
    assert not any(v in text for v in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    if NATIVE_SHA is not None and not source_prefix:assert H(text.encode())==NATIVE_SHA
    return text


def main():
    ap=argparse.ArgumentParser();mode=ap.add_mutually_exclusive_group()
    mode.add_argument('--run',action='store_true');mode.add_argument('--source-prefix',action='store_true');args=ap.parse_args()
    installed=Frozen.ROM.read_bytes();guard=Frozen.check(Frozen.ROM);parent,recovery=Frozen.parent_image(installed)
    with Frozen.recipe_cache():
        image,layout=S.proposal(parent);program=controller(image,source_prefix=args.source_prefix).encode()
    native_program=program[:-len(PREFIX_END.encode())]if args.source_prefix else program
    print('DK FLOWER PIPE2 BINDING '+json.dumps(dict(ROM_SHA256=CANDIDATE,controller_SHA256=H(program),
        source_prefix=args.source_prefix,native_controller_SHA256=H(native_program),parent_recovery=recovery,layout=layout,
        frozen_native=Frozen.NATIVE_SHA,factory_SHA256=H(Path(__file__).read_bytes()),outputs=0),separators=(',',':')),flush=True)
    if args.source_prefix:
        m,opening=Frozen.Head.cold(image)
        with patch.object(S.Check.Route.Frames,'frame',S.Check.normal_frame):
            result=S.Check.Route.route(m,image,3000,controller_text=program.decode())
        q=result.get('receipt');passed=bool(q and q.get('reason')=='Source-only guarded second-pipe prefix completed')
        print('DK FLOWER PIPE2 SOURCE '+json.dumps(dict(passed=passed,opening_Main=opening,
            actual_linked_source=True,native_Mesen=False,receipt=q,terminal=Frozen.Head.state(m),
            actors=Frozen.Head.actors(m),raw_result=result if not q else None),separators=(',',':')),flush=True)
        return int(not passed)
    if not args.run:return 0
    target,script=Frozen.OUT/'candidate.nes',Frozen.OUT/'controller.lua'
    assert set(Frozen.OUT.iterdir())=={target,script} and not guard['matching_patch_files']
    before_target,before_script=target.read_bytes(),script.read_bytes()
    assert H(before_target)in(guard['ROM_sha256'],S.PIN)
    Frozen.require_free_workspace(Frozen.R,target,allow_interactive=True)
    try:
        target.write_bytes(image);script.write_bytes(program);private=Frozen.check(target)
        assert private['ROM_sha256']==CANDIDATE and not private['matching_patch_files']
        result=Frozen.run(script,target,Frozen.OUT/'capture',CANDIDATE,320,long_no_capture=True)
        assert result['script_SHA256']==H(program) and result['outputs_written']==0 and not result['images']
        assert target.read_bytes()==image and script.read_bytes()==program and Frozen.check(target)==private
        print('DK FLOWER PIPE2 NATIVE '+json.dumps(result,separators=(',',':')),flush=True)
        return int(not result['passed'])
    finally:
        script.write_bytes(before_script);target.write_bytes(before_target)
        assert set(Frozen.OUT.iterdir())=={target,script} and target.read_bytes()==before_target and script.read_bytes()==before_script
        assert Frozen.ROM.read_bytes()==installed and Frozen.check(Frozen.ROM)==guard


if __name__=='__main__':raise SystemExit(main())
