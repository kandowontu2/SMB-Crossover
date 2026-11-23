"""Deliver the physically qualified DK Jr. terrain speedup to Downloads."""

import argparse
import json

import compose_dkjr_public_side_forward_1123 as Side
import compose_dkjr_sonic_dispatch_1123 as Combined
import compose_sonic_current_auth_epoch_1122 as Sonic
from install_dkjr_sonic_dispatch_1123 import cadence_programs, deliver
import repair_rogue_side_pipe_1123 as Pipe
from run_roster_empty_cadence_1122 import Timing


FULL_STAGE_PROOFS = {
    'DONKEY KONG JR': 'ca794b5ef7aeff1691c16246c3f665fc594033538a873d6db9dd551924dd728a',
    'SONIC': 'b0accb408b3b0f5a462b6ae195c9555c5e520fcc0057dc45256823e9e9ff73e6',
    'SUPER SONIC': '467576a927314bdf8d35cbf278b001ea4883544f1d6ac64ef7a2e8d4210671a1',
}
PRIVATE_CADENCE = {'DONKEY KONG JR': '928876ca96c1db045f15332e6492e3a21c73b6e64630a41080d3fccdbc111e8e'}
EXPECTED_FRAMES = {
    'DONKEY KONG JR': (104,),
    'SONIC': range(96, 100),
    'SUPER SONIC': range(96, 100),
    'MINI MARIO': (64,),
}
DK_CADENCE_CONTROLLER = 'c04d14e83c72d8ee0967b5912dd27e568e968996212b3a44885d58277113199a'


def prepare(installed):
    parent = Side.inverse(installed) if Side.H(installed) == Side.CANDIDATE else installed
    candidate, _ = Side.proposal(parent)
    assert Side.inverse(candidate) == parent
    reference = Sonic.inverse(Pipe.restore_pipe_bytes(Combined.inverse(parent)))
    programs = cadence_programs(reference, Side.CANDIDATE, EXPECTED_FRAMES)
    assert Side.H(programs['DONKEY KONG JR']) == DK_CADENCE_CONTROLLER
    return candidate, programs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    installed = Timing.ROM.read_bytes()
    candidate, programs = prepare(installed)
    print('DK SIDE NIGHTLY SOURCE '+json.dumps(dict(ROM_SHA256=Side.H(candidate),
          controllers={name:Side.H(program) for name,program in programs.items()})), flush=True)
    if args.install:
        deliver(installed, candidate, programs, proofs=FULL_STAGE_PROOFS,
                private_cadence=PRIVATE_CADENCE, expected_frames=EXPECTED_FRAMES)


if __name__ == '__main__':
    main()
