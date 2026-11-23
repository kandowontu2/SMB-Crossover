"""Qualify Karnov's full route and optionally replace the verified nightly."""

import argparse
import json

import compose_karnov_side_route_1123 as Trial
import run_karnov_side_pickup_1123 as Pickups
import run_sparse_sprite_scan_native_1123 as Cadence


Previous, Timing = Cadence.Previous, Cadence.Timing


def controller(parent, image):
    text = Pickups.binding(parent, image).decode()

    def replace(before, after):
        nonlocal text
        assert text.count(before) == 1, before
        text = text.replace(before, after, 1)

    # Complete the exact measured Mushroom and Star route before advancing
    # to the final gap and flagpole with normal controller inputs.
    replace('local function drive(c)\n', """local function drive(c)
 if T.stage then
  if c.level==1 then return{}end
  local stage=T.stage
  if c.x>=2420 and c.x<2480 then
   if not stage.gap then
    if c.x<2433 then return{right=true}end
    if c.grounded then stage.gap=c.update+3 end
    return{}
   end
   if c.update<stage.gap then return{}end
   return{right=true,a=c.update<stage.gap+36}
  end
  return ordinary(c)
 end
""")
    replace("assert(identity() and s.world==0 and s.level==0", "assert(identity() and s.world==0 and s.level<=1")
    replace("assert(updates<5000 and s.yHigh<2 and s.lives>=2",
            "assert(updates<9000 and (s.level==1 or s.yHigh<2) and s.lives>=2")
    replace('assert(physical<=6900', 'assert(physical<=15000')
    replace("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates');return end", """
 if complete and not T.stage then T.stage={pickup=s,maxX=s.x,checkpoint_at=0,checkpoints={}}end
 if T.stage then
  local stage=T.stage
  if s.level==0 then
   if s.x>stage.maxX then stage.maxX=s.x;stage.progress=motor end
   if s.engine==4 then stage.flag=stage.flag or s end
   if s.engine==5 then stage.castle=stage.castle or s end
   if motor>=stage.checkpoint_at and #stage.checkpoints<12 then
    stage.checkpoints[#stage.checkpoints+1]=s;stage.checkpoint_at=motor+240
   end
   assert(not stage.progress or motor-stage.progress<600,'Bounded progress to flag')
  elseif scope() and s.yHigh==1 and s.y==176 and s.state==0 then
   stage.grounded=stage.grounded or motor
   stage.grounded_updates=motor-stage.grounded
   if stage.grounded_updates>=25 then
    assert(stage.flag and stage.castle and s.lives==2,'Native flag and castle before the 1-2 entry')
    finish(true,'Cleared 1-1 and completed grounded movement updates in 1-2');return
   end
  else
   stage.grounded=nil
  end
 end""")
    Previous.LuaRuntime().compile(text)
    return text.encode()


def replay(script, rom, expected, capture):
    guard = Previous.check(rom)
    assert guard['ROM_sha256'] == expected and not guard['matching_patch_files']
    proof = Previous.run(script, rom, capture, expected, 210, long_no_capture=True)
    assert not proof['images'] and proof['outputs_written'] == 0
    result = proof['receipt']
    keep = ('passed', 'reason', 'physical_frames', 'movement_updates', 'terminal', 'head')
    summary = {key: result[key] for key in keep if key in result}
    summary['stage'] = result.get('phase', {}).get('stage')
    summary.update(ROM=expected, receipt_SHA256=proof['receipt_SHA256'], script_SHA256=proof['script_SHA256'])
    print('KARNOV SIDE FULL STAGE ' + json.dumps(summary, separators=(',', ':')), flush=True)
    assert proof['passed'], result['reason']
    assert result['controller_only']
    assert {key: value['birth']['actor']['x'] for key, value in result['items'].items()} == {'0': 336, '2': 1616}
    stage = result['phase']['stage']
    assert stage['flag']['engine'] == 4 and stage['castle']['engine'] == 5 and stage['grounded_updates'] >= 25
    assert result['terminal']['lives'] == 2 and result['terminal']['level'] == 1
    assert Previous.check(rom) == guard
    return proof['receipt_SHA256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--installed', action='store_true')
    args = parser.parse_args()
    guard = Previous.check(Timing.ROM)
    parent = Timing.ROM.read_bytes()
    work = Timing.SHARED
    candidate, script = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {candidate, script} and candidate.read_bytes() == parent
    current = guard['ROM_sha256']
    assert not guard['matching_patch_files']
    if args.installed:
        assert current in (Trial.Cookie.PIN, Trial.CANDIDATE)
        image = parent
    else:
        image = Trial.compose(parent)
        assert Trial.inverse(image) == parent
    expected = Timing.H(image)
    source = controller(parent, image)
    original = script.read_bytes()
    Previous.require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)
    replaced = delivered = False
    try:
        script.write_bytes(source)
        if not args.installed:
            candidate.write_bytes(image)
        receipt = replay(script, Timing.ROM if args.installed else candidate, expected, work / 'capture')
        if args.install:
            assert Previous.check(Timing.ROM) == guard
            replaced = True
            Timing.ROM.write_bytes(image)
            assert replay(script, Timing.ROM, expected, work / 'capture') == receipt
            assert Timing.ROM.read_bytes() == image
            delivered = True
            print(f'KARNOV NIGHTLY {expected} {receipt} {Timing.ROM}', flush=True)
    finally:
        if not delivered:
            if not args.installed:
                candidate.write_bytes(parent)
            if replaced:
                Timing.ROM.write_bytes(parent)
            assert Previous.check(Timing.ROM) == guard
        script.write_bytes(original)
        assert set(work.iterdir()) == {candidate, script}
        assert candidate.read_bytes() == Timing.ROM.read_bytes() == (image if delivered else parent)


if __name__ == '__main__':
    main()
