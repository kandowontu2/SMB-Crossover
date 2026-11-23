"""Play authored Easy 1-1 pickups with Simon Belmont and Ryu Hayabusa."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
from compose_dkjr_public_side_forward_1123 import CANDIDATE as NIGHTLY
from current_ice_stock_binding_1122 import RAM_FIELDS
from nightly_patch_guard_v1 import check
from replay_sonic_hidden_life_f7c9_1116 import value
from replay_ryan_full11_current_1114 import N, W, once
from run_mario_luigi_stock_native_1122 import H, OUT, R, ROM, preserve_script
from run_stdout_mesen_1110 import run


FORMS = {
    'simon': (5, 'SIMON BELMONT', 'Cv3Variant', 0xff, 'RosterMovement'),
    'ryu': (10, 'RYU HAYABUSA', 'FmAlts', 0x44, 'ExpandedMovement'),
}
ROUTES = {'mushroom': (0,), 'upgrades': (0, 1), 'life': (0, 3), 'star': (0, 2)}
OBSERVER = R/'tools/audit/ice_climbers_stock_observer_1122.lua'
OPENING = R/'tools/playthroughs/link_simon_ryu_policy.lua'
STOCK = R/'tools/playthroughs/megaman_proto_stock_1123.lua'


def bindings(raw, form, route):
    digest = H(raw)
    if digest != NIGHTLY:
        from compose_dkjr_side_epoch_fast_1123 import inverse
        assert H(inverse(raw)) == NIGHTLY
    char, name, variant_field, variant_mask, move = FORMS[form]
    bundle = dict(W.Symbols.bundle(), raw=raw)
    menu = W.UI.seed(bundle, char)
    assert W.UI.menu_name(menu)[0] == name and N.get(menu, 'SelectedCharacter') == char
    assert N.get(menu, variant_field) & variant_mask == 0
    fields = [n for n in RAM_FIELDS if not n.startswith('Ic')]
    fields += [variant_field, 'GuestPowerupActive', 'GuestPowerupTarget', 'GuestLegacyHurt',
               'RgDoubleJump', 'RgAttack', 'Enemy_BoundBoxCtrl', 'XgWall', 'PlayerScoreDisplay']
    if form=='ryu' and route=='upgrades':
        fields += ['InvPickup', 'InvPickupOwner', 'InvOwnedLo']
    ram = {n: W.address(bundle, n) for n in fields}

    def hook(symbol, delta=0):
        pc, at = W.address(bundle, symbol)+delta, W.location(bundle, symbol)+delta
        bank = (at-16)//8192
        assert at-16 == bank*8192+(pc&8191)
        return dict(pc=pc, tag=bank|128, offset=at-16, hex=raw[at:at+12].hex())

    hooks = {name: hook(name) for name in ('GameLoop', 'HandlePowerUpCollision', 'PlayerHeadCollision')}
    hooks['Movement'] = hook(move)
    if route == 'life':
        symbol = 'DecNumTimer'
        at = W.location(bundle, symbol)
        body = raw[at:at+48]
        life_increment = b'\xee'+ram['NumberofLives'].to_bytes(2, 'little')
        assert body.count(life_increment) == 1
        hooks['LifeCredit'] = hook(symbol, body.index(life_increment))
    navigation = ['']*32
    if char>=8:
        navigation[0] = 'down'
    for cursor in range(char&24, char):
        navigation[cursor] = 'right'
    return dict(sha=digest, form=form, route=route, char=char, name=name, slot=char, variant=0,
                variant_field=variant_field, variant_mask=variant_mask, mode_value=0,
                expected=list(ROUTES[route]), ram=ram, hooks=hooks, navigation=navigation)


def controller(raw, form, route):
    cfg = bindings(raw, form, route)
    text = OBSERVER.read_text(encoding='utf-8')

    def edit(before, after):
        nonlocal text
        text = once(text, before, after)

    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant",
         "r('SelectedCharacter')==C.char and r(C.variant_field)&C.variant_mask==0")
    edit("if r('IcVariant')~=C.variant then return pulse('select') end",
         "assert(r(C.variant_field)&C.variant_mask==0,'Original identity in menu')")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected=C.expected')
    edit("power=r('IcPower')", "power=r('PlayerStatus'),growth=r('GuestPowerupActive')")
    edit('c.poll=polls;c.char=20;', 'c.poll=updates;c.char=C.char;c.update=updates;')
    edit('c.lastA=mask&128~=0', "c.lastA=r('PreviousA_B_Buttons')&128~=0")
    edit('local lifePending', '''local lifePending
local clockInput={}
local cues={}
local function score()
 local n=0;for i=0,5 do n=n*10+r('PlayerScoreDisplay',i)end;return n
end''')
    edit('Living Ice Climber','Living requested fighter')
    edit('if #tail==6 then','if #tail==12 then')
    edit("assert(updates<5100,'Bounded pickup route')", "assert(updates<5100 and s.yHigh<2,'Bounded living pickup route')")
    edit("q.birth={actor=a,player=s}", "assert(heads[tostring(a.kind)],'Authored head bump before item birth');q.birth={actor=a,player=s}")
    edit(' local complete=true', ''' local q=checks['0']
 local stock=ROBOT_STOCK_STATE
 if C.route=='upgrades' and q.after and (r('GuestLegacyHurt')==1 or (s.status==0 and s.growth==0)) then
  finish(false,'Injury after the first pickup');return
 end
 if stock.missing and not checks[tostring(stock.kind)].collect then
  finish(false,'Authored item disappeared before collection');return
 end
 local complete=true''')
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then',
         '''if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==kind+1
     and score()>=q.collect.score_before+1000 then q.grant=s end
  if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() and s.state==0 then''')
    edit("if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')",
         "if kind==3 then assert(s.lives==q.grant.lives and (cues[64]or 0)>q.collect.life_cue,'Earned life and cue persist')")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')",
         "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Earned Star and score persist')")
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end",
         "if complete then finish(true,'Authored pickups, native credit and 25 further movement updates');return end\n clockInput=scope()and choose(context())or{}")
    edit("assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')",
         "assert((cues[32]or 0)>p.cue,'Actual new pickup cue')")
    edit("sound=r('Square2SoundQueue')}", "sound=r('Square2SoundQueue'),score_before=p.score,life_cue=cues[64]or 0}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')",
         "assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Actual source growth');return")
    edit("if p.name=='IcMovement' then","if p.name=='Movement' then")
    edit('  p.actor=a;p.before=state()', """  assert(a.state&128~=0,'Mature pickup reaches its native collector')
  q.mature=q.mature or {actor=a,player=state()}
  p.actor=a;p.before=state();p.score=score();p.cue=cues[32]or 0""")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0',
         'phase=ROBOT_STOCK_STATE or {},sound_cues=cues,controller_only=true,files=0,images=0')
    edit('local bits={a=128', """emu.addMemoryCallback(guarded('Pickup and extra-life cues',function(_,v)
 if entered and(v==32 or v==64)then cues[v]=(cues[v]or 0)+1 end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
local bits={a=128""")
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})',
         'local b=not entered and menu() or (scope() and clockInput or {})')
    edit('  entered=physical', '  entered=physical;clockInput=choose(context())')
    if form=='ryu' and route=='upgrades':
        edit("kind=r('PowerUpType',i),", "kind=r('PowerUpType',i),stamp=r('InvPickup',i),owner=r('InvPickupOwner',i),")
        edit("power=r('PlayerStatus'),growth=", "power=r('PlayerStatus'),owned=r('InvOwnedLo',C.char),growth=")
        edit("assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Actual source growth');return",
             """if a.kind==1 then
   assert(a.owner==C.char and a.stamp>=1 and a.stamp<=7,'Actual randomized Ryu upgrade')
   local bit=1<<a.stamp
   assert(p.before.owned&bit==0 and s.owned&bit~=0 and s.status==1,'Earned a new inventory upgrade')
   q.collect.upgrade=a.stamp;q.grant=s;return
  end
  assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Actual source growth');return""")
        edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end",
             """elseif kind==1 then
    assert(s.owned&(1<<q.collect.upgrade)~=0 and score()>=q.collect.score_before+1000,
     'Earned Ryu inventory upgrade and score persist')
   else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end""")
    policy = '''local firstFood={}
local flowerJump
local starPursuit
local function flowerRowRightEdge(c,x)
 local edge=x+16
 for j=1,6 do
  if c.block(edge+8,144)==0 then break end
  edge=edge+16
 end
 return edge
end
local function reachRyuFlower(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==1 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if not flowerJump then
    local edge=flowerRowRightEdge(c,x)
    flowerJump={phase='runout',started=c.update,minY=c.y,edge=edge,launch=edge+12}
    ROBOT_STOCK_STATE.ryu_flower=flowerJump
   end
   local j=flowerJump;j.minY=math.min(j.minY,c.y)
   assert(c.update-j.started<220,'Cross the safe right side of the Flower row')
   if j.phase=='runout' then
    local e=c.enemy()
    if c.grounded and e and e.dx>22 and e.dx<58 and e.y>=c.y
       and c.r('PlayerFacingDir')==1 then
     return{down=true,b=c.r('RgAttack')==0}
    end
    if c.grounded and c.y==176 and math.abs(c.x-j.launch)<=2 and c.vx==0 and not c.lastA then
     assert(c.block(c.x+8,208)~=0,'Actual floor on the right of the Flower row')
     j.phase='jump';j.first=c.update;return{a=true}
    end
    return{right=c.x<j.launch-2,left=c.x>j.launch+2}
   end
   if j.phase=='jump' then
    if c.grounded and c.y<=112 then j.phase='walk'
    elseif c.r('XgWall')~=0 then
     local probe=c.x+(c.r('PlayerFacingDir')==1 and 21 or -5)
     local lip=c.block(probe,c.y+3)
     j.attached=j.attached or {x=c.x,y=c.y,update=c.update}
     return{up=true,left=c.x>x+2,a=not c.lastA and lip==0}
    else
     -- Approach the wall within grabbing height, before the jump peaks.
     return{left=c.y<=147 and c.x>x+2,a=c.update-j.first<32}
    end
   end
   return{right=c.x<x-5,left=c.x>x+2}
  end
 end
end
local function reachSimonFlower(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==1 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if not flowerJump then
    local launch=flowerRowRightEdge(c,x)+36
    flowerJump={phase='takeoff',started=c.update,minY=c.y,trace={},launch=launch}
    ROBOT_STOCK_STATE.simon_flower=flowerJump
   end
   local j=flowerJump;j.minY=math.min(j.minY,c.y)
   assert(c.update-j.started<230,'Reach the Flower row with both jumps')
   if j.phase~='takeoff' and c.update%6==0 and #j.trace<24 then
    j.trace[#j.trace+1]={x=c.x,y=c.y,vx=c.vx,state=c.state,itemY=c.r('Enemy_Y_Position',i),
                       pad=c.r('SavedJoypadBits')}
   end
   if j.phase=='takeoff' then
    if c.grounded and c.y<=112 then
     j.phase='walk'
    elseif c.grounded and c.y==176 and math.abs(c.x-j.launch)<=2 and c.vx==0 and not c.lastA then
     j.phase='rise';j.first=c.update;return{left=true,a=true}
    else
     local e=c.enemy()
     if c.grounded and e and e.dx>25 and e.dx<55 and e.y>=c.y and c.r('PlayerFacingDir')==1 then
      return{down=e.id==6,b=c.r('RgAttack')==0}
     end
     return{right=c.x<j.launch-2,left=c.x>j.launch+2}
    end
   end
   if j.phase=='rise' then
    if c.update-j.first<14 then return{left=true,a=true}end
    if not c.grounded and not c.lastA and c.r('RgDoubleJump')~=0 then
     -- Easy Simon keeps his direction until the next jump or landing.
     j.phase='second';j.second=c.update;return{left=true,a=true}
    end
    return{left=true}
   end
   if j.phase=='second' then
    if c.grounded and c.y<=112 then j.phase='walk'
    else
     return{left=true,a=c.update-j.second<24}
    end
   end
   return{right=c.x<x-4,left=c.x>x+3}
  end
 end
end
local function followFirstFood(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==0 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   if c.update%12==0 then
    if #firstFood==16 then table.remove(firstFood,1)end
    firstFood[#firstFood+1]={x=x,y=y,player_x=c.x,player_y=c.y,update=c.update}
   end
   ROBOT_STOCK_STATE.first_food=firstFood
   -- Stay on the ground and follow the moving item off the block row.
   local goal=c.r('Enemy_State',i)<128 and 388 or x-5
   return{right=c.x<goal-2,left=c.x>goal+2}
  end
 end
end
local function catchSimonStar(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==2
     and c.r('Enemy_State',i)&128~=0 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   if not starPursuit then
    starPursuit={x=x,direction=1,attempts={}}
    ROBOT_STOCK_STATE.simon_star=starPursuit
   end
   local p=starPursuit
   if x~=p.x then p.direction=x>p.x and 1 or -1 end
   p.x=x
   if p.launch then
    local age=c.update-p.launch
    if c.grounded and age>4 then p.launch=nil
    else return{right=p.jumpDirection==1,left=p.jumpDirection==-1,a=age<27}end
   end
   local ahead=(x-c.x)*p.direction
   if c.grounded and not c.lastA and y+17<c.y and ahead>=5 and ahead<=21 then
    p.launch=c.update;p.jumpDirection=p.direction
    assert(#p.attempts<12,'Bounded Star jump attempts')
    p.attempts[#p.attempts+1]={x=c.x,y=c.y,update=c.update,itemX=x,itemY=y,direction=p.direction}
    return{right=p.jumpDirection==1,left=p.jumpDirection==-1,a=true}
   end
   -- Easy Simon keeps launch velocity. Let an approaching Star come within
   -- jump range before committing to its direction of travel.
   return{right=ahead>21 and p.direction==1,left=ahead>21 and p.direction==-1}
  end
 end
end
local function choose(c)
 if c.growth~=0 then return{}end
 if c.status==0 then
  local stockState=ROBOT_STOCK_STATE
  if stockState.kind~=0 and (C.route=='life' or C.route=='star') then return stock(c)end
  if C.char==5 then
   local food=followFirstFood(c)
   if food then return food end
  end
  return opening(c)
 end
 if C.route=='mushroom'then return{}end
 if C.route=='upgrades' and c.status==1 then
  local flower=(C.char==5 and reachSimonFlower or reachRyuFlower)(c)
  if flower then return flower end
 end
 local ordinary=stock(c)
 if C.char==5 and C.route=='star' then return catchSimonStar(c) or ordinary end
 return ordinary
end'''
    stock = once(STOCK.read_text(encoding='utf-8'), 'local distance=goal-c.x-speed(c)/5',
                 'local distance=goal-c.x')
    script = '\n'.join(('local C='+value(cfg), 'local opening=(function()\n'+OPENING.read_text()+'\nend)()',
                        'local base=opening', 'local stock=(function()\n'+stock+'\nend)()', policy, text))
    assert not any(t in script for t in ('emu.write', 'emu.setState', 'io.open', 'dofile',
                                         'saveState', 'loadState', 'takeScreenshot'))
    LuaRuntime().compile(script)
    return script.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', choices=tuple(FORMS), default='simon')
    parser.add_argument('--route', choices=tuple(ROUTES), default='mushroom')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    program = controller(raw, args.form, args.route)
    print('FIGHTER STOCK SOURCE '+json.dumps(dict(form=args.form, route=args.route,
          ROM_SHA256=H(raw), controller_SHA256=H(program))), flush=True)
    if not args.run:
        return 0
    guard = check(ROM)
    candidate, script = OUT/'candidate.nes', OUT/'controller.lua'
    assert guard['ROM_sha256'] == H(raw) and not guard['matching_patch_files']
    assert set(OUT.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    try:
        with preserve_script(script, candidate, raw) as stage:
            stage(program)
            result = run(script, ROM, OUT/'capture', H(raw), 180)
        assert result['script_SHA256'] == H(program)
        assert result['outputs_written'] == 0 and not result['images']
    finally:
        assert ROM.read_bytes() == raw and check(ROM) == guard
    print('FIGHTER STOCK NATIVE '+json.dumps(result,separators=(',',':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
