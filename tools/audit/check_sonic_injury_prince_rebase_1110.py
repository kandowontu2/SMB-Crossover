"""Prove the Sonic injury correction is disjoint from the delivered Prince packet."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_native_injury_tier_1110 as Injury
import stage_prince_sonic_transport_1110 as Prince
from nightly_patch_guard_v1 import check

DONOR_FIX = '19a5ea9001f22afd529c96c6c2401a237f487c0f851678363fb859f0ec7c1936'
PIN = '49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7'
CANDIDATE = Prince.R/'build/sonic-earned-injury-native-1110/candidate.nes'


def reconstruct():
    parent, combined, _, prince_layout, program, packet, _ = Prince.Transport.proposal(sonic_scene=True)
    before, public = parent['raw'], combined['raw']
    assert sha256(before).hexdigest() == Prince.PARENT
    assert sha256(public).hexdigest() == Prince.PIN
    reference, _, reference_record = Injury.proposal(before, packet)
    assert reference_record['image_SHA256'] == DONOR_FIX
    result, next_packet, record = Injury.proposal(public, packet)
    differences = Prince.Transport.Stage.differences
    prince_delta = differences(before, public)
    injury_delta = differences(before, reference)
    assert len(prince_delta) == prince_layout['pure_payload_changed_bytes'] == 14244
    assert len(injury_delta) == record['exact_changed_bytes'] == 19
    assert not prince_delta.keys() & injury_delta.keys()
    assert differences(public, result) == injury_delta
    assert differences(reference, result) == prince_delta
    assert record['image_SHA256'] == PIN
    return result, program, next_packet, dict(record, preserved_Prince_bytes=len(prince_delta),
        qualified_source_ancestor=DONOR_FIX, disjoint=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Stage one exact private ROM in the owned task slot')
    args = parser.parse_args()
    output = args.output.resolve() if args.output else None
    if output:
        assert output == CANDIDATE.parent and not output.exists()
        assert check(Prince.NIGHTLY)['ROM_sha256'] == Prince.PIN
    image, _, _, evidence = reconstruct()
    if output:
        output.mkdir()
        CANDIDATE.write_bytes(image)
        assert CANDIDATE.read_bytes() == image
    print(json.dumps(dict(passed=True, source_only=not output, ROM_written=bool(output),
        Mesen_run=False, output_files=int(bool(output)), record=evidence), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
