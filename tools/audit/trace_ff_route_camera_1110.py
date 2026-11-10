"""Add only a max-camera observer to the frozen full-route controller.

Cartridge bytes come from the v2 in-memory proposal. No engine/controller
change is inserted by the observer; no file or capture is produced.
"""
from hashlib import sha256
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_full_stage_current_1110 as S
import check_ff_head_corner_1110_v2 as Fix


def main():
    assert sha256(Path(S.__file__).read_bytes()).hexdigest() == '4081ddb23a5e1c5dd5a59bfa87ae0058b108dc27f0b7fa2c1bb158ed98124439'
    text = inspect.getsource(S.route)
    old = "                    maximum_jump = max(maximum_jump, s['camera'] - camera_previous)"
    assert text.count(old) == 1
    observer = """                    if s['camera'] - camera_previous > maximum_jump:
                        print(json.dumps(dict(event='new_camera_maximum', previous=camera_previous,
                                              delta=s['camera']-camera_previous, player=s,
                                              oldX=N.get(m,'MmOldX'), scroll=N.get(m,'Player_X_Scroll'),
                                              platform_scroll=N.get(m,'Platform_X_Scroll'),
                                              tail=list(tail)[-4:])), flush=True)
"""
    text = text.replace(old, observer + old)
    names = dict(vars(S))
    exec(compile(text, str(Path(__file__)), 'exec'), names)
    image, _, _, _, _, _ = Fix.proposal(S.W.ROM.read_bytes())
    class MemoryImage:
        def read_bytes(self):
            return image
    with patch.object(S.W, 'ROM', MemoryImage()), patch.object(S.W, 'PIN', sha256(image).hexdigest()):
        q = names['route'](0)
    print(json.dumps(dict(passed=q['passed'], source_only=True, outputs_written=0,
                          maximum_logical_camera_step=q['maximum_logical_camera_step'],
                          active_1_2=q['active_1_2'], no_injuries=not q['injuries'])), flush=True)


if __name__ == '__main__':
    main()
