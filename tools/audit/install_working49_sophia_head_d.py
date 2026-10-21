"""Install the reviewed Sophia repair with an exact recoverable C backup."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-head-axis-d'
A=V/'root49-sophia-head-adoption-a';K=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not A.exists()and not K.exists()
    frozen=D/'freeze-k.json';assert sha(frozen)=='1cc21a9cd78984a167ad2cc6f04301ba5ecd2623fc59476a24e11f3feebeb6d9'
    f=json.loads(frozen.read_text());assert f['provisional_admission']and not f['goal_complete']
    parent=R/'build/checkpoints/roster-audit-v49-combined-ground-audio-samus-c/manifest.json'
    assert sha(parent)==f['parent_checkpoint_sha256'];c=json.loads(parent.read_text())
    for n,h in f['receipt_catalog'].items():
        p=D/n;assert sha(p)==h['sha256']and p.stat().st_size==h['bytes'],n
    before={n:h for n,h in c['source_hashes'].items()}
    before.update({'build/generated/'+n:h for n,h in c['generated11'].items()})
    for b in c['builds']:
        for meta in b['artifacts'].values():before[meta['path']]=meta['sha256']
    assert len(before)==474
    for n,h in before.items():assert sha(R/n)==h,('Main changed; do not overwrite',n)
    for n,h in f['source_sha256'].items():assert sha(D/'source'/n)==h
    A.mkdir();K.mkdir(parents=True)
    backup=A/'before-main-c.zip'
    with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for n in before:z.write(R/n,n)
    with zipfile.ZipFile(backup)as z:
        assert len(z.namelist())==474
        for n,h in before.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    preparation=dict(status='PREPARED_REVIEWED_D_WITH_C_BACKUP',script_sha256=sha(__file__),parent_sha256=sha(parent),
                     freeze_sha256=sha(frozen),before_files=before,backup_sha256=sha(backup),backup_bytes=backup.stat().st_size)
    (A/'preparation.json').write_text(json.dumps(preparation,indent=2)+'\n')
    sourcezip=K/'source.zip'
    with zipfile.ZipFile(sourcezip,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for n in f['source_sha256']:z.write(D/'source'/n,n)
        for n in f['generated11']:z.write(D/'source/build/generated'/n,'build/generated/'+n)
    with zipfile.ZipFile(sourcezip)as z:
        for n,h in f['source_sha256'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
        for n,h in f['generated11'].items():assert hashlib.sha256(z.read('build/generated/'+n)).hexdigest()==h
    builds=[]
    for b in f['builds']:
        stem=f"smb-crossover-{b['mapper']}";artifacts={}
        for ext,key in [('nes','rom'),('dbg','debug'),('lbl','labels'),('map','map')]:
            p=D/'source/build'/f'{stem}.{ext}';assert sha(p)==b['metadata'][key]['sha256']
            artifacts[ext]=dict(path=f'build/{stem}.{ext}',sha256=sha(p),bytes=p.stat().st_size,frozen_path=str((K/p.name).relative_to(R)))
        builds.append(dict(mapper=b['mapper'],artifacts=artifacts))
    manifest=dict(status='INSTALLING_PROVISIONAL_WORKING_SOPHIA_HEAD_D',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  publisher_sha256=sha(__file__),parent_checkpoint=dict(path=str(parent.relative_to(R)),sha256=sha(parent)),
                  backup=dict(path=str(backup.relative_to(R)),sha256=sha(backup)),
                  source_hashes=f['source_sha256'],source_changes=f['source_changes'],source_directory=str(D/'source'),
                  source_archive=dict(path=str(sourcezip.relative_to(R)),sha256=sha(sourcezip)),generated11=f['generated11'],builds=builds,
                  admission=dict(path=str(frozen.relative_to(R)),sha256=sha(frozen)),limits=f['limits'],
                  full_suite='Inherited predecessor-B suite remains688 native passes/73failed slots plus separate stockMario comparison. This scoped D patch was checked separately; no whole-suite pass claim.',
                  accepted_release=False,goal_complete=False)
    path=K/'manifest.json';path.write_text(json.dumps(manifest,indent=2)+'\n')
    # Revalidate all actual target paths immediately before the first write.
    for n,h in before.items():assert sha(R/n)==h,n
    for n in f['source_changes']:
        target=(R/n).resolve();assert target.is_relative_to(R.resolve())
        shutil.copyfile(D/'source'/n,target)
    for b in builds:
        for ext,meta in b['artifacts'].items():
            p=D/'source/build'/Path(meta['path']).name
            shutil.copyfile(p,R/meta['path']);shutil.copyfile(p,R/meta['frozen_path'])
            assert sha(R/meta['path'])==sha(R/meta['frozen_path'])==meta['sha256']
    for n,h in f['source_sha256'].items():assert sha(R/n)==h
    for n,h in f['generated11'].items():assert sha(R/'build/generated'/n)==h
    manifest['status']='INSTALLED_PROVISIONAL_WORKING_SOPHIA_HEAD_AXIS_D_BOTH_MAPPERS';manifest['main_changed']=True
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=manifest['status'],checkpoint_sha256=sha(path),source_changes=f['source_changes'],
                         backup_sha256=sha(backup),ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in builds})))


if __name__=='__main__':main()
