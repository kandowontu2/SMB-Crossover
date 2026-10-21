"""Accept42e only after frozen native, source, audio and crowd controls pass."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'build/checkpoints/roster-audit-v42-provisional-e'
DST=ROOT/'build/checkpoints/roster-audit-v42'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rawp=ROOT/'build/verification/summary-roster-audit-v42-provisional-e.json'
raw=read(rawp);boundp=SRC/'validation/bound-summary.json';bound=read(boundp)
assert raw['result']==bound['result']=='passed'and len(raw['cases'])==bound['case_count']==761
assert bound['passed']==761 and bound['failed']==0 and bound['single_full_run']
assert not raw['failures']and not raw['changed_fixtures']
assert raw['fixture_hashes_before']==raw['fixture_hashes_after']
assert all(sha(ROOT/n)==h for n,h in raw['fixture_hashes_after'].items())
assert bound['summary_sha256']==sha(rawp)
assert all(sha(ROOT/c['log'])==c['log_sha256']for c in bound['cases'])
roms={m:sha(SRC/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
assert roms==raw['roms']==bound['roms']
assert roms=={'mmc3':'b3d6efe9d146c29c299d67f9410f392e65c921e36aa20eee58d719c3253cde0a',
 'mmc5':'796edc52ecf567cac2b7dbbb3100ac3921a6740783825bd6d9660c0069548181'}
unitp=ROOT/'build/verification/mm-bass-audio-v42-proof/candidate-e-layout-exact.json'
unit=read(unitp)
assert unit['result']=='passed'and unit['cases']==20326 and unit['after_sha256']==roms['mmc5']
assert unit['before_sha256']==sha(ROOT/'build/checkpoints/roster-audit-v42-provisional-a/smb-crossover-mmc5.nes')
assert unit['script_sha256']==sha(ROOT/'build/verification/mm-bass-audio-v42-proof/verify_compiled_audio.py')
assert unit['matched_branch_conditions']==5652681 and len(unit['branch_page_cross_differences'])==6
audio_receipt=ROOT/'build/verification/mm-bass-audio-v42-proof/receipt-e.json'
assert read(audio_receipt)['after_sha256']==roms['mmc5']
hardwarep=ROOT/'build/profiling/mmc5-multiplier-ownership-v42e/report.json';hardware=read(hardwarep)
assert hardware['result']=='passed'and hardware['rom_sha256']==roms['mmc5']
assert hardware['transactions']==63 and hardware['apu_records']==20181 and hardware['apu_matches_immutable_reference']
assert hardware['apu_sha256']==sha(hardwarep.parent/'guest-audio-flush.bin')
assert hardware['fixture_sha256']==sha(ROOT/'tests/guest-audio-flush-differential.lua')
hudp=ROOT/'build/roster-through-2-2/sophia-42e-hud-joy-k-11-v0-mmc3/native-controller-receipt.json'
hud=read(hudp);protection=hud['protection']
assert hud['rom_sha256']==roms['mmc3']and protection['protected_body_observations']==5217
assert not protection['protected_body_not_busy255']and protection['SetupNums_observations']==678
assert protection['SetupNums_not_busy255_count']==0 and hud['bad_static_HUD']is None and hud['malformed_commands']==0
assert hud['native_read_completions']==5181 and hud['all_eight_bits']and hud['all_reads_guarded_NMI1_IRQ0_PRG63']
assert hud['max_immediate_catchups_per_group']==1 and hud['max_protected_bodies_per_group']==2
assert hud['max_sample_gap_continuous_active']==3,'Retain the observed three-frame input cost'
for n,h in hud['sha256'].items():assert sha(hudp.parent/n)==h,(n,'Changed passive evidence')
perfpaths=[ROOT/'build/profiling'/n for n in('plain-walking-v41e-v42e-final-comparison.json',
 'plain-walking-v41e-v42e-samus-comparison.json','plain-walking-v41-v42e-four-repeat-comparison.json')]
perfs=[read(p)for p in perfpaths]
assert all(p['canonical_mismatch_count']==0 for p in perfs)
assert sum(r['canonical_rows']for p in perfs for r in p['runs'])==6000
assert all(r['canonical_observation_fields']==204 for p in perfs for r in p['runs'])
for p in perfs:
 manifest=read(Path(p['after'])/'manifest.json')
 assert all(r['exit']==0 and r['rom_sha256']==roms[r['mapper']]for r in manifest['runs'])
repeat_totals={r['character']:{k:{side:sum(s[k][side]for s in r['scenes'])for side in('before','after')}
 for k in('physicalFrames','drawAllCalls')}for r in perfs[2]['runs']}
assert repeat_totals=={1:{'physicalFrames':{'before':1200.,'after':1200.},'drawAllCalls':{'before':1104,'after':1119}},
 9:{'physicalFrames':{'before':1197.,'after':1198.},'drawAllCalls':{'before':904,'after':925}}}
archive=SRC/'source-v42e.zip';rebuildp=ROOT/'build/checkpoint-tests/source-v42e-rebuild-smoke/report.json';rebuild=read(rebuildp)
assert sha(archive)==rebuild['archive_sha256']
assert len(rebuild['cases'])==2 and all(c['exit']==0 and c['equal']and c['sha256']==roms[c['mapper']]for c in rebuild['cases'])
with zipfile.ZipFile(archive)as z:
 sources=json.loads(z.read('archived-file-hashes.json'))
 assert len(sources)==401 and len(z.namelist())==402
 assert sources=={n:hashlib.sha256(z.read(n)).hexdigest()for n in sources}
assert sources=={n:sha(ROOT/n)for n in sources},'Frozen build inputs remain exact'
def labels(path):return {n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',path.read_text(),re.M)}
for m in roms:
 old=ROOT/f'build/checkpoints/roster-audit-v41/smb-crossover-{m}.nes';new=SRC/old.name
 O,N=labels(old.with_suffix('.lbl')),labels(new.with_suffix('.lbl'))
 assert all(N[n]==v for n,v in O.items()if v<0x8000 and n in N),'Unchanged RAM ABI'
 assert N['GuestGameRoutinesBridge']==0xe025 and N['OAMandReadJoypad']==0xe000
 assert old.read_bytes()[16+63*8192:16+63*8192+37]==new.read_bytes()[16+63*8192:16+63*8192+37]
 start=16+62*8192+O['GuestGameRoutinesBridge']-0x8000
 assert old.read_bytes()[start:start+41]==new.read_bytes()[16+63*8192+37:16+63*8192+78],'Unchanged resident injury bridge'
oldfull=read(ROOT/'build/checkpoints/roster-audit-v42-provisional-b/validation/bound-summary.json')
assert oldfull['passed']==754 and oldfull['failed']==7 and oldfull['result']=='failed'
oldstack=read(ROOT/'build/checkpoints/roster-audit-v42-provisional-d/validation/bound-summary.json')
assert oldstack['passed']==759 and oldstack['failed']==2 and oldstack['result']=='failed'
qa=ROOT/'docs/qa/roster-component-v42.md'
assert 'Candidate42e is awaiting' in qa.read_text()
assert not DST.exists(),'Never overwrite an accepted checkpoint'
DST.mkdir()
for m in roms:
 for ext in('.nes','.lbl','.dbg','.map','.lst'):
  p=SRC/f'smb-crossover-{m}{ext}';shutil.copyfile(p,DST/p.name);assert sha(p)==sha(DST/p.name)
shutil.copyfile(archive,DST/'source-v42.zip')
qa.write_text(qa.read_text().replace('Candidate42e is awaiting the complete emulator suite.',
 'Accepted component checkpoint42e passed all761 unchanged-fixture emulator slots in one full run.\nMario matches the baseline replay in all19 fields for521 frames. The401-file\nsource archive rebuilds both ROMs byte identically from fresh extraction.',1))
readme=ROOT/'README.md';readme_before=sha(readme);text=readme.read_text()
anchor='The loading screen also waits for queued VRAM columns to be consumed'
assert anchor in text and '[v42 component update]'not in text
paragraph="The [v42 component update](docs/qa/roster-component-v42.md) protects catch-up graphics publication, bounds catch-up work, and reduces MMC5 native MM/Bass audio overhead. All 761 unchanged-fixture emulator slots pass in one full run; 20,326 compiled audio cases and 6,000 paired crowd updates retain their checked state. The HUD corruption cause, rejected prototypes, individual redraw regressions and a remaining three-frame native-input gap are documented. Outlines stay off by default with a gold option row. ROMs are in `build/checkpoints/roster-audit-v42/`; dense-scene lag and the full roster/weapon/recording audit remain in progress.\n\n"
readme.write_text(text.replace(anchor,paragraph+anchor,1))
manifest={'checkpoint':DST.name,'status':'accepted-component-checkpoint-with-known-roster-defects','goal_complete':False,
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'promoted_from':SRC.name,'copied_byte_identically':True,'roms':roms,
 'source_manifest':sources,'source_archive':{'path':'source-v42.zip','sha256':sha(DST/'source-v42.zip'),'source_files':401,'fresh_rebuild':str(rebuildp.relative_to(ROOT))},
 'validation':{'summary':str(rawp.relative_to(ROOT)),'sha256':sha(rawp),'bound_raw_logs':str(boundp.relative_to(ROOT)),
 'bound_sha256':sha(boundp),'case_count':761,'single_full_run_all_passed':True,'fixtures_unchanged':True},
 'audio_CPU':{'path':str(unitp.relative_to(ROOT)),'sha256':sha(unitp),'cases':20326,'receipt':str(audio_receipt.relative_to(ROOT))},
 'actual_mapper_audio':{'path':str(hardwarep.relative_to(ROOT)),'sha256':sha(hardwarep)},
 'passive_HUD_native_input':{'path':str(hudp.relative_to(ROOT)),'sha256':sha(hudp),'retained_active_read_gap_frames':3},
 'crowds':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in perfpaths],'paired_updates':6000,'repeated_crowd_totals':repeat_totals,
 'rejected_prototypes':['build/checkpoints/roster-audit-v42-provisional-b/validation/bound-summary.json',
 'build/checkpoints/roster-audit-v42-provisional-d/validation/bound-summary.json','build/verification/enemy-bbox-v42d-caller-negative.json',
 'build/checkpoints/roster-audit-v42-provisional-b/responsiveness-rejection.json','build/checkpoints/roster-audit-v42-provisional-c/candidate.json',
 'build/build-v42b-first-generator-negative.log'],'qa':str(qa.relative_to(ROOT)),'qa_sha256':sha(qa),
 'documentation_updates':{'README.md':{'archived_sha256':readme_before,'current_sha256':sha(readme),'scope':'Checkpoint paragraph after immutable source archive'}},
 'known_gaps':['Dense crowds still lag and hardware scanline limits still flicker.','Individual redraw/physical-frame counterexamples remain; no universal speedup.',
 'Actual native input sampling gaps reach three gameplay frames, versus two in paired41 diagnostic; no global responsiveness bound.',
 'Simon/Ryu geometry and input phase, Ryu wall/vine action gates and Bill Flare source differences remain.',
 'Every weapon/upgrade, final-hash all14 routes, recordings and final audiovisual review remain unfinished.',
 'Older34/38d/40 routes do not certify42. No physical cartridge or source-perfect claim.']}
(DST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PROMOTED',roms,'761 single full run; roster goal remains active',flush=True)
