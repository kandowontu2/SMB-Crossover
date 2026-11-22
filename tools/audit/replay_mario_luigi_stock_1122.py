"""Standard Source Mario/Luigi hidden life and Star, controller input only."""

from pathlib import Path

import current_mario_luigi_stock_1122 as Current
import replay_smb3_pickups_1122 as Observer
import replay_smb1_alts_full11_1114 as Navigation
import replay_kamikaze_mario_ground_stock_91dc_1116 as Ground
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value

R, ROM, H, PIN = Current.R, Current.ROM, Current.H, Current.PIN
POLICY = R/'tools/playthroughs/smb3_pickups_1122.lua'

LUIGI_FLOWER_CROSSING = r'''
local function luigiFlowerCrossing(c)
 local g=T.ground_route
 if not g or g.phase~='done' or c.x<1136 or c.x>=1400 then return end
 local q=T.flower_crossing
 if not q then
  q={phase='runway',since=c.update,start={x=c.x,y=c.y,vx=c.vx}}
  T.flower_crossing=q
 end
 if q.phase=='done' then return end
 assert(c.update-q.since<500,'One ordinary Luigi running crossing of the Flower row')
 local vx=c.vx>=128 and c.vx-256 or c.vx
 if q.phase=='runway' then
  -- The native negative landed at X1224 beside the low roof Goomba.
  -- Build actual running speed on the far-bank floor before taking off.
  if c.grounded and c.y>=160 and math.abs(c.x-1150)<=2 and math.abs(vx)<=1 and not c.lastA then
   q.phase='run';q.runway={update=c.update,x=c.x,y=c.y,vx=c.vx}
  else return starSteer(c,1150,2) end
 end
 if q.phase=='run' then
  assert(c.x<1192,'Fresh running jump starts left of the low roof enemy')
  if c.x>=1176 and vx>=32 and c.grounded and not c.lastA then
   q.phase='jump';q.launch={update=c.update,x=c.x,y=c.y,vx=c.vx}
   return {right=true,b=true,a=true}
  end
  return {right=true,b=true}
 end
 if q.phase=='jump' then
  if not q.apex or c.y<q.apex.y then q.apex={update=c.update,x=c.x,y=c.y} end
  if c.x<1304 then return {right=true,b=true,a=c.update-q.launch.update<36} end
  q.phase='land'
 end
 if q.phase=='land' then
  if c.grounded and c.y>=160 and c.x>=1296 and c.x<1360 then
   q.phase='done';q.landing={update=c.update,x=c.x,y=c.y,vx=c.vx}
   return {}
  end
  assert(c.x<1370,'Brake on the real floor before the second pit')
  return starSteer(c,1320,2)
 end
end
'''


def once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after, 1)


def travel():
    for path, expected in Navigation.ROUTE_PINS.items():
        assert H(path.read_bytes()) == expected, path
    nav = Navigation.NAV.read_text()
    policy = Navigation.POLICY.read_text()
    prefix = "local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n"
    policy = once(policy, prefix, '')
    return once(policy, "local travel=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_nav.lua'))",
                'local travel=(function()\n'+nav+'\nend)()')


def body():
    s = Observer.body()
    s = once(s, "r('SelectedCharacter')==17 and r('M3Variant')==C.variant",
             "r('SelectedCharacter')==C.owner and r('MarioVariant')==C.variant")
    s = once(s, "power=r('M3Form'),growth=r('M3Growth'),poof=r('M3Poof')",
             "power=r('PlayerStatus'),growth=r('GuestPowerupActive'),poof=0")
    s = once(s, 'c.char=17;', 'c.char=C.owner;')
    s = once(s, "c.lastA=r('M3Previous')&128~=0", "c.lastA=r('PreviousA_B_Buttons')&128~=0")
    s = once(s, " assert(r('M3Ready')==0xb3,'Actual SMB3 constructor remains ready')\n", '')
    s = once(s, " assert(updates<5100,'Bounded authored pickup route')",
             " assert(s.yHigh<2,'Requested hero remains above the bottom world boundary')\n assert(updates<5100,'Bounded authored pickup route')")
    s = once(s, 'if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()then',
             'if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()and s.state==0 and s.yHigh==1 then')
    s = s.replace('M3Variant', 'MarioVariant')
    s = s.replace('M3CollectPickup', 'MarioSourcePowerupCollision')
    s = s.replace('M3Movement', 'GuestMovement').replace('M3Step', 'GuestMovement')
    s = s.replace('SMB3_PICKUP_STATE', 'STANDARD_STOCK_STATE')
    s = s.replace('SMB3', 'Source Mario/Luigi').replace('m3_before', 'source_before')
    s = s.replace('native_M3_dispatches', 'native_source_dispatches')
    s = once(s, "if name=='GuestMovement'and pc<0x8000 then assert(pc==C.smc_return_pc,'Actual RAM farcall movement return')end\n ", '')
    assert 'M3' not in s and 'Ic' not in s
    return s


