"""Check Kirby's natural 1-UP and Star pickups from the installed MMC5 nightly."""

import argparse
import json

import replay_kirby_food_native_1111 as Food
from capture_budget import preflight
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import R, run


ROM = Food.Cpu.ROM
OUT = R / 'build/smb2-flag-native-1113'
TAIL = R / 'tools/playthroughs/kirby_stock_native_1122.lua'

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('item', choices=('oneup', 'star', 'star-lifecycle'))
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
        script.write_bytes(controller(raw, kind, lifecycle=args.item == 'star-lifecycle').encode())
        result = run(script, ROM, OUT / 'capture', initial['ROM_sha256'], 120)
        print('RESULT ' + json.dumps(result, sort_keys=True), flush=True)
        assert result['passed'] and result['outputs_written'] == 0 and not result['images']
    finally:
        script.write_bytes(previous)
        assert check(ROM) == initial and ROM.read_bytes() == raw


if __name__ == '__main__':
    main()
