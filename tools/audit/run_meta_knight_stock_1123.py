"""Verify Meta Knight's earned pickups in ordinary Easy 1-1."""

import argparse
import json

import compose_scrooge_prepare_stack_1123 as Nightly
import replay_kirby_food_native_1111 as Food
import replay_kirby_stock_native_1122 as Stock
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_mario_luigi_stock_native_1122 import H, OUT, ROM, preserve_script
from run_stdout_mesen_1110 import run


def food_controller(raw, goal):
    assert H(raw) == Nightly.CANDIDATE
    authority = Food.Cpu.Authority
    bundle = authority.scoped_load(authority.AUTHORITY)
    addresses = {name: Food.Cpu.Host.address(bundle, name) for name in ('KbClock',)}
    source = Food.controller(raw)

    def edit(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new, 1)

    edit("C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))",
         "C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))\n"
         f"assert(C.sha=='{H(raw)}','Exact installed nightly')\n"
         f"local goal={goal}\n"
         f"for key,address in pairs({authority.lua(addresses)}) do C.ram[key]=address end")
    edit("r('SelectedCharacter')==13 and r('KbVariant')==0",
         "r('SelectedCharacter')==13 and r('KbVariant')==1")
    edit(" assert(r('CrossoverMenuIndex')==C.slot and identity(),'Actual Easy Kirby selection')",
         " press('select')\n"
         " assert(r('CrossoverMenuIndex')==C.slot and identity(),'Actual Easy Meta Knight selection')")
    edit('local pad=0', 'local pad=0\nlocal continued')
    edit("local passed=reason=='both-earned-food' and #births==2 and #mature==2 and\n"
         "   #contacts==2 and #heals==2 and #graphics==2 and r('KbHealth')==6 and r('NumberofLives')==2 and\n"
         "   r('KbFoodKind')==0 and active() and stage() and identity()",
         "local passed=reason=='earned-food' and #births==goal and #mature==goal and\n"
         "   #contacts==goal and #heals==goal and #graphics==goal and r('KbHealth')==6 and r('NumberofLives')==2 and\n"
         "   r('KbFoodKind')==goal%2 and active() and stage() and identity() and continued and continued.moves>=25")
    edit('contacts=contacts,heals=heals,graphics=graphics,injuries=injuries,menu=events',
         'contacts=contacts,heals=heals,graphics=graphics,injuries=injuries,menu=events,continued=continued')
    edit(" if #heals==2 then finish('both-earned-food');return end",
         """ assert(r('KbFloat')==0 and r('KbCopy')==0,'Grounded sword alternate has no float or copy')
 if #heals==goal then
  pad=0
  local now=r('KbClock')
  if not continued then continued={clock=now,moves=0}end
  continued.moves=(now-continued.clock)&255
  if continued.moves>=25 and r('Player_State')==0 then finish('earned-food')end
  return
 end""")
    LuaRuntime().compile(source)
    return source.encode()


def stock_controller(raw, kind):
    assert H(raw) == Nightly.CANDIDATE
    source = Stock.controller(raw, kind)
    for old, new in (
        ("C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))",
         "C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))\n"
         f"assert(C.sha=='{H(raw)}','Exact installed nightly')"),
        ("r('SelectedCharacter')==13 and r('KbVariant')==0",
         "r('SelectedCharacter')==13 and r('KbVariant')==1"),
        (" assert(r('CrossoverMenuIndex')==C.slot and identity(),'Actual Easy Kirby selection')",
         " press('select')\n"
         " assert(r('CrossoverMenuIndex')==C.slot and identity(),'Actual Easy Meta Knight selection')"),
        ("  if C.stockKind == 3 and y <= 152 then pad = pad | 8 end\n", ''),
        ("   if not ground and px >= 1332 then pad = pad | 8 end\n", ''),
        (" local item=pickupState()", " assert(r('KbFloat')==0 and r('KbCopy')==0,'Grounded sword alternate')\n"
         " local item=pickupState()"),
    ):
        source = Stock.replace_once(source, old, new)
    LuaRuntime().compile(source)
    return source.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', choices=('mushroom', 'flower', 'life', 'star'), default='mushroom')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    digest = H(raw)
    if args.route in ('mushroom', 'flower'):
        program = food_controller(raw, 1 if args.route == 'mushroom' else 2)
    else:
        program = stock_controller(raw, 3 if args.route == 'life' else 2)
    guard = check(ROM)
    rom, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    assert guard['ROM_sha256'] == digest and not guard['matching_patch_files']
    assert set(OUT.iterdir()) == {rom, script} and rom.read_bytes() == raw
    try:
        with preserve_script(script, rom, raw) as stage:
            stage(program)
            result = run(script, ROM, OUT / 'capture', digest, 190)
        assert result['script_SHA256'] == H(program) and result['outputs_written'] == 0 and not result['images']
    finally:
        assert ROM.read_bytes() == raw and check(ROM) == guard
    print('META STOCK ' + json.dumps(result, separators=(',', ':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
