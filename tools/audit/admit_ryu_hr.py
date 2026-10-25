"""Admit the current-source Ryu side repair with unchanged old code/RAM layout."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';C=V/'ryu-current-hl/source';O=V/'ryu-admission-hr';CP=R/'build/checkpoints/ryu-overlap-hr'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())


def main():
    assert not O.exists()and not CP.exists();O.mkdir()
    parent=R/'build/checkpoints/weapons-source-go/manifest.json';prep=read(C.parent/'preparation.json');build=read(C.parent/'build.json')
    assert build['passed']and sha(parent)==prep['parent_manifest_sha256']
    for n,h in prep['source_before'].items():assert sha(R/n)==h,n
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==h for m,h in prep['parent_ROMs'].items())
    assert set(prep['modified_files'])=={'src/entrypoint.s','src/samus_collision_ram.s','src/ryu_side_overlap.s','smb1base.cfg'}
    verification={}
    for name in('ryu-native-hm','ryu-dispatch-cost-ho','ryu-final-regressions-hp'):
        p=V/name/'summary.json';j=read(p);assert j['passed'];verification[p.relative_to(R).as_posix()]=sha(p)
    j=read(V/'ryu-native-hm/summary.json');assert j['actual_compiled_calls']==119 and j['actual_interrupt_gaps']==5
    expected={m:sha(C/f'build/smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
    (O/'preparation.json').write_text(json.dumps(dict(parent_sha256=sha(parent),expected_ROMs=expected,verification=verification,goal_complete=False),indent=2)+'\n')
    for n,h in prep['modified_files'].items():assert sha(C/n)==h;shutil.copyfile(C/n,R/n)
    for mapper in expected:
        with(O/(mapper+'-build.log')).open('wb')as f:z=subprocess.run([sys.executable,str(R/'tools/build.py'),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT)
        assert z.returncode==0 and sha(R/f'build/smb-crossover-{mapper}.nes')==expected[mapper]
        print('MAIN',mapper,'literal HL',flush=True)
    names=set(prep['source_before'])|set(prep['modified_files'])
    for mapper in expected:
        for base in('','-baseline'):
            for ext in('nes','dbg','lbl','map'):names.add(f'build/smb-crossover-{mapper}{base}.{ext}')
    for n in names:
        dst=CP/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,dst)
    manifest=dict(status='RYU_SOURCE_CLIMB_AND_PRIOR_INTERIOR_SIDE_REPAIR_ADMITTED_FULL_GOAL_ACTIVE',utc=datetime.now(timezone.utc).isoformat(),parent_checkpoint=parent.relative_to(R).as_posix(),parent_checkpoint_sha256=sha(parent),ROMs=expected,hashes={n:sha(CP/n)for n in sorted(names)},source_overlay=prep['modified_files'],verification=verification,limits=['124native whole-BG source/fallback checks;119exact complete compiled caller reexecutions. Five actual interrupt cases remain standalone CPU-model gaps and are not hidden.','Normal25 prior/current overlap and source climb bypass only; general stuck state/later recovery and other source geometry remain open.','Forty-byte source-guard dispatcher and literal725-byte predicate occupy existing bank24 B700..B9FC. No new RAM, CHR, header or old public-PC changes.','Local matched guard costs: climb234cycles and landing313cycles faster than first HD wrapper; detailed uncommon predicates18cycles slower. The repair as a whole is not a global lag reduction claim.','No new current full Ryu route or final media proof.'],goal_complete=False)
    (CP/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (O/'summary.json').write_text(json.dumps(dict(passed=True,checkpoint_sha256=sha(CP/'manifest.json'),ROMs=expected,verification=verification,goal_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
