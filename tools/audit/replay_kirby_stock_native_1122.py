"""Check Kirby's natural 1-UP and Star pickups from the installed MMC5 nightly."""

import argparse
from hashlib import sha256
import json

import replay_kirby_food_native_1111 as Food
import replay_kirby_current_checks_1114 as Kirby
from capture_budget import preflight
from check_ff_stdout_controller_source_1110 import LuaRuntime
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import R, run


ROM = Food.Cpu.ROM
OUT = R / 'build/smb2-flag-native-1113'
TAIL = R / 'tools/playthroughs/kirby_stock_native_1122.lua'
GROUND_CHARGE = R / 'tools/playthroughs/kirby_ground_charge_native_1122.lua'
COPY_RECOVERY = R / 'tools/playthroughs/kirby_copy_recovery_native_1122.lua'
SPIT_STAR = R / 'tools/playthroughs/kirby_spit_star_native_1122.lua'

# Verify the native instructions used as pickup witnesses before launching.
HOOKS = {
    'stockCollector': (3, 0xAF71, '202f8da90620b598'),
    'starReturn': (3, 0xAF92, '60'),
    'lifeReturn': (3, 0xAFF2, '60'),
    'lifeCredit': (126, 0x8987, 'ee5f07a9408d0401'),
    'lifeCredited': (126, 0x898F, 'beb589b9aa899d31'),
}


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def controller(raw, kind, *, lifecycle=False):
    assert not lifecycle or kind == 2
    authority = Food.Cpu.Authority
    bundle = authority.scoped_load(authority.AUTHORITY)
    addresses = {name: Food.Cpu.Host.address(bundle, name) for name in (
        'MmVX', 'KbHurtMove', 'Player_Y_HighPos', 'StarInvincibleTimer',
        'AreaMusicQueue', 'Square2SoundQueue', 'FloateyNum_Control',
        'PlayerScoreDisplay', 'GuestPowerupActive', 'Block_Buffer_1',
        'GuestHurtTicks', 'BlockBounceTimer', 'KbJumpAge', 'Player_Y_Speed',
    )}
    # The life writer and both popup returns are inside routines, so their
    # bindings include the physical bank as well as the CPU address.
    hooks = {}
    for name, (bank, pc, hex_bytes) in HOOKS.items():
        offset = bank * 8192 + (pc & 8191)
        expected = bytes.fromhex(hex_bytes)
        assert raw[16 + offset:16 + offset + len(expected)] == expected, name
        hooks[name] = dict(pc=pc, offset=offset, bytes=list(expected))
    if lifecycle:
        for name, symbol in (('starDefeat', 'ShellOrBlockDefeat'),
                             ('restoreMusic', 'GetAreaMusic')):
            at = Food.Cpu.Host.location(bundle, symbol)
            expected = bundle['raw'][at:at+4]
            assert raw[at:at+4] == expected, symbol
            hooks[name] = dict(pc=Food.Cpu.Host.address(bundle, symbol),
                               offset=at-16, bytes=list(expected))

    base = Food.controller(raw)
    bindings = [f'C.stockKind={kind}', f'C.stockLifecycle={str(lifecycle).lower()}',
                f'for k,v in pairs({authority.lua(addresses)}) do C.ram[k]=v end',
                f'for k,v in pairs({authority.lua(hooks)}) do C.hooks[k]=v end']
    base = replace_once(base, "C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))",
                        '\n'.join(bindings) + "\nC.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))")
    base = replace_once(base, 'local pad=0', 'local pad=0\nlocal stock={resume=0}')
    before = base.index(" local passed=reason=='both-earned-food'")
    after = base.index(" print('SMB_NATIVE_RECEIPT '", before)
    expectation = ("reason=='natural-star-lifecycle' and stock.defeat and stock.musicRestored"
                   " and stock.expiry and stock.injury and stock.resume>=25"
                   if lifecycle else "reason=='natural-stock-credit' and stock.credit and stock.resume>=25")
    base = base[:before] + (
        f" local passed={expectation}\n"
        "   and active() and stage() and identity()\n"
    ) + base[after:]
    base = replace_once(base, 'phase=phase,initial=firstActive', 'stock=stock,phase=phase,initial=firstActive')
    base = replace_once(base, " local expected=#births==0 and 336 or 1248\n"
                        " assert(#births<2 and a.x==expected and a.y==136,'Expected authored food block')",
                        " if stock.request then\n"
                        "  local bx=C.stockKind==3 and 1024 or 1616\n"
                        "  local by=C.stockKind==3 and 120 or 136\n"
                        "  assert(not stock.birth and a.x==bx and a.y==by,'Expected authored stock block')\n"
                        "  stock.birth={x=a.x,y=a.y,frame=frame,slot=slot}\n"
                        "  return\n"
                        " end\n"
                        " local expected=#births==0 and 336 or 1248\n"
                        " assert(#births<2 and a.x==expected and a.y==136,'Expected authored food block')")
    base = replace_once(base, ' local kind=#contacts', ' if a.kind>=2 then return end\n local kind=#contacts')
    marker = 'emu.addEventCallback(guarded(function()\n polls=polls+1'
    base = replace_once(base, marker, TAIL.read_text(encoding='utf-8') + '\n' + marker)
    base = replace_once(base, " and r('NumberofLives')==2,'Live native World 1-1')",
                        " and r('NumberofLives')==(stock.life and 3 or 2),'Live native World 1-1')")
    base = replace_once(base, " if #heals==2 then finish('both-earned-food');return end\n", '')
    if lifecycle:
        base = replace_once(base, " assert(frame<=5400,'Bounded physical Kirby food route')",
                            " assert(frame<=7200,'Bounded physical Kirby Star lifecycle route')")
    return replace_once(base, 'if #heals==0 then pad=mushroom(px,y,ground,item) else pad=flower(px,y,ground,item) end',
                        "if stockControl(px,y,ground,item) then return end\n"
                        " if #heals==0 then pad=mushroom(px,y,ground,item) else pad=flower(px,y,ground,item) end")


