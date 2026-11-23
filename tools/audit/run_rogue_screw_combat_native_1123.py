"""Separate earned-Screw combat approach; no game bytes or actor seeds."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import run_rogue_screw_block_native_1123 as Block
import run_stdout_mesen_1110 as Stdout
from check_ff_stdout_controller_source_1110 import LuaRuntime


H, ROM, PIN = Block.H, Block.ROM, Block.PIN
PARENT_CONTROLLER = Block.PINS[False]
ORIGINAL_CONTROLLER = Block.controller
STOMP_CONTROLLER = 'c12824c42b3b0fc7cfec2a6654cd32a8750198522f985630da56d58664a7a7ce'
STOMP_SOURCE_RECEIPT = '1270bbec518850f497f4c837e30c98037ef9bb33a62f49ac13327f2752cfbcc1'
SHORT_ARC_CONTROLLER = 'f0290d30745de8d2c9dc8de1fd3c139a4bc34ce9e414aa7a3405714e3c1dc761'
SHORT_ARC_SOURCE_RECEIPT = 'b95b4b0d92edc5f115a5ed354564e07f73de12b8c2249a2fb46c9f00c9401c5c'
WALL_OBSERVER_CONTROLLER = '53f6e4077450b4fa36958c7da4a6b39362b572ecd84eecb02ecf1aafc1ecd6eb'
WALL_OBSERVER_SOURCE_RECEIPT = 'ed8cc2f2d1b636dce6dae4c5a01fddeef17ac14df8ed0d1642a1b1be6b1a557e'
CONTROLLER = '8ed50b13523a50c72cf1991665b4532632cf71d232ed9a31cfc4084c044ec303'

POLICY = r'''
local screwCombatSpecs={
 power={left=944,rightExclusive=960,plane=160},
 high={left=960,rightExclusive=1024,plane=80,low=984,high=987},
 middle={left=1120,rightExclusive=1168,plane=144,low=1136,high=1139}
}
local function screwCombatTravel(c,grounded,f)
 if not f.combatApproach then
  f.combatApproach={started=updates,phase='bank-power',target='power',contacts={},events={},tail={}}
 end
 local t=f.combatApproach
 if t.ready then return end
 assert(updates-t.started<650,'Bounded natural approach to a live Screw target')
 local function aim(low,high)return{left=c.x>high,right=c.x<low}end
 local function phase(name)
  t.phase=name;assert(#t.events<32,'Bounded combat approach milestones')
  t.events[#t.events+1]={phase=name,player=state(),target=t.target}
 end
 local function support(spec)
  local center=r('RdX')+256*r('RdRoomHi');local bottom=r('RdY')+r('RdRadiusY')
  return grounded and c.yHigh==1 and r('RdGravity')==0 and bottom==spec.plane
         and center-r('RdRadiusX')>=spec.left and center+r('RdRadiusX')<spec.rightExclusive,
         center,bottom,c.block(center,spec.plane)
 end
 local function targetActor()
  local chosen
  for i=0,5 do
   local a=actor(i)
   if a.flag==1 and a.id==6 and a.state==0 and a.x>=1244 and a.x<1312 and a.y==72
      and r('Enemy_Y_HighPos',i)==1 and r('Enemy_BoundBoxCtrl',i)<13
      and r('MmEnemyHealthLo',i)>0 then
    if not chosen or a.x>chosen.x then chosen=a end
   end
  end
  return chosen
 end
 if updates%8==0 then
  if #t.tail==20 then table.remove(t.tail,1)end
  local actors={};for i=0,5 do local a=actor(i);if a.flag>0 then actors[#actors+1]=a end end
  t.tail[#t.tail+1]={phase=t.phase,player=state(),yHigh=c.yHigh,actors=actors,
                   animation={r('RdAnimReset'),r('RdAnimIndex')}}
 end
 local released=r('RdHeld')&128==0
 if t.phase=='bank-power'then
  local good,center,bottom,tile=support(screwCombatSpecs.power)
  assert(good and(tile==0xc4 or tile==0xc1),'Start the combat approach on the actual power block')
  local b=aim(944,947)
  if not b.left and not b.right and released and r('RdAction')==0 then
   t.powerBank={player=state(),center=center,bottom=bottom,tile=tile}
   t.request={player=state()};t.target='high';phase('vertical-high');return{a=true}
  end
  return b
 end
 if t.phase=='vertical-high'then
  if not grounded and not released and r('RdVY')>=128 then
   t.request.armed=t.request.armed or state()
   if c.y<t.request.player.y then t.verticalTakeoff=t.verticalTakeoff or state()end
  end
  assert(updates-t.request.player.Main<60,'Vertical jump clears the upper canopy before moving underneath it')
  if t.verticalTakeoff and c.yHigh==1 and c.y<=45 then phase('fly-high');return{right=true,a=true}end
  return{a=true}
 end
 if t.phase=='fly-high'or t.phase=='fly-middle'then
  local spec=screwCombatSpecs[t.target]
  local good,center,bottom,tile=support(spec)
  if good and c.x>=spec.low-8 and c.x<=spec.high+4 then
   assert(t.contacts[t.target]and updates-t.contacts[t.target].Main<=8
          and(tile==0x16 or tile==0x17 or tile==0x18),'Real canopy collision precedes natural combat-route landing')
   t.landings=t.landings or{}
   t.landings[t.target]={player=state(),center=center,bottom=bottom,tile=tile,contact=t.contacts[t.target]}
   if t.target=='high'then phase('edge-high')else phase('prepare-running')end
   return{}
  end
  local b=aim(spec.low,spec.high);b.a=r('RdVY')>=128;return b
 end
 if t.phase=='edge-high'then
  assert(support(screwCombatSpecs.high),'The real high canopy still supports the launch edge')
  local b=aim(1008,1011)
  if not b.left and not b.right and released and r('RdAction')==0 then
   t.highEdge=state();t.request={player=state()};t.target='middle'
   phase('request-middle');return{right=true,a=true}
  end
  return b
 end
 if t.phase=='request-middle'then
  if not grounded and not released and r('RdVY')>=128 then
   t.request.armed=t.request.armed or state()
   if c.y<t.request.player.y then t.middleTakeoff=state();phase('fly-middle')end
  end
  if t.phase=='request-middle'then
   assert(updates-t.request.player.Main<12 and c.x<1020,'Real middle-tree jump before leaving the high ledge')
   return{right=true,a=true}
  end
  return{right=true,a=true}
 end
 if t.phase=='prepare-running'then
  assert(support(screwCombatSpecs.middle),'Natural middle-tree support before the running spin')
  local b=aim(1136,1139)
  if not b.left and not b.right and released and r('RdAction')==0 then
   local a=targetActor()
   if a then t.targetActor=a;phase('run-to-spin');return{right=true}end
  end
  return b
 end
 if t.phase=='run-to-spin'then
  assert(support(screwCombatSpecs.middle),'The real middle tree supports the running launch')
  if c.x<1150 then return{right=true}end
  local a=targetActor()
  assert(a and c.x<=1155 and released and r('RdAction')==1 and r('RdHeld')&3==1,
         'Live grounded Goomba and genuine running source pose precede fresh A')
  t.targetActor=a;t.attackRequest=state();f.screwShortStart=updates
  phase('attack-launch');return{right=true,a=true}
 end
 if t.phase=='attack-launch'then
  if not grounded and not released and r('RdVY')>=128 and c.y<t.attackRequest.y then
   assert(r('RdAction')==1,'Actual running jump retains the source Screw action')
   local a=actor(t.targetActor.slot)
   assert(a.flag==1 and a.id==6 and r('MmEnemyHealthLo',a.slot)>0,'Same naturally spawned target remains live')
   f.takeoff={player=state(),target=a};f.trackedEnemy={slot=a.slot,id=a.id}
   t.runningTakeoff=state();t.ready={player=state(),target=a};phase('fight')
   return
  end
  assert(updates-t.attackRequest.Main<10 and c.x<1164,'Confirmed running ascent before leaving the middle tree')
  return{right=true,a=true}
 end
 return{}
end
'''


WALL_APPROACH = r'''
 if t.phase=='wall-approach'then
  local a=actor(t.targetActor.slot)
  assert(a.flag==1 and a.id==6 and a.state==0 and r('MmEnemyHealthLo',a.slot)>0,
         'The same naturally spawned Goomba remains live above the real canopy lip')
  assert(not grounded and c.x<=1205 and c.yHigh==1 and c.y<126,
         'The running short arc stays below the canopy edge without landing')
  if c.x>=1202 and a.x<=1216 and released and t.wallProbe and updates-t.wallProbe.Main<=3 then
   assert(c.y>=72 and c.y<=111 and r('RdAction')==1 and r('RdHeld')&3==1,
          'Airborne running pose and released A meet the real canopy wall')
   t.wallRequest={player=state(),target=a,probe=t.wallProbe};f.screwShortStart=updates
   phase('wall-press');return{right=true,a=true}
  end
  assert(updates-t.attackRequest.Main<76,'Bounded approach to the live Goomba before it leaves its canopy')
  return{right=true,a=r('RdVY')>=128 and updates-f.screwShortStart<22}
 end
 if t.phase=='wall-press'then
  if t.wallGate and not grounded and not released and r('RdVY')>=128 and c.y<t.wallRequest.player.y then
   assert(r('RdAction')==1 and r('RdGear')==15,'Earned Wall Jump retains the real running Screw action')
   local a=actor(t.targetActor.slot)
   assert(a.flag==1 and a.id==6 and r('MmEnemyHealthLo',a.slot)>0,'Same live Goomba at actual wall launch')
   f.trackedEnemy={slot=a.slot,id=a.id};t.wallTakeoff=state()
   t.ready={player=state(),target=a,gate=t.wallGate};phase('fight');return
  end
  assert(updates-t.wallRequest.player.Main<10 and c.x<=1208,'Actual fresh A and upward Wall Jump before body contact')
  return{right=true,a=true}
 end
'''


def controller(installed, *, historical_short_arc=False, historical_wall_observer=False):
    assert not(historical_short_arc and historical_wall_observer)
    original=ORIGINAL_CONTROLLER(installed)
    assert H(original.encode())==PARENT_CONTROLLER
    text=original;edits=[]
    def edit(old,new):
        nonlocal text
        assert text.count(old)==1,(old,text.count(old))
        text=text.replace(old,new,1);edits.append((old,new))
    owner,_=Block.Trees.images(installed);b=Block.Trees.Base.bundle(owner)[2]
    W=Block.Trees.W;lua=Block.Trees.Base.Base.J.Previous.Previous.Frozen.lua
    line=text.split('\n',1)[0]
    edit(line,line+'\nfor n,at in pairs('+lua({n:W.address(b,n)for n in('Enemy_Y_HighPos','Enemy_BoundBoxCtrl')})+')do C.ram[n]=at end')
    edit('local function screwDrive(c)',POLICY+'\nlocal function screwDrive(c)')
    edit('  if f.hit then', '  local approach=screwCombatTravel(c,grounded,f);if approach then return approach end\n  if f.hit then')
    needle="  elseif n=='RdHsGeometry'then\n"
    edit(needle,needle+"""   local combat=gear.screw and gear.screw.combatApproach
   if combat and not combat.ready and p.tree.service==9 and cpu()['cpu.ps']&1==0 then
    local spec=screwCombatSpecs[combat.target]
    if p.tree.bottom==spec.plane and p.tree.x-r('RdRadiusX')>=spec.left
       and p.tree.x+r('RdRadiusX')<spec.rightExclusive
       and(p.tree.tile==0x16 or p.tree.tile==0x17 or p.tree.tile==0x18 or p.tree.tile==0xc4)then
     combat.contacts[combat.target]=combat.contacts[combat.target]or{Main=updates,C=0,source=p.tree}
    end
   end
