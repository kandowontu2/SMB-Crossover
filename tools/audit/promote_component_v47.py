"""Accept the bounded MMC5 walking-Goomba renderer, with timing negatives kept."""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'build/checkpoints/roster-audit-v46'
SRC=ROOT/'build/checkpoints/roster-audit-v47-provisional-a'
DST=ROOT/'build/checkpoints/roster-audit-v47'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
proofs={}
def retain(name,n):
 p=ROOT/n;proofs[name]=dict(path=n,sha256=sha(p));return read(p)
def main():
 assert not DST.exists(),'Accepted checkpoints are immutable'
 candidate=read(SRC/'candidate.json')
 roms={m:sha(SRC/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
 assert roms=={m:r['sha256']for m,r in candidate['roms'].items()}
 assert roms['mmc3']==sha(OLD/'smb-crossover-mmc3.nes')
 assert roms['mmc5']=='3f5e8fdff30ce057ebf136a6e93d5f5481ff8962345dc98039458e3abb679dc8'
 summary=retain('full_suite','build/verification/summary-roster-audit-v47-provisional-a.json')
 bound=retain('bound_suite','build/checkpoints/roster-audit-v47-provisional-a/validation/bound-summary.json')
 assert summary['result']==bound['result']=='passed'and len(summary['cases'])==bound['case_count']==bound['passed']==761
 assert bound['failed']==0 and bound['single_full_run']and not summary['failures']and not summary['changed_fixtures']
 assert summary['fixture_hashes_before']==summary['fixture_hashes_after']
 assert all(sha(ROOT/n)==h for n,h in summary['fixture_hashes_after'].items())
 assert summary['roms']==bound['roms']==roms and bound['summary_sha256']==proofs['full_suite']['sha256']
 assert all(sha(ROOT/r['log'])==r['log_sha256']for r in bound['cases'])
 for name in('cpu','native'):
  q=retain(name,f'build/verification/goomba46-47-{name}-a.json')
  assert q['result']=='passed-exact-compiled-renderer'and q['cases']==14608
  assert q['binding']['before_sha256']==sha(OLD/'smb-crossover-mmc5.nes')and q['binding']['after_sha256']==roms['mmc5']
  assert sum(v['cases']for v in q['groups'].values())==14608
  if name=='native':
   assert len(q['native'])==2 and sum(r['calls']for r in q['native'])==128
   for r in q['native']:
    assert sha(Path(r['path']))==r['sha256']and r['summary']['interrupted_calls']==0 and r['summary']['entry_cap_enforced']
 retain('native_execution','build/verification/goomba47-native-execution-a/report.json')
 for name,n in [('binding_freeze','native-goomba-metadraw46-binding-repair'),('native_binding_freeze','native-goomba-metadraw47-native-binding'),('apu_freeze','goomba46-47-apu-origin-preparation')]:
  retain(name,f'build/verification/{n}/freeze.json')
 crowds=[]
 for name in('three','other','six-repeat'):
  q=retain('crowds_'+name,f'build/verification/plain-walking-v46-v47a-goomba-{name}-comparison.json')
  assert q['canonical_mismatch_count']==0 and len(q['runs'])==(5 if name=='six-repeat'else 3)
  assert all(r['canonical_rows']==1200 and r['canonical_observation_fields']==204 for r in q['runs'])
  crowds.extend(q['runs'])
 screen=retain('screen_and_pcm_negative','build/verification/goomba46-47-ppu-samus-e-a/report.json')
 assert screen['rgb24']['literal_rgb24_identity']and screen['rgb24']['frames']==1199
 assert screen['actual_controller_receipts_identical']and screen['input_phase_mismatches']==[0,0]
 assert screen['continuous_pcm']['literal_pcm_identity']is False
 retain('literal_pcm_statistics','build/verification/goomba46-47-apu-origin-preparation/raw-wav-difference.json')
 apu=retain('actual_apu_origin','build/verification/goomba46-47-apu-samus-e-a/report.json')
 assert apu['result']=='completed-read-only-diagnostic-pcm-negative-retained'
 c=apu['comparison']
 assert c['frameStateDifferenceCount']==0 and c['actualInputsIdentical']and all(c['actualInputsIdenticalToExistingCapture'])
 for k in('apuGlobalOrderedData','apuPerFrameOrderedData','sourceQueuesGlobalOrderedData','sourceQueuesPerFrameOrderedData','combinedPerFrameOrderedData'):
  assert c[k]['equal']and c[k]['differing_event_pairs']==0
 owner_fields=['frame','kind','address','value','pc','physicalBank','physicalRomOffset','nmiDepth','irqDepth','context','selected','guestAudioCharacter','mixOwner','mixMask','nativeEnable','combinedEnable','remainingId','remainingRequest','expandedCharacter','expandedEvent','mmSfx','smSfx','bassDmc']
 root=ROOT/'build/verification/goomba46-47-apu-samus-e-a'
 streams=[]
 for side in('before46','candidate47'):
  streams.append([r for r in csv.DictReader((root/side/'events.csv').open(newline=''))if r['kind']=='apu'])
 assert len(streams[0])==len(streams[1])==4463
 assert all(all(a[k]==b[k]for k in owner_fields)for a,b in zip(*streams))
 apu_cycle_delta=max(abs(int(a['cycle'])-int(b['cycle']))for a,b in zip(*streams))
 assert apu_cycle_delta==112
 # Independent causal classification is retained without erasing the PCM negative.
 retain('apu_classification','build/verification/goomba46-47-apu-origin-preparation/actual-classification.json')
 rebuild=retain('fresh_archive_rebuild','build/checkpoint-tests/source-v47a-rebuild-smoke/report.json')
 archive=SRC/'source-v47a.zip'
 assert rebuild['archive_sha256']==sha(archive)and rebuild['source_files']==402
 assert len(rebuild['cases'])==2 and all(r['exit']==0 and r['equal']and r['sha256']==roms[r['mapper']]for r in rebuild['cases'])
 with zipfile.ZipFile(archive)as z:
  sources=json.loads(z.read('archived-file-hashes.json'))
  assert len(sources)==402 and len(z.namelist())==403
  assert all(hashlib.sha256(z.read(n)).hexdigest()==h and sha(ROOT/n)==h for n,h in sources.items())
 sys.path.insert(0,str(ROOT/'tools/playthroughs'))
 from roster_run import workspace_bytes
 used=workspace_bytes(ROOT)
 assert used+sum(p.stat().st_size for p in SRC.rglob('*')if p.is_file())+64*1024*1024<30_000_000_000
 qa=ROOT/'docs/qa/roster-component-v47.md';assert qa.is_file()
 shutil.copytree(SRC,DST);shutil.copyfile(archive,DST/'source-v47.zip')
 readme=ROOT/'README.md';text=readme.read_text();at=text.index('The [v46 component update]')
 paragraph=('The [v47 renderer update](docs/qa/roster-component-v47.md) reduces MMC5 walking-Goomba sprite work. All761 unchanged-fixture regression cases,14,608 compiled CPU cases plus128 native receipts and fresh402-file rebuilds pass. All13,200 paired crowd updates retain204 gameplay fields. Six-enemy repeated tests save about128–143 CPU cycles per update; dense scenes still skip redraws and individual timing/visibility counterexamples remain. All1,199 captured RGB frames match; same-frame ordered APU/queue data and ownership match, while literal PCM differs with register-write timing. MMC3 stays byte identical45/46. Outlines default OFF with a gold option row. ROMs are in `build/checkpoints/roster-audit-v47/`; full roster/weapon/recording work remains open.\n\n')
 readme.write_text(text[:at]+paragraph+text[at:],encoding='utf8')
 manifest=dict(status='accepted-bounded-component',goal_complete=False,parent=OLD.name,
  accepted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),roms=roms,
  candidate_sha256=sha(SRC/'candidate.json'),source_archive_sha256=sha(archive),source_count=402,
  scope=candidate['scope'],proofs=proofs,qa=qa.relative_to(ROOT).as_posix(),qa_sha256=sha(qa),
  README_postarchive=dict(archived_sha256=sources['README.md'],current_sha256=sha(readme),reason='Post-validation release ledger only'),
  paired_crowd_updates=sum(r['canonical_rows']for r in crowds),apu_writes_same_frame_and_owner=4463,max_paired_apu_cycle_delta=apu_cycle_delta,
  literal_rgb24_frames_equal=1199,literal_pcm_equal=False,workspace_bytes_before=used,workspace_cap_bytes=30_000_000_000,
  limits=['Dense scenes still skip redraws; hardware8-sprite scanline limit unchanged.',
   'Six-enemy repeats preserve gameplay but physical-frame and visibility counters have individual negative rows, including Samus+3 physical frames over1200updates.',
   'Literal PCM negative is retained; identical same-frame register data/ownership does not assert waveform identity or full musical equivalence.',
   'All14 final-hash routes, every weapon/upgrade and final audiovisual review remain incomplete.'])
 (DST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('ACCEPTED47',roms,'761regressions/14608CPU+128native/13200crowd updates; goal remains active',flush=True)
if __name__=='__main__':main()
