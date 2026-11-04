"""Compose the qualified native transport over an exact Mini candidate."""
import argparse
import json
from pathlib import Path
import shutil

from prepare_selected_native_packet_v1 import R, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    contract = R/'build/mini-direct-native-1103/CPU.json'
    boundaries = R/'build/mini-direct-native-1103/boundaries.json'
    proof = json.loads(contract.read_text())
    assert proof['passed'] and json.loads(boundaries.read_text())['passed']
    source = R/'tools/reference/mini_mario_direct_native_1103.s'
    pins = json.loads(boundaries.read_text())['source_bindings']
    assert sha(source) == pins[str(source.relative_to(R))]
    raw = bytearray(args.parent.read_bytes())
    for patch in proof['patches']:
        start = patch['file_offset']
        old = bytes.fromhex(patch['old_hex'])
        new = bytes.fromhex(patch['new_hex'])
        assert len(old) == len(new)
        assert raw[start:start+len(old)] == old, patch['name']
        raw[start:start+len(new)] = new
    args.output.mkdir()
    rom = args.output/'mini-optimized.nes'
    rom.write_bytes(raw)
    for extension in ['.lbl', '.dbg']:
        shutil.copyfile(args.parent.with_suffix(extension), rom.with_suffix(extension))
    for name in ['mini-zero.lbl', 'mini-zero.bin', 'render.lbl']:
        shutil.copyfile(args.parent.parent/name, args.output/name)
    (args.output/'candidate.json').write_text(json.dumps(dict(
        parent_SHA256=sha(args.parent), ROM_SHA256=sha(rom), candidate_SHA256=sha(rom),
        contract_SHA256=sha(contract), boundaries_SHA256=sha(boundaries),
        patches=proof['patches']), indent=2)+'\n')
    print(sha(rom))


if __name__ == '__main__':
    main()
