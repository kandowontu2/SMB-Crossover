"""Prove the Sonic injury correction is disjoint from the delivered Prince packet."""
from hashlib import sha256
import json

import check_sonic_native_injury_tier_1110 as Injury
import stage_prince_sonic_transport_1110 as Prince

DONOR_FIX = '19a5ea9001f22afd529c96c6c2401a237f487c0f851678363fb859f0ec7c1936'


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
    return result, program, next_packet, dict(record, preserved_Prince_bytes=len(prince_delta),
        qualified_source_ancestor=DONOR_FIX, disjoint=True)


if __name__ == '__main__':
    _, _, _, evidence = reconstruct()
    print(json.dumps(dict(passed=True, source_only=True, ROM_written=False,
        Mesen_run=False, output_files=0, record=evidence), sort_keys=True), flush=True)
