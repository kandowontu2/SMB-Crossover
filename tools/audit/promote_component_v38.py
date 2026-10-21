"""Publish immutable38e component bytes after the frozen full run closes."""
from pathlib import Path
import datetime, hashlib, json, shutil, zipfile

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT/'build/checkpoints/roster-audit-v38-provisional-e'
DST = ROOT/'build/checkpoints/roster-audit-v38'
RAW = ROOT/'build/verification/summary-roster-audit-v38-provisional-e.json'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text())
raw = read(RAW)
assert raw['result'] == 'passed' and len(raw['cases']) == 761
assert not raw['failures'] and not raw['changed_fixtures']
assert raw['fixture_hashes_before'] == raw['fixture_hashes_after']
roms = {m: sha(SRC/f'smb-crossover-{m}.nes') for m in ('mmc3', 'mmc5')}
assert roms == raw['roms']
for m in roms:
    unit = read(ROOT/f'build/verification/firebar-init-v37-v38e-{m}.json')
    assert unit['result'] == 'passed' and unit['cases'] == 3072 and unit['after_sha256'] == roms[m]
for name, count in (('audio-copies-v37-v38e-mmc5.json', 1928), ('expansion-flush-v37-v38e-mmc5.json', 4096)):
    unit = read(ROOT/'build/verification'/name)
    assert unit['result'] == 'passed' and unit['cases'] == count and unit['after_sha256'] == roms['mmc5']
perf_path = ROOT/'build/profiling/plain-walking-v37c-v38e-comparison.json'
perf = read(perf_path)
assert perf['canonical_mismatch_count'] == 0 and len(perf['runs']) == 12
assert sum(r['canonical_rows'] for r in perf['runs']) == 14400
rebuild_path = ROOT/'build/checkpoint-tests/source-v38e-rebuild-smoke/report.json'
rebuild = read(rebuild_path)
archive = SRC/'source-v38e.zip'
assert sha(archive) == rebuild['archive_sha256']
assert all(c['exit'] == 0 and c['equal'] and c['sha256'] == roms[c['mapper']] for c in rebuild['cases'])
with zipfile.ZipFile(archive) as z:
    sources = json.loads(z.read('archived-file-hashes.json'))
    assert len(sources) == 401 and len(z.namelist()) == 402
    assert sources == {n: hashlib.sha256(z.read(n)).hexdigest() for n in sources}
source_delta = [n for n, h in sources.items() if sha(ROOT/n) != h]
assert source_delta in ([], ['README.md']), source_delta
baseline = sha(ROOT/'build/smb-crossover-mmc3-baseline.nes')
assert baseline == '0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'
assert not DST.exists(), 'Do not overwrite accepted bytes'
DST.mkdir()
for m in roms:
    for ext in ('.nes', '.lbl', '.dbg', '.lst', '.map'):
        p = SRC/f'smb-crossover-{m}{ext}'
        shutil.copyfile(p, DST/p.name)
        assert sha(p) == sha(DST/p.name)
shutil.copyfile(archive, DST/'source-v38.zip')
manifest = {
    'checkpoint': 'roster-audit-v38', 'status': 'accepted-component-checkpoint-with-known-roster-defects',
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'promoted_from': SRC.name,
    'copied_byte_identically': True, 'roms': roms, 'source_manifest': sources,
    'source_archive': {'path': 'source-v38.zip', 'sha256': sha(DST/'source-v38.zip'),
                       'bytes': (DST/'source-v38.zip').stat().st_size, 'source_files': 401,
                       'fresh_extraction_rebuild': str(rebuild_path.relative_to(ROOT)), 'both_roms_byte_identical': True},
    'validation': {'summary': str(RAW.relative_to(ROOT)), 'sha256': sha(RAW), 'case_count': 761,
                   'single_full_run_all_passed': True, 'fixtures_unchanged': True,
                   'log': 'build/verification/roster-audit-v38e-full.log',
                   'log_sha256': sha(ROOT/'build/verification/roster-audit-v38e-full.log'),
                   'verify_script_sha256': sha(ROOT/'tools/verify.py')},
    'performance_report': str(perf_path.relative_to(ROOT)),
    'focused_fixture_migration': 'build/verification/samus-ceiling38d-focused-receipt.json',
    'qa': 'docs/qa/crowd-performance-v38.md', 'baseline_sha256': baseline,
    'known_gaps': ['Dense scenes still lag and hardware scanline limits remain.',
                   'Normal Simon/Ryu pose geometry and Simon hurt ceiling transition remain.',
                   'All exact-final-hash character routes, every attack/upgrade and final recordings remain incomplete.',
                   'Earlier34/34b route proofs have explicit qualifications and are not38 proofs.',
                   'No physical cartridge test or source-perfect port claim.'],
    'documentation_updates': {'README.md': {'archived_sha256': sources['README.md'], 'current_sha256': sha(ROOT/'README.md')}},
}
(DST/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print('PROMOTED', roms, '761 frozen component cases; full roster goal remains active')
