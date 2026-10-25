"""Freeze the adopted Proto expansion and exact standard-cartridge controls."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'build/checkpoints/protoman-ky'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    O.mkdir()
    adoption = R/'build/verification/proto-adoption-ks/adoption.json'
    assert json.loads(adoption.read_text())['status'] == 'ADOPTED_MAIN_EXPANDED_PROTO_NATIVE_SMOKE_PASSES'
    parent = R/'build/checkpoints/rygar-walk-kb'
    with zipfile.ZipFile(parent/'source.zip') as archive:
        names = set(archive.namelist())
    gm=json.loads((R/'build/player-guide-agent/mmc5-native-kb-private/incremental-merge-manifest.json').read_text())
    pm=json.loads((R/'build/verification/protoman-candidate-agent/manifest.json').read_text())
    names.update(x['path'] for x in gm['merge_files'])
    names.update(pm['new_source_hashes'])
    names.update(p.relative_to(R).as_posix() for p in (R/'build/generated/guest-audio').rglob('*') if p.is_file())
    names.update(('tools/build.py','tools/prepare_guest_audio.py','tools/reference/pack_chr.py','tools/reference/tag_player_outlines.py'))
    for name in sorted(names):
        assert (R/name).is_file(), name
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted(names):
            archive.write(R/name,name)
    roms={}
    for mapper in ('mmc3','mmc5','mmc5-expanded'):
        stem='smb-crossover-'+mapper
        for ext in ('.nes','.lbl','.dbg','.map'):
            source=R/'build'/(stem+ext)
            target=O/'build'/source.name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(source,target)
        roms[mapper]=sha(R/'build'/(stem+'.nes'))
    prior=json.loads((parent/'manifest.json').read_text())['ROMs']
    assert all(roms[m]==prior[m] for m in ('mmc3','mmc5'))
    assert roms['mmc5-expanded']==pm['ROM_SHA256']
    report=dict(status='ADOPTED_PROTO_MMC5_EXPANSION_FULL_GOAL_ACTIVE',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint=str((parent/'manifest.json').relative_to(R)),
        ROMs=roms,source_files={n:sha(R/n) for n in sorted(names)},
        artifacts={p.relative_to(O).as_posix():sha(p) for p in O.rglob('*') if p.is_file()},
        adoption_receipt={'path':str(adoption.relative_to(R)),'sha256':sha(adoption)},
        scope='Expanded cartridge adds Proto Man. Standard MMC3/MMC5 exactly KB. Full roster/arsenal/campaign/final-film work still active.',
        bass_corner_installed=False,level_helpers_installed=False,goal_complete=False)
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checkpoint':str(O),'ROMs':roms,'files':len(names)}))


if __name__=='__main__':
    main()
