"""Verify the exact V8 native route, all capture checksums, and reference pixels."""
from pathlib import Path
import csv
import json
import sys
import numpy as np

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
import review_rogue_current_route_v1 as reference

O = R/'build/rogue-current-menu-v8/native/route'
P = R/'build/verification/rogue-dawn-victory-native-easy-v1'
EXPECTED = 'cdce3d9f26c26e367ca2aa1e4cfee0101c005bdb8f8ac10ea78a47fed3f8707f'
sha = reference.sha
codec = reference.codec


def main():
    assert not (O/'review.json').exists()
    result = json.loads((O/'result.json').read_text())
    binding = json.loads((O/'binding.json').read_text())
    driver = json.loads((O/'driver-binding.json').read_text())
    budget = json.loads((O/'capture-budget.json').read_text())
    controls_path = O.parents[1]/'prune-controls.json'
    controls = json.loads(controls_path.read_text())
    assert result['passed'] and result['zero_deaths'] and result['cheats_off']
    assert result['ROM_sha256'] == binding['ROM_sha256'] == controls['ROM_sha256'] == EXPECTED
    assert sha(O.parents[1]/'candidate.nes') == EXPECTED
    assert binding['exit_code'] == driver['exit_code'] == budget['returncode'] == 0
    assert not budget['violations'] and binding['no_native_RAM_writes'] and binding['normal_sprite_limit']
    assert driver['driver_sha256'] == sha(R/'tools/audit/rogue_foreign_prune_route_v1.py')
    assert driver['runner_binding_sha256'] == sha(O/'binding.json')
    assert driver['CPU_controls_sha256'] == sha(controls_path)
    assert result['frames'] == 6513 and result['real_1_2_control_updates'] == 25
    inputs = dict(binding['inputs'])
    inputs.update(controls['source_bindings'])
    for path, digest in inputs.items():
        assert sha(path) == digest, path
    old = json.loads((P/'review.json').read_text())
    checkpoint = R/'docs/qa/checkpoints/2026-10-30/rogue-dawn-victory-pose/root-review.json'
    frozen = json.loads(checkpoint.read_text())
    assert sha(P/'review.json') == frozen['runtime_references'][str(P/'review.json')]
    assert old['passed'] and sha(P/'captures.nesppuv1') == old['container']['container_sha256']
    assert sha(P/'captures-index.jsonl') == old['container']['index_sha256']
    assert (P/'inputs.csv').read_bytes() == (O/'inputs.csv').read_bytes()
    rows = list(csv.DictReader((O/'trace.csv').open()))
    assert len(rows) == 6513
    walk = next(r for r in rows if r['engine'] == '5' and r['level'] == '0' and int(r['x']) >= 3210)
    index = [json.loads(s) for s in (O/'captures-index.jsonl').open()]
    names = ['cold-menu', 'cold-lives', 'first-active', 'corner-332', 'power-change', 'flagpole', 'endpoint']
    selected = {name: next(q['record'] for q in index if q.get('name') == name+'.argb') for name in names}
    selected['castle-walk'] = int(walk['captured'])
    wanted = set(selected.values())
    images = {}
    original_decode, original_fnv, original_records = codec.decode, codec.word_fnv, codec.records

    def fast_fnv(raw):
        return int(reference.fnv_words(np.frombuffer(raw, dtype='<u4')))

    def fast_decode(mode, payload, previous, expected):
        if mode != 2:
            return original_decode(mode, payload, previous, expected)
        assert previous is not None and len(previous) == expected
        delta = original_decode(1, payload, None, expected)
        return np.bitwise_xor(np.frombuffer(delta, dtype=np.uint8), np.frombuffer(previous, dtype=np.uint8)).tobytes()

    for n in [0, 1, 2, 16, 257, 1024, 61440]:
        raw = bytes((i*31+19) & 255 for i in range(n*4))
        assert fast_fnv(raw) == original_fnv(raw)

    def records(path):
        for meta, raw in original_records(path):
            if meta['record'] in wanted:
                images[meta['record']] = raw
            yield meta, raw

    xor_checks = 0
    previous = None
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
    codec.decode, codec.word_fnv, codec.records = fast_decode, fast_fnv, records
    try:
        verified = codec.verify(O/'captures.nesppuv1', O/'captures-index.jsonl')
    finally:
        codec.decode, codec.word_fnv, codec.records = original_decode, original_fnv, original_records
    assert verified['full_frames'] == result['full_frames'] == 5801
    assert wanted == set(images)
    equal, different = [], []
    for meta in index:
        if meta['type'] != 'record':
            continue
        same = verified['record_sha256'][meta['record']] == old['container']['record_sha256'][str(meta['record'])]
        (equal if same else different).append(dict(ordinal=meta['full_ordinal'], frame=meta['stamp']['ppu_frame']))
    assert different == [dict(ordinal=i, frame=77+i) for i in range(1, 6)], different[:30]
    assert len(equal) == 5796
    sheet = O/'selected-whole-frames.png'
    reference.png(sheet, [images[selected[name]] for name in names+['castle-walk']])
    castle = O/'actual-victory-walk.png'
    reference.png(castle, [images[selected['castle-walk']]])
    paths = [Path(__file__).resolve(), Path(reference.__file__), checkpoint, controls_path,
             R/'tools/audit/rogue_foreign_prune_route_v1.py', P/'review.json', P/'captures.nesppuv1',
             P/'captures-index.jsonl', P/'inputs.csv', sheet, castle,
             R/'tools/audit/final_inventory_compact_capture_v1.py',
             R/'tools/audit/current_roster_compact_11_v1.py']
    paths += [O/name for name in ['binding.json', 'driver-binding.json', 'result.json', 'trace.csv',
                                  'captures-index.jsonl', 'captures.nesppuv1', 'capture-budget.json', 'config.json']]
    inputs.update({str(path): sha(path) for path in paths})
    report = dict(passed=True, ROM_sha256=EXPECTED, native=result, container=verified,
                  full_frame_comparison=dict(exact_pairs=len(equal), changed_menu_frames=different,
                      every_lives_gameplay_powerup_flagpole_castle_and_endpoint_frame_identical=True,
                      reference_ROM_sha256=old['native']['ROM_sha256'], same_controller_polls=True),
                  host_decoder_acceleration=dict(canonical_checksum_vectors=7,
                      actual_XOR_frames_crosschecked=xor_checks, complete_container_checksums_and_aliases_verified=True),
                  selected_whole_frames=dict(path=str(sheet), order=names+['castle-walk'], sha256=sha(sheet)),
                  castle_walk=dict(trace=walk, path=str(castle), sha256=sha(castle)), root_visual_review_pending=True,
                  limits=['Pixel equality preserves the reference behavior; it does not prove the reference is flawless.',
                          'No all-upgrade/Hard/full-campaign/native-hardware/constant60Hz claim.',
                          'Foreign Bill timing remains worse than the installed parent; no shared installation.'],
                  inputs=inputs)
    (O/'review.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, verified_frames=5801, exact_reference_pairs=len(equal),
                         changed_menu_frames=len(different), sheet=str(sheet))))


if __name__ == '__main__':
    main()
