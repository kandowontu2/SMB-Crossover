"""Verify Jay earns and fires the original machine gun after clearing 1-1."""

import argparse
import json
from pathlib import Path

import check_jay_silius_machinegun_1111 as Source
from deliver_roster_repair_1111 import NIGHTLY, R
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


PIN = 'c8d328a27efbc900216985aeb86600a1f626f8cc76e93a91bb30b2c1f8c2e727'
COOKIE = 'a710200a5b78f52474bff8a681fb9156'
CANDIDATE = R / 'build/jay-machinegun-native-1111/candidate.nes'


def replay(script, rom, output, expected=PIN):
    result = run(script, rom, output, expected, 130, variant=2,
                 extra_env={'SMB_JAY_COOKIE': COOKIE, 'SMB_JAY_DONOR_FLAGS': '49170'})
    receipt = result['receipt']
    if result['passed']:
        assert receipt['controller_only'] and receipt['flag'] and receipt['castle']
        assert receipt['three_way'] and receipt['lives'] == 2 and receipt['extended_slot_dma'] > 0
        bursts = receipt['machine_gun_births']
        assert [b[1:] for b in bursts] == [[240, 62], [224, 61], [208, 60], [192, 59], [176, 58]]
        assert all((right[0] - left[0]) & 255 == 5 for left, right in zip(bursts, bursts[1:]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output.resolve()
    assert output == CANDIDATE.parent
    assert check(NIGHTLY)['ROM_sha256'] == Source.PIN
    image, linked = Source.proposal(NIGHTLY.read_bytes())
    assert Source.T.digest(image) == PIN and linked['cookie'].hex() == COOKIE
    output.mkdir(exist_ok=True)
    if CANDIDATE.exists():
        assert CANDIDATE.read_bytes() == image
    else:
        CANDIDATE.write_bytes(image)
    script = output / 'controller.lua'
    script.write_text(Source.controller(), encoding='utf-8', newline='\n')
    result = replay(script, CANDIDATE, output / 'capture')
    print(json.dumps(dict(passed=result['passed'], receipt=result['receipt'],
                          receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256']),
                     sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
