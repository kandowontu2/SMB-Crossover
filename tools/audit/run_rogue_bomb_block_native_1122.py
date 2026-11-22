"""Verify Rogue Dawn's Bomb and optionally continue to the earned jumps."""

import argparse
import json

from capture_budget import preflight
from check_contra_force_combined_palette_1122 import comparison_base
from check_ff_stdout_controller_source_1110 import LuaRuntime
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from replay_rogue_hud_scene_dirty79fd_1116 import J, R, ROM, W, H, controller as current_bomb
from run_stdout_mesen_1110 import run


OUT = R / 'build/smb2-flag-native-1113'
HIGH_JUMP_ROUTE = R / 'tools/playthroughs/rogue_high_jump_native_1122.lua'
WALL_JUMP_ROUTE = R / 'tools/playthroughs/rogue_wall_jump_native_1122.lua'

POSITION = """elseif gear.phase=='position'then
  assert(r('RdAction')==3,'Stay morphed while approaching the coin block')
  if c.x<176 then return{right=true}end
  if c.x>180 then return{left=true}end
  assert(c.block(176,144)==0xc0,'Actual unspent 1-2 coin-question block')
  gear.block={before=c.block(176,144),coins=r('CoinTally'),start=state()}
  gear.phase='release';return{}
 elseif gear.phase=='release'then"""

OBSERVE = """
hook('PlayerHeadCollision',function()
 if not gear.block or not gear.bomb or not active() or not identity() then return end
 local q=gear.bomb.shot
 if r('RdBombTerrainPhase')~=3 or r('MmBulletType')~=10 then return end
 local x=pos('MmBulletX','MmBulletPage')
 local y=r('MmBulletY')
 assert(x==q.x and y==q.y+16 and x>=176 and x<192 and y>=144 and y<160,
        'Native downward Bomb point touches the loaded coin block')
 assert(not gear.block.hit and r('CoinTally')==gear.block.coins,'A single unclaimed coin-block hit')
 gear.block.hit={x=x,y=y,Main=updates,tile=cpu()['cpu.a']}
end)
"""


