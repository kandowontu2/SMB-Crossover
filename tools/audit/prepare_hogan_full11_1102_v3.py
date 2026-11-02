"""Later-edge controller attempt on the installed WWF death-recovery successor."""
from pathlib import Path
import prepare_hogan_full11_1102_v2 as P
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/hogan-full11-1102-v3'
ROM = R / 'build/wwf-death-1102-v2/candidate.nes'
PIN = '1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'


def main():
    O.mkdir(exist_ok=True)
    assert sha(ROM) == PIN
    source = P.CONTROLLER
    assert source.count('not solid(x+24,216)') == 1
    source = source.replace('not solid(x+24,216)', 'not solid(x+8,216)')
    source = source.replace('#trace<80', '#trace<130')
    source = source.replace('age>=10500', 'age>=18000').replace('frame>=11500', 'frame>=19000')
    prepare(O / 'native', ROM, source, [Path(__file__), Path(P.__file__)],
            expected=PIN, timeout=240, allow_interactive=True,
            scope='Natural Hogan1-1 attempt using later x+8 ground-edge input, retaining actual '
                  'no-life-loss/active1-2 assertions. No game state writes or modified physics. '
                  'One PNG. Earlier x+24 first-gap failure is retained; this input attempt '
                  'does not by itself prove a helper need.')


if __name__ == '__main__':
    main()