def policy():
    s = POLICY.read_text()
    s = once(s, 'if c.char~=17 or c.world~=0 or c.level~=0 then return ordinary end',
             'if (c.char~=0 and c.char~=8)or c.world~=0 or c.level~=0 then return ordinary end')
    s = once(s, "if c.r('M3Growth')~=0 or c.r('M3Poof')~=0 then return {}end",
             "if c.r('GuestPowerupActive')~=0 then return {}end")
    # Chasing the 1-UP above its block sends an unnecessary second jump
    # toward the first pit. Meet its ordinary descent on the safe floor.
    s = once(s, '(enemyAhead or (a.y<c.y-12 and math.abs(dx)<40))',
             '(enemyAhead or (kind==2 and a.y<c.y-12 and math.abs(dx)<40))')
    s = s.replace('SMB3_PICKUP_STATE', 'STANDARD_STOCK_STATE')
    # Reuse the Source Mario cap walkoff/ground-pit route without the old
    # Kamikaze selection or recovery prerequisites.
    ground = Ground.CONTROL.split('local function chooseStock(c)\n', 1)[0]
    ground = ground.replace('stock.ground_route', 'T.ground_route').replace("stock.phase=='travel'", "phase=='route'")
    ground = ground.replace('guestReturns', 'c.update').replace('C.stock_type', 'kind').replace('not lastA', 'not c.lastA')
    ground = ground.replace('state()', '{x=c.x,y=c.y,vx=c.vx,update=c.update}')
    s = once(s, 'return function(c)\n', ground+'\nreturn function(c)\n')
    s = once(s, ' local ordinary=base(c)\n',
             ' local ordinary=base(c)\n local crossing=sourceGroundRoute(c);if crossing then return crossing end\n')
    return s


def controller(raw, form='mario', item='1up'):
    c = Current.bindings(raw, form, item)
    names = ('GameLoop', 'GuestMovement', 'MarioSourcePowerupCollision',
             'HandlePowerUpCollision', 'PlayerHeadCollision')
    c['hooks'] = {n: c['hooks'][n] for n in names + (('LifeCredit',) if item == '1up' else ())}
    navigation, control, observer = travel(), policy(), body()
    if form == 'luigi' and item == 'star':
        control = once(control, 'return function(c)\n', LUIGI_FLOWER_CROSSING+'\nreturn function(c)\n')
        control = once(control, ' local crossing=sourceGroundRoute(c);if crossing then return crossing end\n',
                       ' local crossing=sourceGroundRoute(c);if crossing then return crossing end\n'
                       ' local flower=luigiFlowerCrossing(c);if flower then return flower end\n')
    c.update(base_policy_SHA256=H(navigation.encode()), stock_policy_SHA256=H(control.encode()),
             observer_SHA256=H(observer.encode()))
    script = '\n'.join(('local C='+value(c), 'local SMB3_PICKUP_KIND=C.stockKind',
        'local SMB3_PICKUP_BASE=(function()\n'+navigation+'\nend)()',
        'local choose=(function()\n'+control+'\nend)()', observer))
    LuaRuntime().compile(script)
    assert not any(t in script for t in ('emu.write', 'emu.setState', 'io.open', 'dofile',
                                        'saveState', 'loadState', 'takeScreenshot'))
    return script
