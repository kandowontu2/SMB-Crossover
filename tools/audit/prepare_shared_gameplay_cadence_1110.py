"""Bind comparable Samus and Bill opening replays to adjacent public builds."""

import argparse
from pathlib import Path

from prepare_current_helper_3_3_1110 import NIGHTLY, PIN, ROM
from prepare_selected_native_packet_v1 import R, prepare, sha


BASE = R / 'build/mini-platform-pair-native-1110/candidate.nes'
BASE_SHA = 'df03fc35ebdc516a8df0b501bbe2008e52836aa8fcfad5c34e4df76783e9f331'
SCRIPT = Path(__file__).with_name('shared_gameplay_cadence_1110.lua')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build') and not out.exists()
    assert sha(NIGHTLY) == sha(ROM) == PIN and sha(BASE) == BASE_SHA
    out.mkdir()
    for version, rom, digest in (('baseline', BASE, BASE_SHA), ('current', ROM, PIN)):
        raw = rom.read_bytes()
        menu = 16 + 124 * 8192 + 0x40
        assert raw[menu:menu + 4] == bytes((0, 1, 2, 3))
        for slot, name in ((2, 'samus'), (3, 'bill')):
            prefix = f'local C = {{rom="{digest}",slot={slot}}}\n'
            prepare(out / f'{version}-{name}', rom, prefix + SCRIPT.read_text(encoding='utf-8'),
                    {Path(__file__), SCRIPT}, expected=digest, timeout=45, allow_interactive=True,
                    scope=f'{name}, cold Easy 1-1, idle and walk to the first Goomba approach')


if __name__ == '__main__':
    main()
