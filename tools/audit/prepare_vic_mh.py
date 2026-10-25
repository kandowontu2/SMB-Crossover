"""Stage the real Vic Viper instructions/art/world queries over frozen MG."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/vic-viper-mh-private'


def main():
    assert not O.exists()
    O.mkdir(parents=True);source=O/'source'
    checkpoint=R/'build/checkpoints/kirby-roster-mg'
    with zipfile.ZipFile(checkpoint/'source.zip') as z:z.extractall(source)
    # Reuse authenticated generators, with an explicit independent destination.
    import sys
    sys.path.insert(0,str(R/'tools/reference'))
    import build_vic_weapons as generator
    generator.O=O;generator.movement.OUT=O
    generator.main()
    s=source/'src'
    weapons=s/'vic_native_weapons.s'
    text=weapons.read_text();a=text.index('; CPU fixture ONLY.')
    text=text[:a]+'.popseg\n.include "vic_world_queries.s"\n'
    # Remove the two test-only aliases: real probes own the same free bytes.
    for line in ('VvTestTerrainUnder=$5dfe\n','VvTestTerrainSide=$5dff\n',
                 '.export VvTestTerrainUnder,VvTestTerrainSide\n'):
        assert text.count(line)==1;text=text.replace(line,'')
    weapons.write_text(text)
    shutil.copyfile(R/'tools/reference/vic_world_queries.s',s/'vic_world_queries.s')
    art=R/'build/verification/vic-viper-lq/art/packed-mh2'
    shutil.copyfile(art/'vic_art.inc',s/'vic_art.inc')
    shutil.copyfile(art/'vic.chr',source/'chr/characters/vic-viper.chr')
    (s/'vic_viper.s').write_text('''.include "vic_native_motion.s"
.include "vic_art.inc"
.pushseg
.segment "VIC_CHR"
.incbin "chr/characters/vic-viper.chr"
.popseg
''')
    ep=s/'entrypoint.s';text=ep.read_text();assert text.count('.include "x5_palette.s"')==1
    ep.write_text(text.replace('.include "x5_palette.s"','.include "x5_palette.s"\n.include "vic_viper.s"'))
    cfg=source/'smb1base-mmc5-expanded.cfg';text=cfg.read_text()
    assert text.count('X5_NEW_4C: start=$a000')==1
    text=text.replace('X5_NEW_4C: start=$a000','X5_NEW_4C: start=$c000')
    text=text.replace('SEGMENTS {','''SEGMENTS {
    VIC_CORE: load=X5_NEW_4B,type=ro;
    VIC_GFX: load=X5_NEW_4C,type=ro;
    VIC_WORLD: load=X5_NEW_4D,type=ro,optional=yes;
    VIC_CHR: load=VIC_CHR_MEM,type=ro;
''',1)
    old='X5_CHR_TAIL: start=$5f000, size=$a1000'
    assert text.count(old)==1
    text=text.replace(old,'VIC_CHR_MEM: start=$5f000, size=$8000, type=ro, fill=yes, file=%O, fillval=$00;\n    X5_CHR_TAIL: start=$67000, size=$99000')
    cfg.write_text(text)
    report=dict(status='PRIVATE_REAL_COMPONENTS_WORLD_QUERY_STAGED_NOT_SELECTABLE',
        baseline='kirby-roster-mg',baseline_manifest_sha256=hashlib.sha256((checkpoint/'manifest.json').read_bytes()).hexdigest(),
        source_ROM='GradiusUSA',sprite_CHR_first=380,sprite_CHR_bytes=14336,
        corrections=['Real terrain query maps originalA4=X/A5=Y; replaces deterministic callbacks.',
                     'Original capsule poses16/17/18 and native death45/46/47/48; earlier90..93 shield classification rejected.'],
        missing=['Playableadmission/body/contact/camera','Physicalcapsules/drops','Nativepowerbar','Audio'])
    (O/'stage.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
