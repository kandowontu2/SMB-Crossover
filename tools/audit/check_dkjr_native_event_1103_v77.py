"""Correct75's original stack oracle and metadata-bank observer.

76 proved its only state differences were original dead return-stack bytes
01DF/01E0; relocated calls use the genuine native stack rather than C1xx.
"""
import inspect
import json
from pathlib import Path
import check_dkjr_native_event_1103_v75 as P


def main():
    text = inspect.getsource(P.main)
    old = "assert source(m) == bytes(oracle[:0x800]), ('original transition', state, direction, velocity, flags)"
    new = "assert all(a == z for i, (a, z) in enumerate(zip(source(m), oracle[:0x800])) if not 0x100 <= i < 0x200), ('original transition', state, direction, velocity, flags)"
    assert text.count(old) == 1
    text = text.replace(old, new)
    text = text.replace("points = {(3, L['DkNativeBounce'])", "points = {(2, L['DkNativeBounce'])")
    text = text.replace('native-event-v75-CPU.json', 'native-event-v77-CPU.json')
    text = text.replace("Path(__file__), Path(B.__file__)", "Path(__file__), V75_PATH, Path(B.__file__)")
    text = text.replace('Complete original2048 bytes versus genuine originalROM D257',
        'All original2048 bytes except its dead0100..01FF return stack versus genuine originalROM D257')
    env = dict(P.__dict__, __file__=__file__, V75_PATH=Path(P.__file__))
    exec(compile(text, __file__, 'exec'), env)
    env['main']()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        (P.O / 'native-event-v77-negative.json').write_text(json.dumps(dict(passed=False, exception=repr(error), ROM_written=False, native_owner_admitted=False), indent=2) + '\n')
        raise
