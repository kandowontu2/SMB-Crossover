"""Publish the bounded, root-reviewed CF camera/enemy-graphics successor."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
J = R / 'build/contra-force-world-chr-publisher-1031-v1/joint'
S = R / 'docs/qa/checkpoints/2026-10-31/contra-force-world-chr-source-v1/handoff.json'
N = R / 'build/contra-force-scroll-native-1031-v4'
P = R / 'build/ready74-cf-world-chr-peach-native-1031-v1/peach'
D = R / 'docs/qa/checkpoints/2026-10-31/ready74-cf-scroll-chr-native-v1'
OLD = 'a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
NEW = 'a4410264ffccc7ce44e3b5ead1da639428cfa0594c94b2f63fa99fb4feab5b38'
SOURCE = '907a1e86aac05423eb560cf767965ecf9919ec7a6e043aff7f8ddf9c0bd06d02'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def bound(data):
    for name, digest in data['bindings'].items():
        assert sha(name) == digest, name


def save(path, data):
    assert not path.exists(), path
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    assert not D.exists()
    assert sha(J / 'candidate.nes') == NEW and sha(S) == SOURCE
    source = read(S)
    bound(source)
    assert len(source['bindings']) == 638 and source['candidate'] == NEW
    assert source['source_ready74'] and source['menu_profiles'] == 86
    assert source['all_nonCF_ROM_CHR_header_menu_BT_exact']
    assert source['all_native_and_private_entry_PCs_exact']
    members = read(S.parent / 'source-members.json')
    with zipfile.ZipFile(S.parent / 'source-only.zip') as z:
        assert set(z.namelist()) == set(members) and len(members) == 45
        for name, digest in members.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest, name
    prepared = read(N / 'prepared.json')
    bound(prepared)
    assert prepared['source_candidate'] == NEW
    assert prepared['source_handoff_sha256'] == SOURCE
    assert prepared['observer_binding_sha256'] == sha(N / 'source-observer-binding.json')
    files = {Path(__file__), N / 'prepared.json', N / 'source-observer-binding.json'}
    files.update(Path(name) for name in prepared['bindings']
                 if Path(name).is_relative_to(R / 'tools')
                 and Path(name).suffix.lower() in ['.py', '.lua'])
    results = []
    cases = [(name, N / name) for name in ['burns', 'smith', 'iron', 'beans']]
    cases.append(('Peach', P))
    for name, folder in cases:
        ready = read(folder / 'ready.json')
        binding = read(folder / 'capture/binding.json')
        result = read(folder / 'capture/result.json')
        bound(ready)
        bound(binding)
        assert binding['ready_sha256'] == sha(folder / 'ready.json')
        assert binding['exit_code'] == 0 and result['passed'], name
        assert ready['ROM_sha256'] == binding['ROM_sha256'] == result['ROM_sha256'] == NEW
        assert result['jumped'] and result['landed'] and result['walked'] > 16
        assert result['timing']['nmi'] == result['gameplay_frames']
        if name == 'Peach':
            assert ready['source_handoff_sha256'] == SOURCE
            assert result['main_updates'] == result['source_Main'] == result['source_movement'] == 180
            assert result['body_P0_source_exact'] and result['vector_guards'] == 360
            assert result['actual_UI_DMA_checks']['selected'] > 0
            assert result['actual_UI_DMA_checks']['lives'] > 0
            assert result['rendered_UI']['selected']['pixels'] > 0
            assert result['rendered_UI']['lives']['pixels'] > 0
            middle = 'entered.png'
        else:
            assert sha(ready['source_handoff']) == SOURCE
            assert result['main_updates'] == result['source_Main'] == result['source_body_steps']
            assert result['main_updates'] >= 200 and result['source_construct'] == 1
            assert result['maximum_worldX'] >= 369 and result['maximum_camera'] >= 257
            assert result['terrain_changed'] and result['actual_parser_calls'] > 0
            assert result['native_enemy_DMAS'] >= 4 and result['native_enemy_pixel_frames'] >= 4
            assert result['native_enemy_last_opaque'] > 0 and result['vector_guards'] >= 1200
            assert result['actual_DMA']['selected'] > 0 and result['actual_DMA']['lives'] > 0
            assert result['body_checks'] > 20 and result['rendered']['jump']['opaque'] > 0
            assert result['rendered']['jump']['bottom'] < result['standing_DMA']['bottom'] - 12
            middle = 'jump.png'
        pngs = sorted((folder / 'capture').glob('*.png'))
        assert {p.name for p in pngs} == {'selected.png', 'lives.png', middle, 'endpoint.png'}
        assert len(list(folder.rglob('*'))) <= 64
        assert sum(p.stat().st_size for p in folder.rglob('*') if p.is_file()) < 512 * 1024 * 1024
        results.append(dict(identity=name, result=result,
                            root_reviewed_full_frame_PNGs={p.name: sha(p) for p in pngs},
                            result_sha256=sha(folder / 'capture/result.json')))
        files.update(p for p in folder.rglob('*') if p.is_file())
    # This archive records actual successor runs only. Earlier BT/native attack
    # results stay attached to their old ROM hash; source byte equality is separate.
    assert all(p.suffix.lower() in ['.py', '.json', '.lua', '.csv', '.png', '.log'] for p in files)
    assert sum(p.stat().st_size for p in files) < 16 * 1024 * 1024
    downloads = Path.home() / 'Downloads'
    latest = downloads / 'SMB-Crossover-Latest-WIP-MMC5.nes'
    version = downloads / 'SMB-Crossover-2026-10-31-Ready74-CF-Scroll-Graphics-MMC5.nes'
    backup = downloads / 'SMB-Crossover-Before-CF-Scroll-a12661c1-MMC5.nes'
    temporary = downloads / 'SMB-Crossover-Latest-WIP-MMC5.pending'
    assert sha(latest) == OLD
    assert not version.exists() and not backup.exists() and not temporary.exists()
    D.mkdir(parents=True)
    archive = D / 'native-results.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(files):
            z.write(path, path.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for path in files:
            assert z.read(path.relative_to(R).as_posix()) == path.read_bytes()
    limits = [
        'Controller-only cold menu/lives and bounded opening movement on exact a441; no full1-1 or every-powerup completion.',
        'Contra Force ground-shot/native enemy contact still needs repair. These advancing-scroll cases avoid enemies by jumping. They do not test projectile hits or powerup collections.',
        'Substantial lag remains; measured Main updates, physical frames and lag NMIs are in each result. No60Hz or hardware claim.',
        'This narrow camera/CHR repair does not alter shared menu code or establish that every menu transition is polished.',
        'Thomas, Shinobi, WWF, remaining pending characters and newly requested alternates remain unfinished. The roster count stays74/86.',
        'Older roster issues, full special moves/audio, required FF outlines and White Mage damage remain pending.',
    ]
    manifest = dict(passed=True, candidate=NEW, source_handoff_sha256=SOURCE,
                    verified_source_bindings=638, verified_source_archive_members=45,
                    exact_candidate_native=results, limits=limits,
                    archive_sha256=sha(archive), archive_members=len(files),
                    files={p.relative_to(R).as_posix(): sha(p) for p in sorted(files)})
    save(D / 'manifest.json', manifest)
    (D / 'README.md').write_text(
        '# Ready74 Contra Force camera and enemy graphics verification\n\n'
        'Root verified638 source bindings and45 archived source members, then ran Burns, '
        'Smith, Iron, Beans and Peach on exact a4410264 with the normal eight-sprite limit, '
        'cold all-zero power-on and controller input only. Root reviewed all20 full-frame PNGs. '
        'Each capture is capped at four PNGs,64 files and512MiB; there are no videos. '
        'The CF cases cross worldX369/camera257 and inspect genuine native enemy patterns, '
        'actual DMA and rendered enemy pixels. Peach retains her source palette and body.\n\n'
        + '\n\n'.join(limits) + '\n', encoding='utf-8', newline='\n')
    shutil.copy2(latest, backup)
    assert sha(backup) == OLD
    shutil.copy2(J / 'candidate.nes', version)
    assert sha(version) == NEW
    shutil.copy2(version, temporary)
    assert sha(temporary) == NEW
    os.replace(temporary, latest)
    assert sha(latest) == NEW
    receipt = dict(date='2026-10-31', passed=True, installed=True,
                   status='INSTALLED_READY74_CF_CAMERA_AND_NATIVE_ENEMY_CHR_WIP',
                   ROM_sha256=NEW, previous_sha256=OLD,
                   latest=str(latest), versioned=str(version), backup=str(backup),
                   playable=74, individual_identities=86, pending_individual_identities=12,
                   menu_slots=32, menu_rows=4, source_handoff_sha256=SOURCE,
                   native_manifest_sha256=sha(D / 'manifest.json'), limits=limits,
                   all_characters_1_1_and_every_powerup_complete=False, goal_complete=False)
    save(R / 'docs/qa/functional-roster-ready74-cf-scroll-chr-2026-10-31.json', receipt)
    print(json.dumps(dict(installed=str(latest), versioned=str(version), candidate=NEW,
                          playable=74, archive_bytes=archive.stat().st_size, goal_complete=False)))


if __name__ == '__main__':
    main()