def inhale_parts(raw, hook_names, ram_names):
    authority = Food.Cpu.Authority
    host = Food.Cpu.Host
    assert authority.sha(authority.AUTHORITY) == authority.AUTHORITY_ROM
    assert authority.sha(authority.AUTHORITY.with_suffix('.dbg')) == authority.AUTHORITY_DBG
    bundle = authority.scoped_load(authority.AUTHORITY)
    start = 16 + 74 * 8192
    bank = raw[start:start+8192]
    if sha256(bank).hexdigest() != Kirby.BANK_SHA:
        # The Sonic contact update shares bank 74 with Kirby. Compare the bank
        # after undoing only the two known native Sonic ingress changes.
        import compose_sonic_original_contact_1122 as Sonic
        assert sha256(raw).hexdigest() == '59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
        program = Sonic.program()['images']
        for at, before, after in ((0xBDC, Sonic.OLD_GATE, program['INGRESS'].ljust(64, b'\xea')),
                                  (0x1F03, Sonic.OLD_BODY_GATE, program['BODY_GATE'])):
            assert len(before) == len(after) and bank[at:at+len(after)] == after
            bank = bank[:at] + before + bank[at+len(after):]
    assert sha256(bank).hexdigest() == Kirby.BANK_SHA
    assert authority.sha(Kirby.INHALE) == Kirby.PINS[Kirby.INHALE]
    config, body = Kirby.INHALE.read_text(encoding='utf-8').split('\n', 1)
    lua = LuaRuntime()
    q = lua.execute(config + '\nreturn C')
    for name, address in q.ram.items():
        assert host.address(bundle, name) == address, name
    for name, hook in q.hooks.items():
        expected = bytes.fromhex('a9018d0c5c') if name == 'erased' else bytes(
            value for _, value in sorted(hook.bytes.items()))
        at = 16 + hook.offset
        assert raw[at:at+len(expected)] == expected, name
    hooks = {}
    for name, symbol in hook_names:
        at = host.location(bundle, symbol)
        expected = bundle['raw'][at:at+6]
        assert raw[at:at+6] == expected, symbol
        hooks[name] = dict(pc=host.address(bundle, symbol), offset=at-16, bytes=list(expected))
    addresses = {name: host.address(bundle, name) for name in ram_names}
    config += ('\nC.hooks.erased.bytes={169,1,141,12,92}'
               f'\nfor k,v in pairs({authority.lua(addresses)}) do C.ram[k]=v end'
               f'\nfor k,v in pairs({authority.lua(hooks)}) do C.hooks[k]=v end')
    return config, body, lua


