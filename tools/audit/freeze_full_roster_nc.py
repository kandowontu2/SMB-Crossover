"""Publish the 32-identity roster after combined traversal and feature checks."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT/'build/verification/final-roster-nc'
OUTPUT = ROOT/'build/checkpoints/full-roster-nc'
EXPECTED = '3ecdc4b8e44d0cf7ca3a7e627d8719b474a23531c7867a76e38b3fdfe0463776'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUTPUT.exists()
    parent = read(ROOT/'build/checkpoints/full-roster-mz/manifest.json')
    rom = VERIFY/'full-roster.nes'
    assert digest(rom) == EXPECTED
    entry = read(VERIFY/'roster/results.json')
    features = read(VERIFY/'feature-native-results.json')
    scroll = read(VERIFY/'scroll/full-roster-scroll.json')
    scroll_binding = read(VERIFY/'scroll/binding.json')
    traversal = read(VERIFY/'traversal-v2/results.json')
    composition = read(VERIFY/'traversal-composition-proof.json')
    adapters = read(VERIFY/'adapter-native-results.json')
    spring = read(VERIFY/'bounce/build/verification/full-roster-bounce.json')
    assert entry['rom_sha256'] == EXPECTED and len(entry['results']) == entry['identities'] == 32
    assert all(x['exit'] == 0 for x in entry['results'].values())
    assert features['sha256'] == EXPECTED and len(features['results']) == 14 and all(x == 0 for x in features['results'].values())
    assert scroll_binding['ROM_sha256'] == EXPECTED and scroll_binding['exit'] == 0
    assert scroll['all_profiles_pass'] and len(scroll['results']) == 18 and all(x['passed'] for x in scroll['results'])
    assert traversal['ROM_sha256'] == EXPECTED and len(traversal['results']) == 8 and all(x['exit'] == 0 for x in traversal['results'].values())
    assert composition['ROM_sha256'] == EXPECTED and composition['passed']
    assert adapters == {'bounce': 0, 'outline-mike': 0, 'outline-samus': 0}
    assert spring['passed'] and spring['arenas'] == 30
    paths = {m: VERIFY/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3', 'mmc5')}
    paths['mmc5-expanded'] = rom
    assert all(digest(paths[m]) == parent['ROMs'][m] for m in ('mmc3', 'mmc5'))
    text = (ROOT/'README.md').read_text().replace('build/checkpoints/full-roster-mz', 'build/checkpoints/full-roster-nc')
    start = text.index('All **32 identities** pass')
    end = text.index('\n\n', start)
    text = text[:start]+('All **32 identities** pass cold controller selection, alternate persistence, highlighted-name checks and bounded World 1-1 movement. All **18 added identities** also pass sustained native scrolling. The combined build passes focused pickup/combat/death checks, 30 spring/stomp arenas, native platform carrying, and eight physical-upgrade/obstacle fixtures. Those include Zelda II Link collecting and casting Jump, Darkwing\'s Arrow Gas recovery, and Sypha/Alucard clearing native pipe heights and the 1-3 gap geometry. Seeded arenas remain labeled; these checks do not certify full campaigns. The frozen manifest records ROM hashes, rejected fixture assumptions and remaining source differences.')+text[end:]
    (ROOT/'README.md').write_text(text)
    names = set(parent['source_files'])
    names.update('tools/audit/'+n for n in (
        'adopt_z2_traversal_nc.py', 'adopt_cv3_traversal_nc.py', 'check_full_roster_nc.py',
        'check_character_features_mz.py', 'check_traversal_nc.py', 'check_traversal_components_nc.py',
        'freeze_full_roster_nc.py', 'archive_capture_headroom_nb.py'))
    names.add('docs/qa/new-roster-native-scroll-fixture-2026-10-23.md')
    source_changes = {n: digest(ROOT/n) for n in names if n in parent['source_files'] and digest(ROOT/n) != parent['source_files'][n]}
    assert {n for n in source_changes if n.startswith('src/')} == {'src/zelda2_link_motion.s', 'src/x5_bounce.s', 'src/cv3_combat.s'}
    artifact_files = [p.with_suffix(ext) for p in paths.values() for ext in ('.nes', '.lbl', '.dbg', '.map')]
    sys.path.insert(0, str(ROOT/'tools'))
    from playthroughs.roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    reserve = sum(p.stat().st_size for p in artifact_files)+sum((ROOT/n).stat().st_size for n in names)
    assert used+reserve < 30_000_000_000, (used, reserve)
    proof = dict(ROM_sha256=EXPECTED, identities=32, portraits=19, rows=[6, 6, 7],
        entry=entry, features=features, sustained_scroll=scroll, scroll_binding=scroll_binding,
        traversal=traversal, composition=composition, native_adapters=adapters, native_springs=spring,
        source_changes=source_changes, standard_mapper_ROMS_unchanged=True,
        video_work_deferred=True, full_campaign_verified=False,
        harness_revisions=[
            'Turtle fixed-video-frame input stopped at world325 and hit the adjacent brick. Retained failed trace has zero powerup actors. Corrected controller input reaches world330..335 before jumping; all original food/emergence, stationary-X, enemy-defeat and palette assertions pass. No ROM change.',
            'Darkwing strict physical-entry C-bank assertion caught a shadow-before-hardware bank publication. Final check uses the existing decoded publication-window assertion and records hardware68/logical13 with a pending STA5116 value141. Logical restoration and all shared operands remain checked. No ROM change.',
            'Adapted CV3 feature oracles explicitly expect72px rather than the historical source36px; all prior original-kernel proofs remain historical. Geometry arenas and ScrollLock are disclosed, and diagnostic periodic-input routes are not presented as completed campaigns.'],
        scope='Focused controller, source, compiled component and native emulator checks. Exact-bank component reuse is explicit. No campaign, physical-cartridge or video-review certification.')
    (VERIFY/'completion-evidence.json').write_text(json.dumps(proof, indent=2)+'\n')
    OUTPUT.mkdir(parents=True)
    with zipfile.ZipFile(OUTPUT/'source.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(names):
            archive.write(ROOT/name, name)
    for mapper, path in paths.items():
        for ext in ('.nes', '.lbl', '.dbg', '.map'):
            target = OUTPUT/'build'/('smb-crossover-'+mapper+ext)
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext), target)
            shutil.copyfile(target, ROOT/'build'/target.name)
    report = dict(parent, status='REQUESTED_32_IDENTITY_ROSTER_CORE_ADDED_AND_VERIFIED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), parent_checkpoint='full-roster-mz',
        ROMs={m: digest(p) for m, p in paths.items()}, source_zip_sha256=digest(OUTPUT/'source.zip'),
        source_files={n: digest(ROOT/n) for n in sorted(names)}, completion_evidence=proof,
        remaining_profiles=[], scope=proof['scope'])
    report['limitations'] = parent['limitations']+[
        'Ordinary Sypha/Alucard airborne displacement is doubled for SMB obstacles while retaining source curve timing and ground speed; this is a declared geometry adaptation.',
        'The first unowned Zelda II Jump from a mushroom-origin block walks/falls after its full visible rise; it retains its genuine icon and requires physical contact.']
    report['space_before_freeze'] = dict(bytes=used, reserved_upper_bound=reserve, cap=30_000_000_000)
    (OUTPUT/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    (ROOT/'build/verification/root-current61-roster-nc.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUTPUT), ROMs=report['ROMs'], identities=32,
        source_zip_sha256=report['source_zip_sha256'], scope=proof['scope'])))


if __name__ == '__main__':
    main()
