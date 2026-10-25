"""Compose the playable Gradius adapter privately over the frozen MJ roster."""
from pathlib import Path
import json
import argparse
import shutil
import subprocess
import sys
import zipfile
from PIL import Image

R=Path(__file__).resolve().parents[2]
O=R/'build/vic-viper-mk-private'


def main():
    global O
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=O)
    O=parser.parse_args().output.resolve()
    assert not O.exists()
    O.mkdir(parents=True)
    S=O/'source'
    with zipfile.ZipFile(R/'build/checkpoints/chip-roster-mj/source.zip') as z:z.extractall(S)
    old=R/'build/vic-viper-mh-private/source'
    for path in (old/'src').glob('vic_*'):
        shutil.copyfile(path,S/'src'/path.name)
    hud=R/'build/verification/vic-viper-lq/art/hud-mk'
    shutil.copyfile(hud/'vic_hud.inc',S/'src/vic_hud.inc')
    art=R/'build/verification/vic-viper-lq/art/packed-mh2'
    (S/'chr/characters/vic-viper.chr').write_bytes((art/'vic.chr').read_bytes()+(hud/'vic-hud.chr').read_bytes())
    (S/'src/vic_viper.s').write_text('''.include "vic_native_motion.s"
.include "vic_art.inc"
.include "vic_adapter.s"
.include "vic_render.s"
.include "vic_dispatch.s"
.pushseg
.segment "VIC_CHR"
.incbin "chr/characters/vic-viper.chr"
.popseg
''')
    def edit(file,old,new,count=1):
        path=S/file;text=path.read_text()
        assert text.count(old)==count,(file,old[:90],text.count(old))
        path.write_text(text.replace(old,new))
    edit('src/entrypoint.s','.include "x5_palette.s"','.include "x5_palette.s"\n.include "vic_viper.s"')
    edit('smb1base-mmc5-expanded.cfg','X5_NEW_4C: start=$a000','X5_NEW_4C: start=$c000')
    edit('smb1base-mmc5-expanded.cfg','X5_CHR_TAIL: start=$5f000','VIC_CHR_MEM: start=$5f000')
    edit('smb1base-mmc5-expanded.cfg','SEGMENTS {','''SEGMENTS {
    VIC_CORE:load=X5_NEW_4B,type=ro;
    VIC_GFX:load=X5_NEW_4C,type=ro;
    VIC_WORLD:load=X5_NEW_4D,type=ro;
    VIC_CHR:load=VIC_CHR_MEM,type=ro;
''')
    for file,old,new in (
        ('src/player.s','CdMovementDispatch','VvMovementDispatch'),('src/player.s','CdGraphicsDispatch','VvGraphicsDispatch'),
        ('src/player.s','CdDeathDispatch','VvDeathDispatch'),('src/object.s','CdWeaponsDispatch','VvWeaponsDispatch'),
        ('src/roster.s','CdResetDispatch','VvResetDispatch'),('src/screen_render.s','CdPortraitDispatch','VvPortraitDispatch'),
        ('src/collision.s','CdInjuryStartDispatch','VvInjuryDispatch'),('src/collision.s','CdPickupDispatch','VvPickupDispatch'),
        ('src/guest_body_contact.s','CdBodyDispatch','VvBodyDispatch'),('src/guest_body_contact.s','CdInjuryStatusDispatch','VvInjuryStatusDispatch'),
        ('src/megaman_death.s','CdInventoryDeathDispatch','VvDeathStartDispatch'),('src/kirby_draw.s','CdNewDrawDispatch','VvDrawDispatch'),
        ('src/characters.s','CdStatusNameDispatch','VvStatusName'),('src/expanded.s','CdAdderDispatch','VvAdderDispatch'),
        ('src/expanded.s','CdBoxDispatch','VvBoxDispatch'),('src/union_rare.s','Z2PreparePickupGate','VvPrepareDispatch'),
        ('src/level_tiles.s','Z2PreparePickupGate','VvPrepareDispatch')):
        edit(file,old,new)
    # Existing reserved resident tail; every old public entry retains its PC.
    edit('src/expanded.s','  .res 21,$ea','::VvScrollBridge:\n  farcall VvScrollGate,jmp\n  .res 3,$ea')
    edit('src/player.s','  jsr ScrollHandler           ;move the screen if necessary','''.if ::ENABLE_MMC5_EXPANDED
  jsr VvScrollBridge
.else
  jsr ScrollHandler           ;move the screen if necessary
.endif''')
    edit('src/mmc5.s','.bank(CdArtBegin)\n  .res 136','.bank(CdArtBegin),94,97,91,.bank(VicArtBegin)\n  .res 136')
    edit('src/x5_palette.s','  cmp #14\n','  cmp #18\n  bne :+\n  farcall VvGetPlayerColors,jmp\n:\n  cmp #14\n',1)
    edit('src/kirby_world_palette.s','  cmp #14\n  beq Mario','  cmp #14\n  beq Mario\n  cmp #18\n  beq Mario')
    edit('src/character_select.s','  .byte 120,120\n.endif\n.endproc','  .byte 120,120,120,120,120,120\n.endif\n.endproc')
    edit('src/character_select.s','  cmp #14\n  bne CdOtherName','  cmp #18\n  bne :+\n  lda #20\n  jmp NameIndex\n:\n  cmp #14\n  bne CdOtherName')
    edit('src/character_select.s','"     DALE       "','"     DALE       ","   VIC VIPER    "')
    # Source pose1 reconstructed from the same packed pixels used at runtime.
    manifest=json.loads((art/'manifest.json').read_text())
    data=(art/'vic.chr').read_bytes();picture=Image.new('RGBA',(48,32))
    palette={0:[(0,0,0,0),(0,64,88,255),(248,120,88,255),(0,232,216,255)],2:[(0,0,0,0),(0,0,0,0),(252,252,252,255),(0,0,0,0)]}
    for tile,attr,dy,dx in reversed(manifest['body_records']['1']):
        raw=data[tile*16:tile*16+32]
        dx=(dx+128)%256-128;dy=(dy+128)%256-128
        for y in range(16):
            for x in range(8):
                sx=7-x if attr&64 else x;sy=15-y if attr&128 else y
                value=((raw[(sy//8)*16+sy%8]>>(7-sx))&1)|(((raw[(sy//8)*16+sy%8+8]>>(7-sx))&1)<<1)
                if value:picture.putpixel((dx+x+16,dy+y),palette[attr&3][value])
    portrait=O/'vic-portrait.png';picture.save(portrait)
    spec=json.loads((R/'build/verification/chip-dale-candidate-agent/menu-input.json').read_text())
    spec['portraits'].append(dict(slot=17,character=18,image=str(portrait)))
    (O/'menu-input.json').write_text(json.dumps(spec,indent=2)+'\n')
    menu=O/'menu'
    subprocess.run([sys.executable,str(R/'tools/reference/build_x5_menu.py'),'--manifest',str(O/'menu-input.json'),'--output',str(menu)],check=True)
    shutil.copyfile(menu/'x5-menu-layout.inc',S/'src/x5_menu_layout.inc')
    shutil.copyfile(menu/'x5-menu.bin',S/'chr/raw/x5-character-select.bin')
    packed=bytearray((S/'chr/characters/packed-mmc5-expanded.chr').read_bytes())
    packed[4096:8192]=(menu/'x5-menu.chr').read_bytes()
    (S/'chr/characters/packed-mmc5-expanded.chr').write_bytes(packed)
    print(json.dumps(dict(private_source=str(S),baseline='chip-roster-mj',not_yet_verified=True)))


if __name__=='__main__':main()
