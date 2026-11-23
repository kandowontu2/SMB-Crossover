"""Replay Mario the Tank's normal 1-1 hidden 1-UP and Star pickups."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
from current_sonic_parent_rom_1122 import CANDIDATE as PIN, inverse
from nightly_patch_guard_v1 import check
import replay_mario_luigi_stock_1122 as Stock
import replay_smb3_stock59_1122 as Direct
from replay_sonic_hidden_life_f7c9_1116 import value
from run_mario_luigi_stock_native_1122 import OUT, preserve_script
from run_stdout_mesen_1110 import run


R, ROM, H = Stock.R, Stock.ROM, Stock.H
ITEMS = ('1up', 'star')


FLOWER_ROW = r'''
local function tankFlowerCrossing(c)
 local g=T.ground_route
 if not g or g.phase~='done' or c.x<1136 or c.x>=1328 then return end
 local q=T.flower_crossing
 if not q then
  if not c.grounded or c.lastA then return {}end
  q={phase='hop',launch={update=c.update,x=c.x,y=c.y,vx=c.vx}}
  T.flower_crossing=q
  return {right=true,b=true,a=true}
 end
 if q.phase=='hop' then
  if c.grounded and c.update-q.launch.update>4 then
   q.phase='floor';q.landing={update=c.update,x=c.x,y=c.y,vx=c.vx}
  else
   -- Land on the near side of the brick row so its upper Goomba stays clear.
   local b=starSteer(c,1207,2)
   b.a=c.update-q.launch.update<32
   return b
  end
 end
 return {right=true,b=true}
end
'''


def bindings(raw, item):
    reference = inverse(raw)
    q = Direct.bindings(raw, 'mario3', item)
    bundle = Direct.Current.authority()
    w = Direct.W
    selected = w.UI.seed(dict(bundle, raw=raw), 0)
    for _ in range(7):
        w.UI.key(selected, 32)
    assert w.UI.menu_name(selected)[0] == 'MARIO THE TANK'
    assert Stock.Current.N.get(selected, 'MarioVariant') == 7
    assert Stock.Current.N.get(selected, 'SelectedCharacter') == 0

    names = ('GameLoop', 'HandlePowerUpCollision', 'PlayerHeadCollision')
    if item == '1up':
        names += ('LifeCredit',)
    q['hooks'] = {name: q['hooks'][name] for name in names}
    # Observe actual returns from the native call that selects the Tank motor.
    # Compare its entry bytes against the previously pinned engine.
    for event, routine in (('GuestMovement', 'PlayerMovementSubs'),
                           ('MarioSourcePowerupCollision', 'MarioSourcePowerupCollision')):
        at = w.location(bundle, routine)
        pc = w.address(bundle, routine)
        bank = (at - 16)//8192
        assert (at-16) == bank*8192+(pc&8191)
        code = raw[at:at+16]
        assert code == reference[at:at+16]
        q['hooks'][event] = dict(pc=pc, tag=bank|128, offset=at-16,
                                  hex=code.hex(), bytes=list(code))
    for hook in q['hooks'].values():
        start = 16 + hook['offset']
        code = bytes.fromhex(hook['hex'])
        assert code == raw[start:start+len(code)]
    for name in ('MarioVariant', 'PlayerScoreDisplay', 'GuestPowerupActive', 'GuestPowerupOld',
                 'GuestPowerupTarget', 'GuestPowerupAge'):
        q['ram'][name] = w.address(bundle, name)
    # Current menu directions wrap separately on the four rows and eight columns.
    navigation = []
    for position in range(32):
        row, col = divmod(position, 8)
        navigation.append(('left' if col <= 4 else 'right') if col else
                          ('up' if row in (1, 2) else 'down' if row == 3 else ''))
    q.update(sha=PIN, form='tank', key='tank', name='MARIO THE TANK',
             owner=0, character=0, slot=0, variant=7, select=7, navigation=navigation)
    return q


def controller(raw, item):
    q = bindings(raw, item)
    observer = Stock.body().replace('Source Mario/Luigi', 'Mario the Tank')
    navigation = Stock.travel()
    policy = Stock.once(Stock.policy(), '  if not a then return {}end -- The observer, never disappearance, grants credit.',
                        '''  if not a then
   -- The Tank's neutral drift can reach the pit before delayed 1-UP credit.
   -- Brake with the ordinary opposite direction while the observer checks the grant.
   local vx=c.vx>=128 and c.vx-256 or c.vx
   return {left=vx>1,right=vx< -1}
  end''')
    if item == 'star':
        policy = Stock.once(policy, 'return function(c)\n', FLOWER_ROW+'\nreturn function(c)\n')
        route = ' local crossing=sourceGroundRoute(c);if crossing then return crossing end\n'
        policy = Stock.once(policy, route, route+' local flower=tankFlowerCrossing(c);if flower then return flower end\n')
    text = '\n'.join(('local C='+value(q), 'local SMB3_PICKUP_KIND=C.stockKind',
                      'local SMB3_PICKUP_BASE=(function()\n'+navigation+'\nend)()',
                      'local choose=(function()\n'+policy+'\nend)()', observer))
    LuaRuntime().compile(text)
    return text.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--item', choices=ITEMS, action='append')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    assert H(raw) == PIN
    scripts = {item: controller(raw, item) for item in args.item or ITEMS}
    if not args.run:
        print('SOURCE ' + json.dumps({item: H(script) for item, script in scripts.items()}), flush=True)
        return 0

    guard = check(ROM)
    assert guard['ROM_sha256'] == PIN and not guard['matching_patch_files']
    candidate, script = OUT/'candidate.nes', OUT/'controller.lua'
    assert set(OUT.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    try:
        with preserve_script(script, candidate, raw) as stage:
            for item, program in scripts.items():
                stage(program)
                result = run(script, ROM, OUT/'capture', PIN, 150)
                assert result['outputs_written'] == 0 and not result['images']
                print('TANK STOCK ' + json.dumps(dict(item=item, **result), separators=(',', ':')), flush=True)
                if not result['passed']:
                    return 1
    finally:
        assert check(ROM) == guard and ROM.read_bytes() == raw
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
