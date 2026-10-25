"""Freeze four authentic turtle primary profiles with palette scheduling fixes."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
V=R/'build/verification/tmnt-adoption-mn'
O=R/'build/checkpoints/tmnt-roster-mn'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/chip-roster-mj/manifest.json').read_text())
    adoption=json.loads((V/'adoption.json').read_text())
    native=json.loads((V/'native-results.json').read_text())
    assert len(native)==7 and all(r['exit']==0 for r in native.values())
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'tmnt-composed.nes'
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    names=set(parent['source_files'])|set(adoption['before'])|set(adoption['owned'])
    names.update(('chr/characters/tmnt.chr','tools/audit/adopt_tmnt_mn.py','tools/audit/check_tmnt_mn.py','tools/audit/freeze_roster_mn.py'))
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(status='ADOPTED_FOUR_TMNT_PRIMARY_PROFILES',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                parent_checkpoint='chip-roster-mj',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},
                source_zip_sha256=sha(O/'source.zip'),implemented_identities=24,target_identities=32,
                native_results=native,graphics_correction='Constant Kirby/Chip/TMNT body palettes no longer queue VRAM every pose; used-block replacement proven in ordinary turtle scene.',
                remaining_profiles=['Grant/Sypha/Alucard','SMB3 Mario/Luigi','Vic Viper','Little Mac','Mike Jones'],
                limitations=['Turtle primary equipment only; secondary equipment/audio/dam swimming remain partial.',
                             'Inherited audio remains provisional for several new profiles; full campaign coverage unclaimed.'],videos_deferred=True,goal_complete=False)
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (R/'build/verification/root-current51-progress-mn.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],identities=24,source_files=len(names),source_zip_sha256=report['source_zip_sha256'])))


if __name__=='__main__':main()
