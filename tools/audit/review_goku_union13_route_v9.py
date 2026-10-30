"""Verify the finished controller-only Goku route and bounded lossless evidence."""
from pathlib import Path
from collections import Counter
import csv
import json
import sys
import numpy as np

R = Path(__file__).resolve().parents[2]
O = R/'build/character-host-union-routes-v13-v4/goku-route-v1'
sys.path.insert(0, str(R/'tools/audit'))
import review_rogue_current_route_v1 as reference

codec = reference.codec
sha = reference.sha
EXPECTED = '3f24a0e1bc73d8655811b333aa52285ace1af5e469fcc7b6158b06afce54f72c'


def main():
    assert not (O/'review.json').exists()
    result = json.loads((O/'result.json').read_text())
    binding = json.loads((O/'binding.json').read_text())
    ready = json.loads((O/'ready.json').read_text())
    budget = json.loads((O/'capture-budget.json').read_text())
    assert result['passed'] and result['zero_deaths'] and result['cheats_off']
    assert result['ROM_sha256'] == binding['ROM_sha256'] == ready['ROM_sha256'] == EXPECTED
    assert binding['ready_sha256'] == sha(O/'ready.json')
    assert binding['exit_code'] == budget['returncode'] == 0 and not budget['violations']
    assert binding['native_controller_only'] and binding['normal_sprite_limit']
    assert binding['source_SMC_guard_bytes'] == 33
    assert result['frames'] == 5222 and result['real_1_2_control_updates'] >= 25
    for path, digest in binding['inputs'].items():
        assert sha(path) == digest, path
    telemetry = list(csv.DictReader((O/'source-telemetry.csv').open()))
    supports = [q for q in telemetry if int(q['platform_owner']) == 0x83
                and int(q['platform_id']) == 0x25 and int(q['platform_flag']) == 1
                and int(q['platform_collision']) < 0x80]
    # Telemetry records the native actor's left edge; its source spawn uses
    # HpX(center)-16 for the existing32px girder.
    centers = Counter(int(q['platform_x'])+16 for q in supports)
    assert set(centers) == {704, 888}, centers
    left = next(q for q in telemetry if q['x'] == '2188' and q['y'] == '112'
                and q['DpAction'] == '1')
    right = next(q for q in telemetry if 2250 <= int(q['x']) <= 2260
                 and q['y'] == '112' and q['DpAction'] == '1')
    assert int(left['ppu_frame']) < int(right['ppu_frame'])
    assert min(int(q['DpHP']) for q in telemetry) > 0
    selected = {n: result['markers'][n]['stamp']['ppu_frame']
                for n in ['cold-menu', 'cold-lives', 'power-change', 'flagpole', 'endpoint']}
    selected.update(native_platform_support=int(supports[0]['ppu_frame']),
                    left_stair_landing=int(left['ppu_frame']),
                    right_stair_landing=int(right['ppu_frame']))
    index = [json.loads(s) for s in (O/'captures-index.jsonl').open()]
    by_frame = {q['stamp']['ppu_frame']: q['record'] for q in index if q['type'] == 'record'}
    wanted = {by_frame[f] for f in selected.values()}
    assert len(wanted) == 8
    images = {}
    original_decode, original_fnv, original_records = codec.decode, codec.word_fnv, codec.records

    def fast_fnv(raw):
        return int(reference.fnv_words(np.frombuffer(raw, dtype='<u4')))

    def fast_decode(mode, payload, previous, expected):
        if mode != 2:
            return original_decode(mode, payload, previous, expected)
        assert previous is not None and len(previous) == expected
        delta = original_decode(1, payload, None, expected)
        return np.bitwise_xor(np.frombuffer(delta, dtype=np.uint8),
                              np.frombuffer(previous, dtype=np.uint8)).tobytes()

    for n in [0, 1, 2, 16, 257, 1024, 61440]:
        raw = bytes((i*31+19) & 255 for i in range(n*4))
        assert fast_fnv(raw) == original_fnv(raw)
    xor_checks, previous = 0, None
    with (O/'captures.nesppuv1').open('rb') as stream:
        assert stream.read(16) == codec.MAGIC
        while xor_checks < 16:
            header = stream.read(codec.HEADER.size)
            assert len(header) == codec.HEADER.size
            kind, mode, reserved, seq, mb, pb, checksum = codec.HEADER.unpack(header)
            meta = json.loads(stream.read(mb))
            payload = stream.read(pb)
            decoded = original_decode(mode, payload, previous, meta['decoded_bytes'])
            assert fast_decode(mode, payload, previous, meta['decoded_bytes']) == decoded
            assert fast_fnv(decoded) == original_fnv(decoded) == checksum
            if kind != 3:
                previous = decoded
            if mode == 2:
                xor_checks += 1

    def records(path):
        for meta, raw in original_records(path):
            if meta['record'] in wanted:
                images[meta['record']] = raw
            yield meta, raw

    codec.decode, codec.word_fnv, codec.records = fast_decode, fast_fnv, records
    try:
        verified = codec.verify(O/'captures.nesppuv1', O/'captures-index.jsonl')
    finally:
        codec.decode, codec.word_fnv, codec.records = original_decode, original_fnv, original_records
    assert verified['full_frames'] == result['full_frames'] == 4534
    assert wanted == set(images)
    sheet = O/'selected-eight-whole-frames.png'
    reference.png(sheet, [images[by_frame[f]] for f in selected.values()])
    bindings = dict(binding['inputs'])
    for path in [Path(__file__).resolve(), Path(reference.__file__), Path(codec.__file__),
                 R/'tools/audit/current_roster_compact_11_v1.py', sheet,
                 *[O/n for n in ['ready.json', 'binding.json', 'result.json', 'capture-budget.json',
                                'trace.csv', 'inputs.csv', 'events.jsonl', 'source-telemetry.csv',
                                'captures-index.jsonl', 'captures.nesppuv1', 'candidate-run.log']]]:
        bindings[str(path)] = sha(path)
    report = dict(passed=True, evidence_integrity_passed=True, ROM_sha256=EXPECTED,
                  native=result, container=verified,
                  controller_only=True, source_ROM_unchanged=True,
                  controller_diagnosis='Frozen v9 retains the original horizontal stop at2188, adds the missing climb jump, lands atY112, then crosses the valley. No geometry, physics, HP, or runtime state was patched.',
                  actual_platform_support=dict(native_owner=0x83, native_id=0x25,
                                               completed_Main_samples_by_center=dict(centers),
                                               telemetry_coordinate='Native left edge; source center=left+16'),
                  stair_landings=dict(left=left, right=right),
                  HP_range=[min(int(q['DpHP']) for q in telemetry),
                            max(int(q['DpHP']) for q in telemetry)],
                  selected_whole_frames=dict(path=str(sheet), names_and_frames=selected,
                                            sha256=sha(sheet)),
                  host_decoder_acceleration=dict(canonical_checksum_vectors=7,
                      actual_XOR_frames_crosschecked=xor_checks,
                      complete_container_checksums_and_aliases_verified=True),
                  root_visual_review_pending=True,
                  limits=['Every captured frame is integrity-checked; eight selected frames are prepared for human visual review.',
                          'No all-items/all-abilities/Hard/full-campaign/source-fidelity/constant60Hz claim.',
                          'This is exact V13, before the separate resource relocation and joint host additions.',
                          'No shared download installation.'], bindings=bindings)
    (O/'review.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, verified_frames=4534, platform_supports=dict(centers),
                          stair_landing_frames=[left['ppu_frame'], right['ppu_frame']], sheet=str(sheet))))


if __name__ == '__main__':
    main()
