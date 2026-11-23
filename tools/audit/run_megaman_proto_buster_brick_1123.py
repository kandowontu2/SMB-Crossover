"""Verify a full Buster charge shatters an authored brick after the Mushroom."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from replay_sonic_hidden_life_f7c9_1116 import value
import run_megaman_proto_charge_1123 as Charge


Stock = Charge.Stock


def controller(raw, form):
    source = Charge.controller(raw, form).decode()
    bundle = Stock.W.Symbols.bundle()
    fields = ('MmProbeX', 'MmProbePage', 'MmProbeY', 'MmBlockAttack', 'MmBreakBlock', 'NoiseSoundQueue',
              'SprDataOffset_Ctrl', 'CoinTally', 'Block_State', 'Block_Metatile', 'Block_X_Position', 'Block_PageLoc')
    addresses = {name:Stock.W.address(bundle, name) for name in fields}

    def edit(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new, 1)

    edit('local base=(function()', f'for n,v in pairs({value(addresses)})do C.ram[n]=v end\n'
         'C.expected={0}\nlocal base=(function()')
    witness = (Stock.R/'tools/playthroughs/megaman_proto_buster_brick_1123.lua').read_text(encoding='utf-8')
    edit('local function json(v)', witness+'\nlocal function json(v)')
    edit('terminal=state(),buster=charge.tiers', 'terminal=state(),buster=charge.tiers,brick=impact')
    edit("if complete and charge.tiers[2] and charge.tiers[2].complete then\n"
         "  finish(true,'Earned Buster tiers passed releases at 47, 48 and 87');return",
         "if complete and charge.tiers[1] and charge.tiers[1].complete then\n"
         "  finish(true,'A naturally earned full Buster charge shatters the authored brick');return")
    edit(" if name=='PlayerHeadCollision' then\n  local s=state()",
         " if name=='PlayerHeadCollision' then\n  witnessBrick(cpu)\n  local s=state()")
    edit('local bits={a=128', "emu.addMemoryCallback(guarded('Brick shatter noise',observeBrickNoise),"
         'emu.callbackType.write,C.ram.NoiseSoundQueue)\nlocal bits={a=128')
    LuaRuntime().compile(source)
    return source.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', choices=tuple(Stock.FORMS), required=True)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = Stock.ROM.read_bytes()
    program = controller(raw, args.form)
    print('BUSTER BRICK SOURCE '+json.dumps(dict(form=args.form, ROM_SHA256=Stock.H(raw),
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
            print('BUSTER BRICK NATIVE '+json.dumps(result,separators=(',', ':')), flush=True)
            assert result['script_SHA256'] == Stock.H(program)
            assert result['outputs_written'] == 0 and not result['images']
    finally:
        assert Stock.ROM.read_bytes() == raw and check(Stock.ROM) == guard
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
