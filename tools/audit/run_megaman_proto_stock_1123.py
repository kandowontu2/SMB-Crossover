"""Replay ordinary Mega Man and Proto Man pickups in Easy 1-1."""

import argparse
from functools import lru_cache
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
from current_ice_stock_binding_1122 import RAM_FIELDS
from nightly_patch_guard_v1 import check
import profile_sonic_empty_cpu_1110 as Linked
from replay_sonic_hidden_life_f7c9_1116 import value
from run_mario_luigi_stock_native_1122 import H, OUT, R, ROM, preserve_script
from run_rogue_side_pipe_nightly_1123 import NIGHTLY
from run_stdout_mesen_1110 import run


FORMS = {'megaman': (0, 'MEGA MAN'), 'proto': (1, 'PROTO MAN')}
ROUTES = {'upgrades': (0, 1), 'life': (0, 3), 'star': (0, 2)}
W, N = Linked.W, Linked.N


@lru_cache(maxsize=1)
def bindings(raw, form, route):
    assert H(raw) == NIGHTLY
    variant, name = FORMS[form]
    bundle = W.Symbols.bundle()
    menu = W.UI.seed(dict(bundle, raw=raw), 1)
    for _ in range(variant):
        W.UI.key(menu, 32)
    assert W.UI.menu_name(menu)[0] == name
    assert (N.get(menu, 'SelectedCharacter'), N.get(menu, 'ProtoVariant')) == (1, variant)
    fields = [n for n in RAM_FIELDS if not n.startswith('Ic')]
    fields += ['ProtoVariant', 'GuestPowerupActive', 'GuestPowerupTarget', 'GuestLegacyHurt',
               'MmSliding', 'PlayerScoreDisplay']
    ram = {n: W.address(bundle, n) for n in fields}

    hooks = {}
    for tag, symbol in (('GameLoop', 'GameLoop'), ('RobotMovement', 'MegaManMovement'),
                        ('HandlePowerUpCollision', 'HandlePowerUpCollision'),
                        ('PlayerHeadCollision', 'PlayerHeadCollision')):
        pc, at = W.address(bundle, symbol), W.location(bundle, symbol)
        bank = (at-16)//8192
        assert at-16 == bank*8192+(pc&8191), symbol
        hooks[tag] = dict(pc=pc, tag=bank|128, offset=at-16, hex=raw[at:at+12].hex())
    if route == 'life':
        pc, bank = 0x8987, 126
        at = bank*8192+(pc&8191)
        assert raw[16+at:16+at+3] == b'\xee'+ram['NumberofLives'].to_bytes(2, 'little')
        hooks['LifeCredit'] = dict(pc=pc, tag=bank|128, offset=at, hex=raw[16+at:16+at+8].hex())
    navigation = ['right', ''] + [
        ('up' if i < 24 else 'down') if i%8 == 1 else
        ('right' if i%8 >= 6 or i%8 == 0 else 'left') for i in range(2, 32)
    ]
    return dict(sha=NIGHTLY, form=form, route=route, name=name, char=1, slot=1,
                variant=variant, mode_value=0, expected=list(ROUTES[route]), ram=ram,
                hooks=hooks, navigation=navigation)


