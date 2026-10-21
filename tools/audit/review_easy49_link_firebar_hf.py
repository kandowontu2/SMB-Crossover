"""Review the actual disjoint native Link/firebar incident, with phase limits."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'agent-lsr-link-gq-route-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-link-firebar-lead-hf.json'
    assert not out.exists()
    review = H / 'firebar-f-source-review.json'
    assert sha(review) == '2ace3ecfe1cdaa26b6536bc27eb0167317678f1e0eb46c9708a432a2d1834f35'
    d = json.loads(review.read_text())
    for n, value in {**d['source_file_hashes'], **d['artifacts']}.items():
        assert sha(R / n) == value, n
    native = json.loads((H / 'g-firebar-passive-actual.json').read_text())
    proof = Path(native['output'])
    for n, item in native['raw_files'].items():
        assert sha(proof / n) == item['sha256'] and (proof / n).stat().st_size == item['bytes'], n
    before = R / 'build/roster-through-2-2/agent-lsr-link-gq-f-nearestbar-4-v0-mmc3'
    for filename in d['full9CSVliteral']:
        assert (before / filename).read_bytes() == (proof / filename).read_bytes(), filename
    assert d['original_F_result'] == d['passive_G_result'] == native['result']
    assert native['result']['frames'] == 15299 and native['result']['failure'] == 'death'
    fatal, complete = d['fatal'], d['complete_end']
    assert int(fatal['y']) == int(complete['y']) == 112
    assert fatal['sourceFrame'] == '4' and fatal['attack'] == '0' and fatal['yf'] == '0'
    body = list(map(int, fatal['body'].split(':')))
    assert body == [113, 129, 127, 144] and body[1] == 112 + 17 and body[3] == 112 + 32
    scratch = list(map(int, fatal['R0R7'].split(':')))
    assert scratch == [3, 31, 6, 2, 116, 0, 122, 106]
    assert abs(112 - scratch[7]) == 6 < 8 and abs(scratch[4] - scratch[6]) == 6 < 8
    parts = complete['parts'].split(';')[0].split(':', 7)[7].split('/')
    centers = [tuple(map(int, item.split(':'))) for item in parts]
    assert len(centers) == 6 and [y for x, y in centers] == [100, 101, 103, 104, 106, 107]
    conservative_whole_container_bottom = max(y for x, y in centers) + 13
    assert conservative_whole_container_bottom == 120 < body[1]
    report = dict(status='PASS_ACTUAL_NATIVE_FIREBAR_BODY_BOX_DISCREPANCY_REVIEW',
        script_sha256=sha(__file__), source_review_sha256=sha(review),
        source_and_artifact_refs_rehashed=len(d['source_file_hashes']) + len(d['artifacts']),
        native_files_rehashed=len(native['raw_files']), all9_actual_CSVs_literal_F_G=True,
        actual_native_sampler=dict(playerY=112, pieceY=106, horizontal_distance=6, vertical_distance=6),
        actual_source_shaped_body=body, complete_actual_piece_centers=centers,
        conservative_render_container_bottom=120, body_top=129,
        conclusion='The native current-body box and every emitted piece container are vertically disjoint, but the legacy big-player PY sampler injures and changes direction. This is a definite current-native-body consumer inconsistency.',
        source_qualification='Original FireBar uses bitmap against Character.boundsRect. Here prior/current vertical position and normal15 height agree, so cached-display bounds do not close the gap. Full Flash/native birth/rotation/anchor timing and arbitrary pixel-positive parity remain unproved.',
        next_action='Private bounded normal EasyLink disjoint gate before ChgSDir, with genuine overlap and unsupported/edge/ABI/interrupt controls; preserve both existing ceiling behavior and Bill successor in eventual union.',
        root_scope='Receipt/source/geometry review, not another native executor run or repaired runtime admission.',
        source_runtime_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out))


if __name__ == '__main__':
    main()
