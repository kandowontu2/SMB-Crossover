"""Install DK Jr.'s verified block-hit fix and recheck the Downloads build."""

import argparse
import json

import compose_dkjr_head_bridge_current_1123 as Bridge
import compose_dkjr_public_side_forward_1123 as Side
import compose_dkjr_side_epoch_fast_1123 as Fast
import compose_dkjr_sonic_dispatch_1123 as Combined
import compose_sonic_current_auth_epoch_1122 as Sonic
from check_dkjr_head_bridge_current_1123 import controller as head_controller
from install_dkjr_sonic_dispatch_1123 import cadence_programs, deliver
import repair_rogue_side_pipe_1123 as Pipe
from run_roster_empty_cadence_1122 import Timing


FULL_STAGE_PROOFS = {
    'DONKEY KONG JR': '15d7c2bf7e271a985a19e38af1a1ea288173f42a8701a304263bf38e6a5b3247',
}
PRIVATE_CADENCE = {
    'DONKEY KONG JR': 'fc5ac6f6fa109a08507bcf9df24d2c3949d112fbca28771c277acce20594f549',
}
EXPECTED_FRAMES = {
    'DONKEY KONG JR': (96,),
    'SONIC': (97,),
    'SUPER SONIC': (97,),
    'MINI MARIO': (64,),
}
HEAD_RECEIPT = '36d395014b68dcc0d730f5dc3783d36767ea688a37e6ec5371b30138e62c1fe9'
HEAD_CONTROLLER = 'df7be9d589e55a86ee9d506a077aa3c06de94f0b3add460c8a2027881616be49'
DK_CADENCE_CONTROLLER = 'c479a3dbf2f6f1218f4add037b3840ebe0881ec9513b91e0f6110ed793778cdd'


def prepare(installed):
    parent = Bridge.inverse(installed) if Bridge.H(installed) == Bridge.CANDIDATE else installed
    candidate, _ = Bridge.proposal(parent)
    assert Bridge.inverse(candidate) == parent
    base = Combined.inverse(Side.inverse(Fast.inverse(parent)))
    reference = Sonic.inverse(Pipe.restore_pipe_bytes(base))
    programs = cadence_programs(reference, Bridge.CANDIDATE, EXPECTED_FRAMES)
    assert Bridge.H(programs['DONKEY KONG JR']) == DK_CADENCE_CONTROLLER
    assert Bridge.H(head_controller(candidate).encode()) == HEAD_CONTROLLER
    return candidate, programs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    installed = Timing.ROM.read_bytes()
    candidate, programs = prepare(installed)
    print('DK HEAD NIGHTLY SOURCE ' + json.dumps({
        'ROM_SHA256': Bridge.H(candidate),
        'head_receipt_SHA256': HEAD_RECEIPT,
        'controllers': {name: Bridge.H(program) for name, program in programs.items()},
    }), flush=True)
    if args.install:
        deliver(installed, candidate, programs, proofs=FULL_STAGE_PROOFS,
                private_cadence=PRIVATE_CADENCE, expected_frames=EXPECTED_FRAMES)


if __name__ == '__main__':
    main()
