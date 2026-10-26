"""Preserve the completed, held BASIC matrix; never launch or adopt a ROM."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SOURCE = ARCHIVE / 'cv3-remaining-queue-native-basic-v3'
OUT = ROOT / 'docs/qa/checkpoints/2026-10-26/cv3-basic-native-held'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def main():
    ready_path = SOURCE / 'freeze-v1/readiness-source-only.json'
    native_path = SOURCE / 'native-freeze-v1/qualification-native.json'
    assert digest(ready_path) == '2cc9dc9d2aab9759e5d6223fb969bf9d5bc40114dc50cb6981ac4eeb6e319b00'
    assert digest(native_path) == '81c39fd576a61e007d937cb3e70d292cc6339fffa0312f4148eb164f170c96d5'
    ready, native = read(ready_path), read(native_path)
    assert native['native_launches'] == 26 and native['strict_cadence_passes'] == 12
    assert native['strict_cadence_failures'] == ['hard-ice']
    assert native['worker_released'] and not native['accepted']
    assert not OUT.exists(), OUT
    OUT.mkdir(parents=True)
    catalog = {}

    def copy(path, relative, expected=None):
        path = Path(path)
        actual = digest(path)
        if expected:
            assert actual == expected, path
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        assert digest(target) == actual
        catalog[target.relative_to(OUT).as_posix()] = dict(source=str(path), sha256=actual)

    copy(ready_path, 'readiness-source-only.json')
    copy(native_path, 'qualification-native.json')
    copy(SOURCE / 'native-freeze-v1/hard-ice-deadline.json', 'hard-ice-deadline.json')
    for name, expected in ready['source_receipts'].items():
        copy(SOURCE / name, 'source-receipts/' + name, expected)
    for name, expected in {**ready['frozen_tools'], **native['tools']}.items():
        copy(ROOT / name, 'frozen-tools/' + Path(name).name, expected)
    for case in native['cases']:
        name = case['name']
        copy(case['comparison']['path'], f'native-cases/{name}/comparison.json', case['comparison']['sha256'])
        for kind, game in case['game'].items():
            for field in ['proof', 'launch']:
                record = game[field]
                copy(record['path'], f'native-cases/{name}/{kind}-{field}.json', record['sha256'])
    env_record = native['environment']
    assert digest(env_record['path']) == env_record['sha256']
    env = read(env_record['path'])
    # The exact raw user settings and full environment packet stay external.
    # Only relevant conditions and hashes belong in this public repository.
    public = dict(external_environment=env_record,
                  current_settings_source_sha256=env['current_settings_source_sha256'],
                  historical_settings_sha256=env['historical_settings_sha256'],
                  conditions=env['conditions'],
                  user_settings_written=env['user_settings_written'],
                  all_fresh_pairs_use_current_settings=env['all_fresh_pairs_use_current_settings'],
                  raw_settings_published=False)
    (OUT / 'environment-public-review.json').write_text(json.dumps(public, indent=2) + '\n')
    for name in ['cv3-remaining-sfx-queue-basic-ready-2026-10-25.txt',
                 'cv3-remaining-sfx-queue-basic-native-2026-10-25.txt',
                 'cv3-remaining-sfx-queue-basic-environment-2026-10-25.txt']:
        copy(ROOT / 'docs/qa' / name, 'reports/' + name)
    review = dict(passed=False, accepted=False, production_adopted=False,
                  source_hardware_cells_passed=13, strict_cadence_cells_passed=12,
                  retained_failure='hard-ice: 140 updates/137 draws vs baseline 140/138',
                  root_independent_checks='654 actual native/batch/tool bindings and all13 cumulative draw-prefix comparisons verified before checkpoint.',
                  scope='BASIC only. Lifecycle, active DMC, priority, pause, death, scene and pressure remain required.',
                  recordings_and_raw_settings_retained_external=True,
                  copied_bindings=catalog)
    (OUT / 'root-review.json').write_text(json.dumps(review, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=str(OUT), copied_files=len(catalog), passed=False, accepted=False)))


if __name__ == '__main__':
    main()
