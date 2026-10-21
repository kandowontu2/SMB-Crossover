"""Accept only the fully validated 193-byte MMC5 terrain component."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'build/checkpoints/roster-audit-v47'
SRC=ROOT/'build/checkpoints/roster-audit-v48-provisional-a'
DST=ROOT/'build/checkpoints/roster-audit-v48'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
proofs={}

def retain(name,path):
    p=ROOT/path
    proofs[name]=dict(path=path,sha256=sha(p))
    return read(p)

def main():
    assert not DST.exists(),'Accepted checkpoints are immutable'
    assert sha(OLD/'manifest.json')=='12d650833e3b7fae9ecfab91c37a9d284492cdd9af313a0ab4503917906140db'
    candidate=read(SRC/'candidate.json')
    roms={m:sha(SRC/f'smb-crossover-{m}.nes')for m in ('mmc3','mmc5')}
    assert roms=={m:r['sha256']for m,r in candidate['roms'].items()}
    assert roms['mmc3']==sha(OLD/'smb-crossover-mmc3.nes')
    assert roms['mmc5']=='54d27a36bd04a2c54aeb0219fc6c6317394af7861ba4aa4a2d4b1c1a68d97da7'
    summary=retain('full_suite','build/verification/summary-roster-audit-v48-provisional-a.json')
    bound=retain('bound_suite','build/checkpoints/roster-audit-v48-provisional-a/validation/bound-summary.json')
    assert summary['result']==bound['result']=='passed'
    assert len(summary['cases'])==bound['case_count']==bound['passed']==761
    assert bound['failed']==0 and bound['single_full_run']
    assert not summary['failures']and not summary['changed_fixtures']
    assert summary['fixture_hashes_before']==summary['fixture_hashes_after']
    assert all(sha(ROOT/n)==v for n,v in summary['fixture_hashes_after'].items())
    assert summary['roms']==bound['roms']==roms
    assert bound['summary_sha256']==proofs['full_suite']['sha256']
    assert all(sha(ROOT/r['log'])==r['log_sha256']for r in bound['cases'])
    cpu=retain('cpu','build/verification/goomba47-48-cpu-v3-a.json')
    native=retain('native','build/verification/goomba47-48-native-cpu-v3-a.json')
    for q in (cpu,native):
        assert q['result']=='passed-actual-compiled-terrain-differential'
        assert [r['rom_sha256']for r in q['binding']['provenance']]==[sha(OLD/'smb-crossover-mmc5.nes'),roms['mmc5']]
    assert cpu['cases']==82272 and cpu['dynamic_transition_calls']==96
    assert sum(r['cases']for r in cpu['groups'].values())==82176
    assert native['cases']==0 and len(native['native'])==2
    assert sum(r['calls']for r in native['native'])==128
    for r in native['native']:
        assert sha(r['path'])==r['sha256']and r['summary']['interrupted_calls']==0
        assert r['summary']['ordinary_inputs_only']and r['summary']['no_memory_register_or_PC_writes']
    for version in ('v1','v2','v3'):
        suffix=''if version=='v1'else '-'+version
        retain('cpu_freeze_'+version,f'build/verification/goomba-terrain48-validation{suffix}/freeze.json')
    retain('native_capture','build/verification/goomba47-48-native-terrain-real-a/report.json')
    retain('cpu_v1_negative','build/verification/goomba47-48-cpu-a.json')
    retain('native_v2_negative','build/verification/goomba47-48-native-cpu-v2-a.json')
    timing=retain('host_cycle_qualification','build/verification/goomba47-48-apu-classification/CPU-native-cycle-qualification.json')
    review=retain('crowd_review','build/verification/goomba47-48-crowd-review-a.json')
    assert review['canonical_updates']==13200 and len(review['runs'])==11
    assert len(review['negative_rows'])==75
    assert all(sha(ROOT/r['path'])==r['sha256']for r in review['inputs'])
    screen=retain('screen_and_pcm_negative','build/verification/goomba47-48-ppu-samus-e-a/report.json')
    assert screen['rgb24']['literal_rgb24_identity']and screen['rgb24']['frames']==1199
    assert screen['actual_inputs_identical']and screen['native_result']['inputPhaseMismatches']==0
    assert screen['continuous_pcm']['literal_equal']is False
    assert all(sha(ROOT/'build/verification/goomba47-48-ppu-samus-e-a/candidate48'/n)==v for n,v in screen['candidate_artifacts'].items())
    apu=retain('actual_audio','build/verification/goomba47-48-apu-samus-e-a/report.json')
    assert apu['result']=='completed-read-only-diagnostic-pcm-negative-retained'
    assert apu['frame_state_difference_count']==0 and apu['inputs_identical']and apu['inputs_identical_to_capture']
    assert all(r['equal']and r['differing_event_pairs']==0 for r in apu['comparison'].values())
    assert apu['native_result']['apuWrites']==4463 and apu['native_result']['queueWrites']==15486
    classification=retain('audio_classification','build/verification/goomba47-48-apu-classification/actual-classification.json')
    assert proofs['audio_classification']['sha256']=='2e85e36e83166723f0108159dba6b68a4d7864dd04d9a75abf86eb31f87a3ec3'
    retain('audio_classification_freeze','build/verification/goomba47-48-apu-classification/freeze.json')
    rebuild=retain('source_rebuild','build/checkpoint-tests/source-v48a-rebuild-smoke/report.json')
    archive=SRC/'source-v48a.zip'
    assert rebuild['archive_sha256']==sha(archive)==candidate['archive_sha256']
    assert rebuild['source_files']==403 and len(rebuild['cases'])==2
    assert all(r['exit']==0 and r['equal']and r['sha256']==roms[r['mapper']]for r in rebuild['cases'])
    with zipfile.ZipFile(archive)as z:
        sources=json.loads(z.read('archived-file-hashes.json'))
        assert len(sources)==403 and len(z.namelist())==404
        assert all(hashlib.sha256(z.read(n)).hexdigest()==v and sha(ROOT/n)==v for n,v in sources.items())
    qa=ROOT/'docs/qa/roster-component-v48.md'
    assert qa.is_file()
    sys.path.insert(0,str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used=workspace_bytes(ROOT)
    assert used+sum(p.stat().st_size for p in SRC.rglob('*')if p.is_file())+64*1024*1024<30_000_000_000
    shutil.copytree(SRC,DST)
    shutil.copyfile(archive,DST/'source-v48.zip')
    readme=ROOT/'README.md'
    text=readme.read_text()
    at=text.index('The [v47 renderer update]')
    paragraph=('The [v48 terrain update](docs/qa/roster-component-v48.md) reduces MMC5 settled-Goomba collision work. All 761 unchanged-fixture regression cases, 82,272 strict compiled CPU cases, 128 actual native receipts and fresh 403-file rebuilds pass. All 13,200 paired crowd updates preserve 204 gameplay fields; six-Goomba rows with equal redraw counts save approximately 1,343 foreground CPU cycles/update. Dense scenes still skip redraws, and timing/visibility counterexamples remain, including Ryu physical-frame regressions. All 1,199 captured RGB frames match; ordered same-frame audio values and ownership match, while literal PCM differs with write timing. MMC3 remains byte identical to v45–47. Outlines default OFF and the option row is gold. ROMs are in `build/checkpoints/roster-audit-v48/`; full roster/weapon/recording work remains open.\n\n')
    readme.write_text(text[:at]+paragraph+text[at:],encoding='utf8')
    manifest=dict(status='accepted-bounded-component',goal_complete=False,parent=OLD.name,
        accepted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),roms=roms,
        candidate_sha256=sha(SRC/'candidate.json'),source_archive_sha256=sha(archive),source_count=403,
        scope=candidate['scope'],proofs=proofs,qa=qa.relative_to(ROOT).as_posix(),qa_sha256=sha(qa),
        README_postarchive=dict(archived_sha256=sources['README.md'],current_sha256=sha(readme),reason='Post-validation release ledger only'),
        full_suite_cases=761,cpu_cases=82272,actual_native_receipts=128,paired_crowd_updates=13200,
        literal_rgb24_frames_equal=1199,literal_pcm_equal=False,
        audio_same_frame_and_owner=dict(apu=4463,source_queues=15486),
        workspace_bytes_before=used,workspace_cap_bytes=30_000_000_000,
        limits=['Dense scenes still skip redraws; hardware eight-sprite scanline limit unchanged.',
            'All75 negative crowd metric rows retained; Ryu repeat physical frames1187to1200 and individual visibility/redraw regressions remain.',
            'Host cycle model old-native difference+6 retained; performance claims use direct Mesen observations.',
            'Literal PCM negative retained; equal ordered register values/ownership is not waveform or perceptual identity.',
            'All14 final-hash routes, every weapon/upgrade and full audiovisual review remain incomplete.',
            'Separate173-byte stack-residue proposal remains unapplied.'])
    (DST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('ACCEPTED48',roms,'761regressions/82272CPU/128native/13200crowd updates; goal remains active',flush=True)

if __name__=='__main__':main()