""")
    old="or(gear.screw and gear.screw.low and not gear.screw.low.complete))and active()"
    new="or(gear.screw and gear.screw.low and not gear.screw.low.complete)or(gear.screw and gear.screw.combatApproach and not gear.screw.combatApproach.ready))and active()"
    edit(old,new)
    edit("return{right=c.x<a.x,left=c.x>=a.x,a=r('RdVY')>=128}",
         "return{right=c.x<a.x,left=c.x>=a.x,a=r('RdVY')>=128 and updates-f.screwShortStart<24}")
    # The former longer arc made a real stock stomp before body contact.  Keep
    # that exact controller reconstructible while lowering the contact arc.
    assert H(text.replace('updates-f.screwShortStart<24','updates-f.screwShortStart<30').encode())==STOMP_CONTROLLER
    assert H(text.encode())==SHORT_ARC_CONTROLLER
    if not historical_short_arc:
        old="""   f.takeoff={player=state(),target=a};f.trackedEnemy={slot=a.slot,id=a.id}
   t.runningTakeoff=state();t.ready={player=state(),target=a};phase('fight')
   return"""
        new="""   f.takeoff={player=state(),target=a};t.runningTakeoff=state()
   phase('wall-approach');return{right=true,a=true}"""
        edit(old,new)
        edit(" return{}\nend\n\nlocal function screwDrive(c)",WALL_APPROACH+" return{}\nend\n\nlocal function screwDrive(c)")
        edit('updates-f.screwShortStart<24','updates-f.screwShortStart<30')
        needle="          tile=context().block(x,bottom),player=state()}"
        edit(needle,needle+"""
  if r('RdHostService')==16 then
   local probeX=x+r('RdRadiusX')+1;local y=r('RdY');local rr=r('RdRadiusY')
   p.wall={x=probeX,y=y,top=y-rr,bottom=y+rr-1,player=state(),
           tiles={context().block(probeX,y-rr),context().block(probeX,y),context().block(probeX,y+rr-1)}}
  end""")
        needle="  elseif n=='RdHsGeometry'then\n"
        edit(needle,needle+"""   local wall=gear.screw and gear.screw.combatApproach
   if wall and wall.phase=='wall-approach'and p.tree.service==16 and cpu()['cpu.ps']&1==0 then
    assert(p.wall and p.wall.x>=1216 and p.wall.x<1232,'Actual right probe touches the authored canopy face')
    local solid=false;for _,v in ipairs(p.wall.tiles)do if v==0x16 or v==0x17 or v==0x18 then solid=true end end
    assert(solid,'Wall Jump uses real canopy tiles rather than a live actor or hidden support')
    wall.wallProbe={Main=updates,C=0,source=p.wall}
   end
