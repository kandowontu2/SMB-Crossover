"""Additive normal-input first-tree landings for the frozen Rogue55df route."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import run_rogue_screw_native_1122 as Base
import run_rogue_side_pipe_nightly_1123 as Nightly
from check_ff_stdout_controller_source_1110 import LuaRuntime


H, W, ROM = Base.H, Base.Base.W, Base.ROM
PIN = Nightly.NIGHTLY
PARENT_CONTROLLER = '55df5042dc6e6e614a46e01c18eb447790bd8ea78558dd13a5e8b59faf618d59'
PINS = {
    False: 'ebd1ae870690a5095c79e0ab6148ad3ddf34c279b1fca7fb136f0c6bfed035d4',
    True: '7c5d2c39afcb0b45d2f8cc2aa76688b87a7fa7c8f8e1962a21e34fac844a253e',
}

POLICY = r'''
local firstTreeLegs={
 {left=288,rightExclusive=352,plane=192,low=312,high=315},
 {left=384,rightExclusive=416,plane=144,low=392,high=395}
}
local function firstTreeTravel(c,grounded,f)
 if not f.trees and c.x<216 then return end
 if not f.trees then
  f.trees={started=updates,phase='bank',leg=1,geometry=firstTreeLegs,
           baseline=state(),events={},contacts={},landings={},tail={}}
  f.trees.cache={}
  for y=128,208,16 do local row={y=y,tiles={}}
   for x=224,432,16 do row.tiles[#row.tiles+1]=c.block(x,y)end
   f.trees.cache[#f.trees.cache+1]=row
  end
 end
 local t=f.trees
 if t.complete then return end
 assert(updates-t.started<800,'Bounded two natural tree landings')
 assert(r('RdHealthLo')==t.baseline.health_raw[1]and r('RdHealthHi')==t.baseline.health_raw[2],
        'First tree traversal preserves captured natural health')
 assert(r('RdGear')==7 and r('NumberofLives')==2,'Earned upgrades and lives survive the trees')
 local function aim(low,high)return{left=c.x>high,right=c.x<low}end
 local function phase(name)
  t.phase=name
  assert(#t.events<32,'Bounded first-tree milestones')
  t.events[#t.events+1]={phase=name,leg=t.leg,player=state()}
 end
 local function record(b)
  t.previous={player=state(),bottom=r('RdY')+r('RdRadiusY'),gravity=r('RdGravity')}
  return b
 end
 if updates%8==0 then
  if #t.tail==16 then table.remove(t.tail,1)end
  t.tail[#t.tail+1]={phase=t.phase,leg=t.leg,player=state(),bottom=r('RdY')+r('RdRadiusY')}
 end
 local released=r('RdHeld')&128==0
 local spec=firstTreeLegs[t.leg]
 if t.phase=='bank'then
  local b=aim(236,239)
  if not b.left and not b.right and grounded and c.y>=175 and c.y<=177
     and released and r('RdAction')==0 then
   t.request={player=state()};phase('request');return record({right=true,a=true})
  end
  return record(b)
 end
 if t.phase=='release'then
  local b=aim(firstTreeLegs[1].low,firstTreeLegs[1].high)
  if not b.left and not b.right and grounded and released and r('RdAction')==0 then
   t.leg=2;spec=firstTreeLegs[2];t.request={player=state()};t.descent=nil
   phase('request');return record({right=true,a=true})
  end
  return record(b)
 end
 if t.phase=='request'or t.phase=='armed'then
  if not grounded and not released and r('RdVY')>=128 and not t.request.armed then
   t.request.armed=state();phase('armed')
  end
  if t.request.armed and not grounded and not released and r('RdVY')>=128 and c.y<t.request.player.y then
   t.takeoffs=t.takeoffs or{};t.takeoffs[t.leg]=state();phase('fly')
  else
   assert(updates-t.request.player.Main<12,'Actual negative-VY tree jump moves before leaving its bank')
   assert(c.x< (t.leg==1 and 248 or 340),'Unconfirmed request stays over its real launch support')
   return record({right=true,a=true})
  end
 end
 if t.phase=='fly'then
  local bottom=r('RdY')+r('RdRadiusY')
  if not grounded and r('RdVY')<128 and bottom<=spec.plane
     and c.x+8-r('RdRadiusX')>=spec.left and c.x+8+r('RdRadiusX')<spec.rightExclusive then
   t.descent={player=state(),bottom=bottom}
  end
  if grounded and c.x>=spec.low-4 and c.x<=spec.high+4 and bottom==spec.plane then
   local center=r('RdX')+256*r('RdRoomHi')
   local tile=c.block(center,spec.plane)
   assert(t.contacts[t.leg]and updates-t.contacts[t.leg].Main<=8 and t.descent,
          'Natural move-down collision precedes the settled tree landing')
   assert(tile==0x16 or tile==0x17 or tile==0x18,'Real native tree canopy supports the landing')
   assert(r('RdGravity')==0 and center-r('RdRadiusX')>=spec.left
          and center+r('RdRadiusX')<spec.rightExclusive,'Body rests fully within the authored ledge')
   t.landings[t.leg]={player=state(),center=center,bottom=bottom,tile=tile,
                     geometry=spec,contact=t.contacts[t.leg],descent=t.descent}
   if t.leg==1 then phase('release');return record({})end
   t.settled={entered=screwCounts('_entered'),returned=screwCounts('_returned')}
   phase('settle');return record({})
  end
  local b=aim(spec.low,spec.high);b.a=r('RdVY')>=128;return record(b)
 end
 if t.phase=='settle'then
  assert(grounded and r('RdY')+r('RdRadiusY')==spec.plane,'Keep natural second-tree support during25 updates')
  local er,rr=screwCounts('_entered'),screwCounts('_returned');local enough=true
  t.post_entered={};t.post_returned={}
  for n,v in pairs(er)do
   t.post_entered[n]=v-t.settled.entered[n];t.post_returned[n]=rr[n]-t.settled.returned[n]
   if t.post_entered[n]<25 or t.post_returned[n]<25 then enough=false end
  end
  if enough then
   assert(#pending==0 and #t.landings==2,'Both real landings and25 paired returns complete')
   t.complete={passed=true,player=state(),returned=t.post_returned,entered=t.post_entered}
   if C.trees_only then finish('natural-first-two-tree-landings-and25');return record({})end
   return
  end
  return record(aim(spec.low,spec.high))
 end
 return record({})
end
'''


def images(installed):
    assert H(installed)==PIN
    owner,image=Nightly.images(installed)
    assert image==installed and H(owner)==Base.PIN
    return owner,image


def controller(installed, *, trees_only=False):
    owner,image=images(installed)
    original=Base.native_program(owner,image).decode()
    assert H(original.encode())==PARENT_CONTROLLER
    text=original;edits=[]
    def edit(old,new):
        nonlocal text
        assert text.count(old)==1,(old,text.count(old))
        text=text.replace(old,new,1);edits.append((old,new))
    b=Base.bundle(owner)[2]
    lua=Base.Base.J.Previous.Previous.Frozen.lua
    name='RdHsGeometry';at=W.location(b,name)
    assert installed[at:at+8]==owner[at:at+8]
    line=text.split('\n',1)[0]
    extra='C.hooks.RdHsGeometry='+lua(dict(PC=W.address(b,name),offset=at-16,bytes=list(installed[at:at+8])))
    extra+='\nfor n,at in pairs('+lua({n:W.address(b,n)for n in('RdHostService','RdRadiusY','RdRadiusX','RdGravity')})+')do C.ram[n]=at end'
    if trees_only:extra+='\nC.trees_only=true'
    edit(line,line+'\n'+extra)
    edit('local function screwDrive(c)',POLICY+'\nlocal function screwDrive(c)')
    edit(" if f.phase=='travel'then\n  if c.x>=886", " if f.phase=='travel'then\n  local b=firstTreeTravel(c,grounded,f);if b then return b end\n  if c.x>=886")
    needle=" if n=='RdControlScrew'then p.before=state()"
    edit(needle,""" if n=='RdHsGeometry'then
  local x=r('RdX')+256*r('RdRoomHi');local bottom=r('RdY')+r('RdRadiusY')
  p.tree={service=r('RdHostService'),x=x,bottom=bottom,y=r('RdY'),radius=r('RdRadiusY'),
          tile=context().block(x,bottom),player=state()}
 end
