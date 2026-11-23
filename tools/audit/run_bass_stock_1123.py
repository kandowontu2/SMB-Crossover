"""Verify Bass's authored first Mushroom in the installed MMC5 nightly."""

import argparse
from hashlib import sha256
import json
from unittest.mock import patch

from check_ff_stdout_controller_source_1110 import LuaRuntime
from current_ice_stock_binding_1122 import RAM_FIELDS
from replay_sonic_hidden_life_f7c9_1116 import value
import run_roster_empty_cadence_1122 as Cadence
import run_darkwing_stock_1123 as Stock


PIN = 'ffd7081036bca9cb165d9f4c5527e909126df70f993b4ebec75b7dd7ac83a6b1'
ROM, OUT, W, N = Stock.ROM, Stock.OUT, Stock.W, Stock.N

POLICY = r'''
local route={phase='align',at=0,attempts=0}
ICE_STOCK_STATE=route
local function change(c,p)route.phase=p;route.at=c.update end
local function steer(c,x,n)return{right=c.x<x-n,left=c.x>x+n}end
return function(c)
 if BASS_EARNED then return{}end
 local a
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==0 then
   a={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),
      mature=c.r('Enemy_State',i)&128~=0};break
  end
 end
 if a then
  if route.phase~='collect'then change(c,'collect')end
  local x=a.mature and math.min(419,math.max(385,a.x-4)) or 388
  return steer(c,x,2)
 end
 if route.phase=='jump'then
  if not c.grounded or c.update-route.at<18 then return{a=c.update-route.at<21}end
  change(c,'align')
 end
 if route.phase=='collect'then return{}end
 if c.grounded and not c.lastA and math.abs(c.x-332)<=2 then
  route.attempts=route.attempts+1;assert(route.attempts<=5,'Bounded grounded Bass attempts')
  change(c,'jump');return{a=true}
 end
 local pad=steer(c,332,2)
 local enemy=c.enemy()
 if c.x<303 and enemy and enemy.dx>0 and enemy.dx<96 and math.abs(enemy.y-c.y)<28 then
  pad.b=c.update%18<2
 end
 return pad
end
'''


