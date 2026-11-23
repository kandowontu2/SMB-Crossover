"""Verify the Rogue Dawn side-pipe repair from the Downloads nightly."""

import argparse
import json

import compose_sonic_current_auth_epoch_1122 as Sonic
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import repair_rogue_side_pipe_1123 as Pipe
import run_rogue_screw_native_1122 as Route


NIGHTLY = '28708fa9a4e7dd88f1aaa72653b7d5a6ba0fb3c6d5abf544a526b09d333a884c'
EXTERIOR_CONTROLLER = 'f0b0e409a9927850d36fb40980c76347e3bc254eb72f4bdb3debb97cc8f90554'
PRIVATE_RECEIPT = 'a1b28f926ba78c15ea3eb365352b4d36281eb4e37658b79bbcc3d93ff37cb3fe'


def images(installed):
    parent = Pipe.restore_pipe_bytes(installed) if Route.H(installed) == NIGHTLY else installed
    assert Route.H(parent) == Sonic.CANDIDATE
    owner, candidate = Route.side_pipe_candidate(parent)
    assert Route.H(candidate) == NIGHTLY and Pipe.restore_pipe_bytes(candidate) == parent
    return owner, candidate


def exterior_report(result):
    receipt = result['receipt']
    assert result['passed'] and receipt['reason'] == 'natural-side-pipe-exterior-and25'
    exterior = receipt['natural_Bomb']['screw']['exterior']
    assert exterior['complete']['passed']
    assert min(exterior['complete']['returned'].values()) >= 25
    assert result['script_SHA256'] == EXTERIOR_CONTROLLER
    return dict(receipt_SHA256=result['receipt_SHA256'],
                ROM_SHA256=result['ROM_SHA256'], exterior=exterior)


def deliver(owner, installed, candidate):
    target = Route.Base.OUT/'candidate.nes'
    assert target.read_bytes() == installed
    public_guard, test_guard = check(Route.ROM), check(target)
    assert public_guard['ROM_sha256'] == test_guard['ROM_sha256'] == Route.H(installed)
    require_free_workspace(Route.R, Route.ROM, allow_interactive=True)
    assert Route.H(Route.native_program(owner, candidate, exterior_only=True)) == EXTERIOR_CONTROLLER

    try:
        if candidate != installed:
            Route.ROM.write_bytes(candidate)
            target.write_bytes(candidate)
        assert check(Route.ROM)['ROM_sha256'] == check(target)['ROM_sha256'] == NIGHTLY
        report = exterior_report(Route.native(owner, candidate, exterior_only=True))
        assert report['receipt_SHA256'] == PRIVATE_RECEIPT
        assert Route.ROM.read_bytes() == target.read_bytes() == candidate
        assert check(Route.ROM)['ROM_sha256'] == NIGHTLY
    except BaseException:
        if candidate != installed:
            Route.ROM.write_bytes(installed)
            target.write_bytes(installed)
        assert check(Route.ROM) == public_guard and check(target) == test_guard
        raise
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--install', action='store_true', help='Install and replay the verified repair')
    mode.add_argument('--full', action='store_true', help='Continue the earned Screw Attack route')
    args = parser.parse_args()
    installed = Route.ROM.read_bytes()
    owner, candidate = images(installed)
    if args.install:
        report = deliver(owner, installed, candidate)
    elif args.full:
        assert installed == candidate
        result = Route.native(owner, installed)
        print('ROGUE_SCREW '+json.dumps(result, separators=(',', ':')), flush=True)
        return int(not result['passed'])
    else:
        program = Route.native_program(owner, candidate, exterior_only=True)
        assert Route.H(program) == EXTERIOR_CONTROLLER
        report = dict(ROM_SHA256=NIGHTLY, controller_SHA256=EXTERIOR_CONTROLLER)
    print('ROGUE_SIDE_PIPE_NIGHTLY '+json.dumps(report, separators=(',', ':')), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
