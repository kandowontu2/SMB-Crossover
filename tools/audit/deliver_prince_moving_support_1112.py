"""Deliver the five-byte Prince support correction after native qualification."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import prince_cold_packet_1111 as Packet
import replay_prince_native_flag_1111 as Replay
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check

PARENT = '464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0'
PIN = '6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2'
RECEIPT = 'a3c15de76676ba9ebdf3ffdbc84049ef953b70d14015285e31e05251c0fd773c'
SCRIPT_PIN = 'a115265b9c2a3cc12fbf792a3460e01c5ce67264e2829dc901dfe5ee37ce33d0'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
OUTPUT = Packet.R/'build/prince-first-pickup-1112'
CANDIDATE = OUTPUT/'candidate.nes'
REPORT = Packet.R/'docs/qa/prince-moving-support-delivery-1112.md'


def digest(data):
    return sha256(data).hexdigest()


def transform(image, reverse=False):
    assert digest(image) == (PIN if reverse else PARENT)
    before, after = bytes.fromhex('ad16c6d017'), bytes([0xea])*5
    if reverse:
        before, after = after, before
    def mutate(runtime, metadata, state):
        at = 0xd736-0xc800
        assert metadata[at:at+5] == before
        metadata[at:at+5] = after
        return runtime, metadata, state
    result, layout = Packet.rebuild(image, mutate)
    assert digest(result) == (PARENT if reverse else PIN)
    return result, layout


def install():
    assert check(NIGHTLY)['ROM_sha256'] == PARENT
    parent = NIGHTLY.read_bytes()
    image, layout = transform(parent)
    assert CANDIDATE.read_bytes() == image and transform(image, True)[0] == parent
    base = SOURCE_BASE.read_bytes()
    assert digest(base) == SOURCE_PIN
    ips = ips_for(image)
    assert apply_ips(base, ips)[0] == image
    script = OUTPUT/'controller.lua'
    script.write_text(Replay.controller(layout['cookie'], 0xd74b, 3115, True),
                      encoding='utf-8', newline='\n')
    assert digest(script.read_bytes()) == SCRIPT_PIN
    try:
        NIGHTLY.write_bytes(image)
        assert check(NIGHTLY)['ROM_sha256'] == PIN
        result, _ = Replay.replay(script, NIGHTLY, OUTPUT/'capture', PIN)
        assert result['passed'] and result['receipt_SHA256'] == RECEIPT, result['receipt']
        assert check(NIGHTLY)['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == image
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert check(NIGHTLY)['ROM_sha256'] == PARENT
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=digest(ips),
                          receipt=RECEIPT, backup_files=0)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true', required=True)
    parser.parse_args()
    install()
