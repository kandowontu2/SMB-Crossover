"""Measure a private Donkey Kong Jr. candidate and restore the existing slot."""

import json

import compose_dkjr_rect_read_current_1123 as Rect
import run_roster_empty_cadence_current_1123 as Cadence

Previous = Cadence.Previous
Timing = Previous.Timing
CANDIDATE = 'b66f046e82f43bd6f4d2a25cd345d86fdaedc16461c32b7bec58684c3b89fb3b'


def main():
    installed_guard = Previous.check(Timing.ROM)
    installed = Timing.ROM.read_bytes()
    assert installed_guard['ROM_sha256'] == Timing.H(installed) == Rect.PIN
    assert not installed_guard['matching_patch_files']
    work = Timing.SHARED
    rom, script = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, script} and rom.read_bytes() == installed
    Previous.require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)

    reference = Cadence.reference(installed)
    candidate, _ = Rect.compose(installed)
    assert Timing.H(candidate) == CANDIDATE and Rect.inverse(candidate) == installed
    row = Previous.roster(installed)['DONKEY KONG JR']
    controller = Cadence.controller(reference, row)
    assert controller.count(Timing.PIN) == 1
    program = controller.replace(Timing.PIN, CANDIDATE, 1).encode()
    prior_script = script.read_bytes()
    try:
        rom.write_bytes(candidate)
        script.write_bytes(program)
        guard = Previous.check(rom)
        assert guard['ROM_sha256'] == CANDIDATE and not guard['matching_patch_files']
        result = Previous.run(script, rom, work / 'capture', CANDIDATE, 90)
        assert result['outputs_written'] == 0 and not result['images']
        report = dict(ROM=CANDIDATE, receipt=result['receipt'],
                      receipt_SHA256=result['receipt_SHA256'],
                      script_SHA256=result['script_SHA256'])
        print('DKJR RECT CADENCE ' + json.dumps(report, separators=(',', ':')), flush=True)
        assert result['passed'], result['receipt']['reason']
    finally:
        rom.write_bytes(installed)
        script.write_bytes(prior_script)
        assert rom.read_bytes() == Timing.ROM.read_bytes() == installed
        assert Previous.check(Timing.ROM) == installed_guard


if __name__ == '__main__':
    main()
