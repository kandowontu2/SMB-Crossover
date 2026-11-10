"""Full earned FF 1-1 to active underground 1-2 on the v2 memory image.

No files, ROM or Mesen capture. The frozen controller and real native startup,
parser, flag/score and pipe entrance execute; no actor/state grants are made.
"""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_full_stage_current_1110 as S
import check_ff_head_corner_1110_v2 as Fix

PIN = '96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', type=int, choices=range(4))
    args = p.parse_args()
    assert sha256(Path(S.__file__).read_bytes()).hexdigest() == '4081ddb23a5e1c5dd5a59bfa87ae0058b108dc27f0b7fa2c1bb158ed98124439'
    image, kernel, cookie, _, _, _ = Fix.proposal(S.W.ROM.read_bytes())
    assert sha256(image).hexdigest() == PIN
    class MemoryImage:
        def read_bytes(self):
            return image
    original_fixture, results = S.fixture, []
    holder = {}
    def capture(v):
        prefix, model = original_fixture(v)
        holder['model'] = model
        return prefix, model
    with patch.object(S.W, 'ROM', MemoryImage()), patch.object(S.W, 'PIN', PIN), patch.object(S, 'fixture', capture):
        for variant in range(4) if args.variant is None else (args.variant,):
            print('Natural full1-1 and automatic1-2 class', variant, flush=True)
            log = io.StringIO()
            try:
                with redirect_stdout(log):
                    q = S.route(variant)
            except Exception:
                print(log.getvalue(), flush=True)
                raise
            m = holder['model']
            assert q['passed'] and q['full_1_1'] and not q['injuries']
            # GuestCameraCatchUp deliberately adds one pixel after a wall
            # hold leaves a non-Mario guest beyond its follow point. The
            # independent observer pins the sole maximum3 at that recovery;
            # requiring at most the raw1/2px motor speed was an invalid bound.
            assert q['active_1_2']['lives'] == 2 and q['maximum_logical_camera_step'] <= 3
            assert q['active_1_2']['power'] == q['active_1_2']['earned'] == 2
            assert S.N.get(m, 'AreaType') == 2, ('Not underground', q['active_1_2'])
            assert S.N.get(m, 'WorldNumber') == 0 and S.N.get(m, 'LevelNumber') == 1
            assert bytes(m.ram[3][0x1fe0:0x1ff0]) == cookie
            active_image = bytearray(m.ram[3])
            active_image[0x1fe0:0x1ff0] = b'\xff' * 16
            assert active_image == kernel, ('Loaded code/data differ beyond header',
                [(hex(i + 0xa000), a, b) for i, (a, b) in enumerate(zip(active_image, kernel)) if a != b][:12])
            result = dict(passed=True, variant=variant, class_name=q['class_name'],
                          earned_mushroom_flower_attack=True, full_1_1=True,
                          native_flag=q['native_flag'], active_underground_1_2=q['active_1_2'],
                          area_pointer=S.N.get(m, 'AreaPointer'), area_offset=S.N.get(m, 'AreaAddrsLOffset'),
                          camera_max=q['maximum_logical_camera_step'], no_injuries=True,
                          calls=q['calls'], jumps=len(q['jump_events']),
                          exact_cold_loaded_kernel_and_cookie=True)
            results.append(result)
            print(json.dumps(dict(event='class_full_stage_pass', result=result), sort_keys=True), flush=True)
    print(json.dumps(dict(passed=True, source_only=True, CPU_controller_only=True,
                          Mesen_run=False, ROM_written=False, outputs_written=0,
                          in_memory_SHA256=PIN, cookie=cookie.hex(), classes=results,
                          scope='Natural cold-menu earned pickups/attack, non-shortcut1-1 flag/score sequence and automaticpipe into activeunderground1-2, lives2/noinjury. ExactnewFFimage/header; not physicalcadence, graphics, shortcut or everyenemykill.'), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
