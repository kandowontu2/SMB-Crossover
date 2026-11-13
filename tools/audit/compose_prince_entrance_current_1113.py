"""Explicit reversible composition of frozen Prince repairs over Karnov526."""
from hashlib import sha256
import json

import prince_entrance_handoff_1113 as Entry
import compose_karnov_ladder_native_1113 as Karnov

PARENT = '526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2'
ENTRY = '309bbdae23b2dbe76951d3320c5afcb895e25b0fd081a558e93241b12f96389c'
KARNOV_CACHE = 'c5afaa7b9693655e283a8bdd6a21fc78041d91c4c6bc9f5c91943a045eb42359'
PIN = '7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'


def digest(raw):
    return sha256(raw).hexdigest()


def proposal(raw):
    assert digest(raw) == PARENT, 'Exact tested Karnov526 parent required'
    original = Karnov.inverse_current(raw)
    assert digest(original) == Entry.Cache.PARENT
    cache, _ = Entry.Cache.proposal(original)
    assert digest(cache) == Entry.PARENT
    entry, entry_info = Entry.proposal(cache)
    assert digest(entry) == ENTRY and Entry.reverse(entry) == cache
    with_karnov, _ = Karnov.proposal_current(cache)
    assert digest(with_karnov) == KARNOV_CACHE
    assert Karnov.inverse_current(with_karnov) == cache
    result = bytearray(with_karnov)
    allowed = set()
    for pc, before, after in Entry.code():
        at = Entry.offset(pc)
        assert with_karnov[at:at+len(before)] == cache[at:at+len(before)] == before
        assert entry[at:at+len(after)] == after
        result[at:at+len(after)] = after
        allowed.update(range(at, at+len(before)))
    delta = {i for i, (a, z) in enumerate(zip(with_karnov, result)) if a != z}
    assert len(delta) == 41 and delta <= allowed
    assert all(a == z or i in delta for i, (a, z) in enumerate(zip(cache, entry)))
    result = bytes(result)
    assert digest(result) == PIN
    assert Entry.Cache.Packet.extract(result) == Entry.Cache.Packet.extract(cache)
    return result, dict(parent_SHA256=PARENT, candidate_SHA256=PIN,
        frozen_entry_SHA256=ENTRY, frozen_cache_SHA256=Entry.PARENT,
        prior_Karnov_cache_SHA256=KARNOV_CACHE, entry_changed_bytes=41,
        declared_native_entry_envelope_bytes=len(allowed),
        exact_Karnov_source_and_feature_bytes_preserved=True,
        cookie=result[Entry.Cache.Packet.COOKIE:Entry.Cache.Packet.COOKIE+16].hex(),
        all_three_Prince_streams_equal_frozen_cache=True,
        entry_gate=entry_info['helper_CPU_half_open'],
        native_qualification=False, outputs_written=0)


def reverse(image):
    assert digest(image) == PIN, 'Only the exact combined private candidate is accepted'
    without_entry = bytearray(image)
    for pc, before, after in Entry.code():
        at = Entry.offset(pc)
        assert without_entry[at:at+len(after)] == after
        without_entry[at:at+len(before)] = before
    without_entry = bytes(without_entry)
    assert digest(without_entry) == KARNOV_CACHE
    cache = Karnov.inverse_current(without_entry)
    assert digest(cache) == Entry.PARENT
    original = Entry.Cache.reverse(cache)
    assert digest(original) == Entry.Cache.PARENT
    parent, _ = Karnov.proposal_current(original)
    assert digest(parent) == PARENT and proposal(parent)[0] == image
    return parent


if __name__ == '__main__':
    public = Karnov.Owner.NIGHTLY.read_bytes()
    if digest(public) == PIN:
        public = reverse(public)
    image, info = proposal(public)
    assert reverse(image) == public
    print(json.dumps(dict(passed=True, **info, exact_inverse=True), separators=(',', ':')), flush=True)
