"""Publish the source-built74-identity WIP after root's six native reviews."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import zipfile
from PIL import Image

R = Path(__file__).resolve().parents[2]
J = R / 'build/contra-force-world-roles-1031-v2/joint'
S = R / 'docs/qa/checkpoints/2026-10-31/contra-force-jump-contact-source-v1/handoff.json'
LAYOUT = R / 'docs/qa/checkpoints/2026-10-31/contra-force-lives-layout-source-v1/handoff.json'
PARENT = R / 'docs/qa/checkpoints/2026-10-31/bt-cf-coherent-source-v1/handoff.json'
D = R / 'docs/qa/checkpoints/2026-10-31/ready74-bt-cf-native-v1'
BT = R / 'build/ready74-final-bt-native-1031-v1'
OLD = '01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'
NEW = 'a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
SOURCE = '072c8e8855ff60b0524d9f62a2e7e2e3e9c762660f3e9bff0c96031f8ba86359'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def bound(data):
    for name, expected in data['bindings'].items():
        assert sha(name) == expected, name


def save(path, data):
    assert not path.exists(), path
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cf-native', type=Path, required=True)
    args = parser.parse_args()
    cf = args.cf_native.resolve()
    assert cf.is_relative_to(R / 'build')
    assert not D.exists()
    assert sha(S) == SOURCE
    source = read(S)
    bound(source)
    assert source['candidate'] == NEW and source['source_ready'] == 74
    assert source['menu_profiles'] == 86 and sha(J / 'candidate.nes') == NEW
    assert len(source['bindings']) == 484
    assert sha(PARENT) == source['inherited_parent_handoffSHA']
    parent = read(PARENT)
    bound(parent)
    source_members = 0
    for handoff in [S, LAYOUT, PARENT]:
        data = read(handoff)
        bound(data)
        archive = next(p for p in handoff.parent.glob('*.zip'))
        with zipfile.ZipFile(archive) as z:
            assert len(z.infolist()) == data['archive_members']
            source_members += len(z.infolist())
            for item in z.infolist():
                path = (R / item.filename).resolve()
                assert path.is_relative_to(R) and not item.is_dir()
                assert str(path) in data['bindings'] and z.read(item) == path.read_bytes()
    assert source_members == 139
    menu_file = R / 'build/bt-cf-coherent-controls-1031-v1/menu-final-controls.json'
    menu = read(menu_file)
    bound(menu)
    assert menu['passed'] and menu['candidate'] == source['parent'] == parent['candidate']
    assert source['all_nonCF_bytes_and_public_PCs_preserved'] and source['source_byte_oracle_equal']
    assert menu['result']['menu_profiles'] == 86 and menu['result']['ready'] == 74
    prepared = read(cf / 'prepared.json')
    bound(prepared)
    assert prepared['source_candidate'] == NEW
    assert prepared['source_handoff_sha256'] == SOURCE
    files = {Path(__file__), S, LAYOUT, PARENT, menu_file, cf / 'prepared.json'}
    files.update(Path(n) for n in prepared['bindings']
                 if Path(n).is_relative_to(R / 'tools') and Path(n).suffix.lower() in ['.py', '.lua'])
    native = []
    cases = [(name, BT / name, 'Battletoads') for name in ['rash', 'zitz']]
    cases += [(name, cf / name, 'Contra Force') for name in ['burns', 'smith', 'iron', 'beans']]
    for name, folder, family in cases:
        ready = read(folder / 'ready.json')
        binding = read(folder / 'capture/binding.json')
        result = read(folder / 'capture/result.json')
        bound(ready)
        bound(binding)
        assert binding['ready_sha256'] == sha(folder / 'ready.json')
        assert binding['exit_code'] == 0 and result['passed'], name
        assert binding['ROM_sha256'] == result['ROM_sha256'] == NEW
        assert 360 <= result['gameplay_frames'] <= 364 and result['jumped'] and result['landed']
        assert result['vector_guards'] >= 60 and result['timing']['nmi'] == result['gameplay_frames']
        assert result['main_updates'] >= 60 and result['walked'] >= 16
        if family == 'Battletoads':
            assert result['main_updates'] == result['source_Main'] == result['source_movement']
            assert result['gameplay_body_pixel_checks'] >= 20 and result['attack_events'] > 0
            assert result['body_P0_source_exact']
        else:
            assert result['main_updates'] == result['source_Main'] == result['source_body_steps']
            assert result['body_checks'] >= 20 and result['source_construct'] == 1
            assert result['source_projectile_records'] > 0
            assert result['ground_projectile_observations'] > 0 and result['air_projectile_observations'] > 0
            assert result['epochs'] > 0 and result['auth_A2_entries'] > 0
            standing, airborne = result['standing_DMA'], result['rendered']['jump']
            for coordinate in ['sourceY', 'anchorY', 'bottom']:
                assert airborne[coordinate] <= standing[coordinate] - 12, (name, coordinate)
            assert airborne['opaque'] > 0
        pngs = sorted((folder / 'capture').glob('*.png'))
        middle = 'entered.png' if family == 'Battletoads' else 'jump.png'
        assert {p.name for p in pngs} == {'selected.png', 'lives.png', middle, 'endpoint.png'}
        native.append(dict(identity=name, family=family, result=result,
                           root_reviewed_full_frame_PNGs={p.name: sha(p) for p in pngs},
                           result_sha256=sha(folder / 'capture/result.json')))
        files.update(p for p in folder.rglob('*') if p.is_file())
    # Resolve an independent visual-review concern without changing correct code:
    # every gameplay header must match only its own verified lives-screen name.
    def name_mask(path):
        im = Image.open(path).convert('RGB')
        return bytes(int(all(c > 230 for c in im.getpixel((x, y))))
                     for y in range(16, 24) for x in range(24, 88))
    names = ['burns', 'smith', 'iron', 'beans']
    masks = {name: name_mask(cf / name / 'capture/lives.png') for name in names}
    assert len(set(masks.values())) == 4
    for name in names:
        for frame in ['jump.png', 'endpoint.png']:
            observed = name_mask(cf / name / 'capture' / frame)
            assert [other for other, mask in masks.items() if mask == observed] == [name]
    # All evidence is bounded; no ROMs, emulator binaries or raw video enter Git.
    assert all(p.suffix.lower() in ['.py', '.json', '.lua', '.csv', '.png', '.log'] for p in files)
    assert sum(p.stat().st_size for p in files) < 8 * 1024 * 1024
    downloads = Path.home() / 'Downloads'
    latest = downloads / 'SMB-Crossover-Latest-WIP-MMC5.nes'
    version = downloads / 'SMB-Crossover-2026-10-31-Ready74-Battletoads-ContraForce-MMC5.nes'
    backup = downloads / 'SMB-Crossover-Before-Ready74-01a40d40-MMC5.nes'
    temp = downloads / 'SMB-Crossover-Latest-WIP-MMC5.pending'
    assert sha(latest) == OLD
    assert not version.exists() and not backup.exists() and not temp.exists()
    D.mkdir(parents=True)
    out = D / 'native-and-menu-results.zip'
    with zipfile.ZipFile(out, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(files):
            z.write(path, path.relative_to(R).as_posix())
    with zipfile.ZipFile(out) as z:
        for path in files:
            assert z.read(path.relative_to(R).as_posix()) == path.read_bytes()
    limits = [
        'Bounded native menu, lives, walking, jump/landing and attack checks; no full1-1/every-powerup/campaign completion.',
        'Lag and sprite pressure remain. Battletoads completed240 Main updates in360 physical frames, with240 lag NMIs.',
        'Complete donor special moves, audio and all older character issues remain unfinished; these are playable WIP unlocks.',
        'Required Final Fantasy outlines and the reported White Mage damage issue remain outstanding.',
    ]
    manifest = dict(candidate=NEW, passed=True, source_handoff_sha256=SOURCE,
                    native=native, actual_menu=menu['result'], limits=limits,
                    CF_all_eight_gameplay_HUD_names_exact_to_own_lives=True,
                    archive_sha256=sha(out), archive_members=len(files),
                    files={p.relative_to(R).as_posix(): sha(p) for p in sorted(files)})
    save(D / 'manifest.json', manifest)
    (D / 'README.md').write_text(
        '# Ready74 bounded native checks\n\n'
        'Root rehashed all484 final source bindings and all139 source ZIP members, then ran '
        'Rash, Zitz, Burns, Smith, Iron and Beans on exact source-built a12661c1 with the normal '
        'sprite limit and no RAM writes. Root reviewed all24 full-frame screenshots. '
        'Each packet uses four PNGs and360 to364 physical gameplay frames (finish the current Main), with64 files/512MiB '
        'and a90-second emulator deadline. Source and native inputs are frozen in the ZIP.\n\n'
        + '\n\n'.join(limits) + '\n', encoding='utf-8', newline='\n')
    shutil.copy2(latest, backup)
    assert sha(backup) == OLD
    shutil.copy2(J / 'candidate.nes', version)
    assert sha(version) == NEW
    shutil.copy2(version, temp)
    assert sha(temp) == NEW
    os.replace(temp, latest)
    assert sha(latest) == NEW
    receipt = dict(date='2026-10-31', status='INSTALLED_READY74_BT_CF_PLAYABLE_WIP',
                   passed=True, installed=True, ROM_sha256=NEW, previous_sha256=OLD,
                   latest=str(latest), versioned=str(version), backup=str(backup),
                   playable=74, individual_identities=86, pending_individual_identities=12,
                   menu_slots=32, menu_rows=4, source_handoff_sha256=SOURCE,
                   verified_source_bindings=484, verified_source_archive_members=139,
                   native_manifest_sha256=sha(D / 'manifest.json'), native_checks=native,
                   controls='Battletoads: Select cycles Rash/Zitz. Contra Force: Select cycles Burns/Smith/Iron/Beans.',
                   limits=limits, all_characters_1_1_and_every_powerup_complete=False, goal_complete=False)
    save(R / 'docs/qa/functional-roster-ready74-bt-cf-2026-10-31.json', receipt)
    print(json.dumps(dict(installed=str(latest), versioned=str(version), candidate=NEW,
                          playable=74, individual_identities=86, archive_bytes=out.stat().st_size,
                          goal_complete=False)))


if __name__ == '__main__':
    main()
