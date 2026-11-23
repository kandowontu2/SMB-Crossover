"""Verify Alex and Ryan's authored Easy 1-1 pickups in Mesen."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
import compose_dkjr_public_side_forward_1123 as Side
from compose_dkjr_sonic_dispatch_1123 import CANDIDATE as NIGHTLY
from current_ice_stock_binding_1122 import RAM_FIELDS
from nightly_patch_guard_v1 import check
from replay_ryan_full11_current_1114 import BASE, BASE_SHA, N, W, once
from replay_sonic_hidden_life_f7c9_1116 import value
from run_mario_luigi_stock_native_1122 import H, OUT, R, ROM, preserve_script
from run_stdout_mesen_1110 import run


FORMS = {'alex': (0, 'ALEX'), 'ryan': (1, 'RYAN')}
ROUTES = {'upgrades': (0, 1), 'life': (0, 3), 'star': (0, 2)}
MENU_PATH = ('down', 'down', 'right', 'right', 'right', 'right')
OBSERVER = R/'tools/audit/ice_climbers_stock_observer_1122.lua'
STOCK = R/'tools/playthroughs/megaman_proto_stock_1123.lua'


def bindings(raw, form, route):
    digest = H(raw)
    if digest != NIGHTLY:
        assert H(Side.inverse(raw)) == NIGHTLY
    variant, name = FORMS[form]
    bundle = dict(W.Symbols.bundle(), raw=raw)
    menu = W.UI.seed(bundle, 0)
    for key in (4, 4, 1, 1, 1, 1) + (32,) * variant:
        W.UI.key(menu, key)
    assert W.UI.menu_name(menu)[0] == name
    assert tuple(N.get(menu, n) for n in ('CrossoverMenuIndex', 'SelectedCharacter', 'RcVariant')) == (20, 21, variant)
    fields = [n for n in RAM_FIELDS if not n.startswith('Ic')]
    fields += ['RcVariant', 'RcHealth', 'RcTier', 'RcMarker', 'RcClock', 'RcPrevious', 'PlayerScoreDisplay']
    ram = {n: W.address(bundle, n) for n in fields}

    def hook(symbol, delta=0):
        pc, at = W.address(bundle, symbol)+delta, W.location(bundle, symbol)+delta
        bank = (at-16)//8192
        assert at-16 == bank*8192+(pc&8191)
        return dict(pc=pc, tag=bank|128, offset=at-16, hex=raw[at:at+12].hex())

    hooks = {name: hook(name) for name in ('GameLoop', 'RcMovement',
             'HandlePowerUpCollision', 'PlayerHeadCollision')}
    if route == 'life':
        symbol = 'DecNumTimer'
        at = W.location(bundle, symbol)
        life_increment = b'\xee'+ram['NumberofLives'].to_bytes(2, 'little')
        body = raw[at:at+48]
        assert body.count(life_increment) == 1
        hooks['LifeCredit'] = hook(symbol, body.index(life_increment))
    navigation = ['']*32
    for cursor, direction in zip((0, 8, 16, 17, 18, 19), MENU_PATH, strict=True):
        navigation[cursor] = direction
    return dict(sha=digest, form=form, route=route, char=21, name=name, slot=20, variant=variant,
                mode_value=0, expected=list(ROUTES[route]), ram=ram, hooks=hooks, navigation=navigation)


def controller(raw, form, route):
    cfg = bindings(raw, form, route)
    opener = BASE.read_bytes()
    assert H(opener) == BASE_SHA
    text = OBSERVER.read_text(encoding='utf-8')

    def edit(before, after):
        nonlocal text
        text = once(text, before, after)

    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant",
         "r('SelectedCharacter')==C.char and r('RcVariant')==C.variant")
    edit("r('IcVariant')~=C.variant", "r('RcVariant')~=C.variant")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected=C.expected')
    edit("power=r('IcPower')", "power=r('RcTier',C.variant),hp=r('RcHealth',C.variant),growth=0")
    edit('c.poll=polls;c.char=20;', 'c.frame=motor;c.poll=motor;c.char=C.char;c.update=motor;')
    edit('c.lastA=mask&128~=0', "c.lastA=r('RcPrevious')&128~=0")
    edit('local lifePending', '''local lifePending
local clockInput={}
local function score()
 local n=0;for i=0,5 do n=n*10+r('PlayerScoreDisplay',i)end;return n
end''')
    edit('Living Ice Climber', 'Living River City fighter')
    edit("assert(updates<5100,'Bounded pickup route')", "assert(updates<5100 and s.hp>0 and s.yHigh<2,'Bounded living pickup route')")
    edit('q.birth={actor=a,player=s}', "assert(heads[tostring(a.kind)],'Authored head bump before item birth');q.birth={actor=a,player=s}")
    edit(' local complete=true', ''' local stock=ROBOT_STOCK_STATE
 if stock.missing and not checks[tostring(stock.kind)].collect then
  finish(false,'Authored pickup disappeared before collection');return
 end
 local complete=true''')
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then',
         'if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() and s.state==0 then')
    edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end",
         "else assert(s.power==q.grant.power and s.status==q.grant.status and score()>=q.collect.score_before+1000,'Upgrade and score persist') end")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')",
         "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Star and score persist')")
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end",
         "if complete then finish(true,'Authored pickups, native credit and 25 further movement updates');return end\n clockInput=scope()and choose(context())or{}")
    edit("sound=r('Square2SoundQueue')}", "sound=r('Square2SoundQueue'),score_before=p.score}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')",
         """assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,
    'River City pickup advances its own tier')
  assert(s.hp==math.min(64,p.before.hp+24),'River City pickup restores stamina with cap64')""")
    edit("if p.name=='IcMovement' then motor=motor+1",
         "if p.name=='RcMovement' then\n   if r('RcClock')~=p.clock then motor=motor+1 end")
    edit('local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}',
         "local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc),clock=r('RcClock')}")
    edit('  p.actor=a;p.before=state()', """  assert(a.state&128~=0,'Mature authored pickup reaches its real collector')
  q.mature={actor=a,player=state()}
  p.actor=a;p.before=state();p.score=score()""")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0',
         'phase=ROBOT_STOCK_STATE or {},controller_only=true,files=0,images=0')
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})',
         'local b=not entered and menu() or (scope() and clockInput or {})')
    edit('  entered=physical', """  assert(r('RcMarker')==199 and r('RcTier',C.variant)==0 and r('RcHealth',C.variant)==48,
   'Actual selected River City constructor')
  entered=physical;clockInput=choose(context())""")
    policy = '''local function choose(c)
 if c.power==0 then return base(c) end
 return stock(c)
end'''
    stock = once(STOCK.read_text(encoding='utf-8'),
                 'local distance=goal-c.x-speed(c)/5', 'local distance=goal-c.x')
    script = '\n'.join(('local C='+value(cfg), 'local ROSTER_CONFIG={name=C.form}',
                         'local base=(function()\n'+opener.decode()+'\nend)()',
                         'local stock=(function()\n'+stock+'\nend)()',
                         policy, text))
    assert not any(t in script for t in ('emu.write', 'emu.setState', 'io.open', 'dofile',
                                         'saveState', 'loadState', 'takeScreenshot'))
    LuaRuntime().compile(script)
    return script.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', choices=tuple(FORMS), default='alex')
    parser.add_argument('--route', choices=tuple(ROUTES), default='upgrades')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    program = controller(raw, args.form, args.route)
    print('RIVER CITY STOCK SOURCE '+json.dumps(dict(form=args.form, route=args.route,
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
            receipt = run(script, ROM, OUT/'capture', H(raw), 180)
        assert receipt['script_SHA256'] == H(program)
        assert receipt['outputs_written'] == 0 and not receipt['images']
    finally:
        assert ROM.read_bytes() == raw and check(ROM) == guard
    print('RIVER CITY STOCK NATIVE '+json.dumps(receipt, separators=(',', ':')), flush=True)
    return int(not receipt['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
