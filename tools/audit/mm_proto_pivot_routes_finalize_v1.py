"""Freeze the completed bounded 0a Mega/Proto route results without another launch."""
from pathlib import Path
import argparse
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D/'mega-proto-pivot-routes0a-static-v1'
SHA = '0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: list(csv.DictReader(Path(p).open()))
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    ready = json.loads((B/'readiness.json').read_text())
    dependencies = ready['bindings']
    for name, expected in dependencies.items():
        assert sha(name) == expected, name
    native = B/'native'
    aggregate = json.loads((native/'proof.json').read_text())
    assert aggregate['passed'] and aggregate['complete'] and aggregate['ROM_sha256'] == SHA
    assert json.loads((B/'execution.json').read_text())['native_workers_released']
    rows = []
    catalog_paths = {B/'readiness.json', B/'launch.json', B/'execution.json', native/'proof.json'}
    selected = set()
    for case in ['megaman-easy', 'proto-easy']:
        discovery = native/case
        direct = native/(case+'-direct')
        review = D/'mega-proto-pivot-routes0a-review-v1'/case
        proof = json.loads((direct/'proof.json').read_text())
        reviewed = json.loads((review/'proof.json').read_text())
        assert proof['passed'] and proof['ROM_sha256'] == SHA
        assert proof['result']['cleared'] and proof['result']['deaths'] == 0
        assert reviewed['actual_numeric_mode'] == 0
        assert all(z['exact'] for name, z in reviewed['comparisons'].items() if name != 'events.csv')
        assert not reviewed['comparisons']['events.csv']['exact']
        assert reviewed['comparisons']['events.csv']['gameplay_suffix_exact']
        index = read(direct/'direct-frame-index.csv')
        assert len(index) == proof['direct_frames']
        assert [int(z['ppuFrame']) for z in index] == list(range(200, proof['result']['frames']))
        assert sha(direct/'direct-frame-index.csv') == proof['frame_index_sha256']
        assert sha(proof['raw_lossless_archive']['path']) == proof['raw_lossless_archive']['sha256']
        for z in json.loads((review/'selected-frames.json').read_text()):
            assert sha(z['path']) == z['sha256']
            selected.add((case, z['frame']))
        rows.append(dict(case=case, result=proof['result'], actual_numeric_mode=0,
                         direct_PPU_frames=proof['direct_frames'], CHR_commit=proof['body_chr'],
                         completed_loop=reviewed['completed_loop'],
                         literal_gameplay_suffix_exact=True, complete_events_file_exact=False,
                         raw_lossless_archive=proof['raw_lossless_archive']))
        catalog_paths.update(z for parent in [discovery, direct, review] for z in parent.iterdir() if z.is_file())
    for version in [1, 2]:
        samples = D/f'mega-proto-pivot-routes0a-samples-v{version}'
        z = json.loads((samples/'selected-frames.json').read_text())
        for item in z['frames']:
            assert sha(item['source']) == item['sha256']
            selected.add((item['case'], item['frame']))
        catalog_paths.update(samples.iterdir())
    report = R/'docs/qa/mm-proto-pivot-routes-native-2026-10-26.txt'
    tools = [R/'tools/audit'/name for name in [
        'mm_proto_pivot_routes_static_prepare_v1.py', 'mm_proto_pivot_routes_static_controls_v1.py',
        'mm_proto_pivot_routes_static_freeze_v1.py', 'mm_proto_pivot_routes_samples_v1.py',
        'mm_proto_pivot_routes_samples_v2.py', 'mm_proto_pivot_routes_finalize_v1.py']]
    catalog_paths.update([report, R/'docs/qa/mm-proto-pivot-routes-static-2026-10-26.txt', *tools])
    catalog = {str(x): dict(sha256=sha(x), bytes=x.stat().st_size) for x in sorted(catalog_paths)}
    put(a.output/'catalog.json', catalog)
    put(a.output/'review-files.json', dict(owned_tools=[str(x) for x in tools],
        owned_reports=[str(report), str(R/'docs/qa/mm-proto-pivot-routes-static-2026-10-26.txt')],
        actual_selected_sheets=[str(x) for x in sorted(catalog_paths) if x.suffix == '.png' and 'actual-PPU' in x.name],
        no_git_mutation=True, large_raw_payloads_external_only=True))
    put(a.output/'proof.json', dict(passed=True, native_route_pass=True, graphics_complete=False,
        adopted=False, new_native_launches=0, total_granted_launches_completed=4,
        native_worker_released=True, ROM_sha256=SHA, preparation_bindings_checked=len(dependencies),
        catalog_files=len(catalog), catalog_sha256=sha(a.output/'catalog.json'),
        review_files_sha256=sha(a.output/'review-files.json'), rows=rows,
        selected_unique_whole_frames=len(selected),
        ROOT_visual_review='ROOT reported independent review of 42 original selected wholeframes plus adjacent1938..1953 and both20-frame first-block/rise sheets:98 placements. No scenery corruption identified in that sample; real head-only1941..1943 recovers1944.',
        residual='Actual head-only Mega1941..1943. Fairer construction order is incomplete and changing live counts/publication can still omit body or shots.',
        limits='Selected manual visual review only. All saved PNG RGB/lossless roundtrip is a capture integrity result, not manual review of every frame. Original full event-file mismatch remains, literal active-gameplay suffix and other10CSV files exact. No all-weapons, everyitem, audible SFX, per-live-slot fairness, full256DMA/NMI/SP/SMC long-route oracle, or matched performance claim. V1 later767sheet was not the first bump; corrected initial windows are separate v2 outputs.'))
    print(json.dumps(dict(output=str(a.output), proof_sha256=sha(a.output/'proof.json'),
                          catalog_files=len(catalog), selected_unique_whole_frames=len(selected)), indent=2))


if __name__ == '__main__':
    main()