def controller(raw, *, high_jump=False, wall_jump=False, wall_left=False):
    parent = comparison_base(raw)
    bundle = J.bindings(parent)['bundle']
    old = current_bomb(parent, 'bomb')
    assert old.count(J.PIN) == 1
    text = old.replace(J.PIN, H(raw), 1)

    def edit(before, after):
        nonlocal text
        assert text.count(before) == 1, before
        text = text.replace(before, after, 1)

    hook = 'PlayerHeadCollision'
    at = W.location(bundle, hook)
    assert raw[at:at+8] == parent[at:at+8]
    bindings = J.Previous.Previous.Frozen.lua
    config = dict(PC=W.address(bundle, hook), offset=at-16, bytes=list(raw[at:at+8]))
    addresses = {name: W.address(bundle, name) for name in
                 ('CoinTally', 'MmBulletType', 'MmBulletX', 'MmBulletPage', 'MmBulletY')}
    line = text.split('\n', 1)[0]
    # The exact Contra Force successor shares this hook address but its
    # entry path has changed. Keep executing the actual current bytes.
    lua = LuaRuntime()
    pins = lua.execute(line + '\nreturn C.hooks')
    updates = []
    for name, pinned in pins.items():
        offset = 16 + pinned.offset
        expected = bytes(value for _, value in sorted(pinned.bytes.items()))
        assert parent[offset:offset+len(expected)] == expected, name
        current = raw[offset:offset+len(expected)]
        if current != expected:
            assert name == 'GameLoop', name
            updates.append(f'C.hooks.GameLoop.bytes={bindings(list(current))}')
    additions = [f'C.hooks.{hook}={bindings(config)}',
                 f'for name,at in pairs({bindings(addresses)})do C.ram[name]=at end']
    if high_jump or wall_jump:
        at = W.location(bundle, 'RdStartJump')
        assert raw[at:at+8] == parent[at:at+8]
        jump = dict(PC=W.address(bundle, 'RdStartJump'), offset=at-16, bytes=list(raw[at:at+8]))
        additions.append(f'C.hooks.RdStartJump={bindings(jump)}')
        additions.append("C.ram.AreaAddrsLOffset=" + str(W.address(bundle, 'AreaAddrsLOffset')))
    if wall_jump:
        gate = 'RdC_DA68'
        at = W.location(bundle, gate)
        assert raw[at:at+6] == parent[at:at+6]
        assert raw[at:at+3] == b'\x20' + W.address(bundle, 'RdC_CD40').to_bytes(2, 'little')
        jump_gate = dict(PC=W.address(bundle, gate), offset=at-16, bytes=list(raw[at:at+6]))
        additions.append(f'C.hooks.WallJumpGate={bindings(jump_gate)}')
        for name in ('RdMaxSpeed', 'RdFrozenSupport', 'Enemy_Y_HighPos', 'RdRadiusX'):
            additions.append(f'C.ram.{name}={W.address(bundle, name)}')
        if wall_left:
            additions.append('C.wallLeft=true')
    edit(line, '\n'.join([line, *updates, *additions]))
    edit("gear.morph=state();gear.phase='release'", "gear.morph=state();gear.phase='position'")
    edit("elseif gear.phase=='release'then", POSITION)
    edit("local age=0", OBSERVE + "\nlocal age=0")
    edit("gear.complete=true;finish('natural-Bomb-and-lifecycle25');return{}",
         """assert(gear.block and gear.block.hit,'Actual Bomb-to-block transaction')
    gear.block.after=c.block(176,144);gear.block.coinsAfter=r('CoinTally')
    assert(gear.block.after~=gear.block.before and gear.block.after~=0
           and gear.block.coinsAfter==(gear.block.coins+1)%100,
           'Used block and exactly one coin after Bomb expiry')
    gear.complete=true;finish('natural-Bomb-and-lifecycle25');return{}""")
    if high_jump or wall_jump:
        extend_high_jump(edit)
    if wall_jump:
        extend_wall_jump(edit)
    lua.compile(text)
    return text


