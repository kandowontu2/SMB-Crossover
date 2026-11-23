"""Private exact3ce Giant reward repair; in-memory image and stdout evidence only.

The existing exact-owner crush caller already saved the authentic source tile
in R3.  Give that tile to the native head owner instead of replacing the cell
with $51.  Ordinary brick still takes native shatter; item/coin blocks retain
native bump, maturity, pickup, and reward ownership.  No space allocation,
new actor, helper, physics, or collision-box change is made.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import probe_mega_giant_first_pickup_1123 as Base

PARENT = Base.PIN
AT = Base.Giant.at(90, 0xb174)
OLD = bytes.fromhex('a405a95191094cf59e') + b'\xea' * 3
NEW = bytes.fromhex('a5064cf59e') + b'\xea' * 7


def compose(raw):
    assert sha256(raw).hexdigest() == PARENT
    assert raw[AT:AT+12] == OLD
    # Exact owning call remains behind all original raw/variant/play/cell/slot
    # gates, and the leaf has no other PRG call or jump sites.
    assert raw[Base.Giant.at(90, 0xbcde):Base.Giant.at(90, 0xbcde)+5] == bytes.fromhex('2074b1eaea')
    assert raw[16:16+128*8192].count(bytes.fromhex('2074b1')) == 1
    assert raw[16:16+128*8192].count(bytes.fromhex('4c74b1')) == 0
    image = raw[:AT] + NEW + raw[AT+12:]
    assert inverse(image) == raw
    return image


def inverse(image):
    assert image[AT:AT+12] == NEW
    raw = image[:AT] + OLD + image[AT+12:]
    assert sha256(raw).hexdigest() == PARENT
    return raw


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(exist_ok=True)
    image = compose(Base.ROM.read_bytes())
    print(json.dumps(dict(event='private_memory_proposal', parent=PARENT,
        candidate_SHA256=sha256(image).hexdigest(), physical_PRG=90, PC=0xb174,
        file_offset=AT, old_hex=OLD.hex(), new_hex=NEW.hex(), output_ROM_files=0)), flush=True)
    Base.run(a.output, image=image, require_pickup=True)


if __name__ == '__main__':
    main()