def controller(raw):
    assert sha256(raw).hexdigest() == PIN
    reference = Cadence.Authority.scoped_load(Cadence.Authority.AUTHORITY)
    bundle = dict(reference, raw=raw)
    with patch.object(N, 'Bus', W.ControllerBus):
        menu = W.UI.seed(bundle, 0)
    for key in (4, 1):
        W.UI.key(menu, key)
    assert W.UI.menu_name(menu)[0] == 'BASS' and N.get(menu, 'CrossoverMenuIndex') == 9
    fields = set(name for name in RAM_FIELDS if not name.startswith('Ic'))
    fields.update(('RlVariant', 'FmAlts', 'InvPickup', 'InvPickupOwner', 'InvOwnedLo', 'InvOwnedHi',
                   'PlayerScoreDisplay', 'GuestPowerupActive', 'GuestPowerupTarget'))
    ram = {name: W.address(bundle, name) for name in sorted(fields)}
    hooks = {}
    for event, symbol in (('GameLoop', 'GameLoop'), ('Move', 'ExpandedMovement'),
                          ('HandlePowerUpCollision', 'MarioSourcePowerupCollision'),
                          ('PlayerHeadCollision', 'PlayerHeadCollision')):
        pc, at = W.address(bundle, symbol), W.location(bundle, symbol)
        physical_bank = (at - 16) // 8192
        assert 0 <= physical_bank < 128 and (at - 16) % 8192 == pc & 8191
        hooks[event] = dict(pc=pc, tag=physical_bank | 128, offset=at - 16, hex=raw[at:at + 12].hex())
    nav = []
    for i in range(32):
        row, col = divmod(i, 8)
        nav.append('down' if row == 0 else 'up' if row in (2, 3) else
                   'right' if col == 0 else 'left' if col > 1 else '')
    cfg = dict(sha=PIN, form='bass', variant=0, slot=9, route='mushroom', mode_value=0,
               navigation=nav, ram=ram, hooks=hooks)
    text = Stock.OBSERVER.read_text()
    for old, new in (
        ("r('SelectedCharacter')==20 and r('IcVariant')==C.variant", "r('SelectedCharacter')==9 and r('RlVariant')==0 and r('FmAlts')&32==0"),
        ("r('IcVariant')~=C.variant", "r('RlVariant')~=0"),
        ("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected={0}'),
        ("power=r('IcPower')", "power=r('PlayerStatus'),growth=r('GuestPowerupActive'),owned=r('InvOwnedLo',9)"),
        ('c.poll=polls;c.char=20;', 'c.poll=polls;c.char=9;'),
        ('c.lastA=mask&128~=0', "c.lastA=r('PreviousA_B_Buttons')&128~=0"),
        ("'Living Ice Climber in ordinary 1-1'", "'Living Bass in ordinary Easy 1-1'"),
        ("if p.name=='IcMovement' then motor=motor+1", "if p.name=='Move' then motor=motor+1"),
        ("state=r('Enemy_State',i),x=pos", "state=r('Enemy_State',i),stamp=r('InvPickup',i),owner=r('InvPickupOwner',i),x=pos"),
        ('q.birth={actor=a,player=s}', "assert(heads['0'] and a.owner==9 and a.stamp==0,'Bass Mushroom comes from a real head bump and owner 9');q.birth={actor=a,player=s}"),
        ('local lifePending', "local lifePending\nlocal function score()local n=0;for i=0,5 do n=n*10+r('PlayerScoreDisplay',i)end;return n end"),
        (' local complete=true', """ local q=checks['0']
 if q.collect then BASS_EARNED=true end
 if q.collect and not q.grant and s.growth==0 and s.status==1 and score()>=q.collect.score_before+1000 then
  assert(s.owned&1~=0 and s.lives==2,'Earned Mushroom ownership and both lives remain');q.grant=s
 end
 local complete=true"""),
        ("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end", "else assert(s.status==1 and s.growth==0 and s.owned&1~=0,'Earned Bass tier persists during movement') end"),
        ("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')", "assert(a.state&128~=0 and p.before.status==0 and s.owned&1~=0 and s.growth>0 and r('GuestPowerupTarget')==1,'Mature Bass Mushroom starts original growth');return"),
        ("sound=r('Square2SoundQueue')}", "sound=r('Square2SoundQueue'),score_before=p.score}"),
        ('p.actor=a;p.before=state()', 'p.actor=a;p.before=state();p.score=score()'),
    ):
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)
    script = 'local C=' + value(cfg) + '\nlocal choose=(function()\n' + POLICY + '\nend)()\n' + text
    assert not any(term in script for term in ('loadState', 'saveState', 'emu.write', 'io.open', 'dofile'))
    LuaRuntime().compile(script)
    return script.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    program = controller(raw)
    digest = sha256(program).hexdigest()
    if not args.run:
        print('BASS SOURCE ' + json.dumps(dict(ROM_SHA256=PIN, script_SHA256=digest)), flush=True)
        return 0
    guard = Cadence.check(ROM)
    assert guard['ROM_sha256'] == PIN and not guard['matching_patch_files']
    target, script = OUT/'candidate.nes', OUT/'controller.lua'
    assert set(OUT.iterdir()) == {target, script} and target.read_bytes() == raw
    with Stock.Host.Shared.preserve_script(script, target, raw) as stage:
        stage(program)
        result = Cadence.run(script, ROM, OUT/'capture', PIN, 140)
    assert result['script_SHA256'] == digest and result['outputs_written'] == 0 and not result['images']
    assert Cadence.check(ROM) == guard
    print('BASS NATIVE ' + json.dumps(result, separators=(',', ':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
