"""Use an earned Buster charge against a normal 1-1 Goomba."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from replay_sonic_hidden_life_f7c9_1116 import value
import run_megaman_proto_charge_1123 as Charge


Stock = Charge.Stock


def controller(raw, form, *, hard=False):
    source = Charge.controller(raw, form, hard=hard).decode()
    bundle = Stock.W.Symbols.bundle()
    fields = ('MmEnemyHealthLo', 'MmEnemyHealthHi', 'MmSlot', 'FloateyNum_X_Pos', 'FloateyNum_Y_Pos')
    addresses = {name:Stock.W.address(bundle, name) for name in fields}
    symbol = 'MegaManWeapons::DamageEnemy'
    pc, at = Stock.W.address(bundle, symbol), Stock.W.location(bundle, symbol)
    bank = (at-16)//8192
    assert at-16 == bank*8192+(pc&8191)
    helper = Stock.W.address(bundle, 'RosterEnemyHit')
    assert raw[at:at+3] == b'\x20'+helper.to_bytes(2,'little')
    hook = dict(pc=pc, tag=bank|128, offset=at-16, hex=raw[at:at+12].hex())

    def edit(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new, 1)

    edit('local base=(function()', f'for n,v in pairs({value(addresses)})do C.ram[n]=v end\n'
         f'C.expected={{0}};C.hooks.BusterDamage={value(hook)};C.enemy_smack={Stock.W.address(bundle,"Sfx_EnemySmack")}\n'
         'local base=(function()')
    witness = (Stock.R/'tools/playthroughs/megaman_proto_buster_enemy_1123.lua').read_text(encoding='utf-8')
    edit('local function afterMain()', witness+'\nlocal function afterMain()')
    edit('terminal=state(),buster=charge.tiers', 'terminal=state(),buster=charge.tiers,combat=COMBAT_EVIDENCE')
    edit('local combat={}', 'local combat={}\nCOMBAT_EVIDENCE=combat')
    mode_finish = "  finish(true,'The Hard Mushroom grants Charge and releases at 47, 48 and 87 pass');return" if hard else "  finish(true,'Earned Buster tiers passed releases at 47, 48 and 87');return"
    mode_gate = 1 if hard else 2
    edit(f'if complete and charge.tiers[{mode_gate}] and charge.tiers[{mode_gate}].complete then\n'+mode_finish,
         "if complete and charge.tiers[1] and charge.tiers[1].complete then\n"
         "  finish(true,'Earned full Buster charge defeats a live Goomba and earns score');return")
    edit("  elseif p.buster then chargeSpawned(p,cpu['cpu.x'])",
         "  elseif p.buster_hit then witnessDamageReturn(p)\n  elseif p.buster then chargeSpawned(p,cpu['cpu.x'])")
    edit(" if name=='ChargeSpawn' then chargeStarted(p,cpu['cpu.a']);if not p.buster then return end end",
         " if name=='BusterDamage' then witnessDamage(p,cpu['cpu.x']);if not p.buster_hit then return end end\n"
         " if name=='ChargeSpawn' then chargeStarted(p,cpu['cpu.a']);if not p.buster then return end end")
    LuaRuntime().compile(source)
    return source.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', choices=tuple(Stock.FORMS), required=True)
    parser.add_argument('--hard', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = Stock.ROM.read_bytes()
    program = controller(raw, args.form, hard=args.hard)
    print('BUSTER ENEMY SOURCE '+json.dumps(dict(form=args.form, hard=args.hard, ROM_SHA256=Stock.H(raw),
          controller_SHA256=Stock.H(program))), flush=True)
    if not args.run:
        return 0
    guard = check(Stock.ROM)
    candidate, script = Stock.OUT/'candidate.nes', Stock.OUT/'controller.lua'
    assert set(Stock.OUT.iterdir()) == {candidate,script} and candidate.read_bytes() == raw
    try:
        with Stock.preserve_script(script, candidate, raw) as stage:
            stage(program)
            result = Stock.run(script, Stock.ROM, Stock.OUT/'capture', Stock.NIGHTLY, 120)
            print('BUSTER ENEMY NATIVE '+json.dumps(result,separators=(',', ':')), flush=True)
            assert result['script_SHA256'] == Stock.H(program)
            assert result['outputs_written'] == 0 and not result['images']
    finally:
        assert Stock.ROM.read_bytes() == raw and check(Stock.ROM) == guard
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
