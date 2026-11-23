"""Compare actual DK Jr. frame cadence using the existing shared test slot."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
import compose_dkjr_dispatch_epoch_1123 as Dispatch
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import run_roster_empty_cadence_1122 as Roster
from run_stdout_mesen_1110 import run


def prepare(parent, candidate):
    for pc in (0x82D9, 0x82BE, 0x82D0):
        offset = Dispatch.offset(126, pc)
        assert parent[offset:offset+16] == candidate[offset:offset+16]
    row = Roster.roster(parent)['DONKEY KONG JR']
    assert (row['raw'], row['slot'], row['cycle']) == (40, 27, 1)
    original = Roster.controller(parent, row)
    pin = Dispatch.h(parent)
    assert original.count(pin) == 1
    updated = original.replace(pin, Dispatch.h(candidate), 1)
    LuaRuntime().compile(updated)
    return original.encode(), updated.encode()


def prepare_full_stage(parent, candidate):
    import check_contra_force_combined_palette_1122 as Combined
    import compose_jay_status_size_publication_00bb_1116 as Jay
    import compose_metal_life_snapshot_root_1116 as Metal
    import compose_mini_weapon_owner_a2_1116 as Mini
    import compose_rogue_hud_scene_dirty_cb95_1116 as Hud
    import compose_rogue_missile_9826_1116 as Missile
    import compose_sonic_ceiling_complete_1327_1116 as Ceiling
    import current_sonic_parent_rom_1122 as Sonic
    import repair_contra_force_beans_ground_1122 as Beans
    import replay_dkjr_forced_entry_current_1116 as Full

    # Recover the existing exact replay input in memory from the verified
    # public image. Never write an older image to the test slot or Downloads.
    image = Beans.inverse(Sonic.inverse(parent))
    assert Dispatch.h(image) == Combined.COMBINED_SHA
    reference = bytearray(image)
    for at, old in Combined.BASE_PREIMAGES+Combined.Palette.preimages():
        reference[at:at+len(old)] = old
    reference = bytes(reference)
    assert Dispatch.h(reference) == Combined.BASE_SHA
    for layer in (Hud, Missile, Mini, Ceiling, Jay, Metal):
        reference = layer.inverse(reference)
    assert Dispatch.packet(reference) == Dispatch.packet(parent)
    observer = Full.controller(reference)
    # The current baseline can briefly publish native State=2 on the solid
    # bank with the source still grounded, at the same position and height.
    # Keep the support checks and use native State=0 as the jump gate.
    wait = """  assert(player==takeoffX and y==176 and grounded and read(0x1e)==0 and groundTile(player)==0x54,
   'Supported second-gap bank while waiting')"""
    steady = """  local nativeState=read(0x1e)
  assert(player==takeoffX and y==176 and grounded and (nativeState==0 or nativeState==2)
   and groundTile(player)==0x54,'Supported second-gap bank while waiting')
  if nativeState==2 then gap.nativeState2=(gap.nativeState2 or 0)+1 end"""
    observer = Full.once(observer, wait, steady)
    observer = Full.once(observer, '  if movingLeft==gapLeft and direction==2 then\n   gap.takeoff',
                         '  if movingLeft==gapLeft and direction==2 and nativeState==0 then\n   gap.takeoff')
    old_pin = Dispatch.h(reference)
    position = Dispatch.COOKIE
    old_cookie = reference[position:position+16].hex()
    assert observer.count(old_pin) == 1 and observer.count(old_cookie) == 1
    scripts = []
    for image in (parent, candidate):
        source = observer.replace(old_pin, Dispatch.h(image), 1)
        source = source.replace(old_cookie, image[position:position+16].hex(), 1)
        LuaRuntime().compile(source)
        scripts.append(source.encode())
    return scripts


def report(result, image, full_stage):
    receipt = result['receipt']
    if full_stage:
        names = ('passed', 'reason', 'updates', 'physical_frames', 'terminal', 'events',
                 'original_work_grounded_returns', 'original_work_entries', 'original_work_returns')
    else:
        names = ('passed', 'reason', 'character', 'phases', 'inclusive_video_frames',
                 'measured_Main', 'no_controller_read_frames', 'native_lag_NMI',
                 'inclusive_Main_costs', 'Main_return_histogram')
    fields = {key: receipt[key] for key in names if key in receipt}
    fields.update(ROM_SHA256=Dispatch.h(image), receipt_SHA256=result['receipt_SHA256'],
                  script_SHA256=result['script_SHA256'], full_stage=full_stage)
    print('DK NATIVE '+json.dumps(fields, separators=(',', ':')), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--full-stage', action='store_true')
    args = parser.parse_args()
    rom = Roster.Timing.ROM
    parent = rom.read_bytes()
    candidate, spans = Dispatch.proposal(parent)
    scripts = prepare_full_stage(parent, candidate) if args.full_stage else prepare(parent, candidate)
    if not args.run:
        print('DK CADENCE SOURCE '+json.dumps(dict(candidate=Dispatch.h(candidate), spans=spans,
                                                    scripts=list(map(Dispatch.h, scripts)))), flush=True)
        return 0

    out = Roster.Timing.SHARED
    target, script = out/'candidate.nes', out/'controller.lua'
    assert set(out.iterdir()) == {target, script} and target.read_bytes() == parent
    public_guard, test_guard = check(rom), check(target)
    for guard in (public_guard, test_guard):
        assert guard['ROM_sha256'] == Dispatch.h(parent) and not guard['matching_patch_files']
    require_free_workspace(Roster.Timing.R, rom, allow_interactive=True)
    previous = script.read_bytes()
    try:
        for image, program, path in ((parent, scripts[0], rom), (candidate, scripts[1], target)):
            if path == target:
                target.write_bytes(image)
                guard = check(target)
                assert guard['ROM_sha256'] == Dispatch.h(image) and not guard['matching_patch_files']
            script.write_bytes(program)
            result = run(script, path, out/'capture', Dispatch.h(image), 240 if args.full_stage else 90)
            assert result['outputs_written'] == 0 and not result['images']
            report(result, image, args.full_stage)
            if not result['passed']:
                return 1
    finally:
        target.write_bytes(parent)
        script.write_bytes(previous)
        assert check(target) == test_guard and check(rom) == public_guard
        assert script.read_bytes() == previous and set(out.iterdir()) == {target, script}
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
