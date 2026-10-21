"""Promote exact tested bytes, preserving the failed frozen-run provenance."""
from pathlib import Path
import datetime, hashlib, json, shutil, zipfile

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'build/checkpoints/roster-audit-v36-provisional-d'
DST=ROOT/'build/checkpoints/roster-audit-v36'
RAW=ROOT/'build/verification/summary-roster-audit-v36-provisional-d.json'
MIG=ROOT/'build/verification/weapon-input-v36-fixture-migration/summary.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def rel(path):return path.relative_to(ROOT).as_posix()
raw,mig=read(RAW),read(MIG)
assert raw['result']=='failed' and len(raw['cases'])==758
assert raw['failures']==['ryu-weapons failed for smb-crossover-mmc3']
assert raw['fixture_hashes_before']==raw['fixture_hashes_after'] and not raw['changed_fixtures']
assert mig['result']=='passed' and len(mig['cases'])==4
assert mig['fixture_hashes_before']==mig['fixture_hashes_after']
assert all(c['result']=='passed' and c['exit']==0 for c in mig['cases'])
current={p.relative_to(ROOT).as_posix():sha(p) for p in sorted((ROOT/'tests').rglob('*')) if p.is_file()}
current['tools/run_mesen.py']=sha(ROOT/'tools/run_mesen.py')
delta=[k for k in current.keys()|raw['fixture_hashes_after'].keys() if current.get(k)!=raw['fixture_hashes_after'].get(k)]
assert delta==['tests/expanded-weapons.lua'],delta
assert current['tests/expanded-weapons.lua']==mig['after_sha256']
cases={(c['test'],c['rom']):c for c in raw['cases']}
for c in mig['cases']:
    cases[(c['test'],c['rom'])]={'test':c['test'],'rom':c['rom'],'result':'passed','validation':'post-run fixture migration; original assertions retained','log':c['log'],'log_sha256':c['log_sha256']}
assert len(cases)==759 and all(c['result']=='passed' for c in cases.values())
roms={f'smb-crossover-{m}.nes':sha(SRC/f'smb-crossover-{m}.nes') for m in ('mmc3','mmc5')}
assert {m:roms[f'smb-crossover-{m}.nes'] for m in ('mmc3','mmc5')}==raw['roms']
for m in ('mmc3','mmc5'):
    unit=read(ROOT/f'build/verification/outline-cache-v36d-{m}-unit.json')
    assert unit['result']=='passed' and unit['cases']==909 and unit['rom_sha256']==roms[f'smb-crossover-{m}.nes']
    unit=read(ROOT/f'build/verification/weapon-admission-v36b-v36d-{m}.json')
    assert unit['result']=='passed' and unit['cases']==1872 and unit['after_sha256']==roms[f'smb-crossover-{m}.nes']
