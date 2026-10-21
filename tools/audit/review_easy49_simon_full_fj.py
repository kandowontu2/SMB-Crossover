"""Independently verify the frozen C Simon complete route and nine exact audit streams."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
C = V / 'agent-lsr-victory-repair-c'
H = C / 'route-t'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-simon-full-review-fj.json'
    assert not out.exists()
    pins = {'freeze.json': '7b15d9a8827235aea25a79079dac20633608c22b571110576a70986c406a0e40',
        'route-handoff.json': '133fd94b35f10b950462de50509a9d921799789c4bbe059d0a10a25c31afaea1',
        'fixed-review.json': 'f78d5e346dcf8985cbb07039eb77b55148a7ef306a8d005643a041faf44ab42a'}
    for n, h in pins.items():
        assert sha(H / n) == h, n
    frozen = json.loads((H / 'freeze.json').read_text())
    for n, row in frozen['files'].items():
        assert sha(H / n) == row['sha256'] and (H / n).stat().st_size == row['bytes']
    h = json.loads((H / 'route-handoff.json').read_text())
    r = json.loads((H / 'fixed-review.json').read_text())
    assert h['character'] == 5 and h['mode'] == 0 and h['mapper'] == 'mmc3'
    result = h['result']
    assert result['cleared'] and result['all_six_stages'] and result['deaths'] == 0
    assert result['frames'] == 23853 and result['polls'] == 23852 and result['stage_entries']['1-2'] == 23829
    a, b = (Path(h[n]) for n in ('candidate_directory', 'fixed_directory'))
    assert a.is_relative_to(R) and b.is_relative_to(R)
    assert len(h['full_nine_csv_literal']) == 9
    for n, row in h['full_nine_csv_literal'].items():
        assert (a / n).read_bytes() == (b / n).read_bytes()
        assert sha(a / n) == row['before_sha256'] == row['after_sha256']
        assert (b / n).stat().st_size == row['bytes'] and row['literal']
    assert sha(a / 'inputs.csv') == 'e9fcce74d5ea702e1c3fe116b95c35a789119fd45e62a1d018e9607520929e15'
    m = json.loads((b / 'manifest.json').read_text())
    assert m['verified_through_2_2'] and m['full_frame_audit'] and not m['memory_or_register_writes']
    source = json.loads((C / 'build-report.json').read_text())['source_hashes']
    ec = json.loads((R / 'build/checkpoints/roster-audit-v49-victory-ec/manifest.json').read_text())
    assert source == ec['source_hashes'] and len(source) == 441
    assert all(sha(C / 'source' / n) == value for n, value in source.items())
    for artifact in r['artifacts'].values():
        assert sha(artifact['path']) == artifact['sha256']
    with (b / 'trace.csv').open(newline='') as stream:
        trace = list(csv.DictReader(stream))
    tail = [row for row in trace if int(row['frame']) >= 23829]
    assert len(tail) == 25 and int(tail[0]['x']) == 40 and int(tail[-1]['x']) == 70
    report = dict(status='PASS_FROZEN_HISTORICAL_C_SIMON_FULL_ROUTE_NINE_STREAMS_LITERAL',
        script_sha256=sha(__file__), source_count=441, actual_ROM_sha256=h['rom_sha256'],
        input_sha256=sha(a / 'inputs.csv'), result=result, exact_nine_audit_streams=h['full_nine_csv_literal'],
        independently_rehashed_source_and8_artifacts=True,
        real_next_stage_controls=dict(frames=25, x_from=40, x_to=70),
        pins={n: value for n, value in pins.items()}, limits=h['limits'],
        no_final_runtime_or_media_claim=True, main_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out))


if __name__ == '__main__':
    main()
