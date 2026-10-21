"""Freeze and install the reviewed Ice overlay, preserving an exact main-D backup."""
from pathlib import Path
import datetime,hashlib,json,shutil,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
E=V/'root49-ice-integrated-e';A=V/'root49-ice-adoption-e'
K=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not A.exists()and not K.exists()
    cp=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json'
    assert sha(cp)=='1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88'
    d=json.loads(cp.read_text());p=json.loads((E/'preparation.json').read_text())
    b=json.loads((E/'build-review.json').read_text());r=E/'root-review-az/review.json';rev=json.loads(r.read_text())
    assert rev['status']=='PASS_ACTUAL_COMPOSED_E_NATIVE_INSTRUCTION_LIFECYCLE_PROTOCOL_REVIEWS'
    assert sha(E/'build-review.json')==rev['build_review_sha256']
    assert sha(E/'root-review-az/native-receipts.json')==rev['native_receipts_sha256']
    for n,z in json.loads((E/'root-review-az/native-receipts.json').read_text()).items():assert sha(E/n)==z['sha256'],n
    for z in rev['reports']:
        assert sha(E/'root-review-az'/z['report'])==z['report_sha256']
        assert sha(E/'root-review-az'/z['script'])==z['adapter_sha256']
    ice=V/'agent49-samus-bill-arsenal-a/ice-state-freeze-dj/freeze.json'
    assert sha(ice)==p['Ice_freeze_sha256'];f=json.loads(ice.read_text())
    root=V/'root49-ice-state-review-ay/review.json';assert sha(root)==p['root_review_sha256']
    parent=Path(f['source_parent']['path'])
    before=dict(d['source_hashes'])
    before.update({'build/generated/'+n:h for n,h in d['generated11'].items()})
    for oldb in d['builds']:
        for z in oldb['artifacts'].values():before[z['path']]=z['sha256']
    assert len(before)==474
    for n,h in before.items():assert sha(R/n)==h,('main changed; do not overwrite',n)
    for n,h in p['source_hashes'].items():assert sha(E/'source'/n)==h,n
    for n,h in p['generated11'].items():assert sha(E/'source/build/generated'/n)==h,n
    changed=[n for n,h in p['source_hashes'].items()if d['source_hashes'].get(n)!=h]
    assert set(changed)==set(p['owned_overlay'])and len(changed)==16
    for n in p['preserved_D']:assert p['source_hashes'][n]==d['source_hashes'][n]
    # Recompute actual merge commutation instead of trusting the build report.
    for z in b['builds']:
        for v in z['artifacts'].values():assert sha(R/v['path'])==v['sha256']
        if z['baseline']:continue
        name=Path(z['artifacts']['nes']['path']).name
        old=(cp.parent/name).read_bytes();new=(R/z['artifacts']['nes']['path']).read_bytes()
        ancestor=(parent/'build'/name).read_bytes();cy=(Path(f['source_path'])/'build'/name).read_bytes()
        actual={i:(x,y)for i,(x,y)in enumerate(zip(old,new))if x!=y}
        expected={i:(x,y)for i,(x,y)in enumerate(zip(ancestor,cy))if x!=y}
        assert len(old)==len(new)==len(ancestor)==len(cy)and actual==expected and len(actual)==1208
        assert not(set(actual)&{i for i,(x,y)in enumerate(zip(ancestor,old))if x!=y})
    smokes={};host_smokes=E/'private-smoke/host-receipt-az.json'
    observed=json.loads(host_smokes.read_text())
    assert observed['status']=='OBSERVED_PRIVATE_SMOKES_BOTH_EXIT_ZERO'
    for mp in ['mmc3','mmc5']:
        q=E/'private-smoke'/f'smb-crossover-{mp}-baseline.log';text=q.read_text()
        assert 'PASS boot, title, level load, player control, floor collision'in text
        assert 'FAIL'not in text
        assert observed['groups'][mp]['actual_exec_tool_exit_code']==0
        assert sha(q)==observed['groups'][mp]['native_log_sha256']
        smokes[str(q.relative_to(E))]=sha(q)
    smokes[str(host_smokes.relative_to(E))]=sha(host_smokes)
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size+100000000<70000000000
    phase=sum(q.stat().st_size for q in E.rglob('*')if q.is_file());assert phase+50000000<500000000
    freeze=E/'freeze-az.json';assert not freeze.exists()
    frozen=dict(status='FROZEN_REVIEWED_ICE_COMPOSITION_OVER_D_FOR_PROVISIONAL_WORKING_ADOPTION',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
      parent_checkpoint_sha256=sha(cp),preparation_sha256=sha(E/'preparation.json'),
      build_review_sha256=sha(E/'build-review.json'),native_compiled_review_sha256=sha(r),
      Ice_DJ_sha256=sha(ice),root_DJ_review_sha256=sha(root),private_smokes=smokes,
      source_hashes=p['source_hashes'],generated11=p['generated11'],source_changes=changed,
      preserved_D=p['preserved_D'],builds=b['builds'],limits=f['limitations'],cost=f['cost'],
      provisional_admission=True,accepted_release=False,goal_complete=False)
    freeze.write_text(json.dumps(frozen,indent=2)+'\n')
    A.mkdir();K.mkdir(parents=True)
    backup=A/'before-main-d.zip'
    with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for n in before:z.write(R/n,n)
    with zipfile.ZipFile(backup)as z:
        assert len(z.namelist())==474
        for n,h in before.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
    (A/'preparation.json').write_text(json.dumps(dict(status='PREPARED_REVIEWED_E_WITH_ACTUAL_D_BACKUP',
      script_sha256=sha(__file__),freeze_sha256=sha(freeze),parent_sha256=sha(cp),
      before_files=before,backup_sha256=sha(backup),backup_bytes=backup.stat().st_size),indent=2)+'\n')
    sourcezip=K/'source.zip'
    entries=dict(p['source_hashes']);entries.update({'build/generated/'+n:h for n,h in p['generated11'].items()})
    with zipfile.ZipFile(sourcezip,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for n in entries:z.write(E/'source'/n,n)
    with zipfile.ZipFile(sourcezip)as z:
        assert len(z.namelist())==468
        for n,h in entries.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
    builds=[];baselines=[]
    for z in b['builds']:
        artifact={}
        for ext,v in z['artifacts'].items():
            q=R/v['path'];dest=K/q.name;shutil.copyfile(q,dest);assert sha(dest)==v['sha256']
            artifact[ext]=dict(path='build/'+q.name,sha256=v['sha256'],bytes=v['bytes'],frozen_path=str(dest.relative_to(R)))
        (baselines if z['baseline']else builds).append(dict(mapper=z['mapper'],artifacts=artifact))
    manifest=dict(status='INSTALLING_PROVISIONAL_WORKING_ICE_OVER_SOPHIA_E',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),publisher_sha256=sha(__file__),
      parent_checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),
      backup=dict(path=str(backup.relative_to(R)),sha256=sha(backup)),
      source_hashes=p['source_hashes'],source_changes=changed,source_directory=str(E/'source'),
      source_archive=dict(path=str(sourcezip.relative_to(R)),sha256=sha(sourcezip)),generated11=p['generated11'],
      builds=builds,baseline_builds=baselines,admission=dict(path=str(freeze.relative_to(R)),sha256=sha(freeze)),
      limits=f['limitations'],cost=f['cost'],preserved_D=p['preserved_D'],
      full_suite='Original predecessor-B suite688 native passes/73failures plus separate stockMario comparison remains open. E scoped checks do not claim a complete suite pass.',
      accepted_release=False,goal_complete=False)
    target=K/'manifest.json';target.write_text(json.dumps(manifest,indent=2)+'\n')
    for n,h in before.items():assert sha(R/n)==h,n
    for n in changed:
        q=(R/n).resolve();assert q.is_relative_to(R.resolve());q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(E/'source'/n,q)
    for z in builds:
        for v in z['artifacts'].values():
            shutil.copyfile(R/v['frozen_path'],R/v['path']);assert sha(R/v['path'])==v['sha256']
    for n,h in entries.items():assert sha(R/n)==h,n
    manifest.update(status='INSTALLED_PROVISIONAL_WORKING_ICE_OVER_SOPHIA_E_BOTH_MAPPERS',main_changed=True)
    target.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=manifest['status'],checkpoint_sha256=sha(target),freeze_sha256=sha(freeze),
      backup_sha256=sha(backup),ROMs={z['mapper']:z['artifacts']['nes']['sha256']for z in builds})))
if __name__=='__main__':main()
