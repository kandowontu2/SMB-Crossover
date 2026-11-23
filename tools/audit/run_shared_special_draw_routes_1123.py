"""Recheck a full stage and a live powerup route on the private draw ROM."""

import argparse
import json

import compose_dkjr_mushroom_slot_order_1123 as Donkey
import probe_special_draw_routing_1123 as Draw
import run_grant_stock_1123 as Grant


FIRST_PIT = b"""
 if T.kind==1 and T.phase=='travel' and (c.x>=1072 and c.x<1152 or T.firstPit and T.firstPit.air) then
  local g=T.firstPit
  if not g then g={};T.firstPit=g end
  if not g.air and not g.landed then
   if c.x<1094 then return defend(c,{right=true})end
   if not c.grounded or c.lastA or c.r('Cv3AttackAge')~=0 then return{}end
   assert(c.x<=1100 and c.y==176 and solid(c,c.x,208)
     and not solid(c,1112,208) and not solid(c,1128,208) and solid(c,1144,208),
    'Actual first-pit support, gap and far bank')
   g.air=true;g.from=sample(c)
  end
  if g.air then
   if not g.accepted and not c.grounded and c.r('Cv3Previous')&128~=0 then g.accepted=sample(c)end
   if g.accepted and c.grounded then
    assert(c.x>=1130 and c.y==176,'Actual Grant landing beyond the first pit')
    g.air=false;g.landed=sample(c)
   else
    assert(c.update-g.from.update<75,'Bounded first-pit jump')
    return{right=true,a=c.update-g.from.update<32}
   end
  end
 end
"""


def controllers(raw, candidate, *, first_pit=False):
    digest = Draw.Cadence.Timing.H(candidate).encode()
    parent = Donkey.CANDIDATE.encode()
    result = {}
    if not first_pit:
        stage = Donkey.full_controller(raw).encode()
        assert stage.count(parent) == 2
        result['Donkey Kong Jr. full 1-1'] = stage.replace(parent, digest)
    flower = Grant.controller(raw, 'upgrades')
    assert Grant.H(flower) == Grant.PINS[Donkey.CANDIDATE]['upgrades'] and flower.count(parent) == 1
    for name, hook in Grant.bindings(Grant.origin(raw), 'upgrades')['hooks'].items():
        begin = 16 + hook['offset']
        expected = bytes.fromhex(hook['hex'])
        assert raw[begin:begin + len(expected)] == candidate[begin:begin + len(expected)] == expected, name
    if first_pit:
        marker = b" if T.phase=='travel'then\n  if c.x<goal-76 then return travel(c)end"
        assert flower.count(marker) == 1
        flower = flower.replace(marker, FIRST_PIT + marker, 1)
    result['Grant Fire Flower and dagger'] = flower.replace(parent, digest)
    for text in result.values():
        Draw.Cadence.LuaRuntime().compile(text.decode())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--grant-first-pit', action='store_true', help='Use a grounded takeoff at the first pit')
    args = parser.parse_args()
    timing = Draw.Cadence.Timing
    raw = timing.ROM.read_bytes()
    candidate, _ = Draw.proposal(raw)
    digest = timing.H(candidate)
    modes = controllers(raw, candidate, first_pit=args.grant_first_pit)
    output = timing.SHARED
    target, script = output/'candidate.nes', output/'controller.lua'
    assert set(output.iterdir()) == {target, script} and target.read_bytes() == raw
    guard = Draw.Cadence.check(timing.ROM)
    assert guard['ROM_sha256'] == Donkey.CANDIDATE and not guard['matching_patch_files']
    Draw.Cadence.require_free_workspace(timing.R, target, allow_interactive=True)
    original = script.read_bytes()
    success = True
    try:
        target.write_bytes(candidate)
        private = Draw.Cadence.check(target)
        assert private['ROM_sha256'] == digest and not private['matching_patch_files']
        for name, text in modes.items():
            script.write_bytes(text)
            result = Draw.Cadence.run(script, target, output/'capture', digest, 260, long_no_capture=True)
            receipt = result['receipt']
            pit = receipt.get('phase', {}).get('firstPit')
            if args.grant_first_pit and result['passed']:
                assert pit and pit.get('accepted') and pit.get('landed')
            print('SHARED DRAW ROUTE ' + json.dumps(dict(route=name, ROM_SHA256=digest,
                passed=result['passed'], reason=receipt.get('reason'), terminal=receipt.get('terminal'),
                frames=receipt.get('physical_frames'), receipt_SHA256=result['receipt_SHA256'],
                script_SHA256=result['script_SHA256'], first_pit=pit)), flush=True)
            assert result['outputs_written'] == 0 and not result['images']
            success = success and result['passed']
            assert Draw.Cadence.check(target) == private
    finally:
        script.write_bytes(original)
        target.write_bytes(raw)
        assert set(output.iterdir()) == {target, script} and Draw.Cadence.check(timing.ROM) == guard
    return int(not success)


if __name__ == '__main__':
    raise SystemExit(main())
