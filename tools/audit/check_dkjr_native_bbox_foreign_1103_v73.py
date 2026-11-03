"""Run current-owner Fresh at its genuine forced-blank boundary.

The preserved72 negative called Sh's constructor after unblanking; its Cclear
was the correct admission guard, not a runtime collision failure.
"""
import inspect
import json
from pathlib import Path
import check_dkjr_native_bbox_foreign_1103_v72 as P


def main():
    text = inspect.getsource(P.main)
    block = """        N.put(m, NmiDisable=255, DisableScreenFlag=0, Mirror_PPUMASK=30,
            TimerControl=0, AreaType=1, FrameCounter=0, VRAM_Buffer1_Offset=0)
"""
    assert text.count(block) == 1
    text = text.replace(block, '')
    marker = "        if owner in [36, 39]:\n"
    assert text.count(marker) == 1
    text = text.replace(marker, block + marker)
    text = text.replace('native-bbox-current-foreign-v72.json', 'native-bbox-current-foreign-v73.json')
    text = text.replace("Path(__file__), Path(C.__file__)", "Path(__file__), V72_PATH, Path(C.__file__)")
    env = dict(P.__dict__, __file__=__file__, V72_PATH=Path(P.__file__))
    exec(compile(text, __file__, 'exec'), env)
    env['main']()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        (P.O / 'native-bbox-current-foreign-v73-negative.json').write_text(json.dumps(dict(passed=False, exception=repr(error), ROM_written=False, shared_grant=False), indent=2) + '\n')
        raise
