"""Freeze the playable Gradius ship and verified shared IRQ font publication."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
V=R/'build/verification/vic-adoption-mp'
O=R/'build/checkpoints/vic-roster-mp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/tmnt-roster-mn/manifest.json').read_text())
    adoption=json.loads((V/'adoption.json').read_text())
    results=json.loads((V/'final-native-results.json').read_text())
    irq=json.loads((V/'irq-proof.json').read_text())
    assert len(results)==13 and all(r['exit']==0 for r in results.values()) and irq['passed']
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'vic-composed-final.nes'
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    assert sha(paths['mmc5-expanded'])==irq['new_sha256']
    names=set(parent['source_files'])|set(adoption['before'])|set(adoption['owned'])
    names.update(('chr/characters/vic-viper.chr','tools/audit/adopt_vic_mp.py','tools/audit/check_vic_mp.py',
                  'tools/audit/check_vic_irq_mp.py','tools/audit/freeze_roster_mp.py',
                  'tools/reference/build_vic_hud.py','tools/reference/vic_world_queries.s',
                  'tools/reference/build_vic_motion.py','tools/reference/build_vic_weapons.py',
                  'tools/reference/build_vic_assets.py','tools/reference/pack_vic_assets_ma.py','tools/reference/vic_gear.s',
                  'tools/reference/import_gradius_source.py','docs/qa/vic-viper-implementation-2026-10-23.md'))
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(status='ADOPTED_PLAYABLE_VIC_VIPER',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                parent_checkpoint='tmnt-roster-mn',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},
                source_zip_sha256=sha(O/'source.zip'),implemented_identities=25,target_identities=32,
                native_results=results,IRQ_CPU_proof=irq,
                scope='Original ship movement/tilt, native firing/three gun types/missiles/twoOptions/powerbar and five-charge shield; physical capsules, native SMB exits and auto-scroll adapters.',
                remaining_profiles=['Grant/Sypha/Alucard','SMB3 Mario/Luigi','Little Mac','Mike Jones'],
                limitations=['Vic Viper currently inherits Pit music and SMB SFX; original Gradius soundtrack pending.',
                             'Two sprite hues and monochrome powerbar are palette-sharing adaptations; exact pixel masks retained.',
                             'SMB capsule delivery, world contact, one-pixel auto-scroll and level exits are authored adapters; full campaign unclaimed.',
                             'Earlier new-profile secondary equipment/audio polish remains documented and incomplete.'],videos_deferred=True,goal_complete=False)
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (R/'build/verification/root-current52-progress-mp.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],identities=25,source_files=len(names),source_zip_sha256=report['source_zip_sha256'])))


if __name__=='__main__':main()
