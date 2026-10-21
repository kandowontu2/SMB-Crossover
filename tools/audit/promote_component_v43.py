"""Accept narrow Ryu gates only after source negatives and unchanged controls."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'build/checkpoints/roster-audit-v43-provisional-a'
OLD = ROOT / 'build/checkpoints/roster-audit-v42'
DST = ROOT / 'build/checkpoints/roster-audit-v43'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rawp = ROOT / 'build/verification/summary-roster-audit-v43-provisional-a.json'
boundp = SRC / 'validation/bound-summary.json'
raw, bound = read(rawp), read(boundp)
assert raw['result'] == bound['result'] == 'passed'
assert len(raw['cases']) == bound['case_count'] == bound['passed'] == 761
assert bound['failed'] == 0 and bound['single_full_run']
assert not raw['failures'] and not raw['changed_fixtures']
assert raw['fixture_hashes_before'] == raw['fixture_hashes_after']
assert raw['fixture_hashes_after'] == read(ROOT / 'build/verification/summary-roster-audit-v42-provisional-e.json')['fixture_hashes_after']
assert all(sha(ROOT / n) == h for n, h in raw['fixture_hashes_after'].items())
assert bound['summary_sha256'] == sha(rawp)
assert all(sha(ROOT / c['log']) == c['log_sha256'] for c in bound['cases'])
roms = {m: sha(SRC / f'smb-crossover-{m}.nes') for m in ('mmc3', 'mmc5')}
assert roms == raw['roms'] == bound['roms'] == {
    'mmc3': '968fd108bbb87018e56f43f61f56d88028cd174f0361df74fca6b3feb6fc561c',
    'mmc5': '3481e1cdf077d5314815eae66d72b6751f7f8b3b3b8e7550d50f69a79475fa7f'}
negativep = ROOT / 'build/verification/ryu-gates-v42-actual-negative-a/report.json'
positivep = ROOT / 'build/verification/ryu-gates-v43a-source-positive-a/report.json'
negative, positive = read(negativep), read(positivep)
assert negative['completed'] and positive['completed']
assert negative['total_cases'] == positive['total_cases'] == 68
assert negative['total_mismatches'] == 56 and positive['total_mismatches'] == 0
assert len(negative['runs']) == len(positive['runs']) == 10
for p, report in ((negativep, negative), (positivep, positive)):
    for row in report['runs']:
        expected = OLD if p == negativep else SRC
        assert row['rom_sha256'] == sha(expected / f"smb-crossover-{row['mapper']}.nes")
        assert all(sha(p.parent / n) == h for n, h in row['files'].items())
        assert row['result']['completed'] == row['result']['cases']
        if p == positivep:
            assert row['exit'] == 0 and not row['result']['failures']
assert [r['fixture_sha256'] for r in negative['runs']] == [r['fixture_sha256'] for r in positive['runs']]
assert sha(ROOT / 'reference/crossover2/extracted/scripts/com/smbc/characters/Ryu.as') == 'df487c804d685cf11f79c10f31b77a8bb98753a7b8010e0c0693341eb58b48d1'
patches = {'build/verification/ryu-gates-v43-proposal.patch': '8aec82b1b15dae79f79120e4bb4fb49b879228ee3f9e01c806c2f9e21ad00d64',
           'build/verification/ryu-special43-preparation/selected5-wall-gate.patch': '09c690a3d34668178e06ce09a0bada9f8b92fe217cce6485440cff47380f2f12'}
assert all(sha(ROOT / n) == h for n, h in patches.items())
archive = SRC / 'source-v43a.zip'
rebuildp = ROOT / 'build/checkpoint-tests/source-v43a-rebuild-smoke/report.json'
rebuild = read(rebuildp)
assert sha(archive) == rebuild['archive_sha256']
assert len(rebuild['cases']) == 2 and all(c['exit'] == 0 and c['equal'] and c['sha256'] == roms[c['mapper']] for c in rebuild['cases'])
with zipfile.ZipFile(archive) as z:
    sources = json.loads(z.read('archived-file-hashes.json'))
    assert len(sources) == 401 and len(z.namelist()) == 402
    assert sources == {n: hashlib.sha256(z.read(n)).hexdigest() for n in sources}
assert sources == {n: sha(ROOT / n) for n in sources}
with zipfile.ZipFile(OLD / 'source-v42.zip') as z:
    old_sources = json.loads(z.read('archived-file-hashes.json'))
assert {n for n in sources if sources[n] != old_sources[n]} == {'README.md', 'src/expanded_weapons.s', 'src/remaining_weapons.s'}


def labels(p):
    return {n: int(v, 16) for v, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$', p.read_text(), re.M)}


def proc(blob, dbg, name):
    segs, syms = {}, []
    for line in dbg.splitlines():
        f = dict(re.findall(r'(\w+)=("[^"]*"|[^,\t]+)', line))
        if line.startswith('seg\t'):
            segs[f['id']] = f
        elif line.startswith('sym\t') and f.get('type') == 'lab' and f.get('name') == '"' + name + '"' and 'seg' in f:
            syms.append(f)
    assert len(syms) == 1
    q = syms[0]; seg = segs[q['seg']]
    off = int(seg['ooffs']) + int(q['val'], 0) - int(seg['start'], 0)
    size = int(q['size'])
    return (off - 16) // 8192, size, blob[off:off + size]


for mapper in roms:
    before = OLD / f'smb-crossover-{mapper}.nes'; after = SRC / before.name
    a, b = before.read_bytes(), after.read_bytes()
    assert a[:16] == b[:16] and a[16 + 524288:] == b[16 + 524288:]
    A, B = labels(before.with_suffix('.lbl')), labels(after.with_suffix('.lbl'))
    assert all(B[n] == v for n, v in A.items() if v < 0x8000 and n in B), 'RAM ABI unchanged'
    assert B['OAMandReadJoypad'] == 0xe000 and B['GuestGameRoutinesBridge'] == 0xe025
    assert a[16 + 63 * 8192:] == b[16 + 63 * 8192:], 'Resident reader/bridge/FIXED bank unchanged'
    old_dbg, new_dbg = before.with_suffix('.dbg').read_text(), after.with_suffix('.dbg').read_text()
    old_gate, new_gate = proc(a, old_dbg, 'AvRyuSpecial'), proc(b, new_dbg, 'AvRyuSpecial')
    assert old_gate[:2] == (61, 187) and new_gate[:2] == (61, 193)
    guard = bytes([0xad, B['XgWall'] & 255, B['XgWall'] >> 8, 0xf0, 1, 0x60])
    assert new_gate[2][18:24] == guard
    old_weapon, new_weapon = proc(a, old_dbg, 'ExpandedWeapons'), proc(b, new_dbg, 'ExpandedWeapons')
    assert old_weapon[0] == new_weapon[0] == 37 and new_weapon[1] == old_weapon[1] - 2
qa = ROOT / 'docs/qa/roster-component-v43.md'
assert 'Candidate43a is awaiting the complete emulator suite.' in qa.read_text()
assert not DST.exists(), 'Never overwrite an accepted checkpoint'
DST.mkdir()
for mapper in roms:
    for ext in ('.nes', '.lbl', '.dbg', '.map', '.lst'):
        p = SRC / f'smb-crossover-{mapper}{ext}'
        shutil.copyfile(p, DST / p.name)
        assert sha(p) == sha(DST / p.name)
shutil.copyfile(archive, DST / 'source-v43.zip')
qa.write_text(qa.read_text().replace('Candidate43a is awaiting the complete emulator suite.',
    'Accepted component checkpoint43a passes all761 unchanged-fixture emulator slots\nin one full run and all68 independent source-derived Ryu cases. A401-file\nsource archive rebuilds both ROMs byte identically from fresh extraction.', 1))
readme = ROOT / 'README.md'; archived_readme = sha(readme)
text = readme.read_text(); anchor = 'The [v42 component update]'
assert anchor in text and '[v43 component update]' not in text
paragraph = 'The [v43 component update](docs/qa/roster-component-v43.md) corrects Ryu wall/vine sword admission and rejects wall Jump Slash while preserving legal wall projectiles and airborne attacks. All 761 unchanged-fixture emulator checks and 68 independent source-derived Ryu cases pass. ROMs are in `build/checkpoints/roster-audit-v43/`; full routes, all weapon/upgrade checks, audiovisual review and recordings remain in progress.\n\n'
readme.write_text(text.replace(anchor, paragraph + anchor, 1))
manifest = dict(checkpoint=DST.name, status='accepted-component-checkpoint-with-known-roster-defects', goal_complete=False,
    created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), promoted_from=SRC.name, copied_byte_identically=True,
    roms=roms, source_manifest=sources, source_archive=dict(path='source-v43.zip', sha256=sha(DST / 'source-v43.zip'),
    source_files=401, fresh_rebuild=str(rebuildp.relative_to(ROOT))), patches=patches,
    validation=dict(summary=str(rawp.relative_to(ROOT)), sha256=sha(rawp), bound_raw_logs=str(boundp.relative_to(ROOT)),
    bound_sha256=sha(boundp), case_count=761, single_full_run_all_passed=True, fixtures_unchanged=True),
    source_component=dict(negative=str(negativep.relative_to(ROOT)), negative_sha256=sha(negativep),
    positive=str(positivep.relative_to(ROOT)), positive_sha256=sha(positivep), cases=68, source_assertions_corrected=56),
    qa=str(qa.relative_to(ROOT)), qa_sha256=sha(qa),
    documentation_updates={'README.md': dict(archived_sha256=archived_readme, current_sha256=sha(readme), scope='Checkpoint paragraph after immutable source archive')},
    known_gaps=[gap.replace('Ryu wall/vine action gates and ', '') for gap in read(OLD / 'manifest.json')['known_gaps']] +
    ['Ryu admission gates fixed; full geometry/phase, slash-phase transfer/cancellation and source projectile-debit timing remain.'])
(DST / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('PROMOTED', roms, '761 full-run slots plus68 independent source cases; roster goal active', flush=True)