""")
        old="and r('RdHostService')==9 then enter('RdHsGeometry')end"
        new="and(r('RdHostService')==9 or(gear.screw.combatApproach and gear.screw.combatApproach.phase=='wall-approach'and r('RdHostService')==16))then enter('RdHsGeometry')end"
        edit(old,new)
        edit('local age=0',"""hook('WallJumpGate',function()
 local t=gear.screw and gear.screw.combatApproach
 if not t or t.phase~='wall-press'or not active()or not identity()then return end
 assert(not t.wallGate and r('RdAction')==1 and r('RdGear')==15 and r('RdFresh')&128~=0
        and r('RdHeld')&3==1 and r('Player_State')~=0 and cpu()['cpu.ps']&1==0,
        'Actual source WallJumpGate accepts fresh toward-wall A while airborne')
 t.wallGate={player=state(),C=0,probe=t.wallRequest.probe}
end)
local age=0""")
        assert H(text.encode())==WALL_OBSERVER_CONTROLLER
        if not historical_wall_observer:
            edit("if r('RdHostService')==16 then", "if r('RdHostService')==16 or r('RdHostService')==11 then")
            edit("and p.tree.service==16 and cpu()['cpu.ps']&1==0 then",
                 "and(p.tree.service==16 or p.tree.service==11)and cpu()['cpu.ps']&1==0 then")
            edit("gear.screw.combatApproach.phase=='wall-approach'and r('RdHostService')==16",
                 "gear.screw.combatApproach.phase=='wall-approach'and(r('RdHostService')==16 or r('RdHostService')==11)")
            edit("   local b=gearTravel(c);b.b=false;return b\n  end\n  if f.trackedEnemy",
                 "   return{right=c.x<1240,left=c.x>1243,a=r('RdVY')>=128 and updates-f.screwShortStart<30}\n  end\n  if f.trackedEnemy")
            old="combatApproach and not gear.screw.combatApproach.ready))and active()"
            new="combatApproach and not gear.screw.combatApproach.ready)or(gear.screw and gear.screw.hit and not gear.screw.landing))and active()"
            edit(old,new)
            needle="  elseif n=='RdHsGeometry'then\n"
            edit(needle,needle+"""   local hit=gear.screw and gear.screw.hit
   if hit and p.tree.service==9 and cpu()['cpu.ps']&1==0 and p.tree.bottom==96
      and p.tree.x-r('RdRadiusX')>=1216 and p.tree.x+r('RdRadiusX')<1312
      and(p.tree.tile==0x16 or p.tree.tile==0x17 or p.tree.tile==0x18)then
    gear.screw.combatApproach.postHitContact=gear.screw.combatApproach.postHitContact or{Main=updates,C=0,source=p.tree}
   end
