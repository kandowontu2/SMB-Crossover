"""Input-only Spring Ball continuation after the retained earned-Screw proof.

``extend(text)`` accepts the full bound Screw combat Lua.  It preserves that
proof as a checkpoint, crosses the remaining stock 1-3 platforms, then seeks
the next actual power question block in 1-4 (left480/top96).  No emulator,
ROM writer, saved state or artificial pickup is available from this module.
The newly authored route remains a candidate until root runs it.
"""

from hashlib import sha256
import re

from check_ff_stdout_controller_source_1110 import LuaRuntime


TIMEOUT = 540

POLICY = r'''
-- Authored 1-3 tree tops and actual native horizontal platform actors.
local springLegs={
 {kind='platform',y=128,min=1312,max=1488},
 {kind='platform',y=144,min=1424,max=1632},
 {left=1568,right=1632,plane=176},
 {left=1664,right=1792,plane=112},
 {left=1808,right=1856,plane=208},
 {left=1856,right=1920,plane=144},
 {left=1952,right=2016,plane=144},
 {kind='platform',y=96,min=2016,max=2208},
 {left=2208,right=2240,plane=144},
 {left=2240,right=2272,plane=112},
 {left=2272,right=2304,plane=80}
}
local function springPhase(s,name)
 s.phase=name;s.entered=updates
 assert(#s.events<64,'Bounded Spring route milestones')
 local q={phase=name,leg=s.leg,level=r('LevelNumber'),player=state()}
 s.events[#s.events+1]=q
 print('SMB_NATIVE_PROGRESS '..json({milestone='Spring-'..name,leg=s.leg,
       Main=updates,level=q.level,player=q.player}))
end
local function springBox(c,node)
 if node.kind~='platform'then return node end
 local chosen
 for i=0,4 do
  local a=actor(i)
  if a.flag>0 and a.flag<128 and a.id==0x28 and a.state<128
     and r('Enemy_Y_HighPos',i)==1 and a.y==node.y and a.x>=node.min and a.x<node.max then
   if not chosen or math.abs(a.x-c.x)<math.abs(chosen.actor.x-c.x)then
    local control=r('Enemy_BoundBoxCtrl',i)
    assert(control==5 or control==6,'Actual stock large-platform bounding-box owner')
    local width=control==6 and 48 or 32
    chosen={left=a.x,right=a.x+width,plane=a.y,actor=a,kind='platform',boxControl=control}
   end
  end
 end
 return chosen
end
local function springSupport(c,box)
 if not box then return false end
 local center=r('RdX')+256*r('RdRoomHi');local bottom=r('RdY')+r('RdRadiusY')
 local yes=c.grounded and c.yHigh==1 and r('RdGravity')==0
           and math.abs(bottom-box.plane)<=1
           and center-r('RdRadiusX')>=box.left and center+r('RdRadiusX')<box.right
 if box.actor then return yes and r('RdFrozenSupport')~=0 end
 local tile=c.block(center,box.plane)
 return yes and tile~=0 and tile~=0x23 and tile~=0x26 and tile~=0xc2
end
local function springAim(c,low,high)return{left=c.x>high,right=c.x<low}end
local function springFoot(c)
 local y=r('RdY')+r('RdRadiusY')+1
 local x=r('RdX')+256*r('RdRoomHi')
 return c.yHigh==1 and c.grounded and r('RdGravity')==0 and y<240
        and c.block(x,y)~=0 and c.block(x,y)~=0x23 and c.block(x,y)~=0x26,
        {x=x,y=y,tile=y<240 and c.block(x,y)or 0}
end
local function springDrive(c)
 local s=gear.spring
 assert(s and gear.screw.complete and identity()and c.world==0
        and(c.level==2 or c.level==3)and r('NumberofLives')==2,
        'Continue the real earned-Screw checkpoint into the next ordinary stage')
 assert(updates-s.started<6500,'Bounded ordinary route to Spring Ball')
 assert(r('RdHealthLo')+r('RdHealthHi')>0 and r('RdTanks')==1
        and r('RdMissiles')==5 and r('RdMaxMissiles')==5,
        'Spring route keeps positive native health, the tank, ammo and both lives')
 assert(r('RdGear')==(s.acquisition and 31 or(stock=='spring-credit'and 31 or 15)),
        'Only the actual next pickup may add the Spring bit')
 if not active()then return{}end
 if updates%12==0 then
  if #s.tail==24 then table.remove(s.tail,1)end
  local a={};for i=0,5 do local v=actor(i);if v.flag>0 then a[#a+1]=v end end
  s.tail[#s.tail+1]={phase=s.phase,leg=s.leg,level=c.level,player=state(),camera=c.camera,
                    bottom=r('RdY')+r('RdRadiusY'),actors=a}
 end
 local released=r('RdHeld')&128==0
 if c.level==2 then
  assert(r('RdGear')==15 and c.areaType==1,'Actual 1-3 after the earned spin encounter')
  if s.phase=='stage-exit'then
   local b=gearTravel(c);b.b=false;return b
  end
  local target=springBox(c,springLegs[s.leg])
  local current=springBox(c,s.current)
  if s.phase=='bank'then
   assert(updates-s.entered<360,'Bounded genuine platform launch preparation')
   assert(current and springSupport(c,current),'Current natural canopy or platform still supports the launch')
   -- Run close to a real edge, then consume an A release before jumping.
   local x=current.actor and(current.right-26)or(current.right-24)
   local b=springAim(c,x,x+3)
   if not b.left and not b.right and released and r('RdAction')==0 and target
      and target.left-c.x<190 and target.right>c.x+16 then
    s.request={player=state(),target=target,current=current}
    springPhase(s,'request');return{right=true,a=true}
   end
   return b
  end
  if s.phase=='request'then
   if not c.grounded and not released and r('RdVY')>=128 and c.y<s.request.player.y then
    s.request.takeoff=state();springPhase(s,'flight')
   else
    assert(updates-s.entered<12,'Observe real negative-VY takeoff before leaving native support')
    return{right=true,a=true}
   end
  end
  if s.phase=='flight'then
   assert(updates-s.entered<220,'Bounded actual tree or horizontal-platform landing')
   assert(target,'Naturally spawned horizontal target remains loaded throughout the crossing')
   if springSupport(c,target)then
    s.landings[#s.landings+1]={leg=s.leg,player=state(),target=target,request=s.request}
    s.current=springLegs[s.leg];s.leg=s.leg+1;s.request=nil
    if s.leg>#springLegs then springPhase(s,'stage-exit')
    else springPhase(s,'bank')end
    return{}
   end
   local low=target.left+math.min(16,math.floor((target.right-target.left)/2)-8)
   local b=springAim(c,low,low+3);b.a=r('RdVY')>=128;b.b=updates%8==0;return b
  end
  return{}
 end
 -- This is a genuine level transition; no stage selector, savestate or gear seed.
 if not s.castle then
  assert(s.phase=='stage-exit'and c.areaType==3,'Normal 1-3 flag/castle reaches stock 1-4')
  s.castle={player=state(),areaOffset=r('AreaAddrsLOffset')}
  springPhase(s,'castle-travel')
 end
 assert(c.areaType==3 and r('AreaAddrsLOffset')==s.castle.areaOffset,'Keep the actual loaded 1-4')
 if s.phase=='castle-travel'then
  if c.x>=432 then
   s.cache={}
   for y=32,224,16 do local row={y=y,tiles={}}
    for x=400,544,16 do row.tiles[#row.tiles+1]=c.block(x,y)end
    s.cache[#s.cache+1]=row
   end
   assert(c.block(480,96)==0xc1,'Stock 1-4 power question block left480/top96 remains unspent')
   springPhase(s,'block-align')
  else local b=gearTravel(c);b.b=false;return b end
 end
 if stock=='spring-credit'then return{}end
 if s.phase=='block-align'then
  local b=springAim(c,480,483)
  if not b.left and not b.right and springFoot(c)and released and r('RdAction')==0 then
   s.headRequest=state();springPhase(s,'block-jump');return{a=true}
  end
  if not springFoot(c)then b.a=r('RdVY')>=128 end
  return b
 end
 if s.phase=='block-jump'then
  if born then springPhase(s,'collect-rise');return{}end
  assert(updates-s.entered<120,'Actual standing high jump reveals the castle power block')
  return{a=r('RdVY')>=128 or updates-s.entered<4}
 end
 if s.phase=='collect-rise'then
  assert(born and born.actor.private==212,'Actual typed Spring Ball emerges from the contacted block')
  if r('RdAction')==3 then return{up=true}end
  if springFoot(c)and released then
   s.collectRequest=state();springPhase(s,'collect-jump');return{a=true}
  end
  return{}
 end
 if s.phase=='collect-jump'then
  assert(updates-s.entered<180,'Bounded natural jump into the mature Spring Ball')
  if collector then return{}end
  -- Touch the item from the open right side without trying to jump through
  -- the used block. Record the actual cache if this approach cannot reach it.
  local a=born.actor
  local low=c.y<80 and 480 or 500
  local b=springAim(c,low,low+3)
  b.a=r('RdVY')>=128
  if springFoot(c)and released then s.collectRequest=state();b.a=true end
  return b
 end
 if s.phase=='spring-earned'then
  if r('RdAction')==3 then return{up=true}end
  if springFoot(c)and released and r('RdAction')==0 then
   s.proofFloor={player=state(),foot=select(2,springFoot(c))}
   springPhase(s,'morph-proof');return{down=true}
  end
  return{}
 end
 if s.phase=='morph-proof'then
  assert(updates-s.entered<40,'Ordinary Down enters Morph Ball after the earned upgrade')
  if r('RdAction')~=3 then return{down=true}end
  if springFoot(c)and released then
   s.ballRequest={player=state(),foot=select(2,springFoot(c)),sourceY=r('RdY')}
   springPhase(s,'ball-request');return{a=true}
  end
  return{}
 end
 if s.phase=='ball-request'then
  assert(updates-s.entered<12,'Fresh supported ball A must invoke the earned Spring effect')
  if s.springCue and r('RdAction')==3 and r('RdVY')>=128 and r('RdGravity')==0x12
     and r('RdY')<s.ballRequest.sourceY then
   s.launch={player=state(),gravity=r('RdGravity'),cue=s.springCue}
   s.apex=r('RdY');springPhase(s,'ball-flight');return{a=true}
  end
  return{a=true}
 end
 if s.phase=='ball-flight'then
  assert(updates-s.entered<180,'Earned ball jump returns to its actual floor')
  s.apex=math.min(s.apex,r('RdY'))
  if springFoot(c)and r('RdAction')==3 and updates-s.launch.player.Main>10 then
   assert(s.ballRequest.sourceY-s.apex>32,'Actual Spring Ball rises from its supported origin')
   s.ballLanding={player=state(),entered=screwCounts('_entered'),returned=screwCounts('_returned')}
   springPhase(s,'settled');return{}
  end
  return{a=r('RdVY')>=128}
 end
 if s.phase=='settled'then
  assert(springFoot(c)and r('RdAction')==3,'The real floor supports the ball after landing')
  local er,rr=screwCounts('_entered'),screwCounts('_returned');local enough=true
  s.post_entered={};s.post_returned={}
  for n,v in pairs(er)do
   s.post_entered[n]=v-s.ballLanding.entered[n];s.post_returned[n]=rr[n]-s.ballLanding.returned[n]
   if s.post_entered[n]<25 or s.post_returned[n]<25 then enough=false end
  end
  if enough then
   assert(#pending==0 and s.acquisition and s.acquisition.credit and s.launch,
          'Actual Spring collection, score, ball launch, landing and completed workers')
   s.complete=true;finish('natural-Spring-Ball-acquisition-jump-and25')
  end
  return{}
 end
 return{}
end
'''


