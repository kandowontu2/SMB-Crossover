"""Earn Fire Dragon Ball in Easy 1-1 and use it against a live enemy."""

import argparse
import json
from unittest.mock import patch

import compose_dkjr_head_bridge_current_1123 as Nightly
import run_simon_ryu_stock_1123 as Stock


DRAGON_ROUTE = r'''
local dragon={phase='earn'}
local function dragonInput(c)
 local pause=c.r('GamePauseStatus')&1~=0
 if dragon.phase=='pause' and pause then dragon.phase='equip' end
 if dragon.phase=='equip' and c.r('InvSelected',10)==4 then dragon.phase='resume' end
 if dragon.phase=='resume' and not pause then dragon.phase='approach' end
 if dragon.phase=='pause' or dragon.phase=='resume' then return{start=true}end
 if dragon.phase=='equip' then return{right=true}end
 if dragon.phase=='done' then return{}end
 if dragon.phase=='fire' then return{select=c.update==dragon.fireAt}end
 if dragon.phase=='approach' then
  if dragon.lastUpdate==c.update then return dragon.input end
  dragon.lastUpdate=c.update
  local e=c.enemy()
  if e and math.abs(e.dx)<=90 and c.update%4==0 then
   dragon.approach=dragon.approach or {}
   if #dragon.approach>=20 then table.remove(dragon.approach,1)end
   table.insert(dragon.approach,{x=c.x,y=c.y,vy=c.vy,foe=e,facing=c.r('PlayerFacingDir')})
  end
  -- Let the last jump descend over the first line of bricks. The throw
  -- releases a few updates later, when Ryu is close to floor height.
  if c.x>=1900 and c.y>=136 and c.vy>0 and c.vy<128
      and e and e.dx>=32 and e.dx<=50 and e.y>=175 and e.y<=189
      and c.r('PlayerFacingDir')==1 and c.r('RgAttack')==0 then
   dragon.phase='fire';dragon.target=e;dragon.fireAt=c.update;dragon.fireX=c.x
   dragon.ammo=c.r('InvAmmo',160)
   return{select=true}
  end
  local b=opening(c);b.b=false;dragon.input=b;return b
 end
 return{}
end
'''

OBSERVE = r'''
 if complete and dragon.phase=='earn' then
  assert(checks['1'].collect.upgrade==4,'Earned Fire Dragon Ball')
  dragon.selectedAfterPickup=r('InvSelected',10)
  dragon.phase=dragon.selectedAfterPickup==4 and 'approach' or 'pause'
  dragon.earned=s;dragon.ammo=r('InvAmmo',160)
  assert(dragon.ammo>=5,'Earned enough Ninpo for one shot')
  ROBOT_STOCK_STATE.fire_dragon=dragon
 end
 if dragon.earned then
  assert(updates-dragon.earned.update<550,'Bounded Fire Dragon Ball use')
  assert(s.lives==2 and s.status==1,'Keep the earned upgrade and both lives')
 end
 if dragon.fireAt then
  assert(r('InvSelected',10)==4 and s.owned&16~=0,'Fire Dragon Ball equipped')
  if updates-dragon.fireAt<=16 then
   dragon.throw=dragon.throw or {}
   table.insert(dragon.throw,{update=updates,x=s.x,y=s.y,ammo=r('InvAmmo',160),
     attack=r('RgAttack'),age=r('RgAttackAge'),kind=r('RgAttackKind'),
     pad=r('SavedJoypadBits'),wall=r('XgWall')})
  end
  for i=0,9 do
   if r('RgShotType',i)==40 then
    local x=pos('RgShotX','RgShotPage',i)
    if not dragon.shot then
     assert(r('InvAmmo',160)==dragon.ammo-5,'Fire Dragon Ball spends five Ninpo')
     dragon.shot={age=r('RgShotAge',i),x=x,y=r('RgShotY',i),slot=i,update=updates}
    end
    if x>dragon.shot.x then dragon.advance={x=x,update=updates} end
    if not dragon.defeat and r('RgShotImpact',i)>0 and dragon.advance then
     local e=actor(dragon.target.slot)
     if e.id==dragon.target.id and e.state&32~=0 and math.abs(e.x-x)<=32 then
      dragon.defeat=e;dragon.hitUpdate=updates;dragon.hitMotor=motor;dragon.phase='done'
     end
    end
   end
  end
  assert(dragon.defeat or updates-dragon.fireAt<70,'Fired at a live enemy')
  if dragon.defeat and motor-dragon.hitMotor>=25 then
   finish(true,'Earned, equipped and used Fire Dragon Ball against an authored enemy');return
  end
 end
 clockInput=scope()and choose(context())or{}
'''


def controller(raw):
    parent = Nightly.inverse(raw)
    cfg = Stock.bindings(parent, 'ryu', 'upgrades')
    bundle = dict(Stock.W.Symbols.bundle(), raw=raw)
    cfg['sha'] = Stock.H(raw)
    for hook in cfg['hooks'].values():
        offset = 16 + hook['offset']
        data = bytes.fromhex(hook['hex'])
        assert raw[offset:offset + len(data)] == data
    for name in ('GamePauseStatus', 'InvSelected', 'InvAmmo', 'RgShotType', 'RgShotAge',
                 'RgShotX', 'RgShotPage', 'RgShotY', 'RgShotImpact', 'RgAttackAge', 'RgAttackKind'):
        cfg['ram'][name] = Stock.W.address(bundle, name)
    with patch.object(Stock, 'bindings', return_value=cfg):
        source = Stock.controller(raw, 'ryu', 'upgrades').decode()
    source = Stock.once(source, "assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact published ROM')",
                        DRAGON_ROUTE + "\nassert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact published ROM')")
    source = Stock.once(source,
                        " if complete then finish(true,'Authored pickups, native credit and 25 further movement updates');return end\n"
                        " clockInput=scope()and choose(context())or{}", OBSERVE)
    source = Stock.once(source, ' local b=not entered and menu() or (scope() and clockInput or {})',
                        ' local b=not entered and menu() or (dragon.earned and dragonInput(context()))\n'
                        '  or (scope() and clockInput or {})')
    assert not any(t in source for t in ('emu.write', 'emu.setState', 'dofile', 'takeScreenshot'))
    Stock.LuaRuntime().compile(source)
    return source.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = Stock.ROM.read_bytes()
    program = controller(raw)
    sha = Stock.H(raw)
    script_sha = Stock.H(program)
    print('RYU DRAGON SOURCE ' + json.dumps(dict(ROM_SHA256=sha, script_SHA256=script_sha)), flush=True)
    if not args.run:
        return 0
    guard = Stock.check(Stock.ROM)
    rom, script = Stock.OUT / 'candidate.nes', Stock.OUT / 'controller.lua'
    assert guard['ROM_sha256'] == sha and not guard['matching_patch_files']
    assert set(Stock.OUT.iterdir()) == {rom, script} and rom.read_bytes() == raw
    with Stock.preserve_script(script, rom, raw) as stage:
        stage(program)
        result = Stock.run(script, Stock.ROM, Stock.OUT / 'capture', sha, 190)
    assert result['script_SHA256'] == script_sha and result['outputs_written'] == 0 and not result['images']
    assert Stock.ROM.read_bytes() == raw and Stock.check(Stock.ROM) == guard
    print('RYU DRAGON NATIVE ' + json.dumps(result, separators=(',', ':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
