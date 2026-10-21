"""Publish exact frozen component bytes after checks, without a roster-clear claim."""
from pathlib import Path
import datetime, hashlib, json, shutil, zipfile

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT/'build/checkpoints/roster-audit-v37-provisional-c'
DST = ROOT/'build/checkpoints/roster-audit-v37'
RAW = ROOT/'build/verification/summary-roster-audit-v37-provisional-c.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


raw = read(RAW)
assert raw['result'] == 'failed' and len(raw['cases']) == 758
assert raw['failures'] == ['link-beam-impact failed for smb-crossover-mmc3'] and not raw['changed_fixtures']
assert raw['fixture_hashes_before'] == raw['fixture_hashes_after']
migration_path = ROOT/'build/verification/link-beam-v37-fixture-migration/summary.json'
migration = read(migration_path)
assert migration['result'] == 'passed' and len(migration['cases']) == 2
assert migration['fixture_hashes_before'] == migration['fixture_hashes_after']
current = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT/'tests').rglob('*')) if p.is_file()}
current['tools/run_mesen.py'] = sha(ROOT/'tools/run_mesen.py')
assert [n for n in current.keys() | raw['fixture_hashes_after'].keys() if current.get(n) != raw['fixture_hashes_after'].get(n)] == ['tests/link-beam-impact.lua']
assert current['tests/link-beam-impact.lua'] == migration['after_sha256']
cases = {(c['test'], c['rom']): c for c in raw['cases']}
for c in migration['cases']:
    assert c['result'] == 'passed' and c['exit'] == 0
    cases[c['test'], c['rom']] = c
assert len(cases) == 759 and all(c['result'] == 'passed' for c in cases.values())
roms = {m: sha(SRC/f'smb-crossover-{m}.nes') for m in ('mmc3', 'mmc5')}
assert roms == raw['roms']
perf_path = ROOT/'build/profiling/plain-walking-v36d-v37c-comparison.json'
perf = read(perf_path)
assert perf['canonical_mismatch_count'] == 0 and len(perf['runs']) == 12
assert sum(r['canonical_rows'] for r in perf['runs']) == 14400
for m in roms:
    for name, count in ((f'core-render-v36-v37c-{m}.json', None),
                        (f'remaining-empty-v37b-v37c-{m}.json', 2352),
                        (f'weapon-admission-v37b-v37c-{m}.json', 1872),
                        (f'idle-draw-v37b-v37c-{m}.json', 672)):
        unit = read(ROOT/'build/verification'/name)
        assert unit['result'] == 'passed' and unit['after_sha256'] == roms[m]
        if count is not None:
            assert unit['cases'] == count
        else:
            assert unit['entries']['UpdateTopScore']['cases'] == 2034
            assert unit['entries']['MetaspriteRenderLoop']['cases'] == 1640
    unit = read(ROOT/f'build/verification/idle-draw-v37a-v37b-{m}-corrected-bank.json')
    assert unit['result'] == 'passed' and unit['cases'] == 672
    assert unit['actual_linked_entry_banks'] == {'RemainingDraw': 61, 'SamusDrawShots': 10}
rebuild_path = ROOT/'build/checkpoint-tests/source-v37c-rebuild-smoke/report.json'
rebuild = read(rebuild_path)
archive = SRC/'source-v37c.zip'
assert sha(archive) == rebuild['archive_sha256']
assert all(c['exit'] == 0 and c['equal'] and c['sha256'] == roms[c['mapper']] for c in rebuild['cases'])
with zipfile.ZipFile(archive) as z:
    source_hashes = json.loads(z.read('archived-file-hashes.json'))
    assert len(source_hashes) == 400 and len(z.namelist()) == 401
    assert source_hashes == {n: hashlib.sha256(z.read(n)).hexdigest() for n in source_hashes}
delta = [n for n, h in source_hashes.items() if sha(ROOT/n) != h]
assert delta in ([], ['README.md']), delta
baseline = sha(ROOT/'build/smb-crossover-mmc3-baseline.nes')
assert baseline == '0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'
assert not DST.exists(), 'Do not overwrite accepted bytes'
DST.mkdir()
for m in roms:
    for ext in ('.nes', '.lbl', '.dbg', '.lst', '.map'):
        p = SRC/f'smb-crossover-{m}{ext}'
        shutil.copyfile(p, DST/p.name)
        assert sha(p) == sha(DST/p.name)
shutil.copyfile(archive, DST/'source-v37.zip')
consolidated_path = ROOT/'build/verification/summary-roster-audit-v37-consolidated.json'
consolidated = {'result': 'passed-consolidated-component-slots', 'cases': sorted(cases.values(), key=lambda c: (c['rom'], c['test'])),
                'case_count': 759, 'single_full_run_all_passed': False, 'all_slots_passed': True,
                'original_summary': str(RAW.relative_to(ROOT)), 'original_summary_sha256': sha(RAW),
                'fixture_migration': str(migration_path.relative_to(ROOT)), 'fixture_migration_sha256': sha(migration_path),
                'scope': 'Component checks; source parity, exact-final-hash roster routes and final recordings remain incomplete'}
consolidated_path.write_text(json.dumps(consolidated, indent=2)+'\n')
manifest = {
    'checkpoint': 'roster-audit-v37', 'status': 'accepted-component-checkpoint-with-known-roster-defects',
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'promoted_from': SRC.name, 'copied_byte_identically': True, 'roms': roms,
    'source_manifest': source_hashes,
    'source_archive': {'path': 'source-v37.zip', 'sha256': sha(DST/'source-v37.zip'),
                       'bytes': (DST/'source-v37.zip').stat().st_size, 'source_files': 400,
                       'fresh_extraction_rebuild': str(rebuild_path.relative_to(ROOT)), 'both_roms_byte_identical': True},
    'validation': {'summary': str(consolidated_path.relative_to(ROOT)), 'sha256': sha(consolidated_path), 'case_count': 759,
                   'single_full_run_all_passed': False, 'original_frozen_fixtures_unchanged': True,
                   'original_summary': str(RAW.relative_to(ROOT)), 'original_summary_sha256': sha(RAW),
                   'fixture_migration': str(migration_path.relative_to(ROOT)),
                   'log': 'build/verification/roster-audit-v37c-full.log',
                   'log_sha256': sha(ROOT/'build/verification/roster-audit-v37c-full.log')},
    'performance_report': str(perf_path.relative_to(ROOT)),
    'read_only_followup': 'build/profiling/samus-nmi-followup-v37/report.json',
    'qa': 'docs/qa/crowd-performance-v37.md', 'baseline_sha256': baseline,
    'known_gaps': ['Samus/Mega Man four-Goomba redraw limits and dense-scene lag remain.',
                   'Three crowd scenes draw less often; complete results are retained.',
                   'Normal Simon/Ryu pose geometry and Simon hurt ceiling transition remain.',
                   'Firebar first-read-before-producer lifecycle requires correction.',
                   'All final-hash roster routes, every attack/upgrade and final recordings remain incomplete.',
                   'Eight hardware sprites per scanline remain; no physical cartridge test.'],
    'documentation_updates': {'README.md': {'archived_sha256': source_hashes['README.md'], 'current_sha256': sha(ROOT/'README.md')}},
}
(DST/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print('PROMOTED', roms, '759 consolidated component slots, original758/759 and corrected2/2; route/capture goal remains active')
