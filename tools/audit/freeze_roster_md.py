"""Freeze the integrated Darkwing/Zelda II build with physical art ownership."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/checkpoints/darkwing-zelda2-md'
V=R/'build/verification/zelda2-adoption-mc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    parent=R/'build/checkpoints/expanded-profiles-lr'
    old=json.loads((parent/'manifest.json').read_text())
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'smb-crossover-mmc5-dw-z2.nes'
    assert all(sha(paths[m])==old['ROMs'][m] for m in ('mmc3','mmc5'))
    raw=paths['mmc5-expanded'].read_bytes();chr_offset=16+1048576
    original=(parent/'build/smb-crossover-mmc5-expanded.nes').read_bytes()
    assert raw[chr_offset:chr_offset+0x40000]==original[chr_offset:chr_offset+0x40000]
    assets={'Proto':(0x40000,R/'chr/characters/protoman.chr'),
            'Darkwing':(0x45000,R/'chr/characters/darkwing.chr'),
            'ZeldaII body':(0x4d000,R/'chr/characters/zelda2-link-body.chr'),
            'ZeldaII items':(0x53c00,R/'chr/characters/zelda2-link-items.chr')}
    physical={}
    for who,(address,path) in assets.items():
        data=path.read_bytes()
        assert raw[chr_offset+address:chr_offset+address+len(data)]==data,who
        physical[who]=dict(first_physical_1k_page=address//1024,bytes=len(data),sha256=sha(path))
    proofs=[p for folder in ('proto','darkwing','z2') for p in (V/folder).glob('*.json')]
    assert len(proofs)>=3
    for p in proofs:assert json.loads(p.read_text())['passed'],p
    names=set(old['source_files'])
    for location in ('darkwing-adoption-lz','zelda2-adoption-mc'):
        names.update(json.loads((R/'build/verification'/location/'adoption.json').read_text())['after'])
    names.update(('tools/audit/adopt_darkwing_lz.py','tools/audit/adopt_zelda2_mc.py','tools/audit/freeze_roster_md.py'))
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(names):z.write(R/name,name)
    for m,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            target=O/'build'/('smb-crossover-'+m+ext);target.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),target)
            if m=='mmc5-expanded':shutil.copyfile(target,R/'build'/target.name)
    report=dict(status='ADOPTED_DARKWING_AND_ZELDAII_LINK',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='expanded-profiles-lr',
        ROMs={m:sha(p) for m,p in paths.items()},
        source_files={n:sha(R/n) for n in sorted(names)},
        native_proofs={str(p.relative_to(R)):sha(p) for p in proofs},
        physical_chr_slice_proofs=physical,native_first256_chr_pages_unchanged=True,
        playable_identities=17,standard_identities=14,
        scope='Expanded adds original Darkwing alternate and ZeldaII Link alternate, preserving Proto and existing roster.',
        limitations=['New profiles inherit Scrooge/ZeldaI audio; Z2 fairy/item palette and original death-scene polish remain.',
                     'Bounded native controls/abilities/pickups/death proven; no full campaign or video claim.'],
        videos_deferred=True,goal_complete=False)
    report['artifacts']={str(p.relative_to(O)):sha(p) for p in O.rglob('*') if p.is_file()}
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],physical_chr=physical)))


if __name__=='__main__':main()