""")
            needle="   if grounded then\n    f.landing=f.landing or"
            edit(needle,"""   if grounded then
    local pc=f.combatApproach.postHitContact;local center=r('RdX')+256*r('RdRoomHi')
    assert(pc and(f.landing or updates-pc.Main<=8)and c.y==65 and r('RdY')+r('RdRadiusY')==96
           and center-r('RdRadiusX')>=1216 and center+r('RdRadiusX')<1312,
           'Actual post-Screw down collision and natural supported canopy landing')
    f.landing=f.landing or""")
    restored=text
    for old,new in reversed(edits):
        assert restored.count(new)==1
        restored=restored.replace(new,old,1)
    assert restored==original
    LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot','dofile'))
    return text


def source(installed,limit):
    program=controller(installed);assert H(program.encode())==CONTROLLER
    def compiled(raw,*,block_only=False,acquisition_only=False):
        assert raw is installed and not block_only and not acquisition_only
        return program
    pins=dict(Block.PINS);pins[False]=CONTROLLER
    with patch.object(Block,'controller',compiled),patch.object(Block,'PINS',pins):
        return Block.source(installed,limit,False)


def native(installed):
    program=controller(installed);assert H(program.encode())==CONTROLLER
    def compiled(raw,*,block_only=False,acquisition_only=False):
        assert raw is installed and not block_only and not acquisition_only
        return program
    previous=Stdout.run
    def long_run(script,rom,output,expected,timeout,*args,**kwargs):
        assert expected==PIN and timeout==240 and not kwargs.pop('long_no_capture',False)
        return previous(script,rom,output,expected,345,*args,long_no_capture=True,**kwargs)
    pins=dict(Block.PINS);pins[False]=CONTROLLER
    with patch.object(Block,'controller',compiled),patch.object(Block,'PINS',pins),patch.object(Stdout,'run',long_run):
        return Block.native(installed,False)


def main():
    p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group()
    mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=12500);a=p.parse_args();assert 10500<=a.limit<=15000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw)
    else:
        def deny(*args,**kwargs):raise AssertionError('Combat source check attempted files or process launch')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit)
            else:
                program=controller(raw);assert H(program.encode())==CONTROLLER
                q=dict(passed=True,route_executed=False,controller_SHA256=CONTROLLER,ROM_SHA256=PIN,outputs=0,native=False)
    print('ROGUE_COMBAT '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
