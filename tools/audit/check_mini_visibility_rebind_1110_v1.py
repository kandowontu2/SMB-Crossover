"""Verify the same visibility patch with the combined box and terrain changes."""
import json
from pathlib import Path

import check_mini_visibility_dispatch_1110_v1 as V

COMBINED = V.R / 'build/mini-box-terrain-visible-1110/candidate.nes'
COMBINED_SHA = '6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
PROOF = V.OUT / 'visibility-proof.json'
PROOF_SHA = '418c54cc116789e93d292fdeb68c3b86fa3049157959348d3b16b0fadee6d978'


def main():
    raw, proof_bytes = COMBINED.read_bytes(), PROOF.read_bytes()
    assert V.P.sha(raw) == COMBINED_SHA and V.P.sha(proof_bytes) == PROOF_SHA
    original = json.loads(proof_bytes)
    assert original['passed'] and original['base_SHA256'] == V.PIN
    for name, digest in original['bindings'].items():
        assert V.P.sha((V.R / name).read_bytes()) == digest, name

    patch = original['patch']
    at = patch['file_offset']
    assert at == V.AT and bytes.fromhex(patch['old_hex']) == V.OLD
    before = V.install(raw, [dict(file_offset=at, old_hex=patch['new_hex'], new_hex=patch['old_hex'])])
    V.contract(before)
    assert V.install(before, [patch]) == raw

    pair = [V.P.bundle(image) for image in (before, raw)]
    foreground = V.foreground(pair)
    assert foreground['calls'] == original['foreground']['calls']
    assert foreground['raw41_original_SEC_entries'] == original['foreground']['raw41_original_SEC_entries']
    assert foreground['local_savings'] == original['foreground']['local_savings']
    assert all(row['minimum_saved'] == row['maximum_saved'] == 503
               for row in foreground['whole_GameCore'].values())
    print('Combined foreground: 2,624 native calls and 96 GameCore updates pass', flush=True)

    vectors = V.vectors(pair)
    assert vectors['cuts'] == original['vectors']['cuts']
    result = dict(passed=True, ROM_written=False, combined_SHA256=COMBINED_SHA,
                  visibility_reverted_memory_SHA256=V.P.sha(before), foreground=foreground,
                  vectors=vectors, exact_preimage_patch=patch,
                  bindings={path.relative_to(V.R).as_posix(): V.P.sha(path.read_bytes())
                            for path in [Path(__file__), COMBINED, PROOF, Path(V.__file__), V.SOURCE]},
                  scope='Exact combined candidate versus the same in-memory image with only the visibility span reverted. Both box and terrain patches are retained in every comparison.')
    (V.OUT / 'final-vectors.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Combined vectors:', vectors, flush=True)


if __name__ == '__main__':
    main()
