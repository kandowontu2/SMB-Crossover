"""Verify a naturally earned Rogue Dawn Bomb opens an authored 1-2 coin block."""

import json

from capture_budget import preflight
from check_contra_force_combined_palette_1122 import comparison_base
from check_ff_stdout_controller_source_1110 import LuaRuntime
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from replay_rogue_hud_scene_dirty79fd_1116 import J, R, ROM, W, H, controller as current_bomb
from run_stdout_mesen_1110 import run


OUT = R / 'build/smb2-flag-native-1113'

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


def controller(raw):
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
    lua.compile(text)
    return text


def main():
    initial = check(ROM)
    raw = ROM.read_bytes()
    script = OUT / 'controller.lua'
    assert {file.name for file in OUT.iterdir()} == {script.name, 'candidate.nes'}
    assert (OUT / 'candidate.nes').read_bytes() == raw
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    previous = script.read_bytes()
    try:
        script.write_bytes(controller(raw).encode())
        result = run(script, ROM, OUT / 'capture', initial['ROM_sha256'], 120)
        receipt = result['receipt']
        bomb = receipt['natural_Bomb']
        print('ROGUE BOMB BLOCK ' + json.dumps({
            'passed': result['passed'], 'rom': initial['ROM_sha256'],
            'reason': receipt['reason'], 'receipt': result['receipt_SHA256'],
            'script': result['script_SHA256'], 'block': bomb.get('block'),
            'shot': bomb.get('bomb'), 'terminal': receipt['terminal'],
            'phase': bomb.get('phase'), 'nearby_blocks': bomb.get('cache', {}).get('near'),
        }), flush=True)
        assert result['passed'] and result['outputs_written'] == 0 and not result['images']
    finally:
        script.write_bytes(previous)
        assert check(ROM) == initial and ROM.read_bytes() == raw


if __name__ == '__main__':
    main()
