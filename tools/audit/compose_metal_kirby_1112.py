"""Compose independently qualified Metal and Kirby fixes; bounded native replays."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import compose_metal_column_wait_1112 as Metal
import check_kirby_inhale_native_1112 as Kirby
import replay_metal_current_1112 as MR
import replay_kirby_left_inhale_1112 as KL
import replay_kirby_red_current_1112 as KR

PARENT = 'f228e61399432c1a205b8f5ac6dad13d990515f9c2e2f5024bcd5ce443c76653'
PIN = '8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582'
OUTPUT = MR.R/'build/metal-flower-native-1112'


def compose(raw):
    assert sha256(raw).hexdigest() == PARENT
    metal, _ = Metal.compose(raw)
    result, info = Kirby.proposal(metal)
    kirby, _ = Kirby.proposal(raw)
    alternate, _ = Metal.compose(kirby)
    assert result == alternate, 'Independent patches must commute'
    assert sha256(result).hexdigest() == PIN
    restored = bytearray(result)
    for offset, old, new in info['edits']:
        assert restored[offset:offset+len(new)] == new
        restored[offset:offset+len(old)] = old
    assert bytes(restored) == metal
    return result


def controller(raw, mode):
    assert sha256(raw).hexdigest() == PIN
    if mode in ('route', 'upgrades'):
        return MR.controller(raw, mode)
    text = KL.controller(2, True) if mode == 'inhale' else KR.controller(True, True)
    # Capture's existing execution observer must match the changed instruction,
    # while retaining its original mapped address and all behavioral assertions.
    first, body = text.split('\n', 1)
    offset = 16 + 74*8192 + (0xa31a & 8191)
    assert raw[offset:offset+5] == bytes.fromhex('a9018d0c5c')
    return first+'\nC.hooks.erased.bytes={'+','.join(map(str, raw[offset:offset+5]))+'}\n'+body


def reverse(raw):
    assert sha256(raw).hexdigest() == PIN
    image = bytearray(raw)
    for pc, old in (Kirby.CLOCK, Kirby.TAIL):
        at = Kirby.Wide.offset(pc)
        image[at:at+len(old)] = old
    maturity, _ = Metal.transform(bytes(image), True)
    head, _ = Metal.Maturity.transform(maturity, True)
    flower, _ = Metal.Head.transform(head, True)
    parent, _ = Metal.Head.Flower.transform(flower, True)
    assert sha256(parent).hexdigest() == PARENT
    assert compose(parent) == raw
    return parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('route','upgrades','inhale','shell'), required=True)
    parser.add_argument('--rom', type=Path)
    args = parser.parse_args()
    raw = compose(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()) if args.rom is None else args.rom.read_bytes()
    rom = args.rom or OUTPUT/'candidate.nes'
    if args.rom is None:
        rom.write_bytes(raw)
    script = OUTPUT/'controller.lua'
    script.write_text(controller(raw,args.mode),encoding='utf-8',newline='\n')
    result = MR.run(script,rom,OUTPUT/'capture',sha256(raw).hexdigest(),120)
    receipt = result['receipt']
    print(json.dumps(dict(mode=args.mode,ROM_SHA256=sha256(raw).hexdigest(),
        passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],
        script_SHA256=result['script_SHA256'],receipt={k:v for k,v in receipt.items()
            if k in ('reason','frames','lives','armor','weapon','status','collections',
                     'upgradedShot','terminal','catch_verified','passed')})),flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
