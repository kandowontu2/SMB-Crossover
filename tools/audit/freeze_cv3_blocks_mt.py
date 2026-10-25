"""Freeze the precise native terrain adapter for the three CV3 alternates."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
V=R/'build/verification/cv3-blocks-mt'
O=R/'build/checkpoints/cv3-blocks-mt'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/cv3-roster-mr/manifest.json').read_text())
    proof=json.loads((V/'cpu-proof.json').read_text());native=json.loads((V/'native-results-v2.json').read_text())
    assert proof['passed'] and len(native)==3 and all(v==0 for v in native.values())
    paths={m:R/'build/checkpoints/cv3-roster-mr/build'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'cv3-blocks-v3.nes'
    assert sha(paths['mmc5-expanded'])==proof['sha256']
    # Only the guarded CV3 files affect executable code since MR. README and
    # audit programs do not participate in either standard target.
    differences={n for n,h in parent['source_files'].items() if sha(R/n)!=h}
    assert differences<={'README.md','src/cv3.s','src/cv3_combat.s','src/cv3_state.inc'},differences
    names=set(parent['source_files'])|{'src/cv3_blocks.s','tests/cv3-weapon-blocks-mt.lua','tools/audit/check_cv3_blocks_mt.py','tools/audit/freeze_cv3_blocks_mt.py'}
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    limits=[x for x in parent['limitations'] if not x.startswith('CV3 inherited')]
    limits+=['CV3 inherited Simon music/SFX and missing blue Ice tint remain documented. Native single-cell brick/question-block activation is now implemented for primary attacks and projectiles.']
    report=dict(parent,status='ADOPTED_CV3_WEAPON_BLOCKS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='cv3-roster-mr',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},source_zip_sha256=sha(O/'source.zip'),limitations=limits,cv3_weapon_block_CPU=proof,cv3_weapon_block_native=native)
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (R/'build/verification/root-current55-progress-mt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'])))

if __name__=='__main__':main()
