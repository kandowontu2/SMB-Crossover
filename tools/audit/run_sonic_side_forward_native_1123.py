"""Measure the Sonic side-query candidate through the actual MMC5 menus."""

import json

import compose_sonic_side_forward_1123 as Forward
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_sonic_current_empty_cadence_1122 import ROM, SHARED, R
from run_stdout_mesen_1110 import run


def main():
    parent = ROM.read_bytes()
    candidate, info = Forward.proposal(parent)
    programs = Forward.cadence_controllers(parent, candidate)
    target, controller = SHARED/'candidate.nes', SHARED/'controller.lua'
    assert set(SHARED.iterdir()) == {target, controller} and target.read_bytes() == parent
    installed = check(ROM)
    assert installed['ROM_sha256'] == Forward.PIN and not installed['matching_patch_files']
    require_free_workspace(R, ROM, allow_interactive=True)
    original = controller.read_bytes()
    try:
        for kind, path, digest in (('parent', ROM, Forward.PIN), ('candidate', target, Forward.CANDIDATE)):
            if kind == 'candidate':
                target.write_bytes(candidate)
            guard = check(path)
            assert guard['ROM_sha256'] == digest and not guard['matching_patch_files']
            for form, text in programs.items():
                controller.write_bytes(text[kind])
                result = run(controller, path, SHARED/'capture', digest, 110)
                assert result['passed'] and result['outputs_written'] == 0 and not result['images']
                receipt = result['receipt']
                fields = ('inclusive_video_frames', 'actual_motor_returns', 'no_controller_read_frames',
                          'native_lag_NMI', 'inclusive_Main_costs', 'Main_return_histogram', 'terminal', 'phases')
                record = {key: receipt[key] for key in fields}
                record.update(form=form, trial=kind, ROM_SHA256=digest,
                              receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'])
                print('SONIC SIDE NATIVE ' + json.dumps(record, separators=(',', ':')), flush=True)
            assert check(path) == guard
    finally:
        controller.write_bytes(original)
        target.write_bytes(parent)
        assert check(ROM) == installed and set(SHARED.iterdir()) == {target, controller}


if __name__ == '__main__':
    main()
