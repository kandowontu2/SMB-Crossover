"""Stage and physically replay Steve's first original punch on the MMC5 ROM."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import compose_steve_shatterhand_1111 as Source
import deliver_prince_brick_1111 as Parent
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


SCRIPT = Parent.R / 'tools/playthroughs/steve_native_punch_1111.lua'
PIN = '409d5a2e3b8ca1fdf6fa4512cac399310c44c1837b88b9f7d2a1e5bde858d280'
COOKIE = 'a7102009d541d456ddb444f69f81a4f1'


def replay(rom, output, linked):
    assert linked['cookie'].hex() == COOKIE
    symbols = linked['symbols']
    assert (symbols['StevePunchBirth'], symbols['SteveDrawEmit']) == (0xb586, 0xdbd4)
    return run(SCRIPT, rom, output, PIN, 100, extra_env={
        'SMB_STEVE_COOKIE': COOKIE, 'SMB_STEVE_BIRTH': str(symbols['StevePunchBirth']),
        'SMB_STEVE_DRAW': str(symbols['SteveDrawEmit'])})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output.resolve()
    assert output == Parent.R / 'build/steve-punch-native-1111'
    assert check(Parent.NIGHTLY)['ROM_sha256'] == Parent.PIN
    image, linked = Source.proposal(Parent.NIGHTLY.read_bytes())
    assert sha256(image).hexdigest() == PIN
    rom = output / 'candidate.nes'
    if output.exists():
        assert set(output.iterdir()) == {rom} and rom.read_bytes() == image
    else:
        output.mkdir()
        rom.write_bytes(image)
    result = replay(rom, output / 'capture', linked)
    print(json.dumps(result, sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
