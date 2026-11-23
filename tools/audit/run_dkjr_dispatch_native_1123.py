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


def report(result, image):
    receipt = result['receipt']
    names = ('passed', 'reason', 'character', 'phases', 'inclusive_video_frames',
             'measured_Main', 'no_controller_read_frames', 'native_lag_NMI',
             'inclusive_Main_costs', 'Main_return_histogram')
    fields = {key: receipt[key] for key in names if key in receipt}
    fields.update(ROM_SHA256=Dispatch.h(image), receipt_SHA256=result['receipt_SHA256'],
                  script_SHA256=result['script_SHA256'])
    print('DK CADENCE '+json.dumps(fields, separators=(',', ':')), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    rom = Roster.Timing.ROM
    parent = rom.read_bytes()
    candidate, spans = Dispatch.proposal(parent)
    scripts = prepare(parent, candidate)
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
            result = run(script, path, out/'capture', Dispatch.h(image), 90)
            assert result['outputs_written'] == 0 and not result['images']
            report(result, image)
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
