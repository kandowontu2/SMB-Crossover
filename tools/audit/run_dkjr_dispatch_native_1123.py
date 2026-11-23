"""Compare actual DK Jr. frame cadence using the existing shared test slot."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
import compose_dkjr_dispatch_epoch_1123 as Dispatch
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import run_roster_empty_cadence_1122 as Roster
from run_stdout_mesen_1110 import run


def prepare(parent, candidate, name='DONKEY KONG JR'):
    for pc in (0x82D9, 0x82BE, 0x82D0):
        offset = Dispatch.offset(126, pc)
        assert parent[offset:offset+16] == candidate[offset:offset+16]
    expected = {'DONKEY KONG JR': (40, 27, 1), 'MINI MARIO': (41, 0, 8)}
    row = Roster.roster(parent)[name]
    assert (row['raw'], row['slot'], row['cycle']) == expected[name]
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
  local sourceY=ram(2,0x210)
  local sourceStanding=ram(2,0x6b)==1 and sourceY==y+15
  local baseTile=groundTile(player)
  assert(player==takeoffX and y==176 and sourceStanding and (nativeState==0 or nativeState==2)
   and baseTile==0x54,'Supported second-gap bank while waiting')
  if nativeState==2 then
   gap.nativeState2=(gap.nativeState2 or 0)+1
   if not gap.nativeState2First then
    gap.nativeState2First=snapshot()
    gap.nativeState2First.source_y=sourceY;gap.nativeState2First.ground_tile=baseTile
   end
  end"""
    observer = Full.once(observer, wait, steady)
    observer = Full.once(observer, '  if earlyTakeoff or (movingLeft==gapLeft and direction==2) then',
                         '  if nativeState==0 and (earlyTakeoff or (movingLeft==gapLeft and direction==2)) then')
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


def trace_final_cap(program):
    text = program.decode()
    prefix = 'local capTrace={first={},tail={},samples=0,held_right=0,at_gate=0,descending_window=0}\n'
    marker = " if phase=='final-cap'then\n  right=player<stairDown-2\n"
    observer = '''  local row=snapshot()
  local previousTop=priorTop[stairDown]
  local lift=births[tostring(stairDown)]
  row.right_requested=right;row.held=ram(2,0x14);row.input_sample=ram(2,0x15)
  row.source_previous=ram(2,0x6c);row.source_y=ram(2,0x210)
  row.source_x=camera()+ram(2,0x213);row.source_facing=ram(2,0x6d)
  row.source_direction=ram(2,0x54)
  row.contact={ram(2,0x42),ram(2,0x43),ram(2,0x44),ram(2,0x45)}
  row.contact_camera=ram(2,0x435)+256*ram(2,0x436)
  row.lift_top=stairTop;row.lift_previous_top=previousTop;row.on_lift=not not onStairDown
  row.passenger=lift and read(0x566+lift.slot)or nil
  capTrace.samples=capTrace.samples+1
  if row.held&1~=0 then capTrace.held_right=capTrace.held_right+1 end
  if player>=stairDown-2 then capTrace.at_gate=capTrace.at_gate+1 end
  if stairTop and previousTop and stairTop>=80 and stairTop<=92 and stairTop>previousTop then
   capTrace.descending_window=capTrace.descending_window+1
   capTrace.first_window=capTrace.first_window or row
  end
  if not capTrace.furthest or player>capTrace.furthest.x then capTrace.furthest=row end
  if #capTrace.first<8 then capTrace.first[#capTrace.first+1]=row end
  if #capTrace.tail>=12 then table.remove(capTrace.tail,1)end
  capTrace.tail[#capTrace.tail+1]=row
'''
    receipt = 'events=events,'
    traced_receipt = receipt+'final_cap_trace=capTrace,'
    assert text.count(marker) == 1 and text.count(receipt) == 1
    traced = prefix+text.replace(marker, marker+observer, 1).replace(receipt, traced_receipt, 1)
    assert traced[len(prefix):].replace(marker+observer, marker, 1).replace(traced_receipt, receipt, 1) == text
    LuaRuntime().compile(traced)
    return traced.encode()


