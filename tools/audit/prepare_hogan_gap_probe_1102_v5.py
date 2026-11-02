"""Last supported-edge input attempt; source physics and terrain remain unchanged."""
import json
from pathlib import Path
from prepare_hogan_full11_1102_v3 import ROM, PIN
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/hogan-gap-probe-1102-v5'
PREV = R / 'build/hogan-gap-probe-1102-v4/native'


def main():
    q = json.loads((PREV / 'ready.json').read_text(encoding='utf-8'))
    for path, expected in q['bindings'].items():
        assert sha(path) == expected, path
    flights = json.loads((PREV / 'capture/flights.json').read_text())
    assert flights[-1] == dict(x=1368, y=176, minimum_y=110, finish_x=1412,
                              finish_y=243, reason='lost-life')
    s = (PREV / 'controller.lua').read_text(encoding='utf-8')
    assert s.count('not solid(x+8,216)') == 1
    s = s.replace('not solid(x+8,216)', 'not solid(x+4,216)')
    s = s.replace('#trace<80', '#trace<130')
    s = s.replace('age>=10500', 'age>=18000').replace('frame>=11500', 'frame>=19000')
    O.mkdir(exist_ok=True)
    prepare(O / 'native', ROM, s, [Path(__file__), PREV / 'ready.json',
            PREV / 'controller.lua', PREV / 'capture/flights.json'], expected=PIN,
            timeout=240, allow_interactive=True,
            scope='Controller-only x+4 floor-edge attempt after measured x+8 jump starts four pixels '
                  'early: launch1368/minY110/death1412 at the48px opening pit. Retain full-stage '
                  'no-life-loss/actual1-2 assertions and per-jump aggregate. One PNG; no writes, '
                  'physics/helper or terrain changes.')


if __name__ == '__main__':
    main()
