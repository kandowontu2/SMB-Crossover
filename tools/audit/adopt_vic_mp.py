"""Compose verified Vic Viper over the turtle roster, retaining all cold chains."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
D=R/'build/vic-viper-ml-private/source'
O=R/'build/verification/vic-adoption-mp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/tmnt-roster-mn/manifest.json').read_text())
    shared=('src/entrypoint.s','src/player.s','src/object.s','src/roster.s','src/screen_render.s',
            'src/collision.s','src/guest_body_contact.s','src/megaman_death.s','src/kirby_draw.s',
            'src/characters.s','src/expanded.s','src/union_rare.s','src/level_tiles.s','src/x5_palette.s',
            'src/kirby_world_palette.s','src/character_select.s','src/game.s','src/reset.s',
            'src/x5_menu_layout.inc','chr/characters/packed-mmc5-expanded.chr',
            'chr/raw/x5-character-select.bin','smb1base-mmc5-expanded.cfg')
    for name in shared:assert sha(R/name)==parent['source_files'][name],name
    texts={n:(R/n).read_text() for n in shared if not n.endswith(('.chr','.bin'))}
    own={str(p.relative_to(D)).replace('\\','/'):p.read_text() for p in (D/'src').glob('vic_*')}
    assert all(not(R/n).exists() for n in own)
    def edit(name,old,new,count=1):
        assert texts[name].count(old)==count,(name,old[:80],texts[name].count(old))
        texts[name]=texts[name].replace(old,new)
    name='src/vic_dispatch.s'
    for old,new in (('CdMovementDispatch','TnMovementDispatch'),('CdGraphicsDispatch','TnGraphicsDispatch'),('CdPortraitDispatch','TnPortraitDispatch'),
                    ('CdWeaponsDispatch','TnWeaponsDispatch'),('CdNewDrawDispatch','TnDrawDispatch'),('CdInjuryStartDispatch','TnInjuryStartDispatch'),
                    ('CdBodyDispatch','TnBodyDispatch'),('CdDeathDispatch','TnDeathDispatch'),('CdResetDispatch','TnResetDispatch'),
                    ('CdInjuryStatusDispatch','TnInjuryStatusDispatch'),('CdBoxDispatch','TnBoxDispatch'),('CdAdderDispatch','TnAdderDispatch'),('CdPickupDispatch','TnPickupDispatch')):
        own[name]=own[name].replace(old,new)
    old=' pla\n plp\n jmp BoundingBoxCore\nNative:'
    assert own[name].count(old)==1
    own[name]=own[name].replace(old,' pla\n plp\n farcall TnBoundingBoxGate,jmp\nNative:')
    edit('src/entrypoint.s','.include "x5_palette.s"','.include "x5_palette.s"\n.include "vic_viper.s"')
    for file,old,new in (
        ('src/player.s','TnMovementDispatch','VvMovementDispatch'),('src/player.s','TnGraphicsDispatch','VvGraphicsDispatch'),('src/player.s','TnDeathDispatch','VvDeathDispatch'),
        ('src/player.s','TnBoundingBoxGate','VvBoundingBoxGate'),('src/object.s','TnWeaponsDispatch','VvWeaponsDispatch'),('src/roster.s','TnResetDispatch','VvResetDispatch'),
        ('src/screen_render.s','TnPortraitDispatch','VvPortraitDispatch'),('src/collision.s','TnInjuryStartDispatch','VvInjuryDispatch'),('src/collision.s','TnPickupDispatch','VvPickupDispatch'),
        ('src/guest_body_contact.s','TnBodyDispatch','VvBodyDispatch'),('src/guest_body_contact.s','TnInjuryStatusDispatch','VvInjuryStatusDispatch'),
        ('src/megaman_death.s','CdInventoryDeathDispatch','VvDeathStartDispatch'),('src/kirby_draw.s','TnDrawDispatch','VvDrawDispatch'),
        ('src/characters.s','CdStatusNameDispatch','VvStatusName'),('src/expanded.s','TnAdderDispatch','VvAdderDispatch'),('src/expanded.s','TnBoxDispatch','VvBoxDispatch'),
        ('src/union_rare.s','Z2PreparePickupGate','VvPrepareDispatch'),('src/level_tiles.s','Z2PreparePickupGate','VvPrepareDispatch'),('src/game.s','Z2UiTickGate','VvUiDispatch')):
        edit(file,old,new)
    # Reuse two existing resident gaps; old entry addresses and PLAYER size stay fixed.
    edit('src/expanded.s','  .res 21,$ea','::VvScrollBridge:\n  farcall VvScrollGate,jmp\n  .res 3,$ea')
    start=(D/'src/expanded.s').read_text()
    a=start.index('::X5RestoreWorldFont:');b=start.index('  .assert *-ExpandedGraphicsBank',a)
    edit('src/expanded.s','  .res 23,$ea',start[a:b].rstrip())
    edit('src/reset.s','    stx IrqNewScroll\n  plx',''' .if ::ENABLE_MMC5_EXPANDED
    jmp X5RestoreWorldFont
 .else
    stx IrqNewScroll
 .endif
  plx''')
    edit('src/player.s','  jsr ScrollHandler           ;move the screen if necessary',''' .if ::ENABLE_MMC5_EXPANDED
  jsr VvScrollBridge
 .else
  jsr ScrollHandler           ;move the screen if necessary
 .endif''')
    edit('src/x5_palette.s','  cmp #CHARACTER_TMNT\n','  cmp #18\n  bne :+\n  farcall VvGetPlayerColors,jmp\n:\n  cmp #CHARACTER_TMNT\n')
    edit('src/kirby_world_palette.s','  cmp #CHARACTER_TMNT\n  beq Mario','  cmp #CHARACTER_TMNT\n  beq Mario\n  cmp #18\n  beq Mario')
    edit('src/character_select.s','  cmp #CHARACTER_TMNT\n  bne :+\n  lda TnVariant','  cmp #18\n  bne :+\n  lda #24\n  jmp NameIndex\n:\n  cmp #CHARACTER_TMNT\n  bne :+\n  lda TnVariant')
    edit('src/character_select.s','"   DONATELLO    "','"   DONATELLO    ","   VIC VIPER    "')
    edit('smb1base-mmc5-expanded.cfg','X5_NEW_4C: start=$a000','X5_NEW_4C: start=$c000')
    edit('smb1base-mmc5-expanded.cfg','X5_CHR_TAIL: start=$5f000','VIC_CHR_MEM: start=$5f000')
    edit('smb1base-mmc5-expanded.cfg','SEGMENTS {','''SEGMENTS {
    VIC_CORE:load=X5_NEW_4B,type=ro;
    VIC_GFX:load=X5_NEW_4C,type=ro;
    VIC_WORLD:load=X5_NEW_4D,type=ro;
    VIC_CHR:load=VIC_CHR_MEM,type=ro;
''')
    # The fully resident IRQ font restoration relies on the native deduplicated font.
    fonts={(R/f'chr/mmc5/bg_{n}.chr').read_bytes()[:1024] for n in ('water','ground','underground','castle')}
    assert len(fonts)==1
    raw=(R/'build/checkpoints/tmnt-roster-mn/build/smb-crossover-mmc5-expanded.nes').read_bytes()
    assert raw[16+1048576:16+1048576+1024]==next(iter(fonts))
    O.mkdir(parents=True)
    spec=json.loads((R/'build/verification/tmnt-adoption-mn/menu-input.json').read_text())
    spec['portraits'].append(dict(slot=17,character=18,image=str(R/'build/vic-viper-ml-private/vic-portrait.png')))
    (O/'menu-input.json').write_text(json.dumps(spec,indent=2)+'\n')
    subprocess.run([sys.executable,str(R/'tools/reference/build_x5_menu.py'),'--manifest',str(O/'menu-input.json'),'--output',str(O/'menu')],check=True)
    texts['src/x5_menu_layout.inc']=(O/'menu/x5-menu-layout.inc').read_text()
    for name in shared:
        backup=O/'before'/name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,backup)
    for name,text in {**texts,**own}.items():(R/name).write_text(text)
    shutil.copyfile(D/'chr/characters/vic-viper.chr',R/'chr/characters/vic-viper.chr')
    shutil.copyfile(O/'menu/x5-menu.bin',R/'chr/raw/x5-character-select.bin')
    packed=bytearray((R/'chr/characters/packed-mmc5-expanded.chr').read_bytes())
    packed[4096:8192]=(O/'menu/x5-menu.chr').read_bytes()
    (R/'chr/characters/packed-mmc5-expanded.chr').write_bytes(packed)
    report=dict(parent='tmnt-roster-mn',before={n:sha(O/'before'/n) for n in shared},
                after={n:sha(R/n) for n in shared},owned={n:sha(R/n) for n in own},
                asset_sha256=sha(R/'chr/characters/vic-viper.chr'),native_font_dedup_proved=True,
                private_verified_candidate='vic-native-point.nes',qualification='Full native movement/weapons plus authored SMB world/capsule/exit adapters; inherited music provisional.')
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(adopted_files=len(shared)+len(own)+1,evidence=str(O))))


if __name__=='__main__':main()