def time_final_cap_approach(program):
    text = program.decode()
    marker = """  if finalRiser>6 then
   if player>=3026 and settled and y==48 then setPhase('final-cap',stairTop)end
"""
    staged = """  if finalRiser>6 then
   if not capApproach then
    right=player<stairDown-26
    if not right then
     local previousTop=priorTop[stairDown]
     local sourceStanding=ram(2,0x6b)==1 and ram(2,0x210)==y+15
     assert(y==48 and player<stairDown-20,'Wait on the last stair clear of the moving lift')
     if sourceStanding and stairTop and previousTop and stairTop>=66
        and stairTop<=72 and stairTop<previousTop then
      capApproach=true;right=true;remember('final-cap-approach-window',stairTop)
     end
    end
   end
   if capApproach and player>=3026 and settled and y==48 then setPhase('final-cap',stairTop)end
"""
    prefix = 'local capApproach=false\n'
    assert text.count(marker) == 1
    timed = prefix+text.replace(marker, staged, 1)
    assert timed[len(prefix):].replace(staged, marker, 1) == text
    LuaRuntime().compile(timed)
    return timed.encode()


def center_flag_takeoff(program):
    text = program.decode()
    old = '  if not flagHop and player>=3152 and settled and y==176 then\n'
    new = '  if not flagHop and player>=3152 and settled and y==176 and camera()>=3072 then\n'
    assert text.count(old) == 1
    centered = text.replace(old, new, 1)
    assert centered.replace(new, old, 1) == text
    LuaRuntime().compile(centered)
    return centered.encode()


