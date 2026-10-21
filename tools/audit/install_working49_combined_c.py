"""Install the reviewed working QA candidate with recoverable GQ ancestry."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-combined-working-c'
K=R/'build/checkpoints/roster-audit-v49-combined-ground-audio-samus-c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not K.exists(), 'Never overwrite a checkpoint.'
    backup_path=V/'root49-combined-adoption-a/preparation.json'
    assert sha(backup_path)=='5061d8bee2451264bcb5f336ee3176c183ae042e08dc9998e183552cd9c5ffbb'
    backup=json.loads(backup_path.read_text())
    parent=R/backup['parent']['path']
    assert sha(parent)==backup['parent']['sha256']
    archive=R/backup['archive']['path']
    assert sha(archive)==backup['archive']['sha256']
    for n,h in backup['before_files'].items():assert sha(R/n)==h,('Main changed since GQ backup',n)
    catalog=json.loads((D/'source-catalog.json').read_text())
    assert len(catalog)==455
    old=json.loads(parent.read_text())['source_hashes']
    assert not set(old)-set(catalog)
    changes={n:dict(before=old.get(n),after=h) for n,h in catalog.items() if old.get(n)!=h}
    for n,h in catalog.items():
        assert sha(D/'source'/n)==h,n
        assert (R/n).resolve().is_relative_to(R)
        assert n in old or not (R/n).exists(),('New-path local conflict',n)
    prep=json.loads((D/'preparation.json').read_text())
    composition=json.loads((D/'composition-review.json').read_text())
    assert composition['status']=='PASS_EXACT_COMBINED_19BYTE_MISSILE_OVERLAY_FOUR_BUILDS'
    targeted=json.loads((D/'targeted-native/summary.json').read_text())
    assert targeted['status']=='passed' and len(targeted['cases'])==12
    suite_path=V/'root49-combined-full-suite-c/summary.json'
    suite=json.loads(suite_path.read_text())
    assert suite['result'] in ['passed','failed'], 'Wait for the complete retained suite report.'
    assert not suite['changed_fixtures'] and suite['fixture_hashes_before']==suite['fixture_hashes_after']
    for n,h in suite['fixture_hashes_after'].items():assert sha(R/n)==h,n
    triage_path=V/'root49-legacy-fixture-triage-a/freeze.json'
    assert sha(triage_path)=='e74c35a8b6f22676b90f4fcb485e08bd296ee8461e0ce44b7a98b086dbb7ef17'
    admission_path=V/'root49-full-suite-admission-a.json'
    admission=json.loads(admission_path.read_text())
    assert admission['qualifies_provisional_working_adoption'] and not admission['full_suite_passed']
    assert admission['passed_native_slots']==688 and admission['failed_native_slots']==73
    assert admission['all_failed_native_slots_reproduce_on_E'] and admission['fixtures_unchanged']
    builds=[]
    for mapper in ['mmc3','mmc5']:
        stem='smb-crossover-'+mapper
        record=next(z for z in composition['builds'] if z['name']==stem)
        artifacts={}
        for ext in ['nes','dbg','lbl','map']:
            p=D/'source/build'/f'{stem}.{ext}'
            meta=record['metadata'][dict(nes='rom',dbg='debug',lbl='labels',map='map')[ext]]
            assert sha(p)==meta['sha256']
            artifacts[ext]=dict(path=f'build/{stem}.{ext}',sha256=sha(p),bytes=p.stat().st_size)
        builds.append(dict(mapper=mapper,artifacts=artifacts,byte_exact_tested_combined_C=True))
    K.mkdir(parents=True)
    source_archive=K/'source.zip'
    with zipfile.ZipFile(source_archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n in catalog:z.write(D/'source'/n,n)
        for n in prep['generated11']:z.write(D/'source/build/generated'/n,'build/generated/'+n)
    with zipfile.ZipFile(source_archive) as z:
        for n,h in catalog.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
        for n,h in prep['generated11'].items():assert hashlib.sha256(z.read('build/generated/'+n)).hexdigest()==h
    manifest=dict(status='INSTALLING_PROVISIONAL_WORKING_QA_C',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),publisher_sha256=sha(__file__),
        parent_checkpoint=dict(path=str(parent.relative_to(R)),sha256=sha(parent)),
        backup=dict(path=str(archive.relative_to(R)),sha256=sha(archive)),
        source_hashes=catalog,source_changes=changes,source_archive=dict(path=str(source_archive.relative_to(R)),sha256=sha(source_archive)),
        source_directory=str(D/'source'),generated11=prep['generated11'],builds=builds,
        admission={str(p.relative_to(R)):sha(p) for p in [D/'preparation.json',D/'composition-review.json',D/'targeted-native/summary.json',suite_path,triage_path,admission_path,V/'root49-landing-audio-admission-a.json',V/'root49-samus-action-review-a/independent-review.json']},
        full_suite=dict(result=suite['result'],passed_cases=len(suite['cases']),failures=suite['failures'],mario_replay=suite['mario_replay'],changed_fixtures=[]),
        qualification='Working QA integration, not a finished release. The complete predecessor-B suite retains every legacy failure; representative failures are reproduced on E. C differs from B only by nine bytes in the independently checked19-byte missile armor region. The source/natives reviewed in parent packets support the scoped changes; remaining failures, Ice behavior, full roster routes/arsenal/fidelity and final media remain open.',
        accepted_release=False,goal_complete=False)
    path=K/'manifest.json'
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    for n in catalog:
        p=R/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(D/'source'/n,p)
    for n in prep['generated11']:
        p=R/'build/generated'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(D/'source/build/generated'/n,p)
    for b in builds:
        for ext,h in b['artifacts'].items():
            source=D/'source/build'/Path(h['path']).name
            shutil.copyfile(source,R/h['path'])
            frozen=K/source.name;shutil.copyfile(source,frozen)
            h['frozen_path']=str(frozen.relative_to(R))
            assert sha(R/h['path'])==sha(frozen)==h['sha256']
    assert all(sha(R/n)==h for n,h in catalog.items())
    assert all(sha(R/'build/generated'/n)==h for n,h in prep['generated11'].items())
    assert sha(parent)==backup['parent']['sha256']
    manifest['status']='INSTALLED_PROVISIONAL_WORKING_GROUND_AUDIO_SAMUS_C_BOTH_MAPPERS'
    manifest['main_changed']=True
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=manifest['status'],manifest=str(path),sha256=sha(path),source_changes=len(changes),roms={b['mapper']:b['artifacts']['nes']['sha256'] for b in builds})))


if __name__=='__main__':main()