"""+needle)
    needle="  elseif n=='RdControlScrew'then\n"
    edit(needle,"""  elseif n=='RdHsGeometry'then
   local t=gear.screw and gear.screw.trees
   if t and not t.complete and p.tree.service==9 and cpu()['cpu.ps']&1==0 then
    local spec=firstTreeLegs[t.leg]
    if p.tree.bottom==spec.plane and p.tree.x-r('RdRadiusX')>=spec.left
       and p.tree.x+r('RdRadiusX')<spec.rightExclusive
       and(p.tree.tile==0x16 or p.tree.tile==0x17 or p.tree.tile==0x18)then
     t.contacts[t.leg]=t.contacts[t.leg]or{Main=updates,C=0,source=p.tree}
    end
   end
"""+needle)
    edit('local age=0',"""hook('RdHsGeometry',function()
 local t=gear.screw and gear.screw.trees
 if t and not t.complete and active()and identity()and r('LevelNumber')==2
    and r('RdHostService')==9 then enter('RdHsGeometry')end
end)
local age=0""")
    if trees_only:
        old=next(line for line in text.splitlines()if line.startswith(' local ok='))
        assert 'and #completed==2 and collector and gear.acquisition and gear.acquisition.credit and born and mature and not reset and #pending==0' in old
        extra="reason=='natural-first-two-tree-landings-and25'and gear.complete and gear.high.complete and gear.wall.acquisition and gear.wall.acquisition.credit and gear.wall.acquisition.birth and gear.wall.acquisition.mature and gear.wall.acquisition.collector and gear.screw.exterior.complete and gear.screw.trees.complete and #completed==2 and gear.acquisition and gear.acquisition.credit and not reset and #pending==0"
        edit(old,' local ok=('+extra+')or('+old.removeprefix(' local ok=')+')')
    restored=text
    for old,new in reversed(edits):
        assert restored.count(new)==1
        restored=restored.replace(new,old,1)
    assert restored==original
    LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot','dofile'))
    return text


def source(installed,limit,trees_only):
    owner,image=images(installed)
    program=controller(installed,trees_only=trees_only)
    assert H(program.encode())==PINS[trees_only]
    old=Base.bundle(owner);values=old[:2]+(dict(old[2],raw=image),)
    def compiled(raw):
        assert raw is image
        return program
    def cold(raw):
        assert raw is image
        def bindings(image_arg):
            assert image_arg is image
            return values
        with patch.object(Base.Previous,'bundle',bindings):
            return Base.Previous.cold(image)
    with patch.object(Base,'controller',compiled),patch.object(Base,'cold',cold),patch.object(Base,'PIN',PIN):
        return Base.source(image,limit)


def native(installed,trees_only):
    owner,image=images(installed)
    program=controller(installed,trees_only=trees_only).encode()
    assert H(program)==PINS[trees_only]
    def compiled(raw,target,**kwargs):
        assert raw is owner and target==installed and not any(kwargs.values())
        return program
    with patch.object(Base,'native_program',compiled):
        return Base.native(owner,installed)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--trees-only',action='store_true');p.add_argument('--limit',type=int,default=12500)
    a=p.parse_args();assert 9600<=a.limit<=15000
    raw=ROM.read_bytes()
    if a.run:
        q=native(raw,a.trees_only)
    else:
        def deny(*args,**kwargs):raise AssertionError('Tree source check attempted files or process launch')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit,a.trees_only)
            else:
                program=controller(raw,trees_only=a.trees_only)
                assert H(program.encode())==PINS[a.trees_only]
                q=dict(passed=True,route_executed=False,ROM_SHA256=PIN,controller_SHA256=H(program.encode()),outputs=0,native=False)
    print('ROGUE_TREES '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
