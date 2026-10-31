"""Verify eight bounded native checks, retain failures, and install the WIP.

Does not change frozen source handoffs or call a bounded smoke a level clear.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'docs/qa/checkpoints/2026-10-30/ready62-native-unlocks'
RECEIPT = R / 'docs/qa/functional-roster-ready62-2026-10-30.json'
ROM_SHA = 'dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7'
SOURCE_SHA = 'fae1ec38db9525a645a8907fd92608978de15f0f7cf4b12088cee0e0f0393a1c'
OLD_SHA = '44c92ad7f75f74d5d4712a5bb30fb057b6d8adda54983ca149c4b7d03492ff34'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def write(p, value):
    assert not p.exists(), p
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def verify_bindings(d):
    b = d.get('bindings', {})
    assert isinstance(b, dict)
    for p, s in b.items():
        assert sha(p) == s, p
    return len(b)


def main():
    assert not O.exists() and not RECEIPT.exists()
    source = R / 'build/coherent62-lives-fixes-v1/handoff.json'
    assert sha(source) == SOURCE_SHA
    h = read(source)
    assert h['source'] is True and h['candidate'] == ROM_SHA and h['ready'] == 62
    source_bindings = verify_bindings(h)
    assert source_bindings == 652
    rom = Path(h['joint']) / 'candidate.nes'
    assert sha(rom) == ROM_SHA
    source_archives = []
    for name, expected in [
        ('arthur-goku-smb2-native-palette-source', 670),
        ('ff-lives-only-body-palette', 569),
        ('smb2-late-lives-palette-source', 85),
        ('coherent62-both-lives-fixes', 580),
    ]:
        p = O.parent / name / 'source-only.zip'
        count = 0
        with zipfile.ZipFile(p) as z:
            assert len(set(z.namelist())) == len(z.namelist()) == expected
            for n in z.namelist():
                f = (R / n).resolve()
                assert f.is_relative_to(R) and f.is_file(), n
                assert z.read(n) == f.read_bytes(), n
                count += 1
        source_archives.append(dict(path=str(p.relative_to(R)), sha256=sha(p), members=count))

    smb2 = R / 'build/ready62-smb2-final-native-1030-v1'
    ff = R / 'build/ready62-ff-final-native-1030-v1'
    assert sha(smb2 / 'prepared.json') == '5e2f6d1bd437d640448947daf696ee34e9b2e4bb77ff980e774967ba55af67ab'
    assert sha(ff / 'prepared.json') == 'c88774560b59bb16a88bf5cf0a7626a1d932c48076be9f60f128552d9ee3c817'
    verify_bindings(read(ff / 'prepared.json'))
    outcomes = []
    paths = set()
    allowed = {'.json', '.jsonl', '.lua', '.py', '.diff', '.csv', '.log', '.txt', '.png', '.nesppuv1'}

    def collect(folder):
        files = [p for p in folder.rglob('*') if p.is_file()]
        assert len(files) <= 160, folder
        assert sum(p.stat().st_size for p in files) <= 12 * 1024 * 1024, folder
        paths.update(p for p in files if p.suffix.lower() in allowed)

    for i, name in enumerate(['SMB2 Mario', 'SMB2 Luigi', 'SMB2 Toad', 'SMB2 Peach']):
        p = smb2 / ('class' + str(i)) / 'capture'
        d, b = read(p / 'result.json'), read(p / 'binding.json')
        assert d['passed'] and b['exit_code'] == 0
        assert d['ROM_sha256'] == b['ROM_sha256'] == ROM_SHA
        verify_bindings(b)
        assert d['main_updates'] == 220 and d['actual_UI_DMA_checks']['lives'] > 0
        assert d['body_P0_source_exact'] and d['eye_role_original_red']
        assert d['game_background_checks'] == 220
        assert d['jumped'] and d['landed'] and d['clock_errors'] == 0
        outcomes.append(dict(identity=name, passed=True, result_sha256=sha(p / 'result.json'),
                             physical_frames=d['frames'], controlled_Main_updates=d['main_updates'],
                             root_reviewed_whole_PPU_PNGs=4, scope='Cold menu/lives, entrance, walk/jump/land; no level-clear claim.'))
    for name in ['fighter', 'white-mage', 'black-mage', 'thief']:
        p = ff / 'native' / (name + '-cold-v3')
        d, b = read(p / 'result.json'), read(ff / (name + '-postflight.json'))
        assert d['passed'] and d['native'] and not d['debug_RAM_writes']
        assert b['exit_code'] == 0 and b['candidate'] == ROM_SHA
        assert b['source_handoff'] == SOURCE_SHA and b['all_pre_post_bindings_exact']
        assert d['moved'] and d['jumped'] and d['attack'] and d['game_frames'] == 260
        outcomes.append(dict(identity='FF ' + name, passed=True, result_sha256=sha(p / 'result.json'),
                             physical_frames=d['physical_frames'], controlled_game_frames=d['game_frames'],
                             source_movement_calls=d['source_moves'], lag_NMIs=d['lag_nmis'],
                             root_reviewed_whole_PPU_PNGs=5,
                             scope='Cold menu/lives, cache load and bounded walk/jump/attack poses; enemy damage and level-clear not established.'))
    collect(smb2)
    collect(ff)
    # Retain the real full-route failure and passive reproductions. No assertion
    # or historical result is changed to get an unlock publication.
    negative = R / 'build/final62-ff-fighter-route-1030-v1'
    bad = read(negative / 'result.json')
    assert not bad['passed']
    collect(negative)
    for v in [1, 2]:
        p = R / ('build/final62-ff-nmi-budget-1030-v' + str(v))
        assert not read(p / 'result.json')['passed']
        for n in ['inputs.csv', 'trace.csv']:
            assert (p / n).read_bytes() == (negative / n).read_bytes()
        collect(p)
    for folder in ['build/arthur-goku-smb2-palette-native-v1',
                   'build/smb2-lives-palette-diagnostic-v1/class0']:
        collect(R / folder)
    for name in ['ff_nmi_budget_observer_1030_v1.lua', 'ff_nmi_budget_observer_1030_v2.lua',
                 'prepare_ff_nmi_budget_1030_v1.py', 'prepare_ff_nmi_budget_1030_v2.py']:
        paths.add(R / 'tools/audit' / name)
    paths.add(Path(__file__).resolve())
    assert len(paths) <= 600
    assert sum(p.stat().st_size for p in paths) <= 24 * 1024 * 1024
    O.mkdir(parents=True)
    archive = O / 'native-results-and-retained-failure.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(paths):
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for p in paths:
            assert z.read(p.relative_to(R).as_posix()) == p.read_bytes()
    assert archive.stat().st_size <= 5 * 1024 * 1024
    manifest = dict(candidate=ROM_SHA, source_handoff_sha256=SOURCE_SHA,
                    eight_bounded_checks=outcomes,
                    archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
                    members={p.relative_to(R).as_posix(): sha(p) for p in sorted(paths)},
                    source_archives=source_archives,
                    full_route_FF_419_failure_retained=True, full_campaign_qualified=False,
                    no_ROM_object_debug_executable_in_archive=True)
    write(O / 'manifest.json', manifest)
    (O / 'README.md').write_text(
        'Root reviewed all 36 actual PPU PNGs from the eight bounded checks on exact dfdb194a. '
        'SMB2 lives now keeps its original body colors after the native text queue; the FF lives '
        'screen no longer overruns its first palette/text transfer. Eight bounded checks pass. '
        'These are not full 1-1 completions or every-powerup tests.\n\n'
        'The older exact 37210891 Fighter route failed at physical frame 419 when rendering '
        'was reenabled after the vertical-reload deadline, visibly wrapping a ground row to '
        'the top. Both passive profiles reproduce the same controller and game trace. This '
        'subsystem remains unchanged in dfdb194a; the defect is known and unfixed, and the '
        'historical failed result remains intact. The user explicitly prioritized playable '
        'unlocks over further polish. FF mandatory shadows and White Mage enemy damage are '
        'also deferred, not claimed fixed. Performance and full campaign qualification remain open.\n\n'
        'The frozen source handoff accurately says native pending at its creation time. '
        'This later checkpoint adds exact-hash bounded native evidence and the Downloads '
        'installation receipt without rewriting that historical handoff. Goku is now an '
        'Arthur Select alternate; the former slot is a pending Battletoads placeholder. '
        'There are 80 individual identities (62 enabled, 18 pending) plus that generic '
        'family placeholder, not 82 implemented individuals.\n', encoding='utf-8', newline='\n')

    downloads = Path.home() / 'Downloads'
    latest = downloads / 'SMB-Crossover-Latest-WIP-MMC5.nes'
    versioned = downloads / 'SMB-Crossover-2026-10-30-Ready62-WIP-MMC5.nes'
    backup = downloads / 'SMB-Crossover-Before-Ready62-44c92ad7-MMC5.nes'
    assert sha(latest) == OLD_SHA
    for p in [versioned, backup]:
        assert not p.exists(), p
    shutil.copy2(latest, backup)
    assert sha(backup) == OLD_SHA
    shutil.copy2(rom, versioned)
    assert sha(versioned) == ROM_SHA
    shutil.copy2(versioned, latest)
    assert sha(latest) == ROM_SHA
    receipt = dict(date='2026-10-30', status='INSTALLED_UNLOCK62_WIP_WITH_KNOWN_BUGS',
        installed=True, ROM_sha256=ROM_SHA, source_handoff_sha256=SOURCE_SHA,
        verified_source_bindings=source_bindings, latest=str(latest), versioned=str(versioned),
        backup=str(backup), previous_sha256=OLD_SHA, menu_slots=32,
        individual_identities=80, playable=62, pending_individual_identities=18,
        generic_pending_family_placeholders=['Battletoads'],
        newly_unlocked=['SMB2 Mario', 'SMB2 Luigi', 'SMB2 Toad', 'SMB2 Peach',
                        'FF Fighter', 'FF White Mage', 'FF Black Mage', 'FF Thief'],
        changes=['Goku moved to Select on Arthur; old slot is pending Battletoads.',
                 'SMB2 original body/eye colors and native backdrop restored.',
                 'SMB2 late lives palette overwrite and FF lives text/palette overrun repaired.'],
        bounded_native=outcomes, root_checkpoint_manifest_sha256=sha(O / 'manifest.json'),
        full_campaign_pass=False, every_powerup_pass=False, constant_60Hz_qualified=False,
        known_open=['FF gameplay render-deadline failure from retained exact3721 Fighter route.',
                    'FF required black shadow sprites and White Mage damage report deferred by user.',
                    'Lag, missing attacks/audio/upgrades and other character polish remain.'],
        instruction='Reopen the new ROM and start fresh; old save states may contain incompatible code/state.')
    write(RECEIPT, receipt)
    shutil.copy2(smb2 / 'class0/capture/selected.png', R / 'docs/images/character-select.png')
    print(json.dumps(dict(receipt=str(RECEIPT), ROM_sha256=ROM_SHA, installed=str(latest),
                          source_archives_checked=source_archives, archive_bytes=archive.stat().st_size,
                          archive_members=len(paths), bounded_checks=8), indent=2))


if __name__ == '__main__':
    main()