def report(result, image, full_stage):
    receipt = result['receipt']
    if full_stage:
        names = ('passed', 'reason', 'updates', 'physical_frames', 'terminal', 'events',
                 'original_work_grounded_returns', 'original_work_entries', 'original_work_returns',
                 'final_cap_trace')
    else:
        names = ('passed', 'reason', 'character', 'phases', 'inclusive_video_frames',
                 'measured_Main', 'no_controller_read_frames', 'native_lag_NMI',
                 'inclusive_Main_costs', 'Main_return_histogram')
    fields = {key: receipt[key] for key in names if key in receipt}
    if full_stage and (bank := receipt.get('second_gap', {})).get('nativeState2'):
        fields['second_gap_bank'] = dict(count=bank['nativeState2'], first=bank['nativeState2First'])
    fields.update(ROM_SHA256=Dispatch.h(image), receipt_SHA256=result['receipt_SHA256'],
                  script_SHA256=result['script_SHA256'], full_stage=full_stage)
    print('DK NATIVE '+json.dumps(fields, separators=(',', ':')), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    candidate_mode = parser.add_mutually_exclusive_group()
    candidate_mode.add_argument('--combined', action='store_true',
                                help='Qualify the combined DK Jr. and Sonic dispatcher')
    candidate_mode.add_argument('--public-side-forward', action='store_true',
                                help='Qualify the DK Jr. bank-33 shortcut on the combined nightly')
    parser.add_argument('--baseline', action='store_true', help='Run only the full-stage replay on the installed nightly')
    parser.add_argument('--cap-trace', action='store_true', help='Record the last staircase position and lift predicates')
    parser.add_argument('--time-cap-approach', action='store_true',
                        help='Wait on solid stairs for the final lift to reach the boarding height')
    parser.add_argument('--center-flag-takeoff', action='store_true',
                        help='Wait for the flagpole camera to reach the tested takeoff position')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--full-stage', action='store_true')
    mode.add_argument('--sonic', choices=('sonic', 'super', 'both'), help='Check the combined dispatcher with the retained Sonic full-stage routes')
    mode.add_argument('--mini', action='store_true', help='Compare Mini Mario idle and walking cadence')
    args = parser.parse_args()
    shared_dispatch = args.combined or args.public_side_forward
    if (args.sonic or args.mini) and not shared_dispatch:
        parser.error('--sonic and --mini require a shared dispatcher candidate')
    full_stage_options = args.baseline or args.cap_trace or args.time_cap_approach or args.center_flag_takeoff
    if full_stage_options and not (shared_dispatch and args.full_stage):
        parser.error('Full-stage controls require a shared dispatcher candidate and --full-stage')
    rom = Roster.Timing.ROM
    parent = rom.read_bytes()
    reference = parent
    if shared_dispatch:
        import compose_dkjr_sonic_dispatch_1123 as Combined
        import compose_sonic_current_auth_epoch_1122 as Sonic
        import repair_rogue_side_pipe_1123 as Pipe
        if args.public_side_forward:
            import compose_dkjr_public_side_forward_1123 as Side
            original = Combined.inverse(parent)
            candidate, spans = (parent, []) if args.baseline else Side.proposal(parent)
        elif args.baseline:
            assert Dispatch.h(parent) == Combined.PIN
            original = parent
            candidate, spans = parent, []
        else:
            original = parent
            candidate, spans = Combined.proposal(parent)
        reference = Sonic.inverse(Pipe.restore_pipe_bytes(original))
    else:
        candidate, spans = Dispatch.proposal(parent)
    if args.sonic:
        from run_sonic_auth_full11_1123 import controllers
        programs = controllers(reference, candidate)
        forms = tuple(programs) if args.sonic == 'both' else (args.sonic,)
        cases = [(form, candidate, programs[form]) for form in forms]
    else:
        name = 'MINI MARIO' if args.mini else 'DONKEY KONG JR'
        before, after = (prepare_full_stage(reference, candidate) if args.full_stage
                         else prepare(reference, candidate, name))
        if shared_dispatch and not args.full_stage:
            old = Dispatch.h(reference).encode()
            assert before.count(old) == 1
            before = before.replace(old, Dispatch.h(parent).encode(), 1)
            LuaRuntime().compile(before.decode())
        cases = [('baseline' if args.baseline else 'candidate', candidate, after)]
        if not (shared_dispatch and args.full_stage):
            cases.insert(0, ('baseline', parent, before))
    if args.time_cap_approach:
        cases = [(name, image, time_final_cap_approach(program)) for name, image, program in cases]
    if args.center_flag_takeoff:
        cases = [(name, image, center_flag_takeoff(program)) for name, image, program in cases]
    if args.cap_trace:
        cases = [(name, image, trace_final_cap(program)) for name, image, program in cases]
    if not args.run:
        scripts = {name:Dispatch.h(program) for name,_,program in cases} if shared_dispatch else [Dispatch.h(program) for _,_,program in cases]
        print('DK CADENCE SOURCE '+json.dumps(dict(candidate=Dispatch.h(candidate), spans=spans,
            scripts=scripts)), flush=True)
        return 0

    out = Roster.Timing.SHARED
    target, script = out/'candidate.nes', out/'controller.lua'
    assert set(out.iterdir()) == {target, script} and target.read_bytes() == parent
    public_guard, test_guard = check(rom), check(target)
    for guard in (public_guard, test_guard):
        assert guard['ROM_sha256'] == Dispatch.h(parent) and not guard['matching_patch_files']
    require_free_workspace(Roster.Timing.R, rom, allow_interactive=True)
    previous = script.read_bytes()
    passed = True
    try:
        for name, image, program in cases:
            path = rom if image == parent else target
            if path == target:
                target.write_bytes(image)
                guard = check(target)
                assert guard['ROM_sha256'] == Dispatch.h(image) and not guard['matching_patch_files']
            script.write_bytes(program)
            timeout = 300 if args.cap_trace else 240 if args.full_stage or args.sonic else 90
            result = run(script, path, out/'capture', Dispatch.h(image), timeout,
                         long_no_capture=args.cap_trace)
            assert result['script_SHA256'] == Dispatch.h(program)
            assert result['outputs_written'] == 0 and not result['images']
            if args.sonic:
                print('COMBINED SONIC NATIVE '+json.dumps(dict(form=name, passed=result['passed'],
                    ROM_SHA256=result['ROM_SHA256'], receipt_SHA256=result['receipt_SHA256'],
                    script_SHA256=result['script_SHA256'], receipt=result['receipt']),separators=(',', ':')), flush=True)
            else:
                report(result, image, args.full_stage)
            passed = passed and result['passed']
    finally:
        target.write_bytes(parent)
        script.write_bytes(previous)
        assert check(target) == test_guard and check(rom) == public_guard
        assert script.read_bytes() == previous and set(out.iterdir()) == {target, script}
    return int(not passed)


if __name__ == '__main__':
    raise SystemExit(main())
