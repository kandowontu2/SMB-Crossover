"""Accept40c only after the single frozen full run and independent audio proofs."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'build/checkpoints/roster-audit-v40-provisional-c'
DST=ROOT/'build/checkpoints/roster-audit-v40'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
raw_path=ROOT/'build/verification/summary-roster-audit-v40-provisional-c.json'
raw=read(raw_path)
assert raw['result']=='passed'and len(raw['cases'])==761
assert not raw['failures']and not raw['changed_fixtures']
assert raw['fixture_hashes_before']==raw['fixture_hashes_after']
assert all(sha(ROOT/n)==h for n,h in raw['fixture_hashes_after'].items())
roms={m:sha(SRC/f'smb-crossover-{m}.nes')for m in ('mmc3','mmc5')}
assert roms==raw['roms']
assert roms['mmc3']==sha(ROOT/'build/checkpoints/roster-audit-v39/smb-crossover-mmc3.nes')
unit_path=ROOT/'build/profiling/mm3-multiply-v39-v40a-mmc5.json'
unit=read(unit_path)
assert unit['result']=='passed'and unit['cases']==131072 and unit['scope']=='Actual compiled routine comparison'
a=ROOT/'build/checkpoints/roster-audit-v40-provisional-a/smb-crossover-mmc5.nes'
assert sha(a)==unit['after_sha256']
assert a.read_bytes()[16+11*8192:16+12*8192]==(SRC/'smb-crossover-mmc5.nes').read_bytes()[16+11*8192:16+12*8192]
outer_path=ROOT/'build/profiling/mm-audio-outer-v39-v40c-mmc5.json'
outer=read(outer_path)
assert outer['result']=='passed'and outer['cases']==16008 and outer['after_sha256']==roms['mmc5']
assert outer['hardware_multiply_calls']==6440 and outer['stats']['AudioUpdate']['max_delta']==0
assert outer['script_sha256']==sha(ROOT/'tools/profiling/verify_mm_audio_v40.py')
hardware_path=ROOT/'build/profiling/mmc5-multiplier-ownership-v40c/report.json'
hardware=read(hardware_path)
assert hardware['result']=='passed'and hardware['rom_sha256']==roms['mmc5']
assert hardware['apu_records']==20181 and hardware['apu_matches_immutable_reference']and hardware['lag_nmis']>0
assert hardware['transactions']>50 and hardware['nmis']>500 and hardware['irqs']>100
perf_path=ROOT/'build/profiling/plain-walking-v39-v40c-step-aligned-comparison.json'
other_path=ROOT/'build/profiling/plain-walking-v39-v40c-other-comparison.json'
for path,expected_runs,expected_updates in ((perf_path,2,2400),(other_path,5,6000)):
 perf=read(path)
 assert perf['canonical_mismatch_count']==0 and len(perf['runs'])==expected_runs
 assert sum(r['canonical_rows']for r in perf['runs'])==expected_updates
 assert all(s['physicalFrames']['after']<=s['physicalFrames']['before']and s['drawAllCalls']['after']>=s['drawAllCalls']['before']for r in perf['runs']for s in r['scenes'])
rebuild_path=ROOT/'build/checkpoint-tests/source-v40c-rebuild-smoke/report.json'
rebuild=read(rebuild_path);archive=SRC/'source-v40c.zip'
assert sha(archive)==rebuild['archive_sha256']
assert len(rebuild['cases'])==2 and all(c['exit']==0 and c['equal']and c['sha256']==roms[c['mapper']]for c in rebuild['cases'])
with zipfile.ZipFile(archive)as z:
 sources=json.loads(z.read('archived-file-hashes.json'))
 assert len(sources)==401 and len(z.namelist())==402
 assert sources=={n:hashlib.sha256(z.read(n)).hexdigest()for n in sources}
assert sources=={n:sha(ROOT/n)for n in sources},'Frozen build inputs remain exact'
qa=ROOT/'docs/qa/crowd-performance-v40.md'
assert qa.exists()and 'Accepted component checkpoint' in qa.read_text()
assert not DST.exists(),'Never replace an accepted checkpoint'
DST.mkdir()
for m in roms:
 for ext in ('.nes','.lbl','.dbg','.lst','.map'):
  p=SRC/f'smb-crossover-{m}{ext}';shutil.copyfile(p,DST/p.name);assert sha(p)==sha(DST/p.name)
shutil.copyfile(archive,DST/'source-v40.zip')
manifest={'checkpoint':DST.name,'status':'accepted-component-checkpoint-with-known-roster-defects','goal_complete':False,
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'promoted_from':SRC.name,'copied_byte_identically':True,'roms':roms,
 'source_manifest':sources,'source_archive':{'path':'source-v40.zip','sha256':sha(DST/'source-v40.zip'),'source_files':401,'fresh_rebuild':str(rebuild_path.relative_to(ROOT))},
 'validation':{'summary':str(raw_path.relative_to(ROOT)),'sha256':sha(raw_path),'case_count':761,'single_full_run_all_passed':True,'fixtures_unchanged':True,'log':'build/verification/roster-audit-v40c-full.log','log_sha256':sha(ROOT/'build/verification/roster-audit-v40c-full.log')},
 'unit':{'report':str(unit_path.relative_to(ROOT)),'MM3_bank11_identical_40a_to_40c':True},'audio_lifecycle':str(outer_path.relative_to(ROOT)),'hardware_ownership':str(hardware_path.relative_to(ROOT)),
 'performance':[str(perf_path.relative_to(ROOT)),str(other_path.relative_to(ROOT))],
 'preserved_benchmark_negative':'build/profiling/plain-walking-v39-v40c-megaman-comparison.json','setup_diagnosis':'build/profiling/step-timer-v39-v40c-first-phase.json',
 'rejected_prototype':'build/checkpoints/roster-audit-v40-provisional-b/candidate.json','qa':str(qa.relative_to(ROOT)),'qa_sha256':sha(qa),
 'known_gaps':['Four-Goomba MM walking and dense scenes still lag; scanline sprite limits remain.','Known inherited38 regressions retained against37;40 comparisons use39.','Simon/Ryu current and cached source geometry, Simon hurt ceiling, Simon walk-off double jump.','Exact-final-hash all-character routes, every attack/upgrade and final recordings incomplete.','Older34/34b/38d proofs do not certify40.','No physical cartridge or source-perfect port claim.']}
(DST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PROMOTED',roms,'761 unchanged-fixture component checks; full roster goal remains active')
