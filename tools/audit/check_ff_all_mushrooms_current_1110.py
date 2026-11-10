"""Reuse the frozen first-mushroom CPU controller for all four FF classes.

Print aggregate evidence only. No ROM, packet, receipt, capture or cache output.
The frozen White checker remains unchanged; this adapter varies genuine menu
Select edges, expected class-owned charges and the authenticated body palette.
"""
from hashlib import sha256
import inspect
import json
from pathlib import Path
import sys
import traceback

import check_ff_white_mushroom_current_1110 as W

FROZEN_SHA = 'c6c3a7dca9cea3bf4577d5038f74a22261be8989edc1ad87ddd8590d0e581de0'
CLASSES = ('Fighter', 'White Mage', 'Black Mage', 'Thief')
NAMES = ('FF FIGHTER', 'FF WHITE MAGE', 'FF BLACK MAGE', 'FF THIEF')


def route(variant):
    source = Path(W.__file__).read_bytes()
    assert sha256(source).hexdigest() == FROZEN_SHA
    text = inspect.getsource(W.run)
    changes = {
        'def run():': 'def run_variant():',
        "    UI.key(m, 32)\n    assert N.get(m, 'FfVariant') == 1":
            "    for _ in range(VARIANT):\n        UI.key(m, 32)\n    assert N.get(m, 'FfVariant') == VARIANT",
        "assert menu_name == 'FF WHITE MAGE', menu_name":
            'assert menu_name == MENU_NAME, menu_name',
        "N.get(m, 'FfVariant') == 1": "N.get(m, 'FfVariant') == VARIANT",
        "(current['power'], current['earned'], current['heal']) == (1, 1, 1)":
            "(current['power'], current['earned'], current['heal']) == (1, 1, HEAL)",
        "(state()['power'], state()['earned'], state()['heal']) == (1, 1, 1)":
            "(state()['power'], state()['earned'], state()['heal']) == (1, 1, HEAL)",
        "== [0x16, 0x30, 0x36]": '== PALETTE',
        "class_name='White Mage'": 'class_name=CLASS_NAME',
        'return dict(passed=True, ROM_sha256=PIN':
            'return dict(_arena=m, passed=True, ROM_sha256=PIN',
        "        if c.pc < 0x8000:\n            return":
            "        if c.pc < 0x8000:\n            return",
    }
    for old, new in changes.items():
        count = text.count(old)
        assert count == 1, (old, count)
        text = text.replace(old, new)
    space = dict(vars(W), VARIANT=variant, CLASS_NAME=CLASSES[variant],
                 MENU_NAME=NAMES[variant], HEAL=int(variant == 1),
                 PALETTE=[0x16, 0x30, 0x36] if variant < 2 else [0x28, 0x18, 0x21])
    exec(compile(text, str(Path(__file__)), 'exec'), space)
    result = space['run_variant']()
    arena = result.pop('_arena')
    result['variant'] = variant
    result['PlayerOutlinesOff'] = W.N.get(arena, 'PlayerOutlinesOff')
    return result, arena


def main():
    results = []
    for variant in range(4):
        result, arena = route(variant)
        results.append(result)
        print(json.dumps(dict(event='class_pass', result=result)), flush=True)
    print(json.dumps(dict(passed=True, ROM_sha256=W.PIN, CPU_controller_only=True,
                          Mesen_run=False, ROM_written=False, output_files=0,
                          frozen_White_checker_SHA256=FROZEN_SHA, classes=results,
                          scope='All four actual menu selections, first naturally produced mushroom, native collector/60-tick recovery/16px resumed movement. No full stage, flower, Heal use, physical timing or Mesen qualification.')), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
