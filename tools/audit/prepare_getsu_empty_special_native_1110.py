"""Bind the immutable Getsu native observers to their exact 9906 successor."""

import argparse
import json
from pathlib import Path

import check_getsu_empty_special_1110 as Current
import prepare_getsu_giant_native_1110 as Native
from prepare_selected_native_packet_v1 import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--mode', choices=('idle', 'route'), required=True)
    args = parser.parse_args()
    out, rom, proof = args.output.resolve(), args.rom.resolve(), args.proof.resolve()
    rebase = Native.Rebase
    base, pin = rebase.BASE, rebase.PIN
    try:
        rebase.BASE, rebase.PIN = Current.CURRENT, Current.CURRENT_PIN
        Native.stage_packet(out, rom, proof, args.mode)
    finally:
        rebase.BASE, rebase.PIN = base, pin
    ready_path = out/'ready.json'
    ready = json.loads(ready_path.read_text(encoding='utf-8'))
    ready['bindings'][str(Path(__file__).resolve())] = sha(Path(__file__))
    ready_path.write_text(json.dumps(ready, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
