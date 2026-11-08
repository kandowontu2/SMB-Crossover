"""Compose a proven DK Jr frontend and replay its actual cold gameplay entry."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from observe_chip_committed_write import lua
from prepare_prince_resume_1108 import CURRENT, NIGHTLY
from prepare_selected_native_packet_v1 import R, prepare, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    proof = json.loads(args.contract.read_text())
    assert proof['passed'] and proof['parent_SHA256'] == sha(NIGHTLY) == CURRENT
    for path, digest in proof['bindings'].items():
        assert sha(path) == digest, path
    original = NIGHTLY.read_bytes()
    raw = bytearray(original)
    for patch in proof['patches']:
        offset = patch['file_offset']
        before = bytes.fromhex(patch['old_hex'])
        after = bytes.fromhex(patch['new_hex'])
        assert len(before) == len(after) and raw[offset:offset+len(before)] == before, hex(offset)
        raw[offset:offset+len(after)] = after
    assert raw[1048592:] == original[1048592:], 'Menu-only patch must preserve CHR and payloads'

    args.output.mkdir()
    rom = args.output/'dkjr-private.nes'
    rom.write_bytes(raw)
    labels = R/'build/mini-two-fireballs-1103/mini-empty-draw.nes'
    assert sha(labels) == CURRENT
    for ext in ('.lbl','.dbg'):
        shutil.copyfile(labels.with_suffix(ext),rom.with_suffix(ext))
    symbols = R/'build/dkjr-native-source-1102-v2/native-entrance-v89-layout.json'
    source = Path(__file__).with_name('dkjr_smoke_1108.lua')
    native = json.loads(symbols.read_text())['labels']
    pin = sha(rom)
    assert pin == proof['expected_memory_only_SHA256']
    config = dict(pin=pin, main=native['DkNativeMain'], draw=native['DkNativeDraw'],
                  cookie=list(bytes.fromhex('a7280107765b6c49b9189537b7ba67e0')))
    text = 'local C='+lua(config)+'\n'+source.read_text()
    prepare(args.output/'native',rom,text,[Path(__file__),args.contract,source,symbols],expected=pin,
            timeout=120,allow_interactive=True,
            scope='Private DK Jr cold Select and Start, authenticated Main and draw, idle cadence and original walking/jump.')
    return subprocess.call([sys.executable,'-B',args.output/'native/run.py'])


if __name__ == '__main__':
    raise SystemExit(main())
