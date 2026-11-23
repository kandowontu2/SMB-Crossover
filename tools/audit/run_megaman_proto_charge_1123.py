"""Use the Buster after ordinary Easy upgrades and the Hard Charge pickup."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
import run_megaman_proto_stock_1123 as Stock
from replay_sonic_hidden_life_f7c9_1116 import value


def controller(raw, form, *, hard=False):
    source = Stock.controller(raw, form, 'upgrades').decode()
    bundle = Stock.W.Symbols.bundle()
    ram = {name: Stock.W.address(bundle, name) for name in (
        'MmBulletAge', 'MmBulletDir', 'MmBulletPage', 'MmBulletType', 'MmBulletX',
        'MmAudioShotType', 'MmChargeFrames', 'MmCharging')}
    symbol = 'MegaManWeapons::Spawn'
    pc, at = Stock.W.address(bundle, symbol), Stock.W.location(bundle, symbol)
    bank = (at-16)//8192
    assert at-16 == bank*8192+(pc&8191)
    hook = dict(pc=pc, tag=bank|128, offset=at-16, hex=raw[at:at+12].hex())
    temp = Stock.W.address(bundle, 'MmTemp')
    yhi = Stock.W.address(bundle, 'Player_Y_HighPos')
    sta = bytes((0x85, temp)) if temp < 256 else b'\x8d'+temp.to_bytes(2, 'little')
    ldy = bytes((0xa4, yhi)) if yhi < 256 else b'\xac'+yhi.to_bytes(2, 'little')
    assert raw[at:at+len(sta+ldy)] == sta+ldy, 'Authentic Buster Spawn entry'

    def edit(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new, 1)

    line = source.split('\n', 1)[0]
    edit(line, line+f'\nfor n,v in pairs({value(ram)})do C.ram[n]=v end'
         f'\nC.hooks.ChargeSpawn={value(hook)}\nC.buster_cue={Stock.W.address(bundle, "Sfx_Fireball")}')
    observer = (Stock.R/'tools/playthroughs/megaman_proto_charge_1123.lua').read_text(encoding='utf-8')
    edit('local function json(v)', observer+'\nlocal function json(v)')
    edit('items=checks,head=heads,tail=tail,terminal=state()', 'items=checks,head=heads,tail=tail,terminal=state(),buster=charge.tiers')
    last_tier = 1 if hard else 2
    reason = 'The Hard Mushroom grants Charge and releases at 47, 48 and 87 pass' if hard else 'Earned Buster tiers passed releases at 47, 48 and 87'
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates');return end",
         f"if complete and charge.tiers[{last_tier}] and charge.tiers[{last_tier}].complete then\n"
         f"  finish(true,'{reason}');return\n end")
    edit('clockInput=scope()and choose(context())or{}', 'clockInput=scope()and(chargeControl(s)or choose(context()))or{}')
    edit("  elseif p.actor then collected(p) end",
         "  elseif p.buster then chargeSpawned(p,cpu['cpu.x'])\n  elseif p.actor then collected(p) end")
    edit(" local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}",
         " local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}\n"
         " if name=='ChargeSpawn' then chargeStarted(p,cpu['cpu.a']);if not p.buster then return end end")
    if hard:
        inventory = {n:Stock.W.address(bundle,n) for n in ('InvOwnedHi','InvSelected')}
        mask = raw[Stock.W.location(bundle, 'InvMushroomHi')+1]
        name = Stock.W.location(bundle, 'InvName12')
        assert mask == 4 and raw[name:name+7] == bytes.fromhex('0c110a1b100e24'), 'Native CHARGE label'
        edit(f'C.buster_cue={Stock.W.address(bundle, "Sfx_Fireball")}',
             f'C.buster_cue={Stock.W.address(bundle, "Sfx_Fireball")}\n'
             f'for n,v in pairs({value(inventory)})do C.ram[n]=v end\n'
             f'C.mode_value=1;C.expected={{0}};C.charge_owned_mask={mask}')
        edit('  p.actor=a;p.before=state();p.score=score();p.cue=sound[32]or 0',
             '  p.actor=a;p.before=state();p.score=score();p.cue=sound[32]or 0\n'
             "  p.inventory_before=r('InvOwnedHi',C.char)")
        edit(' if a.kind<2 then',
             " local after=r('InvOwnedHi',C.char)\n"
             " assert(p.inventory_before&C.charge_owned_mask==0 and after==p.inventory_before|C.charge_owned_mask,"
             "'The ordinary Hard mushroom awards Charge')\n"
             " assert(r('InvSelected',C.char)==0,'Charge retains the equipped Buster')\n"
             " q.collect.inventory={before=p.inventory_before,after=after,charge=C.charge_owned_mask}\n"
             ' if a.kind<2 then')
        edit(' if not pickup.grant then return end', ' if not pickup.grant then return {}end')
        edit(" if T.phase=='align'then\n  local aim=target-5", """ if T.phase=='align'then
  if kind==0 and not T.hardFloorReached then
   if c.grounded and c.y>=160 then T.hardFloorReached=true
   else return {left=c.x>224}end
  end
  local aim=target-5""")
    LuaRuntime().compile(source)
    assert not any(t in source for t in ('emu.write', 'emu.setState', 'io.open', 'dofile',
                                         'saveState', 'loadState', 'takeScreenshot'))
    return source.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', choices=tuple(Stock.FORMS), required=True)
    parser.add_argument('--hard', action='store_true', help='Verify the Hard Mushroom grants Charge and enables the Buster')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = Stock.ROM.read_bytes()
    program = controller(raw, args.form, hard=args.hard)
    print('BUSTER SOURCE '+json.dumps(dict(form=args.form, hard=args.hard, ROM_SHA256=Stock.H(raw),
          controller_SHA256=Stock.H(program))), flush=True)
    if not args.run:
        return 0
    guard = check(Stock.ROM)
    candidate, script = Stock.OUT/'candidate.nes', Stock.OUT/'controller.lua'
    assert set(Stock.OUT.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    try:
        with Stock.preserve_script(script, candidate, raw) as stage:
            stage(program)
            result = Stock.run(script, Stock.ROM, Stock.OUT/'capture', Stock.NIGHTLY, 180)
            print('BUSTER NATIVE '+json.dumps(result,separators=(',', ':')), flush=True)
            assert result['script_SHA256'] == Stock.H(program)
            assert result['outputs_written'] == 0 and not result['images']
    finally:
        assert Stock.ROM.read_bytes() == raw and check(Stock.ROM) == guard
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
