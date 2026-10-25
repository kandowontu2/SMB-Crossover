"""Freeze the integrated playable Chip/Dale addition and Kirby backdrop fix."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
V=R/'build/verification/chip-adoption-mj'
O=R/'build/checkpoints/chip-roster-mj'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/kirby-roster-mg/manifest.json').read_text())
    adoption=json.loads((V/'adoption.json').read_text())
    admission=json.loads((V/'admission.json').read_text())
    assert admission['passed']
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'chip-final.nes'
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    logs=list(V.glob('*/build/verification/*.log'))
    assert len(logs)==4
    assert all('PASS' in p.read_text() and 'FAIL' not in p.read_text() for p in logs)
    names=set(parent['source_files'])
    names.update(c['path'] for c in adoption['changes'])
    names.update(('tools/audit/adopt_chip_mj.py','tools/audit/check_chip_mj.py','tools/audit/freeze_roster_mj.py','tools/build_mmc5_expanded.py'))
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext)
            dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(status='ADOPTED_PLAYABLE_CHIP_DALE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                parent_checkpoint='kirby-roster-mg',ROMs={m:sha(p) for m,p in paths.items()},
                source_files={n:sha(R/n) for n in sorted(names)},implemented_identities=20,target_identities=32,
                native_logs={str(p.relative_to(R)):sha(p) for p in logs},admission=admission,
                remaining_profiles=['Grant/Sypha/Alucard','TMNT four turtles','SMB3 Mario/Luigi','Vic Viper','Little Mac','Mike Jones'],
                limitations=['Chip/Dale inherited Pit music and SMB SFX; source recoil/death/hull and one-way drop remain partial.',
                             'Original soundtrack additions and campaign validation remain unfinished for earlier new profiles.'],
                videos_deferred=True,goal_complete=False)
    report['source_zip_sha256']=sha(O/'source.zip')
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (R/'build/verification/root-current50-progress-mj.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],identities=20,source_files=len(names),source_zip_sha256=report['source_zip_sha256'])))


if __name__=='__main__':main()
