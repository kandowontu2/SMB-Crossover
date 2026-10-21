"""Accept only the bounded45 component; retain source negatives and open goals."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'build/checkpoints/roster-audit-v45-provisional-b'
FIRST = ROOT / 'build/checkpoints/roster-audit-v45-provisional-a'
OLD = ROOT / 'build/checkpoints/roster-audit-v44'
DST = ROOT / 'build/checkpoints/roster-audit-v45'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
assert not DST.exists(), 'Never overwrite an accepted checkpoint'
candidate = read(SRC / 'candidate.json')
roms = {m:sha(SRC / f'smb-crossover-{m}.nes') for m in ('mmc3','mmc5')}
assert roms == {m:q['sha256'] for m,q in candidate['roms'].items()}
for m in roms:
    for ext in ('.nes','.dbg','.lbl','.map','.lst'):
        assert sha(SRC / f'smb-crossover-{m}{ext}') == sha(FIRST / f'smb-crossover-{m}{ext}')
assert all(sha(ROOT/n)==h for n,h in candidate['patches'].items())
summary = ROOT / 'build/verification/summary-roster-audit-v45-provisional-b.json'
boundp = SRC / 'validation/bound-summary.json'
raw,bound = read(summary),read(boundp)
assert raw['result'] == bound['result'] == 'passed'
assert len(raw['cases']) == bound['case_count'] == bound['passed'] == 761
assert bound['failed'] == 0 and bound['single_full_run'] and not raw['failures']
assert raw['fixture_hashes_before'] == raw['fixture_hashes_after'] and not raw['changed_fixtures']
assert all(sha(ROOT/n)==h for n,h in raw['fixture_hashes_after'].items())
previous = read(ROOT / 'build/verification/summary-roster-audit-v45-provisional-a.json')
changed = {n for n,h in previous['fixture_hashes_after'].items() if raw['fixture_hashes_after'][n]!=h}
assert changed == {'tests/link-sword-timing.lua'}
assert raw['roms'] == bound['roms'] == roms and bound['summary_sha256'] == sha(summary)
assert all(sha(ROOT/q['log']) == q['log_sha256'] for q in bound['cases'])
negative = read(FIRST / 'validation/bound-summary.json')
assert negative['single_full_run'] and negative['passed']==760 and negative['failed']==1
assert all(sha(ROOT/q['log'])==q['log_sha256'] for q in negative['cases'])
proofs = {}
def retain(name, relative):
    p=ROOT/relative
    proofs[name]=dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
    return read(p)

review = retain('link_observer_review','build/verification/ryu-compatibility45-readonly/link-observer-review.json')
assert review['original_assertions_inputs_arena_writes_unchanged'] and review['reconstructed_original_text_exact']
assert review['guarded_fixture_sha256']==sha(ROOT/'tests/link-sword-timing.lua')
assert review['original_fixture_sha256']==previous['fixture_hashes_after']['tests/link-sword-timing.lua']
layout = retain('compiled_compatibility','build/verification/ryu-compatibility45-readonly/compiled-report.json')
assert sha(ROOT/proofs['compiled_compatibility']['path'])=='6d07645376f78f3d1844ccb9665ffdf6ce3281e189ec432aabbd429d5b91008f'
for q in layout['mappers']:
    assert q['after_sha256']==roms[q['mapper']] and q['before_sha256']==sha(OLD/f"smb-crossover-{q['mapper']}.nes")
    assert all(x['all_opcodes_and_mapped_operands_identical'] for x in q['mapped_regions'])
    assert q['compiled_no_Y_write_until_gate'] and q['entire_COLLISION_segment_identical_bytes']>3000
retain('compatibility_freeze','build/verification/ryu-compatibility45-readonly/freeze.json')
assert proofs['compatibility_freeze']['sha256']=='0479209d4d289fc71ed714e0d7b6a3980db9f7595129926407b020c52523defe'
cpu = retain('compiled_helper','build/verification/ryu-koopa-primary45-cpu-proof/summary.json')
assert cpu['result']=='both-mappers-pass-compiled-source-geometry-and-ABI' and cpu['total_final_cases']==1777188
for m,q in cpu['mappers'].items():
    assert q['rom_sha256']==roms[m]
    assert q['dbg_sha256']==sha(SRC/f'smb-crossover-{m}.dbg')
    assert q['lbl_sha256']==sha(SRC/f'smb-crossover-{m}.lbl')
    assert q['result_sha256']==sha(ROOT/'build/verification/ryu-koopa-primary45-cpu-proof'/q['result_file'])
retain('compiled_helper_receipt','build/verification/ryu-koopa-primary45-cpu-proof/receipt.json')
retain('static_budget_classification','build/verification/ryu-koopa-primary45-budget-triage/report.json')
retain('original_preparation_negative','build/checkpoints/roster-audit-v45-preparation-budget-negative-a/guard-negative.json')
retain('koopa44_negative','build/verification/ryu-koopa-primary45-proposal/frozen-B-negative-classification.json')
for name,path,total in (
    ('koopa_positive','build/verification/koopa-head-v45a-positive-b/report.json',56),
    ('lifecycle','build/verification/ryu-lifecycle45a-positive-a/report.json',40),
    ('admission','build/verification/ryu-gates45a-positive-a/report.json',68),
):
    d=retain(name,path)
    assert d['completed'] and d['total_cases']==total
    for q in d['runs']:
        assert q['exit']==0 and q['rom_sha256']==roms[q['mapper']]
        assert q['result']['completed']==q['result']['cases'] and q['result']['mismatches']==0 and not q['result']['failures']
        assert all(sha((ROOT/path).parent/n)==h for n,h in q['files'].items())
flare = retain('flare_positive','build/verification/bill-flare45a-terrain-actual-positive/source-positive-summary.json')
assert flare['total_passes']==52 and flare['ground_filter_positives']==32 and flare['unchanged_positive_controls']==20
assert flare['coverage_failures']==flare['source_disagreements']==0
for q in flare['per_mapper']:
    assert q['rom']['sha256']==roms[q['mapper']] and q['ground_noKill_noImpact']
for q in flare.values():
    if isinstance(q,dict) and 'path'in q and 'sha256'in q:assert sha(ROOT/q['path'])==q['sha256']
retain('flare44_negative','build/verification/bill-flare44-terrain-actual-negative/parent44-negative-summary.json')
obs = retain('historical_AV_observer','build/verification/bill-flare-v1-observer-candidate45a-first-a/report.json')
assert obs['status']=='passed-observer-inspection'
for q in obs['runs']:
    assert q['native_exit']==q['check_exit']==0 and q['rom_sha256']==roms[q['mapper']]
    assert all(sha(ROOT/n)==h for n,h in q['files'].items())
    inspection=read(ROOT/q['inspection'])
    assert inspection['complete_original_csv_byte_identity'] and inspection['full_csv_rows']==2400
    assert not inspection['actual_ground70_contacts'] and not inspection['qualified_case_slots'] and not inspection['mixed_case_slots']
crowds = retain('crowd_retention','build/verification/plain-walking-v44-v45b-crowd-retention-comparison.json')
assert crowds['canonical_mismatch_count']==0 and len(crowds['runs'])==3
for q in crowds['runs']:
    assert q['mapper']=='mmc5' and q['character'] in (1,2,9) and q['canonical_rows']==1200 and q['canonical_observation_fields']==204
for side,cp in (('before',OLD),('after',SRC)):
    d=read(Path(crowds[side])/'manifest.json')
    assert all(q['exit']==0 and q['rom_sha256']==sha(cp/'smb-crossover-mmc5.nes') for q in d['runs'])
archive=SRC/'source-v45b.zip'
rebuildp=ROOT/'build/checkpoint-tests/source-v45b-rebuild-smoke/report.json'
rebuild=read(rebuildp)
assert rebuild['archive_sha256']==sha(archive)
assert len(rebuild['cases'])==2 and all(q['exit']==0 and q['equal'] and q['sha256']==roms[q['mapper']] for q in rebuild['cases'])
with zipfile.ZipFile(archive) as z:
    sources=json.loads(z.read('archived-file-hashes.json'))
    assert len(sources)==401 and len(z.namelist())==402
    assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in sources.items())
assert all(sha(ROOT/n)==h for n,h in sources.items())
with zipfile.ZipFile(OLD/'source-v44.zip') as z:old_sources=json.loads(z.read('archived-file-hashes.json'))
assert {n for n in sources if sources[n]!=old_sources[n]}=={'README.md','src/megaman_weapons.s'}
for m in roms:
    x,y=(OLD/f'smb-crossover-{m}.nes').read_bytes(),(SRC/f'smb-crossover-{m}.nes').read_bytes()
    assert x[:16]==y[:16] and x[16+524288:]==y[16+524288:]
    def labels(p):return {n:int(v,16) for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.read_text(),re.M)}
    old,new=labels(OLD/f'smb-crossover-{m}.lbl'),labels(SRC/f'smb-crossover-{m}.lbl')
    assert all(new[n]==v for n,v in old.items() if v<0x8000 and n in new)
qa=ROOT/'docs/qa/roster-component-v45.md'
pending='Candidate45 is awaiting the complete corrected-observer regression run and linked compatibility review.'
assert pending in qa.read_text()
DST.mkdir()
for m in roms:
    for ext in ('.nes','.dbg','.lbl','.map','.lst'):
        p=SRC/f'smb-crossover-{m}{ext}';shutil.copyfile(p,DST/p.name);assert sha(p)==sha(DST/p.name)
shutil.copyfile(archive,DST/'source-v45.zip')
qa.write_text(qa.read_text().replace(pending,'Accepted component45 passes all761 corrected-observer regression slots in one complete run and the linked compatibility review.',1))
readme=ROOT/'README.md';archived_readme=sha(readme);text=readme.read_text()
anchor='The [v44 component update]';assert anchor in text and '[v45 component update]' not in text
paragraph=('The [v45 component update](docs/qa/roster-component-v45.md) repairs normal Ryu sword admission against Koopa head rectangles and makes Bill Flare pass through non-brick terrain. All761 regression slots pass after a bank-aware Link test-hook correction; the original failure is preserved. Source-backed native components, compiled helper checks and fresh archive rebuilds pass. Dense-crowd flicker and the full roster/weapon/recording audit remain open. ROMs are in `build/checkpoints/roster-audit-v45/`.\n\n')
readme.write_text(text.replace(anchor,paragraph+anchor,1))
manifest=dict(checkpoint=DST.name,status='accepted-component-checkpoint-with-known-roster-defects',goal_complete=False,
    created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent=OLD.name,promoted_from=SRC.name,
    roms=roms,copied_byte_identically=True,patches=candidate['patches'],proofs=proofs,source_manifest=sources,
    source_archive=dict(path='source-v45.zip',sha256=sha(DST/'source-v45.zip'),source_files=401,fresh_rebuild=str(rebuildp.relative_to(ROOT)),rebuild_report_sha256=sha(rebuildp)),
    validation=dict(summary=str(summary.relative_to(ROOT)),sha256=sha(summary),bound_raw_logs=str(boundp.relative_to(ROOT)),bound_sha256=sha(boundp),case_count=761,single_full_run_all_passed=True,
        fixtures_unchanged_during_run=True,only_prior_fixture_change='tests/link-sword-timing.lua physical bank/entry-byte admission; all original assertions preserved',prior_failed_full_run=str((FIRST/'validation/bound-summary.json').relative_to(ROOT))),
    qa=str(qa.relative_to(ROOT)),qa_sha256=sha(qa),documentation_updates={'README.md':dict(archived_sha256=archived_readme,current_sha256=sha(readme))},
    known_gaps=['All14 final-hash normal routes1-1..2-2, every special/alternate/upgrade and final lossless audiovisual review remain incomplete.',
        'Dense-scene lag/flicker and individual redraw regressions remain; no universal performance improvement claimed.',
        'Koopa walking-to-shell lifecycle, upgraded33/winged IDs and full source subpixel/cache geometry are outside this component.',
        'Bill Flare angle/prone anchor/mixed count/visibility require separate actual negatives and repairs.',
        'Final recording space headroom remains constrained; conservative guard remains unchanged.'])
(DST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PROMOTED bounded45 component',roms,'goal remains active',flush=True)
