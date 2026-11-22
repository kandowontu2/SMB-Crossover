"""Separate natural D1 Mushroom / randomly selected native suit observer."""

from pathlib import Path

from check_ff_stdout_controller_source_1110 import LuaRuntime
import current_smb3_upgrades_binding_1122 as Current
import replay_smb3_pickups_1122 as Stock
from replay_sonic_hidden_life_f7c9_1116 import value

R, ROM, H, PIN = Current.R, Current.ROM, Current.H, Current.PIN
POLICY = R / 'tools/playthroughs/smb3_upgrades_1122.lua'
STOCK_SHA = '2fb881163a10ab54b2a2dc9d8222c5bdcaee494e2ed8c2f9d950cf28db87a79c'


ACTOR = r'''
local function actor(i)
 local native=r('PowerUpType',i);local stamp=r('InvPickup',i);local owner=r('InvPickupOwner',i)
 local logical=native
 if owner==17 and stamp==0xd1 then logical=0
 elseif owner==17 and stamp>=0xd2 and stamp<=0xd6 then logical=1 end
 return {slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=logical,native_kind=native,
  stamp=stamp,owner=owner,state=r('Enemy_State',i),rise_phase=r('InvRisePhase',i),
  x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),yHigh=r('Enemy_Y_HighPos',i)}
end
'''

AFTER_MAIN = r'''
local function afterMain()
 if not entered then return end
 updates=updates+1
 local s=state();s.score=score()
 local live={};for i=0,5 do local a=actor(i);if a.flag>0 and a.flag<128 then live[#live+1]=a end end
 if #tail==12 then table.remove(tail,1)end;tail[#tail+1]={player=s,mask=mask,actors=live}
 assert(identity()and s.world==0 and s.level==0 and s.engine~=11 and s.lives==2,'Living requested SMB3 upgrade route, two original lives')
 assert(r('M3Ready')==0xb3 and updates<5100,'Ready current SMB3 and bounded upgrade route')
 for _,kind in ipairs(expected)do
  local q=checks[tostring(kind)]
  if q.collect and not q.after then
   assert(s.power==q.collect.target,'Actual collected form retained until its checkpoint')
   if not q.score_credit and s.score>=q.collect.score_before+1000 then
    q.score_credit={before=q.collect.score_before,after=s.score,player=s}
   end
   if not q.effects_finished and s.growth==0 and s.poof==0 then
    assert((q.growth_ticks or 0)==q.collect.scheduled_growth and(q.poof_ticks or 0)==q.collect.scheduled_poof,
     'All actual source transformation decrements observed')
    q.effects_finished=s
   end
   if q.effects_finished and q.score_credit and not q.resume then q.resume=s end
   if q.resume and s.motor-q.resume.motor>=25 and scope()then
    assert(s.size==0 and s.status==math.min(q.collect.target,2),'Completed source form published to native status/size')
    q.after=s
    if kind==0 then SMB3_UPGRADE_PROGRESS.mushroom=true else SMB3_UPGRADE_PROGRESS.suit=true end
   end
  end
 end
 local complete=true;for _,kind in ipairs(expected)do complete=complete and checks[tostring(kind)].after~=nil end
 if complete then
  assert(counts.M3Step_entries==counts.M3Step_returns and counts.M3Movement_entries==counts.M3Movement_returns,
   'Balanced completed original movement and native step returns')
  finish(true,'Natural Mushroom/suit, actual effects and25 resumed original steps per checkpoint');return
 end
 clockInput=scope()and choose(context())or{}
end
'''