def extend_high_jump(edit):
    edit("local function bombDrive()", HIGH_JUMP_ROUTE.read_text(encoding='utf-8') + "\nlocal function bombDrive()")
    edit("if gear.phase=='travel'then", "if gear.high then return highJumpDrive(c)end\n if gear.phase=='travel'then")
    edit("if not gear.block or not gear.bomb or not active() or not identity() then return end",
         "if gear.high or not gear.block or not gear.bomb or not active() or not identity() then return end")
    edit("local function bombReturned(n,p)\n if not gear.started then return end", """local function bombReturned(n,p)
 if not gear.started then return end
 if gear.high then
  if n=='RdBombAllocate'and gear.high.phase=='place-bomb'then
   for _,i in ipairs({0xd0,0xe0,0xf0})do
    if r('RdWAction',i)==8 and p.bombs[i]==0 then
     assert(not gear.high.bomb and r('RdGear')==1 and r('RdAction')==3,'One earned Bomb on the powerup brick')
     gear.high.bomb=bombShot(i)
    end
   end
  end
  return
 end""")
    edit("local age=0", """hook('PlayerHeadCollision',function()
 local high=gear.high
 if not high or not high.bomb or high.hit or not active() or not identity() then return end
 if r('RdBombTerrainPhase')~=3 or r('MmBulletType')~=10 then return end
 local x,y=pos('MmBulletX','MmBulletPage'),r('MmBulletY')
 assert(x==high.bomb.x and y==high.bomb.y+16 and x>=1104 and x<1120
        and y>=128 and y<144 and cpu()['cpu.a']==0x5a,'Bomb hits the authored High Jump brick')
 high.hit={x=x,y=y,Main=updates}
end)
local age=0""")
    edit("gear.complete=true;finish('natural-Bomb-and-lifecycle25');return{}", """gear.complete=true
    gear.high={started=updates,phase='unmorph',steps={},areaOffset=r('AreaAddrsLOffset'),initialLink=c.area}
    stock='high-jump';born=nil;mature=nil;collector=nil;credit=nil
    return{}""")
    edit("reason=='natural-Bomb-and-lifecycle25'and gear.complete",
         "reason=='natural-high-jump-and-landing'and gear.complete and gear.high.complete")
    edit("(a.private==208 and a.owner==2)", "(a.private==(gear.high and 209 or 208) and a.owner==2)")
    edit("(tank and 216 or(gear.started and 208 or 217))",
         "(tank and 216 or(gear.high and 209 or(gear.started and 208 or 217)))")
    edit("born=born or{actor=a,player=state()}",
         """if gear.high and not born then
   assert(a.x==1104 and a.state<128 and a.saved_raw==1, 'Correct authored High Jump actor')
  end
  born=born or{actor=a,player=state()}""")
    edit("p.actor=actor(i);p.boxes=", """p.actor=actor(i)
  -- Contact can run during the same Main update that makes the item mature.
  if gear.high and born and not mature and p.actor.slot==born.actor.slot
     and p.actor.private==209 and p.actor.state&128~=0 then
   mature={actor=p.actor,player=state()}
  end
  p.boxes=""")
    edit("r('RdGear')==(stock=='bomb-credit'and 1 or 0)",
         "r('RdGear')==(stock=='high-jump-credit'and 3 or(stock=='bomb-credit'and 1 or 0))")
    edit("   else\n    gear.acquisition=", """   elseif stock=='high-jump-credit'then
    gear.high.acquisition={birth=born,mature=mature,collector=collector,credit=credit}
    highJumpPhase(gear.high,'clear');stock='high-jump-earned';credit=nil
   else
    gear.acquisition=""")
    edit("(stock=='tank'and 8 or(stock=='bomb'and 0 or 9))",
         "(stock=='tank'and 8 or(stock=='high-jump'and 1 or(stock=='bomb'and 0 or 9)))")
    edit("r('RdGear')==(stock=='bomb'and 1 or 0)",
         "r('RdGear')==(stock=='high-jump'and 3 or(stock=='bomb'and 1 or 0))")
    edit("(a.private==216 or a.private==217 or a.private==208)",
         "(a.private==216 or a.private==217 or a.private==208 or a.private==209)")
    edit("'RdControlDispatch','RdLifeMovement','RdBombAllocate'",
         "'RdControlDispatch','RdLifeMovement','RdStartJump','RdBombAllocate'")
    edit("  elseif n=='RdBombAllocate'or", """  elseif n=='RdStartJump'and gear.high then
   local launch={Main=updates,vy=r('RdVY'),gravity=r('RdGravity'),player=state()}
   if gear.high.phase=='rise' then
    assert(launch.vy==0xfc and launch.gravity==0x18,'Ordinary dry jump before High Jump')
    gear.high.baseLaunch=gear.high.baseLaunch or launch
   elseif gear.high.phase=='test-arc'then
    assert(not gear.high.launch and launch.vy==0xfc and launch.gravity==0x12,
           'Fresh A uses the earned dry High Jump gravity')
    gear.high.launch=launch
   end
  elseif n=='RdBombAllocate'or""")


