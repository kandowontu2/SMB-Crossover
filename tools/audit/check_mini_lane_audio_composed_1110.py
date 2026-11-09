"""Exercise actual interrupt continuations in the composed Mini successor."""
import argparse
import json
from pathlib import Path

import check_mini_jump_lane_reuse_irq_1110 as J
import check_guest_expansion_sweep_vectors_1110_v1 as A
import check_mini_native_brick_coin_irq_1110_v1 as R
from compose_mini_frame_budget_1108 import digest
from prepare_mini_lane_audio_native_1110 import AUDIO, build_image, without_component


BRICK = Path('build/mini-brick-coin-1110/proof.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--skip-brick-coin', action='store_true')
    parser.add_argument('--platform-proof', type=Path)
    parser.add_argument('--platform-irq', type=Path)
    args = parser.parse_args()
    if bool(args.platform_proof)!=bool(args.platform_irq):
        parser.error('pass both --platform-proof and --platform-irq')
    brick = None if args.skip_brick_coin else BRICK
    brick_irq = brick.with_name('irq.json') if brick else None
    before,rebuilt,_ = build_image(brick,brick_irq,args.platform_proof,args.platform_irq)
    after = args.rom.read_bytes()
    assert after==rebuilt,args.rom
    result = dict(parent_SHA256=digest(before), candidate_SHA256=digest(after))
    result['jump_lane'] = J.qualify(after)
    audio_before = without_component(after,AUDIO)
    result['audio'] = A.qualification([A.M.bundle(x) for x in (audio_before,after)])
    if brick is not None:
        render_before = without_component(after,brick)
        result['renderer'] = R.qualify([R.P.bundle(x) for x in (render_before,after)],
                                       json.loads(brick.read_text()))
    if args.platform_proof is not None:
        from check_native_platform_collision_vectors_1110_v1 import qualify
        platform_before = without_component(after,args.platform_proof)
        result['platform'] = qualify(platform_before,after)
    result['passed'] = True
    args.output.mkdir(exist_ok=True)
    (args.output/'proof.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, candidate_SHA256=digest(after))), flush=True)


if __name__ == '__main__':
    main()
