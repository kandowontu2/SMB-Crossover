"""Accept44 only after immutable ROM, source, negative, caller and profile proof."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'build/checkpoints/roster-audit-v44-provisional-a'
OLD = ROOT / 'build/checkpoints/roster-audit-v43'
DST = ROOT / 'build/checkpoints/roster-audit-v44'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--layout-receipt', type=Path, required=True)
a = ap.parse_args()
layout = a.layout_receipt.resolve()
assert layout.is_relative_to(ROOT) and layout.is_file()
candidate = read(SRC / 'candidate.json')
roms = {m: sha(SRC / f'smb-crossover-{m}.nes') for m in ('mmc3', 'mmc5')}
assert roms == {m: q['sha256'] for m, q in candidate['roms'].items()}
layout_report = read(layout)
assert layout_report['result'] == 'passed-static-collision-layout-audit'
for side, cp in (('before', OLD), ('after', SRC)):
    assert all(layout_report[side][e + '_sha256'] == sha(cp / f'smb-crossover-mmc5.{e}')
        for e in ('nes', 'dbg', 'lbl'))
layout_receipt = read(layout.parent / 'receipt.json')
assert layout_receipt['result'] == 'static-audit-complete'
assert all(sha(layout.parent / n) == q['sha256'] for n, q in layout_receipt['files'].items())
assert not DST.exists(), 'Never overwrite an accepted checkpoint'
summary = ROOT / 'build/verification/summary-roster-audit-v44-provisional-a.json'
raw = read(summary)
boundp = SRC / 'validation/bound-summary.json'
bound = read(boundp)
assert raw['result'] == bound['result'] == 'passed'
assert len(raw['cases']) == bound['case_count'] == bound['passed'] == 761
assert bound['failed'] == 0 and bound['single_full_run']
assert not raw['failures'] and not raw['changed_fixtures']
assert raw['fixture_hashes_before'] == raw['fixture_hashes_after']
assert raw['fixture_hashes_after'] == read(ROOT / 'build/verification/summary-roster-audit-v43-provisional-a.json')['fixture_hashes_after']
assert all(sha(ROOT / n) == h for n, h in raw['fixture_hashes_after'].items())
assert raw['roms'] == bound['roms'] == roms and bound['summary_sha256'] == sha(summary)
assert all(sha(ROOT / q['log']) == q['log_sha256'] for q in bound['cases'])
assert all(sha(ROOT / p) == h for p, h in candidate['patches'].items())
proofs = {}
def retain(name, path):
    path = ROOT / path
    proofs[name] = dict(path=str(path.relative_to(ROOT)), sha256=sha(path))
    return read(path)

prefix = retain('compiled_prefix', 'build/verification/mm-bass-native-bg-v43-readonly/actual44a-prefix-proof.json')
assert prefix['result'] == 'passed-compiled-prefix' and prefix['cases'] == 73728
assert prefix['before_sha256'] == sha(OLD / 'smb-crossover-mmc5.nes')
assert prefix['after_sha256'] == roms['mmc5']
assert prefix['cycle_pairs'] == [dict(before=62, after=29, cases=73728)]
assert prefix['after_sidecars_sha256'] == {e: sha(SRC / f'smb-crossover-mmc5.{e}') for e in ('dbg', 'lbl')}
negative = retain('wall_cancel_negative', 'build/verification/ryu-wall-cancel44-preparation/lifecycle-C-accepted-negative.json')
assert proofs['wall_cancel_negative']['sha256'] == 'eb7b8a2783794e2393225c1c46c6e60dde356be21e7aee2928ac17de3494ef2e'
life_path = ROOT / 'build/verification/ryu-lifecycle-v44a-source-positive-a/report.json'
life = retain('wall_cancel_positive', life_path)
assert life['completed'] and life['total_cases'] == 40 and life['total_mismatches'] == 0
assert life['core_sha256'] == '235f9ce482962490ddc7e4a03fde0782dc7cf7399858b9c0c1839d22a89cfca8'
assert sha(Path(life['frozen_core'])) == life['core_sha256']
gates_path = ROOT / 'build/verification/ryu-gates-v44a-source-positive-a/report.json'
gates = retain('earlier_admission_controls', gates_path)
old_gates = read(ROOT / 'build/verification/ryu-gates-v43a-source-positive-a/report.json')
assert gates['completed'] and gates['total_cases'] == 68 and gates['total_mismatches'] == 0
assert [q['fixture_sha256'] for q in gates['runs']] == [q['fixture_sha256'] for q in old_gates['runs']]
for path, report in ((life_path, life), (gates_path, gates)):
    for q in report['runs']:
        assert q['exit'] == 0 and q['rom_sha256'] == roms[q['mapper']]
        assert not q['result']['failures'] and q['result']['mismatches'] == 0
        assert q['result']['cases'] == q['result']['completed']
        assert all(sha(path.parent / n) == h for n, h in q['files'].items())

profile_files = {}
for name, filename in (
    ('crowds', 'plain-walking-v43-v44a-native-buffer-comparison.json'),
    ('repeated_four', 'plain-walking-v43-v44a-four-repeat-comparison.json'),
):
    comparison = retain(name, 'build/verification/' + filename)
    assert comparison['canonical_mismatch_count'] == 0 and len(comparison['runs']) == 3
    assert {q['character'] for q in comparison['runs']} == {1, 2, 9}
    assert all(q['mapper'] == 'mmc5' and q['canonical_rows'] == 1200
        and q['canonical_observation_fields'] == 204 and not q['canonical_mismatch_count']
        for q in comparison['runs'])
    for side, cp in (('before', OLD), ('after', SRC)):
        directory = Path(comparison[side])
        m = read(directory / 'manifest.json')
        assert m['script_sha256'] == comparison['benchmark_source_sha256']
        assert all(q['exit'] == 0 and q['rom_sha256'] == sha(cp / 'smb-crossover-mmc5.nes') for q in m['runs'])
        for p in directory.rglob('*'):
            if p.is_file():
                profile_files[str(p.relative_to(ROOT))] = sha(p)
        for q in comparison['runs']:
            csv_path = next((directory / f"mmc5-c{q['character']}").glob('*-canonical.csv'))
            assert sha(csv_path) == q[f'canonical_{side}_sha256']
proofs['compiled_relocation_review'] = dict(path=str(layout.relative_to(ROOT)), sha256=sha(layout))

archive = SRC / 'source-v44a.zip'
rebuildp = ROOT / 'build/checkpoint-tests/source-v44a-rebuild-smoke/report.json'
rebuild = read(rebuildp)
assert sha(archive) == rebuild['archive_sha256']
assert len(rebuild['cases']) == 2 and all(q['exit'] == 0 and q['equal'] and q['sha256'] == roms[q['mapper']] for q in rebuild['cases'])
with zipfile.ZipFile(archive) as z:
    sources = json.loads(z.read('archived-file-hashes.json'))
    assert len(sources) == 401 and len(z.namelist()) == 402
    assert sources == {n: hashlib.sha256(z.read(n)).hexdigest() for n in sources}
assert sources == {n: sha(ROOT / n) for n in sources}
with zipfile.ZipFile(OLD / 'source-v43.zip') as z:
    old_sources = json.loads(z.read('archived-file-hashes.json'))
assert {n for n in sources if sources[n] != old_sources[n]} == {'README.md', 'src/collision.s', 'src/remaining_weapons.s'}
assert sha(ROOT / 'reference/crossover2/extracted/scripts/com/smbc/characters/Ryu.as') == 'df487c804d685cf11f79c10f31b77a8bb98753a7b8010e0c0693341eb58b48d1'
for mapper in roms:
    before = OLD / f'smb-crossover-{mapper}.nes'
    after = SRC / before.name
    x, y = before.read_bytes(), after.read_bytes()
    assert x[:16] == y[:16] and x[16 + 524288:] == y[16 + 524288:]
    def labels(p):
        return {n: int(v, 16) for v, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$', p.read_text(), re.M)}
    old, new = labels(before.with_suffix('.lbl')), labels(after.with_suffix('.lbl'))
    assert all(new[n] == v for n, v in old.items() if v < 0x8000 and n in new)
    assert new['OAMandReadJoypad'] == 0xe000 and new['GuestGameRoutinesBridge'] == 0xe025
    assert x[16 + 63 * 8192:16 + 63 * 8192 + 0x4e] == y[16 + 63 * 8192:16 + 63 * 8192 + 0x4e]
    if mapper == 'mmc3':
        assert x[16 + 62 * 8192:] == y[16 + 62 * 8192:]
qa = ROOT / 'docs/qa/roster-component-v44.md'
pending = 'Candidate44a is awaiting the complete emulator suite and paired crowd profiles.'
assert pending in qa.read_text()
DST.mkdir()
for mapper in roms:
    for ext in ('.nes', '.lbl', '.dbg', '.map', '.lst'):
        p = SRC / f'smb-crossover-{mapper}{ext}'
        shutil.copyfile(p, DST / p.name)
        assert sha(p) == sha(DST / p.name)
shutil.copyfile(archive, DST / 'source-v44.zip')
qa.write_text(qa.read_text().replace(pending,
    'Accepted component44a passes all761 unchanged-fixture emulator slots, the\n73,728-case compiled prefix comparison, forty frozen lifecycle cases and all68\nearlier admission cases. Both paired crowd sets retain all204 gameplay fields.\nFresh extraction of401 source inputs rebuilds both ROMs byte identically.', 1))
readme = ROOT / 'README.md'
archived_readme = sha(readme)
text = readme.read_text()
anchor = 'The [v43 component update]'
assert anchor in text and '[v44 component update]' not in text
paragraph = ('The [v44 component update](docs/qa/roster-component-v44.md) reduces MMC5 native tile-probe work by33 CPU cycles per probe and fixes Ryu active Jump Slash cancellation on wall attachment. All761 unchanged-fixture emulator checks pass; paired crowded-scene and repeated-phase tests preserve all204 gameplay fields. Dense-scene flicker and the full roster/weapon/recording audit remain open. ROMs are in `build/checkpoints/roster-audit-v44/`.\n\n')
readme.write_text(text.replace(anchor, paragraph + anchor, 1))
manifest = dict(checkpoint=DST.name, status='accepted-component-checkpoint-with-known-roster-defects',
    goal_complete=False, created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    promoted_from=SRC.name, copied_byte_identically=True, parent=OLD.name, roms=roms,
    source_archive=dict(path='source-v44.zip', sha256=sha(DST / 'source-v44.zip'), source_files=401,
        fresh_rebuild=str(rebuildp.relative_to(ROOT)), rebuild_report_sha256=sha(rebuildp)),
    source_manifest=sources, patches=candidate['patches'], proofs=proofs,
    validation=dict(summary=str(summary.relative_to(ROOT)), sha256=sha(summary),
        bound_raw_logs=str(boundp.relative_to(ROOT)), bound_sha256=sha(boundp), case_count=761,
        single_full_run_all_passed=True, fixtures_unchanged=True),
    profile_files_sha256=profile_files, qa=str(qa.relative_to(ROOT)), qa_sha256=sha(qa),
    documentation_updates={'README.md': dict(archived_sha256=archived_readme, current_sha256=sha(readme), scope='Checkpoint paragraph after immutable source archive')},
    known_gaps=['Full14 final-hash normal routes1-1..2-2, all special/alternate weapons/upgrades, final lossless audiovisual recordings and frame review remain incomplete.',
        'Dense-crowd CPU overload and sprite scanline flicker remain; some individual profile frames worsen. No universal frame-rate claim.',
        'Source Koopa secondary head admission is missing from current Character attack proxies; executable source component is in preparation.',
        'Bill Flare terrain negative is confirmed; source-filter repair and independently audited historical golden revision remain unapplied. Angle, prone anchor, mixed count and visibility require separate actual negatives/repairs.',
        'Ryu/Simon complete current/cached body geometry, input phase and Jump Slash phase/timer semantics remain open.',
        'Final capture space headroom remains constrained; conservative guard is unchanged.'])
(DST / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('PROMOTED', roms, '761 full-run slots; CPU-prefix/lifecycle/admission/crowd proofs; goal remains active', flush=True)
