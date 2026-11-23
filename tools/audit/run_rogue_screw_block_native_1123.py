"""Additive low-tree and Screw-block route after the frozen first-tree proof."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import run_rogue_screw_trees_native_1123 as Trees
import inspect_rogue_missile_targets_cb95_1116 as Engine
from check_ff_stdout_controller_source_1110 import LuaRuntime


H, ROM, PIN = Trees.H, Trees.ROM, Trees.PIN
PARENT_CONTROLLER = 'ebd1ae870690a5095c79e0ab6148ad3ddf34c279b1fca7fb136f0c6bfed035d4'
PINS = {
    False: 'c44b74be7fbc3fb72b5540ff1495592efb19757f53223e2c9e31e6106060afc7',
    True: '982383c859fe87c30865a21b21fbd4079b9b027a6a39069febdca50775e3f6d8',
}
ACQUISITION_PIN = 'fa8d2a096585f2539e72c25a3cf854bcb536fbcf5fcb8f544f50fbb94c4ae9c4'
ORIGINAL_CONTROLLER = Trees.controller

POLICY = r'''
local screwLowSpecs={
 high={left=640,rightExclusive=752,plane=64,low=720,high=723},
 low={left=800,rightExclusive=864,plane=208,low=824,high=827},
 block={left=944,rightExclusive=960,plane=160,low=944,high=947}
}
local function screwLowTravel(c,grounded,f)
 if not f.low and c.x<712 then return end
 if not f.low then
  f.low={started=updates,phase='bank-high',target='high',baseline=state(),
         geometry=screwLowSpecs,contacts={},events={},tail={}}
 end
 local l=f.low
 if l.complete then return end
 assert(updates-l.started<600,'Bounded natural high-tree to Screw-block route')
 assert(r('RdHealthLo')==l.baseline.health_raw[1]and r('RdHealthHi')==l.baseline.health_raw[2]
        and r('RdGear')==7 and r('NumberofLives')==2,'Low-tree route preserves earned health, upgrades and lives')
 local function aim(low,high)return{left=c.x>high,right=c.x<low}end
 local function phase(name)
  l.phase=name;assert(#l.events<24,'Bounded low-tree milestones')
  l.events[#l.events+1]={phase=name,target=l.target,player=state()}
 end
 local spec=screwLowSpecs[l.target]
 local bottom=r('RdY')+r('RdRadiusY')
 local released=r('RdHeld')&128==0
 if updates%8==0 then
  if #l.tail==24 then table.remove(l.tail,1)end
  l.tail[#l.tail+1]={phase=l.phase,target=l.target,player=state(),bottom=bottom,yHigh=c.yHigh}
 end
 local function support(s)
  local center=r('RdX')+256*r('RdRoomHi');local tile=c.block(center,s.plane)
  return grounded and c.yHigh==1 and r('RdGravity')==0 and bottom==s.plane
     and center-r('RdRadiusX')>=s.left and center+r('RdRadiusX')<s.rightExclusive,
         center,tile
 end
 if l.phase=='bank-high'then
  local b=aim(spec.low,spec.high)
  local good,center,tile=support(spec)
  if good and not b.left and not b.right and released and r('RdAction')==0 then
   assert(tile==0x16 or tile==0x17 or tile==0x18,'The real high canopy supports the next takeoff')
   l.highBank={player=state(),center=center,bottom=bottom,tile=tile}
   l.target='low';l.request={player=state()};phase('request');return{right=true,a=true}
  end
  b.a=not grounded and r('RdVY')>=128;return b
 end
 if l.phase=='edge'then
  local good=support(screwLowSpecs.low)
  assert(good,'Walk to the edge while still supported by the actual low tree')
  local b=aim(848,851)
  if not b.left and not b.right and released and r('RdAction')==0 then
   l.edge=state();l.target='block';l.request={player=state()}
   phase('request');return{right=true,a=true}
  end
  return b
 end
 if l.phase=='request'or l.phase=='armed'then
  if not grounded and not released and r('RdVY')>=128 and not l.request.armed then
   l.request.armed=state();phase('armed')
  end
  if l.request.armed and not grounded and not released and r('RdVY')>=128 and c.y<l.request.player.y then
   l.takeoffs=l.takeoffs or{};l.takeoffs[l.target]=state();phase('fly')
  else
   assert(updates-l.request.player.Main<12 and c.x<(l.target=='low'and 740 or 856),
          'Confirm negative-VY ascent while the actual launch ledge remains beneath the request')
   return{right=true,a=true}
  end
 end
 if l.phase=='fly'then
  local good,center,tile=support(spec)
  if good and c.x>=spec.low-8 and c.x<=spec.high+4 then
   assert(l.contacts[l.target]and updates-l.contacts[l.target].Main<=8,
          'Genuine move-down blocked carry precedes each natural landing')
   if l.target=='low'then
    assert(tile==0x16 or tile==0x17 or tile==0x18,'Actual low canopy, not an actor or synthetic floor')
    l.lowLanding={player=state(),center=center,bottom=bottom,tile=tile,contact=l.contacts.low}
    phase('edge');return{}
   end
   assert(tile==0xc1,'Natural landing on the unspent authored raw1 power block')
   l.blockLanding={player=state(),center=center,bottom=bottom,tile=tile,contact=l.contacts.block}
   phase('center-block');return{}
  end
  local b=aim(spec.low,spec.high);b.a=r('RdVY')>=128;return b
 end
 if l.phase=='center-block'then
  local good,center,tile=support(spec);assert(good and tile==0xc1,'Unspent block remains the current support')
  local b=aim(spec.low,spec.high)
  if not b.left and not b.right and released and r('RdAction')==0 then
   l.settled={entered=screwCounts('_entered'),returned=screwCounts('_returned')}
   phase('settle-block');return{}
  end
  return b
 end
 if l.phase=='settle-block'then
  local good,center,tile=support(spec)
  assert(good and tile==0xc1,'Keep the real unspent block throughout25 gameplay updates')
  local er,rr=screwCounts('_entered'),screwCounts('_returned');local enough=true
  l.post_entered={};l.post_returned={}
  for n,v in pairs(er)do
   l.post_entered[n]=v-l.settled.entered[n];l.post_returned[n]=rr[n]-l.settled.returned[n]
   if l.post_entered[n]<25 or l.post_returned[n]<25 then enough=false end
  end
  if enough then
   assert(#pending==0,'Low-tree and block workers have all returned')
   l.complete={passed=true,player=state(),entered=l.post_entered,returned=l.post_returned}
   if C.block_only then finish('natural-low-tree-and-power-block-and25');return{}end
   return
  end
  return{}
 end
 return{}
end
'''


def controller(installed, *, block_only=False, acquisition_only=False):
    assert not(block_only and acquisition_only)
    original=ORIGINAL_CONTROLLER(installed)
    assert H(original.encode())==PARENT_CONTROLLER
    text=original;edits=[]
    def edit(old,new):
        nonlocal text
        assert text.count(old)==1,(old,text.count(old))
        text=text.replace(old,new,1);edits.append((old,new))
    if block_only:
        line=text.split('\n',1)[0];edit(line,line+'\nC.block_only=true')
    if acquisition_only:
        line=text.split('\n',1)[0];edit(line,line+'\nC.acquisition_only=true')
    edit('local function screwDrive(c)',POLICY+'\nlocal function screwDrive(c)')
    edit('  local b=firstTreeTravel(c,grounded,f);if b then return b end',
         '  local b=firstTreeTravel(c,grounded,f);if b then return b end\n  local low=screwLowTravel(c,grounded,f);if low then return low end')
    needle="  elseif n=='RdHsGeometry'then\n"
    edit(needle,needle+"""   local low=gear.screw and gear.screw.low
   if low and not low.complete and p.tree.service==9 and cpu()['cpu.ps']&1==0 then
    local spec=screwLowSpecs[low.target]
    if p.tree.bottom==spec.plane and p.tree.x-r('RdRadiusX')>=spec.left
       and p.tree.x+r('RdRadiusX')<spec.rightExclusive
       and((low.target=='block'and p.tree.tile==0xc1)or(low.target~='block'
           and(p.tree.tile==0x16 or p.tree.tile==0x17 or p.tree.tile==0x18)))then
     low.contacts[low.target]=low.contacts[low.target]or{Main=updates,C=0,source=p.tree}
    end
   end