def extend(text):
    """Append the candidate route to a full current-bound Screw combat Lua."""
    original = text
    changes = []

    def edit(old, new):
        nonlocal text
        assert text.count(old) == 1, (old, text.count(old))
        text = text.replace(old, new, 1)
        changes.append((old, new))

    edit('local function screwDrive(c)', POLICY + '\nlocal function screwDrive(c)')
    edit('local function screwDrive(c)\n local f=gear.screw',
         'local function screwDrive(c)\n local f=gear.screw\n if gear.spring then return springDrive(c)end')
    edit("f.complete=true;finish('natural-Screw-body-defeat-and-landing');return{}", """f.complete=true
     gear.spring={started=updates,entered=updates,phase='bank',leg=1,
                  current={left=1216,right=1312,plane=96},baseline=state(),events={},tail={},landings={}}
     stock='spring';born=nil;mature=nil;collector=nil;credit=nil
     print('SMB_NATIVE_PROGRESS '..json({milestone='Screw-checkpoint-before-Spring',Main=updates,player=state()}))
     return{}""")
    edit("or(gear.screw and r('LevelNumber')==2))",
         "or(gear.screw and r('LevelNumber')==2)or(gear.spring and r('LevelNumber')==3))")
    edit("gear.screw and 211 or(gear.wall and 210 or(gear.high and 209 or 208))",
         "gear.spring and 212 or(gear.screw and 211 or(gear.wall and 210 or(gear.high and 209 or 208)))")
    edit("gear.screw and 211 or(gear.wall and 210 or(gear.high and 209 or(gear.started and 208 or 217)))",
         "gear.spring and 212 or(gear.screw and 211 or(gear.wall and 210 or(gear.high and 209 or(gear.started and 208 or 217))))")
    edit("a.x==(gear.screw and 944 or(gear.wall and 2400 or 1104))",
         "a.x==(gear.spring and 480 or(gear.screw and 944 or(gear.wall and 2400 or 1104)))")
    edit("p.actor.private==(gear.screw and 211 or(gear.wall and 210 or 209))",
         "p.actor.private==(gear.spring and 212 or(gear.screw and 211 or(gear.wall and 210 or 209)))")
    edit("stock=='screw-credit'and 15 or(stock=='wall-jump-credit'and 7 or(stock=='high-jump-credit'and 3 or(stock=='bomb-credit'and 1 or 0)))",
         "stock=='spring-credit'and 31 or(stock=='screw-credit'and 15 or(stock=='wall-jump-credit'and 7 or(stock=='high-jump-credit'and 3 or(stock=='bomb-credit'and 1 or 0))))")
    edit("   elseif stock=='screw-credit'then", """   elseif stock=='spring-credit'then
    assert(gear.spring and born.actor.private==212 and collector.actor.private==212,
           'The seventh genuine acquisition is typed D4 Spring Ball')
    gear.spring.acquisition={birth=born,mature=mature,collector=collector,credit=credit}
    stock='spring-earned';credit=nil;springPhase(gear.spring,'spring-earned')
   elseif stock=='screw-credit'then""")
    edit("stock=='screw'and 3 or(stock=='wall-jump'and 2 or(stock=='high-jump'and 1 or(stock=='bomb'and 0 or 9)))",
         "stock=='spring'and 4 or(stock=='screw'and 3 or(stock=='wall-jump'and 2 or(stock=='high-jump'and 1 or(stock=='bomb'and 0 or 9))))")
    edit("stock=='screw'and 15 or(stock=='wall-jump'and 7 or(stock=='high-jump'and 3 or(stock=='bomb'and 1 or 0)))",
         "stock=='spring'and 31 or(stock=='screw'and 15 or(stock=='wall-jump'and 7 or(stock=='high-jump'and 3 or(stock=='bomb'and 1 or 0))))")
    edit('a.private==208 or a.private==209 or a.private==210 or a.private==211)',
         'a.private==208 or a.private==209 or a.private==210 or a.private==211 or a.private==212)')
    edit("if gear.started and address==C.ram.RdSfx+3", """if gear.spring and gear.spring.phase=='ball-request'and address==C.ram.RdSfx+3
    and value==2 and r('RdAction')==3 and r('RdFresh')&128~=0 and r('RdGear')==31 then
  assert(r('RdVY')==0xfc,'Actual original Spring writes its upward speed before its cue')
  gear.spring.springCue={Main=updates,PC=cpu()['cpu.pc'],value=value,player=state()}
 end
 if gear.started and address==C.ram.RdSfx+3""")
    # Further real Screw contacts are allowed while crossing the tree stage;
    # preserve the first qualified combat witness as the immutable checkpoint.
    edit("local a=actor(cpu()['cpu.x'])\n if a.flag==1",
         "local a=actor(cpu()['cpu.x'])\n if f.complete then return end\n if a.flag==1")
    old = next(line for line in text.splitlines() if line.startswith(' local ok='))
    extra = ("reason=='natural-Spring-Ball-acquisition-jump-and25'and gear.complete "
             "and gear.high.complete and gear.wall.acquisition and gear.screw.complete "
             "and gear.spring and gear.spring.complete and gear.spring.acquisition "
             "and gear.spring.acquisition.credit and gear.spring.launch and #completed==2 "
             "and not reset and #pending==0")
    edit(old, ' local ok=(' + extra + ')or(' + old.removeprefix(' local ok=') + ')')
    edit('updates<16000', 'updates<22000')
    edit('if frame>=28000 then', 'if frame>=42000 then')
    restored = text
    for old, new in reversed(changes):
        assert restored.count(new) == 1
        restored = restored.replace(new, old, 1)
    assert restored == original
    LuaRuntime().compile(text)
    executable = '\n'.join(line.split('--', 1)[0] for line in text.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)', executable)
    return text


def metadata(text):
    """Compact declaration for the root-owned runner; no execution claim."""
    return dict(controller_SHA256=sha256(text.encode()).hexdigest(),
                controller_bytes=len(text.encode()), input_only=True, route_executed=False,
                native_Mesen=False, target=dict(stage='1-4', left=480, top=96,
                                                typed_item=0xd4, before_gear=15, after_gear=31),
                source_sha256=sha256(POLICY.encode()).hexdigest(), outputs=0)
