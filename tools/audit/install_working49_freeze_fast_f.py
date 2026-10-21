"""Freeze the measured single-leaf optimization and install with a complete E backup."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-freeze-render-fast-f'
A=V/'root49-freeze-fast-adoption-f';K=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not A.exists()and not K.exists()
    parent=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e/manifest.json'
    assert sha(parent)=='65072e56ce25e03e748248cb1efdc51312378e23d099259261bc02d71a76d64b'
    e=json.loads(parent.read_text());pre=json.loads((H/'preparation-b.json').read_text())
    br=json.loads((H/'build-review.json').read_text());cost=json.loads((H/'matched-native-cost-f.json').read_text())
    native=H/'native-review-e/review.json';n=json.loads(native.read_text())
    assert n['status']=='PASS_F_ACTUAL_NATIVE_LIFECYCLE_OAM_NSF_AND_WHOLE_CALLER_ISR_REEXECUTION'
    assert cost['status']=='PASS_MATCHED_F_NATIVE_START_STATES_IDENTICAL_OUTPUT_LOWER_ACTIVE_LEAF_CYCLES'
    assert cost['native_review_sha256']==sha(native)
    assert sha(H/'leaf-review-c.json')==n['leaf_review_sha256']and sha(H/'build-review.json')==n['build_review_sha256']
    for z in n['reports']:assert sha(H/'native-review-e'/z['report'])==z['sha256']
    assert sha(H/'native-review-e/native-receipts.json')==n['native_receipts_sha256']
    for name,z in json.loads((H/'native-review-e/native-receipts.json').read_text()).items():assert sha(H/name)==z['sha256']
    before=dict(e['source_hashes']);before.update({'build/generated/'+name:h for name,h in e['generated11'].items()})
    for z in e['builds']:
        for q in z['artifacts'].values():before[q['path']]=q['sha256']
    assert len(before)==476
    for name,h in before.items():assert sha(R/name)==h,('Main changed; do not overwrite',name)
    for name,h in pre['source_hashes'].items():assert sha(H/'source'/name)==h,name
    for name,h in pre['generated11'].items():assert sha(H/'source/build/generated'/name)==h
    changes=[name for name,h in pre['source_hashes'].items()if e['source_hashes'][name]!=h]
    assert changes==['src/samus_freeze_render.s']
    for z in br['builds']:
        for q in z['artifacts'].values():assert sha(R/q['path'])==q['sha256']
        if not z['baseline']:
            old=(parent.parent/Path(z['artifacts']['nes']['path']).name).read_bytes();new=(R/z['artifacts']['nes']['path']).read_bytes()
            delta=[dict(offset=i,old=a,new=b)for i,(a,b)in enumerate(zip(old,new))if a!=b]
            assert len(old)==len(new)and delta==z['delta']and len(delta)==486
            assert all(z['allowed_ROM_span'][0]<=v['offset']<z['allowed_ROM_span'][1]for v in delta)
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    total=workspace_bytes(R);phase=sum(p.stat().st_size for p in H.rglob('*')if p.is_file())
    assert total+100000000<70000000000 and phase+50000000<300000000,(total,phase)
    receipts={str(p.relative_to(H)):dict(sha256=sha(p),bytes=p.stat().st_size)for p in H.rglob('*')if p.is_file()}
    catalog=H/'admission-receipts-g.json';catalog.write_text(json.dumps(receipts,indent=2)+'\n')
    frozen=H/'freeze-g.json';assert not frozen.exists()
    limits=e['limits']+cost['limitations']
    freeze=dict(status='FROZEN_REVIEWED_SINGLE_ACTIVE_LEAF_SPEEDUP_FOR_WORKING_F',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
      parent_checkpoint_sha256=sha(parent),receipt_catalog_sha256=sha(catalog),receipt_count=len(receipts),
      source_hashes=pre['source_hashes'],generated11=pre['generated11'],source_changes=changes,
      native_review_sha256=sha(native),leaf_review_sha256=sha(H/'leaf-review-c.json'),
      cost_review_sha256=sha(H/'matched-native-cost-f.json'),build_review_sha256=sha(H/'build-review.json'),
      matched_cost=[dict(mapper=g['mapper'],samples=g['matched_actual_F_start_states'],summary=g['summary'])for g in cost['groups']],
      limits=limits,provisional_admission=True,accepted_release=False,goal_complete=False)
    frozen.write_text(json.dumps(freeze,indent=2)+'\n')
    A.mkdir();K.mkdir(parents=True);backup=A/'before-main-e.zip'
    with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for name in before:z.write(R/name,name)
    with zipfile.ZipFile(backup)as z:
        assert len(z.namelist())==476
        for name,h in before.items():assert hashlib.sha256(z.read(name)).hexdigest()==h
    (A/'preparation.json').write_text(json.dumps(dict(status='PREPARED_REVIEWED_F_WITH_ACTUAL_E_BACKUP',
      script_sha256=sha(__file__),freeze_sha256=sha(frozen),before_files=before,backup_sha256=sha(backup),backup_bytes=backup.stat().st_size),indent=2)+'\n')
    archive=K/'source.zip';entries=dict(pre['source_hashes']);entries.update({'build/generated/'+name:h for name,h in pre['generated11'].items()})
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for name in entries:z.write(H/'source'/name,name)
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==468
        for name,h in entries.items():assert hashlib.sha256(z.read(name)).hexdigest()==h
    builds=[];baselines=[]
    for z in br['builds']:
        artifacts={}
        for ext,q in z['artifacts'].items():
            path=R/q['path'];dest=K/path.name;shutil.copyfile(path,dest);assert sha(dest)==q['sha256']
            artifacts[ext]=dict(path='build/'+path.name,sha256=q['sha256'],bytes=q['bytes'],frozen_path=str(dest.relative_to(R)))
        (baselines if z['baseline']else builds).append(dict(mapper=z['mapper'],artifacts=artifacts))
    performance=dict(previous_E=e['cost'],F_matched_active_leaf=freeze['matched_cost'],
      inactive_paths='All bytes outside the single active leaf are literal E. Any+86/update, quietNMI+24 and inactiveRender+25/26 remain.',
      scope='Per-active-pass matched cycles; not complete route/FPS/lag/visibility admission.')
    manifest=dict(status='INSTALLING_PROVISIONAL_WORKING_FREEZE_RENDER_FAST_F',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),publisher_sha256=sha(__file__),
      parent_checkpoint=dict(path=str(parent.relative_to(R)),sha256=sha(parent)),backup=dict(path=str(backup.relative_to(R)),sha256=sha(backup)),
      source_hashes=pre['source_hashes'],source_changes=changes,source_directory=str(H/'source'),
      source_archive=dict(path=str(archive.relative_to(R)),sha256=sha(archive)),generated11=pre['generated11'],
      builds=builds,baseline_builds=baselines,admission=dict(path=str(frozen.relative_to(R)),sha256=sha(frozen)),
      limits=limits,cost=performance,preserved_D=e['preserved_D'],full_suite=e['full_suite'],
      accepted_release=False,goal_complete=False)
    target=K/'manifest.json';target.write_text(json.dumps(manifest,indent=2)+'\n')
    for name,h in before.items():assert sha(R/name)==h,name
    shutil.copyfile(H/'source/src/samus_freeze_render.s',R/'src/samus_freeze_render.s')
    for b in builds:
        for q in b['artifacts'].values():shutil.copyfile(R/q['frozen_path'],R/q['path'])
    for name,h in entries.items():assert sha(R/name)==h,name
    for b in builds:
        for q in b['artifacts'].values():assert sha(R/q['path'])==q['sha256']
    manifest.update(status='INSTALLED_PROVISIONAL_WORKING_FREEZE_RENDER_FAST_F_BOTH_MAPPERS',main_changed=True)
    target.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=manifest['status'],checkpoint_sha256=sha(target),freeze_sha256=sha(frozen),backup_sha256=sha(backup),
      ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in builds})),flush=True)
    O=A/'main-smoke';O.mkdir();results=[]
    for mp in ['mmc3','mmc5']:
        q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(O),
          str(R/'tests/baseline.lua'),str(R/'build'/f'smb-crossover-{mp}.nes'),'--timeout','30'],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        log=O/(mp+'-host.log');log.write_bytes(q.stdout);results.append(dict(mapper=mp,exit=q.returncode,host_log_sha256=sha(log)))
        (O/'progress.json').write_text(json.dumps(dict(status='RUNNING',groups=results),indent=2)+'\n')
        assert q.returncode==0 and b'PASS boot, title, level load, player control, floor collision'in q.stdout,(mp,q.stdout)
    for name,h in entries.items():assert sha(R/name)==h,name
    (O/'review.json').write_text(json.dumps(dict(status='PASS_ACTUAL_INSTALLED_F_BOOT_TITLE_CONTROL_FLOOR_BOTH_MAPPERS',
      checkpoint_sha256=sha(target),sources_rehashed=457,generated_rehashed=11,primary_artifacts_rehashed=8,groups=results,goal_complete=False),indent=2)+'\n')
    print('MAIN_SMOKES_PASS',sha(O/'review.json'),flush=True)
if __name__=='__main__':main()
