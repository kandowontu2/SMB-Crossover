"""Accept41e after staged current-ROM validation, controls and rebuild."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'build/checkpoints/roster-audit-v41-provisional-e'
DST=ROOT/'build/checkpoints/roster-audit-v41'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
raw_path=ROOT/'build/verification/summary-roster-audit-v41-provisional-e.json'
raw=read(raw_path)
assert raw['result']=='passed'and len(raw['cases'])==761
assert not raw['failures']and not raw['changed_fixtures']
assert raw['single_full_run']is False
assert sum(c['rom']=='smb-crossover-mmc5'for c in raw['cases'])==378
assert len(raw['cases'])-378==383
assert raw['fixture_hashes_before']==raw['fixture_hashes_after']
assert all(sha(ROOT/n)==h for n,h in raw['fixture_hashes_after'].items())
roms={m:sha(SRC/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
assert roms==raw['roms']
assert roms['mmc3']==sha(ROOT/'build/checkpoints/roster-audit-v41-provisional-a/smb-crossover-mmc3.nes')
old=ROOT/'build/checkpoints/roster-audit-v40/smb-crossover-mmc5.nes'
for bank in(7,9,11,12,14,15,16,17,18,23,24,25,26,27,28,29,38,62,63):
 assert old.read_bytes()[16+bank*8192:16+(bank+1)*8192]==(SRC/'smb-crossover-mmc5.nes').read_bytes()[16+bank*8192:16+(bank+1)*8192],('Inherited audio/resident bank',bank)
unit_path=ROOT/'build/profiling/special-empty-v41a-v41e-mmc5.json'
unit=read(unit_path)
assert unit['result']=='passed'and unit['cases']==1624 and unit['after_sha256']==roms['mmc5']
assert unit['before_sha256']==sha(ROOT/'build/checkpoints/roster-audit-v41-provisional-a/smb-crossover-mmc5.nes')
assert unit['script_sha256']==sha(ROOT/'tools/profiling/verify_special_empty_v41.py')
simon_path=ROOT/'build/verification/simon-walkoff-v41e-positive/report.json'
simon=read(simon_path)
assert simon['fixture_sha256']=='3bfe5df63cf0df9a4621c740aab1da5a06ce76622f181d05ff48c12c0cd06046'
assert sha(ROOT/'build/verification/simon-walkoff-v40-component-b/component.lua')==simon['fixture_sha256']
for m in roms:
 r=simon['mappers'][m]
 assert r['exit']==0 and r['rom_sha256']==roms[m]and r['result']['completed']==12 and r['result']['mismatches']==0
perf_path=ROOT/'build/profiling/plain-walking-v40c-v41e-bass-aligned-comparison.json'
perf=read(perf_path)
assert perf['canonical_mismatch_count']==0 and sum(r['canonical_rows']for r in perf['runs'])==2400
assert all(r['canonical_observation_fields']==204 for r in perf['runs'])
frame_neg=[];draw_neg=[]
for r in perf['runs']:
 for s in r['scenes']:
  if s['drawAllCalls']['after']<s['drawAllCalls']['before']:
   draw_neg.append((r['character'],s['scene'],s['drawAllCalls']))
  assert s['meanForegroundExcludingDrawCycles']['after']<s['meanForegroundExcludingDrawCycles']['before']
  if s['physicalFrames']['after']>s['physicalFrames']['before']:
   frame_neg.append((r['character'],s['scene'],s['physicalFrames'],s['drawAllCalls']))
assert frame_neg==[(9,19,{'before':59.0,'after':60.0},{'before':37,'after':44})],frame_neg
assert draw_neg==[(1,18,{'before':60,'after':59})],draw_neg
other_path=ROOT/'build/profiling/plain-walking-v40c-v41e-other-comparison.json'
other=read(other_path)
assert other['canonical_mismatch_count']==0 and sum(r['canonical_rows']for r in other['runs'])==6000
assert len(other['runs'])==5 and all(r['canonical_observation_fields']==204 for r in other['runs'])
assert all(s['physicalFrames']['after']==s['physicalFrames']['before']and s['drawAllCalls']['after']==s['drawAllCalls']['before']for r in other['runs']for s in r['scenes'])
repeat_path=ROOT/'build/profiling/plain-walking-v40c-v41e-bass-repeated-comparison.json'
repeat=read(repeat_path)
assert repeat['canonical_mismatch_count']==0 and len(repeat['runs'])==1
assert repeat['runs'][0]['canonical_rows']==1200 and repeat['runs'][0]['canonical_observation_fields']==204
ss=repeat['runs'][0]['scenes']
assert all(s['drawAllCalls']['after']>=s['drawAllCalls']['before']for s in ss)
totals={k:{side:sum(s[k][side]for s in ss)for side in('before','after')}for k in('physicalFrames','drawAllCalls')}
assert totals=={'physicalFrames':{'before':1200.0,'after':1199.0},'drawAllCalls':{'before':881,'after':1053}}
phase_path=ROOT/'build/profiling/bass-step-v40c-v41d-first-phase.json'
phase=read(phase_path)
assert phase['before_canonical_equals_main']and phase['after_canonical_equals_main']
rebuild_path=ROOT/'build/checkpoint-tests/source-v41e-rebuild-smoke/report.json'
rebuild=read(rebuild_path);archive=SRC/'source-v41e.zip'
assert sha(archive)==rebuild['archive_sha256']
assert len(rebuild['cases'])==2 and all(c['exit']==0 and c['equal']and c['sha256']==roms[c['mapper']]for c in rebuild['cases'])
with zipfile.ZipFile(archive)as z:
 sources=json.loads(z.read('archived-file-hashes.json'))
 assert len(sources)==401 and len(z.namelist())==402
 assert sources=={n:hashlib.sha256(z.read(n)).hexdigest()for n in sources}
assert sources=={n:sha(ROOT/n)for n in sources},'Frozen build inputs remain exact'
qa=ROOT/'docs/qa/roster-component-v41.md'
assert 'Accepted component checkpoint' in qa.read_text()
assert not DST.exists(),'Never replace an accepted checkpoint'
DST.mkdir()
for m in roms:
 for ext in('.nes','.lbl','.dbg','.lst','.map'):
  p=SRC/f'smb-crossover-{m}{ext}';shutil.copyfile(p,DST/p.name);assert sha(p)==sha(DST/p.name)
shutil.copyfile(archive,DST/'source-v41.zip')
readme=ROOT/'README.md';readme_before=sha(readme)
text=readme.read_text()
anchor='The loading screen also waits for queued VRAM columns to be consumed'
assert anchor in text and '[v41 component update]'not in text
paragraph="The [v41 component update](docs/qa/roster-component-v41.md) fixes Simon's unused air jump after walking off support and skips empty Mega Man/Bass special-weapon loops on MMC5. Staged validation covers all 761 current-ROM slots: MMC3 stays byte identical to its complete initial checks, and all MMC5 slots run again after a retained Water Shield budget failure was corrected. All 9,600 paired crowd gameplay samples match. Default outlines-off four-Goomba walking redraws improve from 30 to 35 for Mega Man and from 37 to 44 for Bass. Dense scenes still lag; small counterexamples, source geometry and a newly traced catch-up-frame HUD race remain documented. Accepted component ROMs are in `build/checkpoints/roster-audit-v41/`; final roster fixes and recordings remain in progress.\n\n"
readme.write_text(text.replace(anchor,paragraph+anchor,1))
manifest={'checkpoint':DST.name,'status':'accepted-component-checkpoint-with-known-roster-defects','goal_complete':False,
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'promoted_from':SRC.name,'copied_byte_identically':True,'roms':roms,
 'source_manifest':sources,'source_archive':{'path':'source-v41.zip','sha256':sha(DST/'source-v41.zip'),'source_files':401,'fresh_rebuild':str(rebuild_path.relative_to(ROOT))},
 'validation':{'summary':str(raw_path.relative_to(ROOT)),'sha256':sha(raw_path),'case_count':761,'single_full_run_all_passed':False,'all_current_ROM_slots_passed':True,'fixtures_unchanged':True,'method':raw['method'],'log':'build/verification/roster-audit-v41e-staged.log','log_sha256':sha(ROOT/'build/verification/roster-audit-v41e-staged.log'),'retained_initial_failure':'build/verification/summary-roster-audit-v41-provisional-d.json'},
 'compiled_units':str(unit_path.relative_to(ROOT)),'simon_independent_component':str(simon_path.relative_to(ROOT)),
 'performance':[str(perf_path.relative_to(ROOT)),str(other_path.relative_to(ROOT)),str(repeat_path.relative_to(ROOT))],
 'performance_retained_frame_counterexample':frame_neg,'performance_retained_draw_counterexample':draw_neg,'repeated_bass_aggregate':totals,
 'preserved_setup_negative':'build/profiling/plain-walking-v40c-v41d-empty-comparison.json','setup_diagnosis':str(phase_path.relative_to(ROOT)),
 'rejected_prototypes':['build/build-v41b-mmc3.log','build/checkpoints/roster-audit-v41-provisional-c/candidate.json','build/checkpoints/roster-audit-v41-provisional-d/candidate.json'],
 'qa':str(qa.relative_to(ROOT)),'qa_sha256':sha(qa),
 'documentation_updates':{'README.md':{'archived_sha256':readme_before,'current_sha256':sha(readme),'scope':'Post-acceptance checkpoint paragraph only; source archive retains its exact pre-update README'}},
 'known_gaps':['Dense crowds still lag and hardware scanline limits still flicker.','One-frame Bass and one-draw MM counterexamples retained; no per-scene zero-regression claim.','Four inherited38 crowd regressions against37 remain qualified.','Simon/Ryu source geometry, attack-phase and cached water lifecycle pending.','Ryu40/41 illegal primary wall sword and vine attacks remain independently reproduced; fix pending.','Sophia38d passive route finds normal NMI consuming a partially published timer command during catch-up; root42 fix/reproduction pending.','Bill Flare source angle/handedness/cap/terrain disagreements are being independently bound.','Exact-final-hash all-character routes, every attack/upgrade and final recordings incomplete.','Older34/34b/38d/40 route proofs do not certify41.','No physical cartridge or source-perfect claim.']}
(DST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PROMOTED',roms,'761 unchanged-fixture checks; roster goal remains active',flush=True)