def extend_wall_jump(edit):
    edit("finish('natural-high-jump-and-landing')", """gear.wall={phase='travel',started=updates,entered=updates,steps={},launches={},landings={}}
  stock='wall-jump';born=nil;mature=nil;collector=nil;credit=nil""")
    edit("local function bombDrive()", WALL_JUMP_ROUTE.read_text(encoding='utf-8') + "\nlocal function bombDrive()")
    edit("if gear.high then return highJumpDrive(c)end",
         "if gear.wall then return wallJumpDrive(c)end\n if gear.high then return highJumpDrive(c)end")
    edit("reason=='natural-high-jump-and-landing'and gear.complete and gear.high.complete",
         "reason=='natural-wall-jump-and-landing'and gear.complete and gear.high.complete and gear.wall.complete")
    edit("(a.private==(gear.high and 209 or 208) and a.owner==2)",
         "(a.private==(gear.wall and 210 or(gear.high and 209 or 208)) and a.owner==2)")
    edit("(tank and 216 or(gear.high and 209 or(gear.started and 208 or 217)))",
         "(tank and 216 or(gear.wall and 210 or(gear.high and 209 or(gear.started and 208 or 217))))")
    edit("a.x==1104 and a.state<128 and a.saved_raw==1, 'Correct authored High Jump actor'",
         "a.x==(gear.wall and 2400 or 1104) and a.state<128 and a.saved_raw==1, 'Correct authored upgrade actor'")
    edit("p.actor.private==209 and p.actor.state", "p.actor.private==(gear.wall and 210 or 209) and p.actor.state")
    edit("stock=='high-jump-credit'and 3 or(stock=='bomb-credit'and 1 or 0)",
         "stock=='wall-jump-credit'and 7 or(stock=='high-jump-credit'and 3 or(stock=='bomb-credit'and 1 or 0))")
    edit("   elseif stock=='high-jump-credit'then", """   elseif stock=='wall-jump-credit'then
    gear.wall.acquisition={birth=born,mature=mature,collector=collector,credit=credit}
    wallJumpPhase('prepare');stock='wall-jump-earned';credit=nil
   elseif stock=='high-jump-credit'then""")
    edit("stock=='high-jump'and 1 or(stock=='bomb'and 0 or 9)",
         "stock=='wall-jump'and 2 or(stock=='high-jump'and 1 or(stock=='bomb'and 0 or 9))")
    edit("stock=='high-jump'and 3 or(stock=='bomb'and 1 or 0)",
         "stock=='wall-jump'and 7 or(stock=='high-jump'and 3 or(stock=='bomb'and 1 or 0))")
    edit("a.private==208 or a.private==209)", "a.private==208 or a.private==209 or a.private==210)")
    edit("if not gear.started then return end\n if gear.high then", """if not gear.started then return end
 if gear.wall then
  local wall=gear.wall
  local field=wall.phase=='place-bomb'and 'bomb' or wall.phase=='place-gap-bomb'and 'gapBomb'
  if n=='RdBombAllocate'and field then
   for _,i in ipairs({0xd0,0xe0,0xf0})do
    if r('RdWAction',i)==8 and p.bombs[i]==0 then
     local expectedGear=field=='bomb' and 3 or 7
     assert(not wall[field] and r('RdGear')==expectedGear and r('RdAction')==3,'One Bomb over the intended brick')
     wall[field]=bombShot(i)
    end
   end
  end
  return
 end
 if gear.high then""")
    edit("  elseif n=='RdStartJump'and gear.high then", """  elseif n=='RdStartJump'and gear.wall then
   local wall=gear.wall
   if wall.pending then
    local launch=wall.pending
    wall.pending=nil
    launch.vy=r('RdVY');launch.gravity=r('RdGravity')
    assert(launch.vy==0xfc and launch.gravity==0x12,'Native launch after a blocked wall probe')
    wall.launches[wall.side]=launch
   end
  elseif n=='RdStartJump'and gear.high then""")
    edit("local age=0", """hook('PlayerHeadCollision',function()
 local wall=gear.wall
 if not wall or not active() or not identity() then return end
 local gap=wall.phase=='wait-gap'
 local shot=gap and wall.gapBomb or wall.bomb
 local field=gap and 'gapHit' or 'hit'
 if not shot or wall[field] then return end
 if r('RdBombTerrainPhase')~=3 or r('MmBulletType')~=10 then return end
 local x,y=pos('MmBulletX','MmBulletPage'),r('MmBulletY')
 local brick=gap and 2384 or 2400
 local tile=gap and 0x52 or 0x5a
 assert(x==shot.x and y==shot.y+16 and x>=brick and x<brick+16
        and y>=128 and y<144 and cpu()['cpu.a']==tile,'Bomb hits the intended authored brick')
 wall[field]={x=x,y=y,Main=updates,tile=tile}
end)
hook('WallJumpGate',function()
 local wall=gear.wall
 if not wall or wall.phase~='press' or not active() or not identity() then return end
 local before=state()
 local facing=wall.side=='left' and 2 or 1
 local reach=r('RdRadiusX')+1
 local probeX=before.source_x+(facing==1 and reach or -reach)
 assert(r('RdGear')==7 and r('RdAction')==1 and r('Player_State')~=0
        and r('RdFresh')&128~=0 and r('RdHeld')&3==facing
        and cpu()['cpu.ps']&1==0 and probeX>=2400 and probeX<2416
        and context().block(2400,128)==0xc4,
        'Fresh A toward a real blocked wall while airborne')
 assert(not wall.pending and not wall.launches[wall.side])
 wall.pending={before=before,side=wall.side}
end)
local age=0""")
    # Wall Jump is the fifth earned pickup in this replay.
    edit('#requests<4 then', '#requests<8 then')
    edit('#popups<16 then', '#popups<24 then')
    edit("updates<8500", "updates<11800")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    stages = parser.add_mutually_exclusive_group()
    stages.add_argument('--high-jump', action='store_true')
    stages.add_argument('--wall-jump', action='store_true')
    stages.add_argument('--wall-jump-left', action='store_true')
    args = parser.parse_args()
    wall_jump = args.wall_jump or args.wall_jump_left
    initial = check(ROM)
    raw = ROM.read_bytes()
    script = OUT / 'controller.lua'
    assert {file.name for file in OUT.iterdir()} == {script.name, 'candidate.nes'}
    assert (OUT / 'candidate.nes').read_bytes() == raw
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    previous = script.read_bytes()
    try:
        script.write_bytes(controller(raw, high_jump=args.high_jump, wall_jump=wall_jump,
                                      wall_left=args.wall_jump_left).encode())
        timeout = 240 if wall_jump else 180 if args.high_jump else 120
        result = run(script, ROM, OUT / 'capture', initial['ROM_sha256'], timeout)
        receipt = result['receipt']
        bomb = receipt['natural_Bomb']
        label = 'ROGUE WALL JUMP ' if wall_jump else 'ROGUE HIGH JUMP ' if args.high_jump else 'ROGUE BOMB BLOCK '
        print(label + json.dumps({
            'passed': result['passed'], 'rom': initial['ROM_sha256'],
            'reason': receipt['reason'], 'receipt': result['receipt_SHA256'],
            'script': result['script_SHA256'], 'block': bomb.get('block'),
            'shot': bomb.get('bomb'), 'terminal': receipt['terminal'],
            'phase': bomb.get('phase'), 'nearby_blocks': bomb.get('cache', {}).get('near'),
            'high_jump': None if wall_jump else bomb.get('high'),
            'wall_jump': compact_wall_receipt(bomb.get('wall')),
        }), flush=True)
        assert result['passed'] and result['outputs_written'] == 0 and not result['images']
    finally:
        script.write_bytes(previous)
        assert check(ROM) == initial and ROM.read_bytes() == raw


def compact_wall_receipt(wall):
    if not wall:
        return None
    result = {key: value for key, value in wall.items() if key not in ('acquisition', 'steps')}
    result['steps'] = [(step['phase'], step['player']['Main'], step['player']['x'], step['player']['y'])
                       for step in wall.get('steps', ())]
    if wall.get('acquisition'):
        result['pickup'] = wall['acquisition']['collector']['actor']
    return result


if __name__ == '__main__':
    main()