perf=read(ROOT/'build/profiling/plain-walking-v35-v36d-comparison.json')
assert perf['canonical_mismatch_count']==0 and sum(c['canonical_rows']for c in perf['runs'])==14400
rebuild=read(ROOT/'build/checkpoint-tests/source-v36d-rebuild-smoke/report.json')
assert all(c['equal'] and c['exit']==0 and c['sha256']==roms[f"smb-crossover-{c['mapper']}.nes"] for c in rebuild['cases'])
archive=SRC/'source-v36d.zip'
assert sha(archive)==rebuild['archive_sha256']
with zipfile.ZipFile(archive)as z:
    source_manifest={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
    archive_index=json.loads(z.read('archived-file-hashes.json'))
assert len(source_manifest)==400
archive_index_sha=source_manifest.pop('archived-file-hashes.json')
assert archive_index==source_manifest,'Generated archive index exactly binds its399 source/build files'
source_delta=[n for n,h in source_manifest.items() if not(ROOT/n).is_file() or sha(ROOT/n)!=h]
assert source_delta==['README.md'],source_delta
baseline=sha(ROOT/'build/smb-crossover-mmc3-baseline.nes')
assert baseline=='0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'
assert not DST.exists(),'Immutable accepted checkpoint must not be overwritten'
DST.mkdir()
for mapper in ('mmc3','mmc5'):
    for ext in ('.nes','.lbl','.dbg','.lst','.map'):
        source=SRC/f'smb-crossover-{mapper}{ext}'
        shutil.copyfile(source,DST/source.name)
        assert sha(source)==sha(DST/source.name)
shutil.copyfile(archive,DST/'source-v36.zip')
consolidated={
 'result':'passed-consolidated-component-slots', 'cases':sorted(cases.values(),key=lambda c:(c['rom'],c['test'])),
 'case_count':759, 'all_slots_passed':True, 'single_full_run_all_passed':False,
 'runtime_unchanged_during_fixture_migration':True, 'roms':roms,
 'original_frozen_run':{'summary':rel(RAW),'sha256':sha(RAW),'result':'failed','passed_slots':758,'failed_slots':1,'fixtures_unchanged_during_run':True},
 'fixture_migration':{'summary':rel(MIG),'sha256':sha(MIG),'affected_slots':4,'all_passed':True,'changed_fixture':delta[0],'before_sha256':mig['before_sha256'],'after_sha256':mig['after_sha256']},
 'scope':'Component verification; not all final-hash routes, complete source parity, physical hardware testing or final video completion',
}
summary=ROOT/'build/verification/summary-roster-audit-v36-consolidated.json'
summary.write_text(json.dumps(consolidated,indent=2)+'\n')
manifest={
 'checkpoint':'roster-audit-v36','status':'accepted-component-checkpoint-with-known-roster-defects',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'promoted_from':SRC.name+'; copied byte-identically after the frozen run closed and four corrected fixture slots passed',
 'roms':roms,'source_manifest':source_manifest,
 'source_archive':{'path':'source-v36.zip','sha256':sha(DST/'source-v36.zip'),'bytes':(DST/'source-v36.zip').stat().st_size,'fresh_extraction_rebuild':'build/checkpoint-tests/source-v36d-rebuild-smoke/report.json','both_roms_byte_identical':True,'generated_index':{'path':'archived-file-hashes.json','sha256':archive_index_sha,'verified399_source_files':True}},
 'validation':{'consolidated_summary':rel(summary),'sha256':sha(summary),'case_count':759,'all_slots_passed':True,'single_full_run_all_passed':False,'original_summary':rel(RAW),'original_log':'build/verification/roster-audit-v36d-full.log','original_log_sha256':sha(ROOT/'build/verification/roster-audit-v36d-full.log'),'migration_summary':rel(MIG),'input_timing_report':'build/verification/ryu-weapons-v36d-input-timing-report.json'},
 'performance_report':'build/profiling/plain-walking-v35-v36d-comparison.json',
 'read_only_followup':'build/profiling/samus-outer-followup-v36/report.json',
 'qa':'docs/qa/crowd-performance-v36.md','baseline_sha256':baseline,
 'known_gaps':['Normal Simon/Ryu pose-dependent geometry and Simon recoil ceiling transition remain.','Samus/Mega Man still have30-draw four-Goomba cases and dense scenes still lag.','Hardware scanline sprite limits remain.','All exact-final-hash roster routes, attacks/upgrades and final recordings are incomplete.'],
 'documentation_updates':{'README.md':{'archived_sha256':source_manifest['README.md'],'current_sha256':sha(ROOT/'README.md'),'reason':'Post-validation component ledger; source archive retains recorded bytes.'},'docs/qa/crowd-performance-v36.md':{'sha256':sha(ROOT/'docs/qa/crowd-performance-v36.md'),'reason':'Validation/performance ledger separate from build inputs.'}},
}
(DST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PROMOTED',roms,'759 consolidated slots; original frozen run758/759 and corrected4/4, no single-green-run claim')
