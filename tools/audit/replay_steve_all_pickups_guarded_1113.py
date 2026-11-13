"""Controller-only four-pickup retry with life invariants and ordinary defense.

The original1869 controller and its physical failure remain frozen. This
derivative changes only controller input/observation, never ROM or runtime RAM.
"""
from hashlib import sha256
import argparse
import json
from unittest.mock import patch

import check_steve_star_oneup_1113 as S
import steve_armor_idle_1113 as Idle


ORIGINAL = '1869b7a86f51e29fe423e27ef9916ecbafa249e9b0a32d3dfff7d211687a5e05'


def controller(raw, *, defend=False, clear_path=False):
    assert not(defend and clear_path)
    text = S.controller(raw)
    assert sha256(text.encode()).hexdigest() == ORIGINAL
    bundle = S.W.Symbols.bundle()
    bundle['raw'] = raw
    fields = {name:S.W.address(bundle,name) for name in
              ('JnInjury','KillPlayer','NumberofLives','Enemy_Y_HighPos')}
    for name in ('JnInjury','KillPlayer'):
        fields[name+'Bank'] = (S.W.location(bundle,name)-16)//8192

    def change(before,after):
        nonlocal text
        assert text.count(before) == 1,before
        text = text.replace(before,after)

    change('local pickupFields={','local guardFields={'+','.join(f'{k}={v}' for k,v in fields.items())+'}\nlocal pickupFields={')
    change('oneupAwarded=false}', 'oneupAwarded=false,lifeEvents={},injuryEvents={},defenseUpdates=0}')
    insertion = '''
local function guardSnapshot(kind,value)
  local slot=emu.getState()['cpu.x']
  local enemy='null'
  if slot>=0 and slot<6 then
    enemy=string.format('{"slot":%d,"id":%d,"flag":%d,"state":%d,"x":%d,"y":%d}',slot,
      read(pickupFields.Enemy_ID+slot),read(pickupFields.Enemy_Flag+slot),
      read(pickupFields.Enemy_State+slot),
      read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot),
      read(pickupFields.Enemy_Y_Position+slot))
  end
  return string.format('{"kind":"%s","value":%d,"phase":"%s","projection":%d,"x":%d,"y":%d,"health":%d,"lives":%d,"enemy":%s}',
    kind,value or -1,phase,projections,x(),read(0xbd),read(0x5f30),read(guardFields.NumberofLives),enemy)
end
for _,name in ipairs({'JnInjury','KillPlayer'})do
  emu.addMemoryCallback(guard(function()
    local at=guardFields[name]
    local mapped=emu.convertAddress(at)
    if natural.authenticated and mapped and mapped.memType==emu.memType.nesPrgRom
      and mapped.address==guardFields[name..'Bank']*8192+(at&8191)then
      if #natural.injuryEvents<8 then
        natural.injuryEvents[#natural.injuryEvents+1]=guardSnapshot(name)
      end
    end
  end),emu.callbackType.exec,guardFields[name])
end
emu.addMemoryCallback(guard(function(_,value)
  if not natural.authenticated then return end
  if #natural.lifeEvents<8 then natural.lifeEvents[#natural.lifeEvents+1]=guardSnapshot('life-write',value)end
  assert(value==2 or value==3,'Only the initial and singly earned life totals')
  assert(not natural.oneupAwarded or value==3,'Unexpected life loss after the earned1UP')
end),emu.callbackType.write,guardFields.NumberofLives)
'''
    change('local function pickupPhase(nextPhase,bits)',insertion+'\nlocal function pickupPhase(nextPhase,bits)')
    change("  assert(natural.authenticated and active() and read(0x5f30)>0,'Living authenticated Steve pickup route')",
           "  assert(natural.authenticated and active() and read(0x5f30)>0,'Living authenticated Steve pickup route')\n"
           "  local expected=natural.oneupAwarded and 3 or 2\n"
           "  assert(read(guardFields.NumberofLives)==expected or (natural.index==2 and read(guardFields.NumberofLives)==3),'No life loss during natural item phases')")
    change('"runtime_authenticated":%s}',
           '"runtime_authenticated":%s,"life_events":[%s],"injury_events":[%s],"defense_updates":%d,"chased_actor":%s}')
    change('tostring(natural.authenticated)))',
           'tostring(natural.authenticated),table.concat(natural.lifeEvents,","),table.concat(natural.injuryEvents,","),natural.defenseUpdates,natural.actorReport or "null"))')
    change('''  return {flag=flag,state=read(pickupFields.Enemy_State+slot),
    x=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot),
    y=read(pickupFields.Enemy_Y_Position+slot),tag=read(pickupFields.InvPickup+slot)}''',
           '''  local actor={flag=flag,state=read(pickupFields.Enemy_State+slot),
    x=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot),
    y=read(pickupFields.Enemy_Y_Position+slot),tag=read(pickupFields.InvPickup+slot)}
  natural.actorReport=string.format('{"flag":%d,"state":%d,"x":%d,"y":%d,"tag":%d}',
    actor.flag,actor.state,actor.x,actor.y,actor.tag)
  return actor''')
    if defend:
        change('  local gap=actor.x-x()-8\n', '''  local nearest,delta=nil,nil
  for slot=0,5 do
    local flag,id=read(pickupFields.Enemy_Flag+slot),read(pickupFields.Enemy_ID+slot)
    local dx=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot)-x()
    local dy=read(pickupFields.Enemy_Y_Position+slot)-read(0xbd)
    if flag>0 and flag<128 and id<21 and read(pickupFields.Enemy_State+slot)&32==0
      and read(guardFields.Enemy_Y_HighPos+slot)==1 and math.abs(dx)<72 and math.abs(dy)<32
      and (delta==nil or math.abs(dx)<math.abs(delta))then nearest,delta=slot,dx end
  end
  if nearest~=nil then
    natural.defenseUpdates=natural.defenseUpdates+1
    local move=delta>=0 and 1 or 2
    if math.abs(delta)<=32 and projections%12~=0 then move=0 end
    return move|(projections%12<6 and 64 or 0)
  end
  local gap=actor.x-x()-8
''')
        # Ordinary defensive stops cost travel time. This is a controller
        # horizon, not a change to item speed, hitboxes or collection criteria.
        change("assert(age<180,'Native moving-item chase bound')",
               "assert(age<600,'Native moving-item chase bound')")
    if clear_path:
        change('defenseUpdates=0}', 'defenseUpdates=0,pathCombat={}}')
        change('"chased_actor":%s}', '"chased_actor":%s,"path_combat":[%s]}')
        change('natural.actorReport or "null"))',
               'natural.actorReport or "null",table.concat(natural.pathCombat,",")))')
        change('local function naturalTick()', '''
-- Clear approaching ground enemies before releasing the moving Star. The
-- earlier stationary-defense experiment waited until the Star was escaping.
-- These are ordinary neutral/fresh-B inputs, not changes to NPC or shot data.
local function clearStarPath()
  if natural.index~=4 then return false end
  local combat=natural.pathGuard
  if not combat then
    if x()<1430 or x()>=natural.target or read(0xbd)~=176 or read(0x1e)~=0 then return false end
    local nearest=73
    for slot=0,5 do
      local flag,id=read(pickupFields.Enemy_Flag+slot),read(pickupFields.Enemy_ID+slot)
      local dx=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot)-x()
      if flag>0 and flag<128 and id<12 and read(pickupFields.Enemy_State+slot)&32==0
        and read(guardFields.Enemy_Y_HighPos+slot)==1 and dx>0 and dx<nearest
        and math.abs(read(pickupFields.Enemy_Y_Position+slot)-read(0xbd))<=16 then
        nearest=dx
        combat={slot=slot,id=id,start=projections,initialX=x(),strike=nil}
      end
    end
    if not combat then return false end
    natural.pathGuard=combat
    pad=0
  end
  local slot=combat.slot
  local flag,state=read(pickupFields.Enemy_Flag+slot),read(pickupFields.Enemy_State+slot)
  assert(flag>0 and read(pickupFields.Enemy_ID+slot)==combat.id,'Tracked path enemy retained until native defeat')
  if state&32~=0 then
    assert(read(pickupFields.FloateyNum_Control+slot)>0,'Path punch native defeat and score')
    natural.pathCombat[#natural.pathCombat+1]=string.format(
      '{"slot":%d,"id":%d,"start":%d,"defeat":%d,"player_x":%d,"enemy_x":%d,"health":%d,"lives":%d}',
      slot,combat.id,combat.start,projections,x(),
      read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot),
      read(0x5f30),read(guardFields.NumberofLives))
    natural.pathGuard=nil
    beginFull()
    return true
  end
  assert(projections-combat.start<220,'Ordinary path-punch encounter bound')
  local gap=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot)-x()
  if projections-combat.start<6 or gap>32 then pad=0
  else
    if not combat.strike then combat.strike=projections end
    pad=(projections-combat.strike)%20<10 and 64 or 0
  end
  return true
end

local function naturalTick()''')
        change("  elseif phase=='natural-traverse'then\n",
               "  elseif phase=='natural-traverse'then\n    if clearStarPath()then return end\n")
        change('''  local gap=actor.x-x()-8
  if gap>4 then return 1 end
  if gap< -4 then return 2 end
  return 0''','''  local gap=actor.x-x()-8
  local direction=gap>4 and 1 or gap< -4 and 2 or 0
  if not natural.starJumpStart and read(0xbd)==176 and read(0x1e)==0 and read(0x5c92)==0 then
    natural.starJumpStart=projections
  end
  local jump=natural.starJumpStart and projections-natural.starJumpStart<9 and 128 or 0
  return direction|jump''')
    assert 'emu.write' not in text and 'emu.setState' not in text
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def source_check(raw, *, defend=False, clear_path=False):
    text = controller(raw,defend=defend,clear_path=clear_path)
    image,info = Idle.proposal(Idle.reverse(raw))
    assert image == raw
    with patch.object(S.Natural,'controller',lambda _raw,_info:text):
        result = S.Natural.controller_cpu(image,info,limit=3000)
    result.update(original_controller_SHA256=ORIGINAL,defensive_controls=defend,
                  clear_path_controls=clear_path,ROM_changes=0,state_seeds=0)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--observe-only',action='store_true',help='Observe the frozen controls (default).')
    modes.add_argument('--defend',action='store_true',help='Experimental stationary defense; frozen negative, not a qualified replay.')
    modes.add_argument('--clear-star-path',action='store_true',help='Punch approach enemies and jump toward the emerging Star.')
    args = parser.parse_args()
    raw = S.Native.Live.Art.D.HOST.read_bytes()
    print(json.dumps(source_check(raw,defend=args.defend,clear_path=args.clear_star_path),sort_keys=True),flush=True)