COLLECTED = r'''
local function collected(p)
 local a=p.actor;local q=checks[tostring(a.kind)]
 assert(q and q.prepare and q.birth and q.mature and not q.collect,'Actual prepared, risen and mature private actor')
 assert(a.owner==17 and a.stamp==q.prepare.actor.stamp and(q.rise_ticks or 0)==48,'Authentic owner/stamp and48 admitted rise calls')
 assert(r('Enemy_Flag',a.slot)==0 and r('FloateyNum_Control',a.slot)==6,'Actual private erase and1000-point popup')
 assert((soundCounts[32]or 0)>p.cue32_before and(counts.M3CollectPickup_entries or 0)>p.m3_before,'New cue and reached native private collector')
 local s=state();local target=a.stamp-0xd0
 assert(s.power==target and s.lives==p.before.lives,'Actual private stamp applied, no life change')
 local growth=p.before.power==0 and 47 or 0
 local poof=p.before.power~=0 and target~=2 and 24 or 0
 assert(s.growth==growth and s.poof==poof,'Actual source growth/poof scheduled')
 q.collect={actor=a,before=p.before,after=s,target=target,suit=C.suit_names[target],
  literal_Fire_Flower=a.stamp==0xd2,popup=6,boxes=p.boxes,score_before=p.score_before,
  scheduled_growth=growth,scheduled_poof=poof}
 q.growth_ticks=0;q.poof_ticks=0
 if a.kind==1 then SMB3_UPGRADE_PROGRESS.suit_collected=true end
end
local function prepared(p)
 local a=actor(p.prepare.slot);local q=checks[tostring(p.prepare.kind)]
 assert(q and not q.prepare and heads[tostring(p.prepare.kind)],'Real authored head before private preparation')
 assert(a.id==46 and a.flag>0 and a.owner==17 and a.native_kind==1 and a.state==1 and a.rise_phase==0,'Native initial private item state')
 if p.prepare.kind==0 then assert(p.prepare.before.power==0 and a.stamp==0xd1,'Small-to-Super D1 choice')
 else
  assert(p.prepare.before.power>=1 and a.stamp>=0xd2 and a.stamp<=0xd6 and p.prepare.rng~=nil,'Naturally selected powered suit')
  assert(a.stamp==0xd0+2+(p.prepare.rng%5),'Actual RNG read selects the recorded suit')
 end
 q.prepare={actor=a,before=p.prepare.before,rng_at_source_read=p.prepare.rng}
 q.birth={actor=a,player=state()};q.rise_ticks=0;activePreparation=nil
end
local function rose(p)
 local q=checks[tostring(p.rising.kind)]
 if not q or not q.birth then return end
 if p.rising.timer==0 then q.rise_ticks=q.rise_ticks+1 end
 local a=actor(p.rising.slot)
 if a.state&128~=0 and not q.mature then
  assert(q.rise_ticks==48,'Actual48 admitted source rise ticks')
  assert(a.native_kind==(a.stamp==0xd1 and 0 or 1),'D1 changes native type only at maturity')
  q.mature={actor=a,player=state()}
 end
end
local function effectReturned(p)
 local q=p.effect.check
 if p.name=='M3Graphics'and p.effect.growth>0 and p.effect.poof==0 then
  assert(r('M3Growth')==p.effect.growth-1,'Actual graphics growth decrement')
  q.growth_ticks=q.growth_ticks+1
 elseif p.name=='M3DrawWorld'and p.effect.poof>0 then
  assert(r('M3Poof')==p.effect.poof-1,'Actual draw-world poof decrement')
  q.poof_ticks=q.poof_ticks+1
 end
end
'''

EXTRA_ENTRY = r'''
 if name=='M3PreparePickup'then
  local a=actor(cpu['cpu.x']);local before=state()
  local kind=before.power==0 and 0 or 1
  local expectedX=kind==0 and 336 or 1248
  if a.id==46 and a.native_kind<2 then
   assert(math.abs(a.x-expectedX)<=2,'Expected natural336 Mushroom or1248 powered suit block')
   assert(checks[tostring(kind)],'Requested upgrade family')
   p.prepare={slot=a.slot,kind=kind,before=before};activePreparation=p.prepare
  end
 elseif name=='M3RisePickup'then
  local a=actor(cpu['cpu.x']);local q=checks[tostring(a.kind)]
  if a.id==46 and a.owner==17 and q and q.birth and q.birth.actor.slot==a.slot and a.state<128 then
   p.rising={kind=a.kind,slot=a.slot,timer=r('TimerControl')}
  end
 elseif name=='M3Graphics'or name=='M3DrawWorld'then
  for _,kind in ipairs(expected)do
   local q=checks[tostring(kind)]
   if q.collect and not q.after then p.effect={check=q,growth=r('M3Growth'),poof=r('M3Poof')};break end
  end
 end
'''


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)


