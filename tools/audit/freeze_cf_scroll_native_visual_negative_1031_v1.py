"""Keep passing scroll assertions separate from the failed native enemy art."""
from pathlib import Path
import hashlib
import json
import zipfile
from PIL import Image

R = Path(__file__).resolve().parents[2]
P = R / 'build/contra-force-scroll-native-1031-v1'
O = R / 'docs/qa/checkpoints/2026-10-31/cf-scroll-native-visual-negative-v1'
EXPECTED = '1cbbd1ccfb22614b206d2e6fe75c55795f31bd47c2bbeda127f0b1645baf9b7d'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    assert not O.exists()
    files = {Path(__file__), P / 'prepared.json',
             R / 'tools/audit/prepare_contra_force_scroll_native_1031_v1.py',
             R / 'tools/audit/check_contra_force_scroll_native_1031_v1.py',
             R / 'tools/reference/contra_force_scroll_native_1031_v1.lua',
             R / 'tools/audit/contra_force_native_enemy_pattern_diagnostic_1031_v1.py',
             R / 'build/contra-force-native-enemy-pattern-diagnostic-1031-v1/controls.json',
             R / 'build/contra-force-scroll-review-1031-v1/burns-enemy-review.png'}
    cases = []
    for name in ['burns', 'smith', 'iron']:
        folder = P / name
        ready, binding, result = [load(folder / path) for path in
                                 ['ready.json', 'capture/binding.json', 'capture/result.json']]
        for receipt in [ready, binding]:
            for path, digest in receipt['bindings'].items():
                assert sha(path) == digest, path
        assert binding['ready_sha256'] == sha(folder / 'ready.json')
        assert binding['exit_code'] == 0 and result['passed']
        assert result['ROM_sha256'] == binding['ROM_sha256'] == EXPECTED
        assert result['maximum_worldX'] >= 369 and result['maximum_camera'] >= 257
        assert result['terrain_changed'] and result['native_enemy_observations'] > 0
        assert result['jumped'] and result['landed'] and result['vector_guards'] > 1200
        pngs = list((folder / 'capture').glob('*.png'))
        assert {p.name for p in pngs} == {'selected.png', 'lives.png', 'jump.png', 'endpoint.png'}
        for path in pngs:
            with Image.open(path) as image:
                assert image.size == (256, 240)
                image.verify()
        cases.append(dict(name=name, automated_scroll_body_assertions_passed=True,
                          root_visual_acceptance=False, result=result,
                          root_reviewed_four_full_frames={path.name: sha(path) for path in pngs}))
        files.update(path for path in folder.rglob('*') if path.is_file())
    assert not (P / 'beans/capture').exists(), 'Known shared visual failure: fourth launch deliberately skipped'
    assert sum(path.stat().st_size for path in files) < 8 * 1024 * 1024
    assert all(path.is_relative_to(R) and path.suffix.lower() in
               ['.py', '.lua', '.json', '.csv', '.log', '.png'] for path in files)
    O.mkdir(parents=True)
    archive = O / 'native-visual-negative.zip'
    members = {}
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(files):
            relative = path.relative_to(R).as_posix()
            bundle.write(path, relative)
            members[relative] = sha(path)
    with zipfile.ZipFile(archive) as bundle:
        for path, digest in members.items():
            assert hashlib.sha256(bundle.read(path)).hexdigest() == digest
    facts = dict(status='NATIVE_VISUAL_REJECTED_NOT_INSTALLED', candidate=EXPECTED,
        passed=False, automated_scroll_cases=cases,
        source_diagnosis='Native Goomba uses OAM tilesA2/A4/palette3 in sprite window2. '
                         'Hardware window2 retained physical533 from portrait setup; actual native art needs17. '
                         'CF only updated its private body window0.',
        additional_UI_issue='Iron selection name row retains A OR outside the checked16-name-cell span.',
        review_derivative=dict(source='build/contra-force-scroll-native-1031-v1/burns/capture/jump.png',
             output='build/contra-force-scroll-review-1031-v1/burns-enemy-review.png',
             crop=[152, 168, 200, 216], size=[384, 384], resampling='nearest',
             purpose='Lossless pixel inspection; original screenshot unchanged.'),
        intentionally_unrun=['Beans1cbb after shared visual defect confirmed',
                            'Prepared Peach successor1cbb; installeda126 Peach was verified separately'],
        limits=['No full1-1, earned pickups, successful shooting or60Hz claim.',
                'Passing body/scroll assertions did not cover native enemy pattern authenticity.',
                'All three have heavy lag; Downloads stays on priora126 until a corrected source child passes.'],
        archive=dict(sha256=sha(archive), bytes=archive.stat().st_size, members=members))
    (O / 'review.json').write_text(json.dumps(facts, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(visual_passed=False, cases=len(cases), reviewed_PNGs=12,
                         archive_members=len(members), archive_bytes=archive.stat().st_size,
                         review_sha256=sha(O / 'review.json'))))


if __name__ == '__main__':
    main()
