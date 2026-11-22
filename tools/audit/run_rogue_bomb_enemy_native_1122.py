"""Follow an earned Rogue Dawn Bomb into a grounded native enemy contact."""

import json

from capture_budget import preflight
from check_ff_stdout_controller_source_1110 import LuaRuntime
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import repair_contra_force_beans_ground_1122 as Beans
import run_rogue_bomb_block_native_1122 as Base
from run_stdout_mesen_1110 import run


POLICY = Base.R / 'tools/playthroughs/rogue_bomb_enemy_native_1122.lua'


def controller(raw):
    baseline = Beans.inverse(raw)
    parent = Base.comparison_base(baseline)
    bundle = Base.J.bindings(parent)['bundle']
    lua = Base.J.Previous.Previous.Frozen.lua
    text = Base.controller(baseline)

    def edit(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)

    edit(Base.H(baseline), Base.H(raw))
    label = 'RdWxActorContact'
    pc, at = Base.W.address(bundle, label), Base.W.location(bundle, label)
    assert raw[at:at + 8] == baseline[at:at + 8] == parent[at:at + 8]
    hook = dict(PC=pc, offset=at - 16, bytes=list(raw[at:at + 8]))
    addresses = {name: Base.W.address(bundle, name) for name in
                 ('MmEnemyHealthLo', 'MmEnemyFlash', 'AreaAddrsLOffset')}
    line = text.split('\n', 1)[0]
    edit(line, line + f'\nC.hooks.{label}={lua(hook)}'
         + f'\nfor n,at in pairs({lua(addresses)})do C.ram[n]=at end')
    edit('local function bombDrive()', POLICY.read_text(encoding='utf-8') + '\nlocal function bombDrive()')
    edit(' local c=context();assert(identity()', ' local c=context();if gear.enemy then return bombEnemyDrive(c)end\n assert(identity()')
    edit("gear.complete=true;finish('natural-Bomb-and-lifecycle25');return{}", """gear.complete=true
    gear.enemy={phase='unmorph',started=updates,areaOffset=r('AreaAddrsLOffset'),approach={}}
    return{}""")
    edit("reason=='natural-Bomb-and-lifecycle25'and gear.complete", "reason=='natural-Bomb-damages-Goomba'and gear.complete and gear.enemy.complete")
    edit("local function bombReturned(n,p)\n if not gear.started then return end", """local function bombReturned(n,p)
 if not gear.started then return end
 if gear.enemy then
  local fight=gear.enemy
  if n=='RdBombAllocate'and fight.phase=='place'then
   for _,i in ipairs({0xd0,0xe0,0xf0})do
    if r('RdWAction',i)==8 and p.bombs[i]==0 then
     assert(not fight.bomb and r('RdAction')==3 and r('RdGear')==1,'Actual second earned Bomb')
     fight.bomb=bombShot(i)
    end
   end
  elseif fight.bomb and p.weapon_slot==fight.bomb.slot and r('RdWAction',p.weapon_slot)==0 and not fight.expiry then
   fight.expiry={player=state(),entered=snapshot('_entered'),returned=snapshot('_returned')}
  end
  return
 end""")
    edit(" if n=='RdBombAllocate'then p.before=state()", """ if n=='RdWxActorContact'then
  p.enemy=actor(c['cpu.x']);p.health=r('MmEnemyHealthLo',p.enemy.slot)
  p.blast=bombShot(gear.enemy.bomb.slot)
 end
 if n=='RdBombAllocate'then p.before=state()""")
    edit("  elseif n=='RdHsCollectActor'then", """  elseif n=='RdWxActorContact'then
   local fight=gear.enemy
   local slot=p.enemy.slot
   local after=r('MmEnemyHealthLo',slot)
   local target=actor(slot)
   assert(p.A==10 and p.blast.action==10,'Original exploding Bomb reached the contact owner')
   if after<p.health then
    assert(after==p.health-1 and (r('MmEnemyFlash',slot)==6 or (target.state&32)~=0),
           'Actual one-point Bomb debit and ordinary hurt or defeat')
    fight.hit=fight.hit or {update=updates,shot=p.blast,before_enemy=p.enemy,after_enemy=target,
                           before_HP=p.health,after_HP=after,flash=r('MmEnemyFlash',slot)}
   end
  elseif n=='RdHsCollectActor'then""")
    edit('local age=0', """hook('RdWxActorContact',function()
 local fight=gear.enemy
 if not fight or not fight.bomb or not active() or not identity() or cpu()['cpu.a']~=10 then return end
 local slot=cpu()['cpu.x']
 local a=actor(slot)
 if a.flag==1 and a.id==6 and a.state<2 and r('RdWAction',fight.bomb.slot)==10 then
  enter('RdWxActorContact')
 end
end)
local age=0""")
    LuaRuntime().compile(text)
    return text


def main():
    guard = check(Base.ROM)
    raw = Base.ROM.read_bytes()
    assert guard['ROM_sha256'] == Beans.CANDIDATE == Base.H(raw)
    assert {p.name for p in Base.OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert (Base.OUT / 'candidate.nes').read_bytes() == raw
    preflight(Base.OUT / 'capture', reserved_files=0)
    require_free_workspace(Base.R, Base.ROM, allow_interactive=True)
    script = Base.OUT / 'controller.lua'
    previous = script.read_bytes()
    try:
        script.write_bytes(controller(raw).encode())
        q = run(script, Base.ROM, Base.OUT / 'capture', Base.H(raw), 180)
        result = q['receipt']
        print('ROGUE BOMB ENEMY ' + json.dumps(dict(passed=q['passed'], reason=result['reason'],
              receipt=q['receipt_SHA256'], script=q['script_SHA256'], terminal=result['terminal'],
              phase=result['natural_Bomb']['phase'], fight=result['natural_Bomb'].get('enemy'))), flush=True)
        assert q['passed'] and not q['images'] and q['outputs_written'] == 0
    finally:
        script.write_bytes(previous)
        assert check(Base.ROM) == guard and Base.ROM.read_bytes() == raw


if __name__ == '__main__':
    main()
