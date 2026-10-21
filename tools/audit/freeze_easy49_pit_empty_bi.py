"""Freeze the measured Pit optimization and its bounded native evidence."""
from pathlib import Path
import hashlib, json, shutil, zipfile

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-pit-empty-be'
P = V / 'root49-easy-advanced-union-ap'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    target = H / 'freeze-bi.json'
    assert not target.exists()
    pins = {
        H / 'report.json': 'bb45ec3ead04515ad6eb56a8164ca39590d0f2ec72e29f64f69a67f4da6e55bd',
        H / 'native/checks-bf/report.json': '2f38cba3582b585f0d94d59208d89d91e1fe3d5a185e24d5302848d3564d5ff0',
        H / 'ordinary-pit-profile-bg/report.json': 'cfd6556ea20c0f588b2cd4c86567eff8aea20b3fa6c0ee88686c8566ae3c1495',
        H / 'native/checks-bh/report.json': '76ec3577e658fbd58ddfdd8975ea1ff549fb0f899f5c0dc6f454de7bf4cc5825',
        P / 'ordinary-pit-profile-bd/report.json': 'b07de012432e63daa207d3258e7698f2f0d2e804af2728927c1946d38f2a9ba7',
        P / 'report.json': 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e',
    }
    for path, expected in pins.items():
        assert sha(path) == expected, path
    build = json.loads((H / 'report.json').read_text())
    parent = json.loads((P / 'report.json').read_text())
    assert all(sha(H / 'source' / path) == digest for path, digest in build['source_hashes'].items())
    assert all(sha(P / 'source' / path) == digest for path, digest in parent['source_hashes'].items())
    assert [name for name in build['source_hashes'] if build['source_hashes'][name] != parent['source_hashes'][name]] == ['src/megaman_weapons.s']
    before = json.loads((P / 'ordinary-pit-profile-bd/report.json').read_text())
    after = json.loads((H / 'ordinary-pit-profile-bg/report.json').read_text())
    gains = []
    for row in after['rows']:
        prior = next(x for x in before['rows'] if x['image'] == 'AP' and x['mapper'] == row['mapper'])
        gains.append(dict(mapper=row['mapper'], physical_frames=3000,
                          weapon_mean_cycles_before=prior['routines']['ExpandedWeapons']['mean'],
                          weapon_mean_cycles_after=row['routines']['ExpandedWeapons']['mean'],
                          terrain_mean_cycles_before=prior['routines']['Blocks']['mean'],
                          terrain_mean_cycles_after=row['routines']['Blocks']['mean'],
                          flagged_lag_frames_before=prior['frames_flagged_lagNmi'],
                          flagged_lag_frames_after=row['frames_flagged_lagNmi']))
    overlay = H / 'frozen-bi/src/megaman_weapons.s'
    overlay.parent.mkdir(parents=True)
    shutil.copyfile(H / 'source/src/megaman_weapons.s', overlay)
    archive = H / 'frozen-bi/overlay.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zipped:
        zipped.write(overlay, 'src/megaman_weapons.s')
    files = list(pins) + [overlay, archive, Path(__file__), R / 'tools/audit/build_easy49_pit_empty_be.py',
                         R / 'tools/audit/pit49_terrain_equivalence_core.lua', R / 'tools/audit/check_easy49_pit_empty_bf.py',
                         R / 'tools/audit/ordinary49_attack_profile_core.lua', R / 'tools/audit/profile_easy49_ordinary_pit_bd.py',
                         R / 'tools/audit/profile_easy49_ordinary_pit_bg.py', R / 'tools/audit/check_easy49_pit_empty_bh.py']
    for folder in [H / 'native/checks-bf', H / 'native/checks-bh', H / 'ordinary-pit-profile-bg']:
        files.extend(path for path in folder.rglob('*') if path.is_file())
    files = sorted(set(files))
    report = dict(status='FROZEN_BOUNDED_PIT_TERRAIN_OPTIMIZATION_FOR_INTEGRATION',
                  parent_report_sha256=sha(P / 'report.json'), source_changes=build['source_changes'],
                  archive=dict(path=archive.relative_to(R).as_posix(), sha256=sha(archive)),
                  overlay=dict(path=overlay.relative_to(R).as_posix(), sha256=sha(overlay)),
                  exact_compiled_delta=dict(GUEST=18), added_RAM_bytes=0,
                  config_CHR_header_audio_size_unchanged=True,
                  behavior='Only selected Pit with native bullet types26..28 uses the existing symmetric distinct-cell terrain path. Solid-cell dispatch order remains original.',
                  native_equivalence=dict(paired_cases_per_mapper=5520, mappers=2, differing_cases=0,
                                          scope='Modes0/1,3tiers,2facings,all16x16within-tile offsets,page/Yseams,terrain/masonry/question/transparent IDs,partialhealth andopposite-corner order; map/health/solid/coin/time-map hashes,playerQ16/reward/enemy/shot/audio observables.'),
                  regressions='All20 foreign weapon/Samus bomb groups pass on actual BE, including222 bombs/map and6 controller-created bombs/map.',
                  ordinary_profile=gains,
                  qualifications=[
                      'Native seeded paired observable equivalence is not full-RAM, CPU-flag, stack-scratch or independent source-parity certification.',
                      'Controlled solid-contact cases can cost up to555additional foreground cycles. The main saving is repeated empty-air lookup work; that tradeoff remains explicit.',
                      'The3000-frame ordinary runs use the same input stream but timing changes cause different subsequent world states. Inclusive routine samples must not be summed; local lag counts are not a full-game percentage guarantee.',
                      'Full integrated routes, every weapon/upgrade and final recordings remain required. AP/Y movies do not certify BE.',
                      'Root/public U source and artifacts are not replaced by this private freeze.'],
                  files=[dict(path=path.relative_to(R).as_posix(), sha256=sha(path), bytes=path.stat().st_size) for path in files],
                  accepted_release=False, goal_complete=False)
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(target.name, sha(target), json.dumps(gains), flush=True)


if __name__ == '__main__':
    main()
