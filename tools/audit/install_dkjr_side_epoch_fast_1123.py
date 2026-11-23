"""Install the Mesen-tested DK Jr. walking speedup and verify Downloads."""

import argparse
import json

import compose_dkjr_public_side_forward_1123 as Side
import compose_dkjr_side_epoch_fast_1123 as Fast
import compose_dkjr_sonic_dispatch_1123 as Combined
import compose_sonic_current_auth_epoch_1122 as Sonic
from install_dkjr_sonic_dispatch_1123 import cadence_programs, deliver
import repair_rogue_side_pipe_1123 as Pipe
from run_roster_empty_cadence_1122 import Timing


FULL_STAGE_PROOFS = {
    'DONKEY KONG JR': 'a010886cbbad8412a630c7fb505f34f6b65c71e97473f58d703a91a5b34a5aea',
}
PRIVATE_CADENCE = {
    'DONKEY KONG JR': 'b1f4e616bd425fbc602eaf5502eb94828cd1c6a78df962a9dfce38e925198f15',
}
EXPECTED_FRAMES = {
    'DONKEY KONG JR': (96,),
    'SONIC': (97,),
    'SUPER SONIC': (97,),
    'MINI MARIO': (64,),
}
DK_CADENCE_CONTROLLER = 'f367dc94cfd375355355fdc75a3cc570b5aaed788b83e028389156b34e4c4c64'


def prepare(installed):
    parent = Fast.inverse(installed) if Fast.H(installed) == Fast.CANDIDATE else installed
    candidate, _ = Fast.proposal(parent)
    assert Fast.inverse(candidate) == parent
    reference = Sonic.inverse(Pipe.restore_pipe_bytes(Combined.inverse(Side.inverse(parent))))
    programs = cadence_programs(reference, Fast.CANDIDATE, EXPECTED_FRAMES)
    assert Fast.H(programs['DONKEY KONG JR']) == DK_CADENCE_CONTROLLER
    return candidate, programs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    installed = Timing.ROM.read_bytes()
    candidate, programs = prepare(installed)
    print('DK FAST NIGHTLY SOURCE ' + json.dumps({
        'ROM_SHA256': Fast.H(candidate),
        'controllers': {name: Fast.H(program) for name, program in programs.items()},
    }), flush=True)
    if args.install:
        deliver(installed, candidate, programs, proofs=FULL_STAGE_PROOFS,
                private_cadence=PRIVATE_CADENCE, expected_frames=EXPECTED_FRAMES)


if __name__ == '__main__':
    main()
