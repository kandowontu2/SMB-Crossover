"""Qualify 1-1 flag/level transition on the FF corner proposal, no files.

Stops explicitly in the still-unqualified 1-2 automatic entrance. This proves
the native 1-1 flag, score sequence and level increment, not active 1-2.
"""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_full_stage_current_1110 as S
import check_ff_head_corner_1110 as Fix


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', type=int, choices=range(4))
    args = p.parse_args()
    assert sha256(Path(S.__file__).read_bytes()).hexdigest() == '4081ddb23a5e1c5dd5a59bfa87ae0058b108dc27f0b7fa2c1bb158ed98124439'
    image, _, cookie, _, _, _ = Fix.proposal(S.W.ROM.read_bytes())
    pin = sha256(image).hexdigest()
    assert pin == 'db20d5a53259b90b0c0892b416e8da78aab1815a1c68fb99c4a1974ad5326069'
    class MemoryImage:
        def read_bytes(self):
            return image
    results = []
    with patch.object(S.W, 'ROM', MemoryImage()), patch.object(S.W, 'PIN', pin):
        for variant in range(4) if args.variant is None else (args.variant,):
            log = io.StringIO()
            try:
                with redirect_stdout(log):
                    q, m = S.route(variant, stop_at_intro=True)
            except Exception:
                print(log.getvalue(), flush=True)
                raise
            assert q['full_1_1_flag_and_level_transition'] and not q['active_1_2']
            assert q['native_flag']['player']['engine'] == 4 and q['native_flag']['player']['x'] >= 3000
            assert q['terminal']['level'] == 1 and q['terminal']['lives'] == 2
            assert q['terminal']['power'] == q['terminal']['earned'] == 2
            assert not q['injuries'] and q['maximum_logical_camera_step'] <= 2
            results.append(dict(variant=variant, prefix_earned_pickups_and_attack=q['prefix']['passed'],
                                native_flag=q['native_flag'], terminal=q['terminal'],
                                camera_max=q['maximum_logical_camera_step'], calls=q['calls'],
                                jumps=len(q['jump_events']), no_injuries=True))
            print(json.dumps(dict(event='class_1_1_clear', result=results[-1]), sort_keys=True), flush=True)
    print(json.dumps(dict(passed=True, source_only=True, CPU_controller_only=True,
                          Mesen_run=False, ROM_written=False, outputs_written=0,
                          in_memory_SHA256=pin, cookie=cookie.hex(), classes=results,
                          active_1_2_not_qualified=True,
                          scope='Natural cold-menu mushroom/flower/upgraded attack, all1-1 obstacles, flagpole/score sequence and level increment, lives2. Automatic1-2 entrance atX230 still under investigation.'), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
