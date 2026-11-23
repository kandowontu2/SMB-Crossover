"""Verify the Sonic dispatch candidate through the retained full-stage route."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
import compose_sonic_current_auth_epoch_1122 as Auth
from current_sonic_parent_rom_1122 import inverse
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import run_sonic_original_full11_1122 as Full
from run_stdout_mesen_1110 import run


PRIVATE_PASSES = {
    'sonic': ('1eb3e50644b3bbe6505e2f91694b7209bcb6a7b91ed881809c6b0d76b055b311',
              '4af2023c9dfe61466a7a58214f23073a8dba51bc8d2edb86c219b36281640e20'),
    'super': ('1b556f854f5e05f32c3c0a222c95d6c96fa3897cc9b895e91782ec9cd056a497',
              '211952d2e32152b83084e04a827ac8b5f25dfaa5b5faefb5edbf5f0fe7a85831'),
}


def controllers(parent, candidate):
    ancestor = inverse(parent)
    position = Auth.M.COOKIE_AT
    old_cookie, new_cookie = (image[position:position+16].hex() for image in (parent, candidate))
    programs = {}
    for form in Full.FORMS:
        binding = Full.bindings(ancestor, parent, form)
        for name, hook in binding['hooks'].items():
            code = bytes.fromhex(hook['hex'])
            tag, pc = hook['tag'], hook['pc']
            if tag == 3:
                actual = Auth.M.kernel(candidate)[pc-0xa000:pc-0xa000+len(code)]
            elif tag == 2:
                page = {0xd000: 328, 0xd400: 333, 0xd800: 334}[pc & 0xfc00]
                offset = pc & 1023
                actual = Auth.M.page(candidate, page)[offset:offset+len(code)]
            else:
                assert tag & 128, (name, tag)
                offset = 16 + hook['offset']
                actual = candidate[offset:offset+len(code)]
            assert code == actual, name
        original = Full.controller(ancestor, parent, form)
        assert Auth.H(original.encode()) == Full.SPIN_PRIVATE_PASSES[form][0]
        program = Full.once(original, Auth.H(parent), Auth.H(candidate))
        program = Full.once(program, old_cookie, new_cookie)
        LuaRuntime().compile(program)
        programs[form] = program.encode()
    return programs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--deliver-nightly', action='store_true')
    args = parser.parse_args()
    assert args.run or not args.deliver_nightly
    parent = Full.ROM.read_bytes()
    candidate, _ = Auth.proposal(parent)
    programs = controllers(parent, candidate)
    pin = Auth.H(candidate)
    print('SONIC AUTH FULL SOURCE '+json.dumps(dict(ROM_SHA256=pin,
          controllers={form:Auth.H(data) for form,data in programs.items()})), flush=True)
    if not args.run:
        return 0

    out = Full.SHARED
    target, script = out/'candidate.nes', out/'controller.lua'
    assert set(out.iterdir()) == {target, script} and target.read_bytes() == parent
    public_guard, test_guard = check(Full.ROM), check(target)
    for guard in (public_guard, test_guard):
        assert guard['ROM_sha256'] == Auth.PIN and not guard['matching_patch_files']
    require_free_workspace(Full.R, Full.ROM, allow_interactive=True)
    original = script.read_bytes()
    passed = True
    verified_install = False
    install_started = False
    try:
        launch = target
        if args.deliver_nightly:
            assert Auth.inverse(candidate) == parent
            for form, program in programs.items():
                assert Auth.H(program) == PRIVATE_PASSES[form][0]
            assert check(Full.ROM) == public_guard
            install_started = True
            Full.ROM.write_bytes(candidate)
            launch = Full.ROM
        else:
            target.write_bytes(candidate)
        installed_guard = check(launch)
        assert installed_guard['ROM_sha256'] == pin and not installed_guard['matching_patch_files']
        for form, program in programs.items():
            script.write_bytes(program)
            result = run(script, launch, out/'capture', pin, 240, extra_env={'SMB_STDOUT_IMAGES':'0'})
            assert result['outputs_written'] == 0 and not result['images']
            passed = passed and result['passed']
            print('SONIC AUTH FULL NATIVE '+json.dumps(dict(form=form,passed=result['passed'],
                  receipt_SHA256=result['receipt_SHA256'],script_SHA256=result['script_SHA256'],
                  receipt=result['receipt']),separators=(',',':')),flush=True)
            if args.deliver_nightly:
                assert result['passed'] and result['receipt_SHA256'] == PRIVATE_PASSES[form][1]
                assert check(Full.ROM) == installed_guard
        if args.deliver_nightly:
            target.write_bytes(candidate)
            assert target.read_bytes() == Full.ROM.read_bytes() == candidate
            verified_install = True
    finally:
        script.write_bytes(original)
        if not verified_install:
            target.write_bytes(parent)
            if install_started:
                Full.ROM.write_bytes(parent)
            assert check(Full.ROM) == public_guard and check(target) == test_guard
        assert set(out.iterdir()) == {target, script} and script.read_bytes() == original
    if verified_install:
        assert check(Full.ROM) == installed_guard and target.read_bytes() == candidate
        print('SONIC AUTH NIGHTLY DELIVERED '+json.dumps(dict(ROM_SHA256=pin,backups=0,
              guarded_Downloads_launches=list(programs),matched_private_receipts=True)),flush=True)
    return int(not passed)


if __name__ == '__main__':
    raise SystemExit(main())