def charge_controller(raw, *, recover_copy=False):
    hooks = [('chargeStart', 'KbWeapons::CopyAttack'), ('chargeDefeat', 'KbBodyContact::Defeat')]
    ram = ['MmVX', 'KbFloat', 'FrameCounter']
    if recover_copy:
        hooks.extend((('dropCopy', 'KbDropCopy'), ('weaponDone', 'KbWeapons::Done')))
        ram.extend(('KbDropKind', 'KbDropAge', 'KbDropX', 'KbDropPage', 'KbDropY', 'KbDropVY'))
    config, body, lua = inhale_parts(raw, hooks, ram)
    body = replace_once(body, 'local function finish(reason)',
                        'local charge={spawns={},pipes={},lastJump=-100,resumed=0}\nlocal function finish(reason)')
    begin = body.index(" local passed=reason=='natural-first-inhale'")
    end = body.index(" print('SMB_NATIVE_RECEIPT '", begin)
    body = body[:begin] + """ local passed=reason=='earned-ground-charge' and constructor and capture and erased
    and charge.swallowed and charge.hit and charge.defeated and not injury and identity() and active()
    and stage() and last.hp==6 and last.lives==2 and last.mouth==0 and last.copy==1
""" + body[end:]
    body = replace_once(body, 'native_erase_return=erased,injury=injury',
                        'native_erase_return=erased,charge=charge,injury=injury')
    marker = 'emu.addEventCallback(guarded(function()\n polls=polls+1'
    controls = GROUND_CHARGE.read_text(encoding='utf-8')
    pad = 'chargePad()'
    if recover_copy:
        controls += '\n' + COPY_RECOVERY.read_text(encoding='utf-8')
        pad = 'recoveryPad() or chargePad()'
        body = replace_once(body, 'and charge.swallowed and charge.hit',
                            'and charge.recovery.restored and charge.swallowed and charge.hit')
    body = replace_once(body, marker, controls + '\n' + marker)
    body = replace_once(body, 'if erased then input={}', f'if erased then input={pad}')
    body = replace_once(body, "  if erased and frame>=erased.player.frame+2 then finish('natural-first-inhale');return end\n"
                        "  if x()>=400 then finish('passed-first-encounter-without-capture');return end",
                        "  if erased then chargeTick()\n"
                        "  elseif x()>=400 then finish('passed-first-encounter-without-capture');return end")
    body = replace_once(body, "if frame>=1600 then finish('bounded-first-encounter-timeout') end",
                        "if frame>=3200 then finish('bounded-ground-charge-route') end")
    text = config + '\n' + body
    lua.compile(text)
    return text


def spit_controller(raw):
    config, body, lua = inhale_parts(raw, (('spitSpawn', 'KbWeapons::Spawn'),
                                          ('spitContact', 'KbWeapons::Defeat'),
                                          ('spitConsumed', 'KbWeapons::Consumed'),
                                          ('spitUpdate', 'KbWeapons')),
                                    ('KbFloat', 'KbSavedSlot', 'KbShotType', 'KbShotX',
                                     'KbShotPage', 'KbShotY', 'KbShotVXHi', 'KbShotAge', 'Square1SoundQueue'))
    body = replace_once(body, 'local function finish(reason)',
                        'local spit={actors={},jumps={},resumed=0}\nlocal function finish(reason)')
    begin = body.index(" local passed=reason=='natural-first-inhale'")
    end = body.index(" print('SMB_NATIVE_RECEIPT '", begin)
    body = body[:begin] + """ local passed=reason=='earned-spit-star' and constructor and capture and erased
    and spit.spawn and spit.hit and spit.defeated and spit.resumed==25 and not injury
    and identity() and active() and stage() and last.hp==6 and last.lives==2
    and last.mouth==0 and last.copy==0
""" + body[end:]
    body = replace_once(body, 'native_erase_return=erased,injury=injury',
                        'native_erase_return=erased,spit=spit,injury=injury')
    marker = 'emu.addEventCallback(guarded(function()\n polls=polls+1'
    body = replace_once(body, marker, SPIT_STAR.read_text(encoding='utf-8') + '\n' + marker)
    body = replace_once(body, 'if erased then input={}', 'if erased then input=spitPad()')
    body = replace_once(body, "  if erased and frame>=erased.player.frame+2 then finish('natural-first-inhale');return end\n"
                        "  if x()>=400 then finish('passed-first-encounter-without-capture');return end",
                        "  if erased then spitTick()\n"
                        "  elseif x()>=400 then finish('passed-first-encounter-without-capture');return end")
    body = replace_once(body, "if frame>=1600 then finish('bounded-first-encounter-timeout') end",
                        "if frame>=2400 then finish('bounded-spit-star-route') end")
    text = config + '\n' + body
    lua.compile(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('item', choices=('oneup', 'star', 'star-lifecycle', 'ground-charge',
                                        'copy-recovery', 'spit-star'))
    args = parser.parse_args()
    kind = 3 if args.item == 'oneup' else 2
    initial = check(ROM)
    raw = ROM.read_bytes()
    assert {p.name for p in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert (OUT / 'candidate.nes').read_bytes() == raw
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    script = OUT / 'controller.lua'
    previous = script.read_bytes()
    try:
        variant = 0
        if args.item in ('ground-charge', 'copy-recovery'):
            text = charge_controller(raw, recover_copy=args.item == 'copy-recovery')
            variant = 2
        elif args.item == 'spit-star':
            text = spit_controller(raw)
            variant = 2
        else:
            text = controller(raw, kind, lifecycle=args.item == 'star-lifecycle')
        script.write_bytes(text.encode())
        result = run(script, ROM, OUT / 'capture', initial['ROM_sha256'], 120, variant=variant)
        print('RESULT ' + json.dumps(result, sort_keys=True), flush=True)
        assert result['passed'] and result['outputs_written'] == 0 and not result['images']
    finally:
        script.write_bytes(previous)
        assert check(ROM) == initial and ROM.read_bytes() == raw


if __name__ == '__main__':
    main()
