"""Reconstruct visible Sonic rings on the verified four-pipe DK Jr. nightly."""
import json
from types import SimpleNamespace
from unittest.mock import patch

import check_dkjr_four_pipe_funded_1110 as Four
import check_sonic_sms_ring_feedback_1110 as Feedback
import deliver_dkjr_second_pipe_1110 as Previous


PARENT = 'b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65'
PIN = '27a8e45c5b631297ecca7429824ec389c1075de38ac69f37dc02e22085ec3351'


def proposal(raw):
    assert Feedback.digest(raw) == PARENT
    previous = Previous.Recipe.proposal(Previous.Recipe.V1.BASE.read_bytes())[0]
    assert Feedback.digest(previous) == Previous.PIN and Four.proposal(previous)[0] == raw
    historical_nightly = SimpleNamespace(read_bytes=lambda: previous)
    with patch.object(Feedback.Contact.DK, 'NIGHTLY', historical_nightly):
        original, _, sonic, common, packet, receipt = Feedback.proposal()
    assert original == previous
    assert Feedback.digest(sonic) == 'fbcb212854eda24891f540a2de143644918f963e9e86555be3c51d94df327ce6'
    differences = Feedback.Contact.differences
    dk_delta, ring_delta = differences(previous, raw), differences(previous, sonic)
    assert dk_delta.isdisjoint(ring_delta)
    joined = bytearray(raw)
    for at in ring_delta:
        joined[at] = sonic[at]
    assert differences(raw, joined) == ring_delta and differences(sonic, joined) == dk_delta
    assert Feedback.digest(joined) == PIN
    details = dict(parent_SHA256=PARENT, image_SHA256=PIN, retained_DK_bytes=len(dk_delta),
                   Sonic_bytes=len(ring_delta), cookie=receipt['cookie'])
    return bytes(joined), common, packet, details


def parent_bytes():
    current = Four.NIGHTLY.read_bytes()
    if Feedback.digest(current) == PARENT:
        return current
    from deliver_dkjr_four_pipe_1110 import Recipe
    original = Recipe.proposal(Recipe.V1.BASE.read_bytes())[0]
    assert Feedback.digest(original) == PARENT
    return original


def main():
    image, _, packet, details = proposal(parent_bytes())
    print(json.dumps(details, sort_keys=True), flush=True)
    print(json.dumps(Feedback.natural(image, packet), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
