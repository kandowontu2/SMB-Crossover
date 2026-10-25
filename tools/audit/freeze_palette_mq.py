"""Freeze bounded native palette/block regression repair over playable MP."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, shutil, zipfile
R=Path(__file__).resolve().parents[2]
V=R/'build/verification/palette-adoption-mq'
O=R/'build/checkpoints/palette-roster-mq'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/vic-roster-mp/manifest.json').read_text())
    proof=json.loads((V/'cpu-proof.json').read_text());native=json.loads((V/'native-results.json').read_text())
    assert proof['passed'] and len(native)==4 and all(v==0 for v in native.values())
    spec=importlib.util.spec_from_file_location('mq_negative',R/'tools/run_mesen.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    negatives={}
    for target in ('darkwing','zelda2'):
        folder=V/('negative-mp-v2-'+target);folder.mkdir(exist_ok=True)
        text=(R/'tests/alternate-block-publication-mq.lua').read_text().replace('f=f+1','f=f+1\n if f%120==0 then print("MENU DEBUG "..f.." phase"..phase.." state"..r("CrossoverMenuState").." index"..r("CrossoverMenuIndex").." var"..r(variant).." oper"..r("OperMode").." engine"..r("GameEngineSubroutine"))end')
        script=folder/'blocks.lua';script.write_text('TARGET="'+target+'"\n'+text)
        runner.ROOT=folder;code=runner.run(script,R/'build/checkpoints/vic-roster-mp/build/smb-crossover-mmc5-expanded.nes',timeout=45)
        log=folder/'build/verification/smb-crossover-mmc5-expanded-blocks.log'
        assert code!=0 and 'Native deferred replacement clears bumped cell' in log.read_text(),target
        negatives[target]=dict(exit=code,reason='Native deferred replacement clears bumped cell')
    (V/'negative-controls.json').write_text(json.dumps(negatives,indent=2)+'\n')
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'palette-final.nes'
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    assert sha(paths['mmc5-expanded'])==proof['sha256']
    names=set(parent['source_files'])|{'tools/audit/check_palette_mq.py','tools/audit/freeze_palette_mq.py','tests/alternate-block-publication-mq.lua'}
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(parent,status='ADOPTED_PALETTE_BLOCK_REPAIR',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='vic-roster-mp',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},source_zip_sha256=sha(O/'source.zip'),palette_CPU_proof=proof,palette_native_results=native,palette_negative_controls=negatives)
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (R/'build/verification/root-current53-progress-mq.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'])))

if __name__=='__main__':main()
