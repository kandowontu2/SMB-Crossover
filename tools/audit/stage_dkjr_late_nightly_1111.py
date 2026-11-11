"""Compose the qualified late DK Jr. platforms with the faster Sonic nightly."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_late_girder_admission_1111 as Late
import check_sonic_sms_fast_snapshot_1111 as Sonic


PIN = 'e295500856ed5a9bfc718699d52bc5b36ecdc2717bed31cf275d87c1af25bf09'
WITH_JAY_PIN = 'b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576'


def proposal(parent):
    assert sha256(parent).hexdigest() == Sonic.PIN
    old = Late.source_parent(parent)
    late, dk_cookie, labels = Late.proposal(old)
    assert sha256(late).hexdigest() == Late.PIN
    sonic_edits, dk_edits = Sonic.changed(old, parent), Sonic.changed(old, late)
    assert len(sonic_edits) == 49 and len(dk_edits) == 280 and dk_edits.isdisjoint(sonic_edits)
    image = bytearray(parent)
    for address in dk_edits:
        image[address] = late[address]
    assert Sonic.changed(parent, image) == dk_edits
    assert sha256(image).hexdigest() == PIN
    return bytes(image), dict(image_SHA256=PIN, dk_cookie=dk_cookie.hex(),
                              dk_edits=len(dk_edits), retained_sonic_edits=len(sonic_edits),
                              constructor=hex(labels['DkAfterNativeConstructor']))


def compose_with_jay(sonic, jay):
    from deliver_jay_stock_draw_1111 import PIN as JAY_PIN

    assert sha256(jay).hexdigest() == JAY_PIN
    dk, evidence = proposal(sonic)
    dk_edits, jay_edits = Sonic.changed(sonic, dk), Sonic.changed(sonic, jay)
    assert len(jay_edits) == 4717 and dk_edits.isdisjoint(jay_edits)
    image = bytearray(jay)
    for address in dk_edits:
        image[address] = dk[address]
    assert Sonic.changed(dk, image) == jay_edits
    assert sha256(image).hexdigest() == WITH_JAY_PIN
    return bytes(image), dict(evidence, image_SHA256=WITH_JAY_PIN,
                              retained_jay_edits=len(jay_edits))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(Late.R / 'build') and output != Late.R / 'build'
    image, evidence = proposal(Sonic.DK.NIGHTLY.read_bytes())
    output.mkdir(exist_ok=True)
    candidate = output / 'candidate.nes'
    with candidate.open('xb') as file:
        file.write(image)
    assert candidate.read_bytes() == image
    print(json.dumps(evidence, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