""")
    edit(' if t and not t.complete and active()and identity()and r(\'LevelNumber\')==2',
         ' if((t and not t.complete)or(gear.screw and gear.screw.low and not gear.screw.low.complete))and active()and identity()and r(\'LevelNumber\')==2')
    if acquisition_only:
        old=next(line for line in text.splitlines()if line.startswith('   credit={writer='))
        assert "entered=snapshot('_entered'),returned=snapshot('_returned')"in old
        edit(old,old+"\n   if stock=='screw-credit'then credit.screw_workers={entered=screwCounts('_entered'),returned=screwCounts('_returned')}end")
        edit(" if f.phase=='use'then\n", """ if f.phase=='use'then
  if C.acquisition_only then
   local a=f.acquisition
   assert(a and a.birth and a.mature and a.collector and a.collector.C==1
          and a.credit and a.credit.writer.after==a.credit.writer.before+1000,
          'Actual mature D3, native collector and thousand-point writer precede acquisition success')
   local er,rr=screwCounts('_entered'),screwCounts('_returned');local enough=true
   local start=assert(a.credit.screw_workers,'Actual four-worker score-writer snapshot')
   a.post_entered={};a.post_returned={}
   for n,v in pairs(er)do
    a.post_entered[n]=v-start.entered[n];a.post_returned[n]=rr[n]-start.returned[n]
    if a.post_entered[n]<25 or a.post_returned[n]<25 then enough=false end
   end
   assert(r('RdGear')==15 and r('NumberofLives')==2 and r('RdTanks')==1
          and r('RdMissiles')==5 and r('RdMaxMissiles')==5
          and r('RdHealthLo')==a.collector.before.health_raw[1]
          and r('RdHealthHi')==a.collector.before.health_raw[2],
          'Earned Screw preserves captured health, lives and resources')
   if enough then
    assert(#pending==0,'All acquisition gameplay scopes returned')
    a.complete={passed=true,player=state(),entered=a.post_entered,returned=a.post_returned}
    finish('natural-Screw-acquisition-and25')
   end
   return{}
  end
""")
        old=next(line for line in text.splitlines()if line.startswith(' local ok='))
        extra="reason=='natural-Screw-acquisition-and25'and gear.complete and gear.high.complete and gear.wall.acquisition and gear.wall.acquisition.credit and gear.screw.exterior.complete and gear.screw.trees.complete and gear.screw.low.complete and gear.screw.acquisition.complete and #completed==2 and collector and gear.acquisition and gear.acquisition.credit and born and mature and not reset and #pending==0"
        edit(old,' local ok=('+extra+')or('+old.removeprefix(' local ok=')+')')
    if block_only:
        old=next(line for line in text.splitlines()if line.startswith(' local ok='))
        extra="reason=='natural-low-tree-and-power-block-and25'and gear.complete and gear.high.complete and gear.wall.acquisition and gear.wall.acquisition.credit and gear.wall.acquisition.birth and gear.wall.acquisition.mature and gear.wall.acquisition.collector and gear.screw.exterior.complete and gear.screw.trees.complete and gear.screw.low.complete and #completed==2 and gear.acquisition and gear.acquisition.credit and not reset and #pending==0"
        edit(old,' local ok=('+extra+')or('+old.removeprefix(' local ok=')+')')
    else:
        # Keep the source running spin active while steering onto the same live
        # actor during descent; a neutral direction can select standing jump.
        edit('  local e=c.enemy()\n  if grounded and e and e.dx>8',"""  if f.trackedEnemy and not f.hit then
   local a=actor(f.trackedEnemy.slot)
   assert(a.flag==1 and a.id==f.trackedEnemy.id and a.state&32==0,'Track the same naturally live Screw target')
   if not grounded then
    f.trackedTail=f.trackedTail or{}
    if updates%8==0 then
     if #f.trackedTail==16 then table.remove(f.trackedTail,1)end
     f.trackedTail[#f.trackedTail+1]={player=state(),target=a,animation={r('RdAnimReset'),r('RdAnimIndex')}}
    end
    return{right=c.x<a.x,left=c.x>=a.x,a=r('RdVY')>=128}
   end
   f.trackedEnemy=nil
  end
  local e=c.enemy()
  if grounded and e and e.dx>8""")
        edit('   f.takeoff=f.takeoff or{player=state(),target=actor(e.slot)}',
             '   f.takeoff=f.takeoff or{player=state(),target=actor(e.slot)}\n   f.trackedEnemy={slot=e.slot,id=e.id}')
    restored=text
    for old,new in reversed(edits):
        assert restored.count(new)==1
        restored=restored.replace(new,old,1)
    assert restored==original
    LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot','dofile'))
    return text


def source(installed,limit,block_only,acquisition_only=False):
    program=controller(installed,block_only=block_only,acquisition_only=acquisition_only)
    expected=ACQUISITION_PIN if acquisition_only else PINS[block_only]
    assert H(program.encode())==expected
    original_run=Engine.run;milestones=set()
    def observed_run(raw,*args,**kwargs):
        frame=Engine.Frames.frame
        def observe(m,*args,**kwargs):
            value=frame(m,*args,**kwargs)
            if Engine.N.get(m,'LevelNumber')==2:
                x=Engine.N.get(m,'Player_X_Position')+256*Engine.N.get(m,'Player_PageLoc')
                y=Engine.N.get(m,'Player_Y_Position');gear=Engine.N.get(m,'RdGear')
                key='Screw-grant'if gear==15 else('power-block-landing'if 940<=x<=947 and y==129 and Engine.N.get(m,'Player_State')==0 else None)
                if key and key not in milestones:
                    milestones.add(key)
                    print('ROGUE_BLOCK_MILESTONE '+json.dumps(dict(kind=key,x=x,y=y,gear=gear,
                        health=[Engine.N.get(m,'RdHealthLo'),Engine.N.get(m,'RdHealthHi')],lives=Engine.N.get(m,'NumberofLives'))),flush=True)
            return value
        with patch.object(Engine.Frames,'frame',observe):
            return original_run(raw,*args,**kwargs)
    def compiled(raw,*,trees_only=False):
        assert raw is installed and trees_only==block_only
        return program
    pins=dict(PINS);pins[block_only]=expected
    with patch.object(Trees,'controller',compiled),patch.object(Trees,'PINS',pins),patch.object(Engine,'run',observed_run):
        return Trees.source(installed,limit,block_only)


def native(installed,block_only,acquisition_only=False):
    program=controller(installed,block_only=block_only,acquisition_only=acquisition_only)
    expected=ACQUISITION_PIN if acquisition_only else PINS[block_only]
    assert H(program.encode())==expected
    def compiled(raw,*,trees_only=False):
        assert raw is installed and trees_only==block_only
        return program
    pins=dict(PINS);pins[block_only]=expected
    with patch.object(Trees,'controller',compiled),patch.object(Trees,'PINS',pins):
        return Trees.native(installed,block_only)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    goal=p.add_mutually_exclusive_group()
    goal.add_argument('--block-only',action='store_true');goal.add_argument('--acquisition-only',action='store_true')
    p.add_argument('--limit',type=int,default=12500)
    a=p.parse_args();assert 10000<=a.limit<=15000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw,a.block_only,a.acquisition_only)
    else:
        def deny(*args,**kwargs):raise AssertionError('Block source check attempted files or process launch')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit,a.block_only,a.acquisition_only)
            else:
                program=controller(raw,block_only=a.block_only,acquisition_only=a.acquisition_only)
                assert H(program.encode())==(ACQUISITION_PIN if a.acquisition_only else PINS[a.block_only])
                q=dict(passed=True,route_executed=False,ROM_SHA256=PIN,controller_SHA256=H(program.encode()),outputs=0,native=False)
    print('ROGUE_BLOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
