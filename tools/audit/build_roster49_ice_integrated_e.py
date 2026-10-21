"""Compose the reviewed owned Ice overlay over exact D, then build privately."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';A=V/'agent49-samus-bill-arsenal-a';H=V/'root49-ice-integrated-e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json';d=json.loads(cp.read_text())
    review=V/'root49-ice-state-review-ay/review.json';rev=json.loads(review.read_text())
    assert rev['status']=='PASS_ROOT_REEXECUTED_FROZEN_DJ_PACKET_NOT_YET_COMPOSED_OR_ADOPTED'
    frozen=A/'ice-state-freeze-dj/freeze.json';f=json.loads(frozen.read_text());assert sha(frozen)=='fc0cc5716511979cd1345479a2ca1e3bd1f0170f0bfa90f409c88994cb13f084'
    cy=Path(f['source_path']);old=Path(f['source_parent']['path']);oldcat=Path(f['source_parent']['catalog'])
    assert sha(oldcat)==f['source_parent']['sha256'];parents=json.loads(oldcat.read_text())
    for n,h in parents.items():assert sha(old/n)==h,n
    for n,h in d['source_hashes'].items():
        assert sha(R/n)==h,n
        p=H/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    for n,h in d['generated11'].items():
        p=R/'build/generated'/n;assert sha(p)==h
        q=H/'source/build/generated'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    overlay=f['owned_overlay']['paths'];assert len(overlay)==16
    for n,h in overlay.items():
        assert n not in['src/characters.s','src/sophia_source_terrain.s']and sha(cy/n)==h
        if n in parents:assert d['source_hashes'][n]==parents[n],('Three-way conflict',n)
        p=H/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(cy/n,p)
    names=sorted(set(d['source_hashes'])|set(overlay));assert len(names)==457
    for n in['src/characters.s','src/sophia_source_terrain.s']:assert sha(H/'source'/n)==d['source_hashes'][n]
    driver=V/'root49-sophia-head-axis-d/build.py';shutil.copyfile(driver,H/'build.py')
    pre=dict(status='PREPARED_REVIEWED_ICE_OVER_D_PRIVATE_COMPOSITION',script_sha256=sha(__file__),
      checkpoint_D_sha256=sha(cp),Ice_freeze_sha256=sha(frozen),root_review_sha256=sha(review),build_driver_sha256=sha(driver),
      owned_overlay=overlay,preserved_D=['src/characters.s','src/sophia_source_terrain.s'],
      source_hashes={n:sha(H/'source'/n)for n in names},generated11=d['generated11'],
      phase_cap_bytes=500000000,final_reserve_bytes=50000000,global_cap_bytes=70000000000,main_changed=False)
    (H/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
    builds=[]
    for mp in['mmc3','mmc5']:
        for base in[False,True]:
            name=f'smb-crossover-{mp}'+('-baseline'if base else'')
            args=[sys.executable,str(H/'build.py'),'--mapper',mp]+(['--baseline']if base else[])
            print('START',name,flush=True)
            with(H/f'{name}.log').open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
            assert q.returncode==0,(name,q.returncode)
            p=H/'source/build'/f'{name}.nes';new=p.read_bytes();cyrom=(cy/'build'/f'{name}.nes').read_bytes()
            if base:
                assert new==cyrom,'Baseline must remain literal'
                delta=[]
            else:
                before=(R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d'/f'{name}.nes').read_bytes()
                parent=(old/'build'/f'{name}.nes').read_bytes();assert len(new)==len(before)==len(parent)==len(cyrom)
                expected={i:(x,y)for i,(x,y)in enumerate(zip(parent,cyrom))if x!=y}
                actual={i:(x,y)for i,(x,y)in enumerate(zip(before,new))if x!=y}
                assert actual==expected,('Merged byte patch does not commute exactly',mp,len(actual),len(expected),list(set(actual)^set(expected))[:12])
                assert not(set(expected)&{i for i,(x,y)in enumerate(zip(parent,before))if x!=y}),'Owned binary changes overlap D terrain/feet'
                delta=[dict(offset=i,old=x,new=y)for i,(x,y)in actual.items()]
            builds.append(dict(mapper=mp,baseline=base,artifacts={ext:dict(path=str(p.with_suffix('.'+ext).relative_to(R)),sha256=sha(p.with_suffix('.'+ext)),bytes=p.with_suffix('.'+ext).stat().st_size)for ext in['nes','lbl','dbg','map']},
              changed_bytes=len(delta),delta=delta,baseline_literal_CY=base,exact_owned_patch_commutes_over_D=not base))
            (H/'build-progress.json').write_text(json.dumps(dict(status='RUNNING',builds=builds),indent=2)+'\n')
            print('END',name,len(delta),'bytes',sha(p),flush=True)
    result=dict(status='PASS_FOUR_PRIVATE_BUILDS_EXACT_OWNED_BINARY_PATCH_OVER_D',script_sha256=sha(__file__),
      preparation_sha256=sha(H/'preparation.json'),builds=builds,main_changed=False,goal_complete=False,
      limits='Private composition only. Native composed-image checks and adoption are separate; no final route/movie or all-arsenal claim.')
    (H/'build-review.json').write_text(json.dumps(result,indent=2)+'\n');print('DONE',sha(H/'build-review.json'),flush=True)
if __name__=='__main__':main()