def body(*, targeted=False):
    assert H(Path(Stock.__file__).read_bytes()) == STOCK_SHA
    s = Stock.body()
    s = once(s, 'local expected={C.stockKind}', "local expected=C.route=='mushroom'and{0}or{0,1}")
    s = once(s, 'local lifePending', 'local lifePending,activePreparation')
    lo, hi = s.index('local function actor(i)'), s.index('local function state()')
    s = s[:lo] + ACTOR + '\n' + s[hi:]
    s = once(s, "lives=r('NumberofLives'),star=", "size=r('PlayerSize'),lives=r('NumberofLives'),star=")
    s = once(s, 'phase=SMB3_PICKUP_STATE or {}', 'phase=SMB3_UPGRADE_STATE or {},logical_item_policy=C.logical_item_classifier')
    lo, hi = s.index('local function afterMain()'), s.index('local function collected(p)')
    s = s[:lo] + AFTER_MAIN + '\n' + s[hi:]
    lo, hi = s.index('local function collected(p)'), s.index('local function settle()')
    s = s[:lo] + COLLECTED + '\n' + s[hi:]
    s = once(s, 'elseif p.actor then collected(p)',
             'elseif p.prepare then prepared(p)\n  elseif p.rising then rose(p)\n  elseif p.effect then effectReturned(p)\n  elseif p.actor then collected(p)')
    s = once(s, " if name=='LifeCredit' then", " if name=='M3RNGRead'then\n  assert(activePreparation and activePreparation.kind==1,'RNG belongs to current natural suit preparation')\n  activePreparation.rng=r('PseudoRandomBitReg',2);return\n end\n if name=='LifeCredit' then")
    s = once(s, " if name=='HandlePowerUpCollision' then", EXTRA_ENTRY + "\n if name=='HandlePowerUpCollision' then")
    s = once(s, '  entered=physical;clockInput=choose(context())',
             "  assert(r('M3Form')==0,'Real cold Small form before any earned upgrade')\n  entered=physical;clockInput=choose(context())")
    if targeted:
        s = once(s, 'logical_item_policy=C.logical_item_classifier',
                 'logical_item_policy=C.logical_item_classifier,requested_suit=C.target_suit_name,requested_stamp=C.target_stamp')
        s = once(s, " if name=='M3RNGRead'then", """ if name=='TargetPauseInput'then
  local q=SMB3_UPGRADE_STATE.rng
  if q and SMB3_UPGRADE_STATE.phase=='rng-unpause'and r('GamePauseStatus')&129==1
     and r('GamePauseTimer')==0 and r('SavedJoypad1Bits')&144==144 then
   local prediction=assert(q.prediction,'A current predicted draw precedes actual Start+A consumption')
   assert(not q.accepted,'Only one genuine target unpause')
   local random={};for i=0,6 do
    random[i+1]=r('PseudoRandomBitReg',i)
    assert(random[i+1]==prediction.rng_before[i+1],'Actual consumed Start+A uses the latest refreshed LFSR origin')
   end
   prediction.scheduled_read_before_update=prediction.read_before_update
   prediction.read_before_update=updates+q.jump_steps-1
   q.accepted={before_update=updates,input=r('SavedJoypad1Bits'),random=random,
    pause=r('GamePauseStatus'),pause_timer=r('GamePauseTimer'),player=state()}
  end
  return
 end
 if name=='M3RNGRead'then""")
        s = once(s, "  activePreparation.rng=r('PseudoRandomBitReg',2);return",
                 """  local prediction=assert(SMB3_UPGRADE_STATE.rng and SMB3_UPGRADE_STATE.rng.prediction,'Real pause prediction before suit RNG read')
  activePreparation.rng=r('PseudoRandomBitReg',2)
  assert(SMB3_UPGRADE_STATE.rng.accepted and r('GamePauseStatus')&1==0 and updates==prediction.read_before_update,
   'Unpaused actual RNG source read occurs at the predicted native head clock')
  assert(activePreparation.rng==prediction.draw and activePreparation.rng%5+2==C.target_suit,
   'Actual naturally evolving RNG byte equals the predicted requested suit')
  activePreparation.prediction=prediction;return""")
        s = once(s, " q.prepare={actor=a,before=p.prepare.before,rng_at_source_read=p.prepare.rng}",
                 """ if p.prepare.kind==1 then
  assert(a.stamp==C.target_stamp and p.prepare.prediction,'Actual source stamps the explicitly requested suit')
  SMB3_UPGRADE_PROGRESS.suit_prepared=true
 end
 q.prepare={actor=a,before=p.prepare.before,rng_at_source_read=p.prepare.rng,
  prediction=p.prepare.prediction,requested_suit=p.prepare.kind==1 and C.target_suit_name or nil}""")
        s = once(s, ' local growth=p.before.power==0 and 47 or 0',
                 " if a.kind==1 then assert(target==C.target_suit and a.stamp==C.target_stamp,'Natural physical collection applies the requested suit')end\n local growth=p.before.power==0 and 47 or 0")
        s = once(s, ' mask=0;for k,v in pairs(bits) do if b[k] then mask=mask|v end end',
                 """ if entered and scope()then
  local refreshed=SMB3_UPGRADE_POLL(context())
  if refreshed then b=refreshed;clockInput=refreshed end
 end
 mask=0;for k,v in pairs(bits) do if b[k] then mask=mask|v end end""")
    assert 'SMB3_PICKUP_STATE' not in s
    return s


def controller(raw, form='peach3', route='mushroom-suit', *, mode='easy', suit=None):
    config = Current.bindings(raw, form, route, mode=mode, suit=suit)
    navigation = Stock.Navigation.policy()
    policy = POLICY.read_text(encoding='utf-8')
    observer = body(targeted=suit is not None)
    config.update(base_policy_SHA256=H(navigation.encode()), upgrade_policy_SHA256=H(policy.encode()),
                  observer_SHA256=H(observer.encode()))
    text = '\n'.join((
        'local C=' + value(config), "local ROSTER_CONFIG={name='smb3'}",
        'local SMB3_UPGRADE_PROGRESS={}', 'local SMB3_UPGRADE_MODE=C.route',
        'local SMB3_UPGRADE_TARGET=C.target_suit',
        'local SMB3_UPGRADE_BASE=(function()\n' + navigation + '\nend)()',
        'local choose=(function()\n' + policy + '\nend)()', observer,
    ))
    LuaRuntime().compile(text)
    assert not any(word in text for word in ('emu.write', 'emu.setState', 'io.open', 'dofile', 'saveState', 'loadState', 'takeScreenshot'))
    return text