def controller(raw, form, route):
    config = bindings(raw, form, route)
    base = (R/'tools/playthroughs/megaman_bass_policy.lua').read_text(encoding='utf-8')
    policy = (R/'tools/playthroughs/megaman_proto_stock_1123.lua').read_text(encoding='utf-8')
    observer = (R/'tools/audit/ice_climbers_stock_observer_1122.lua').read_text(encoding='utf-8')

    def edit(old, new):
        nonlocal observer
        assert observer.count(old) == 1, old
        observer = observer.replace(old, new, 1)

    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant", "r('SelectedCharacter')==C.char and r('ProtoVariant')==C.variant")
    edit("r('IcVariant')~=C.variant", "r('ProtoVariant')~=C.variant")
    edit("power=r('IcPower')", "power=r('PlayerStatus'),growth=r('GuestPowerupActive')")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected=C.expected')
    edit('c.poll=polls;c.char=20;', 'c.poll=updates;c.char=C.char;c.update=updates;')
    edit('c.lastA=mask&128~=0', "c.lastA=r('PreviousA_B_Buttons')&128~=0")
    edit("local lifePending", "local lifePending\nlocal clockInput={}\nlocal sound={}")
    edit("local function afterMain()", "local function score()\n local n=0;for i=0,5 do n=n*10+r('PlayerScoreDisplay',i)end;return n\nend\nlocal function afterMain()")
    edit('if #tail==6 then table.remove(tail,1) end', 'if #tail==12 then table.remove(tail,1) end')
    edit('Living Ice Climber', 'Living requested robot')
    edit("assert(updates<5100,'Bounded pickup route')", "assert(updates<5100 and s.yHigh<2,'Bounded living pickup route')")
    edit(' local complete=true', ''' if checks['0'].after and r('GuestLegacyHurt')==1 then
  local c=context();ROBOT_STOCK_STATE.injury={player=s,nearest=c.enemy(),mask=mask}
  finish(false,'Injury after the naturally earned Mushroom');return
 end
 local stock=ROBOT_STOCK_STATE
 if stock.missing and not checks[tostring(stock.kind)].collect then
  finish(false,'Authored pickup disappeared before collection');return
 end
 local complete=true''')
    edit('local a=actor(i);local q=checks[tostring(a.kind)]', '''local a=actor(i);local q=checks[tostring(a.kind)]
  if q and q.birth and q.birth.actor.slot==i and a.flag>0 and a.flag<128 and a.id==46
     and a.state&128~=0 and not q.mature then q.mature={actor=a,player=s}end''')
    edit('q.birth={actor=a,player=s}', "assert(heads[tostring(a.kind)],'Actual block bump before item birth');q.birth={actor=a,player=s}")
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then', '''if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==kind+1
     and score()>=q.collect.score_before+1000 then q.grant=s end
  if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()and s.state==0 then''')
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end",
         "if complete then finish(true,'Authored pickups, native credit and 25 further movement updates');return end\n clockInput=scope()and choose(context())or{}")
    edit("assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')",
         "assert((sound[32]or 0)>p.cue,'Actual new pickup cue')")
    edit('sound=r(\'Square2SoundQueue\')}', "sound=r('Square2SoundQueue'),score_before=p.score,cue64_before=sound[64]or 0}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')",
         "assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Normal robot growth starts');return")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')",
         "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Earned Star and points persist during movement')")
    edit("if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')",
         "if kind==3 then assert(s.lives==q.grant.lives and (sound[64]or 0)>q.collect.cue64_before,'Earned life and cue persist')")
    edit('p.actor=a;p.before=state()', '''assert(a.state&128~=0,'Native collector sees emerged actor')
  q.mature=q.mature or {actor=a,player=state()}
  p.actor=a;p.before=state();p.score=score();p.cue=sound[32]or 0''')
    edit("p.name=='IcMovement'", "p.name=='RobotMovement'")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0',
         'phase=ROBOT_STOCK_STATE or {},sound_cues=sound,pending_returns=#pending,controller_only=true,files=0,images=0')
    edit("local bits={a=128", '''emu.addMemoryCallback(guarded('Native pickup and life cue',function(_,v)
 if entered and(v==32 or v==64)then sound[v]=(sound[v]or 0)+1 end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
local bits={a=128''')
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})',
         'local b=not entered and menu()or(scope()and clockInput or{})')
    edit('  entered=physical', '  entered=physical;clockInput=choose(context())')
    script = '\n'.join(('local C='+value(config), 'local base=(function()\n'+base+'\nend)()',
                        'local choose=(function()\n'+policy+'\nend)()', observer))
    assert not any(t in script for t in ('emu.write', 'emu.setState', 'io.open', 'dofile',
                                         'saveState', 'loadState', 'takeScreenshot'))
    LuaRuntime().compile(script)
    return script.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', choices=tuple(FORMS), default='megaman')
    parser.add_argument('--route', choices=tuple(ROUTES), default='upgrades')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    program = controller(raw, args.form, args.route)
    print('ROBOT_STOCK_SOURCE '+json.dumps(dict(form=args.form, route=args.route, ROM_SHA256=H(raw),
          controller_SHA256=H(program))), flush=True)
    if not args.run:
        return 0
    guard = check(ROM)
    candidate, script = OUT/'candidate.nes', OUT/'controller.lua'
    assert set(OUT.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    try:
        with preserve_script(script, candidate, raw) as stage:
            stage(program)
            result = run(script, ROM, OUT/'capture', NIGHTLY, 180)
            print('ROBOT_STOCK_NATIVE '+json.dumps(result,separators=(',', ':')), flush=True)
            assert result['script_SHA256'] == H(program)
            assert result['outputs_written'] == 0 and not result['images']
    finally:
        assert ROM.read_bytes() == raw and check(ROM) == guard
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
