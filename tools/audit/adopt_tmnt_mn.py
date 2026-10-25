"""Compose the authenticated TMNT primary packet over the newer Chip roster."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
D=R/'build/tmnt-kd-private/handoff-TMNT-primary-n'
O=R/'build/verification/tmnt-adoption-mn'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not O.exists()
    packet=json.loads((D/'manifest.json').read_text())
    for name,digest in packet['files'].items():assert sha(D/name)==digest,name
    checkpoint=json.loads((R/'build/checkpoints/chip-roster-mj/manifest.json').read_text())
    common=set(packet['common_files'])
    common.update(('chr/characters/packed-mmc5-expanded.chr','chr/raw/x5-character-select.bin'))
    for name in common:assert sha(R/name)==checkpoint['source_files'][name],name
    texts={n:(R/n).read_text() for n in common if not n.endswith(('.chr','.bin'))}
    owned={n:(D/n).read_text() for n in packet['owned_files']}
    assert all(not(R/n).exists() for n in owned)
    def edit(name,old,new,count=1):
        assert texts[name].count(old)==count,(name,old[:80],texts[name].count(old))
        texts[name]=texts[name].replace(old,new)
    for name in owned:
        if name.endswith('tmnt_dispatch.s'):
            # Root's outer Chip chain owns all previously integrated profiles.
            for old,new in (('KbMovementDispatch','CdMovementDispatch'),('KbGraphicsDispatch','CdGraphicsDispatch'),('KbPortraitDispatch','CdPortraitDispatch'),('KbDeathDispatch','CdDeathDispatch'),('KbWeaponsDispatch','CdWeaponsDispatch'),('KbInjuryStatusDispatch','CdInjuryStatusDispatch'),('KbInjuryStartDispatch','CdInjuryStartDispatch'),('KbPickupDispatch','CdPickupDispatch'),('KbBodyDispatch','CdBodyDispatch'),('KbResetDispatch','CdResetDispatch'),('KbAdderDispatch','CdAdderDispatch'),('KbBoxDispatch','CdBoxDispatch')):
                owned[name]=owned[name].replace(old,new)
            start=owned[name].index('.proc TnDrawDispatch\n')
            end=owned[name].index('.endproc',start)+len('.endproc')
            owned[name]=owned[name][:start]+'''.proc TnDrawDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdNewDrawDispatch,jmp
Native:jmp TnDraw
.endproc'''+owned[name][end:]
    edit('src/entrypoint.s','.include "kirby_state.inc"','.include "kirby_state.inc"\n.include "tmnt_state.inc"')
    edit('src/entrypoint.s','.include "x5_palette.s"','.include "tmnt.s"\n.include "x5_palette.s"')
    for name,old,new in (
        ('src/player.s','CdMovementDispatch','TnMovementDispatch'),('src/player.s','CdGraphicsDispatch','TnGraphicsDispatch'),('src/player.s','CdDeathDispatch','TnDeathDispatch'),
        ('src/object.s','CdWeaponsDispatch','TnWeaponsDispatch'),('src/roster.s','CdResetDispatch','TnResetDispatch'),('src/screen_render.s','CdPortraitDispatch','TnPortraitDispatch'),
        ('src/collision.s','CdInjuryStartDispatch','TnInjuryStartDispatch'),('src/collision.s','CdPickupDispatch','TnPickupDispatch'),
        ('src/guest_body_contact.s','CdBodyDispatch','TnBodyDispatch'),('src/guest_body_contact.s','CdInjuryStatusDispatch','TnInjuryStatusDispatch'),
        ('src/guest_injury.s','DwPlayerVisible','TnVisibleDispatch'),('src/metasprite_engine.s','Z2SpecialDrawGate','TnSpecialDrawDispatch'),
        ('src/expanded.s','CdAdderDispatch','TnAdderDispatch'),('src/expanded.s','CdBoxDispatch','TnBoxDispatch'),('src/expanded.s','KbHeadDispatch','TnHeadDispatch'),
        ('src/kirby_draw.s','CdNewDrawDispatch','TnDrawDispatch')):edit(name,old,new)
    edit('src/player.s','  jsr BoundingBoxCore     ;get player\'s bounding box coordinates',''' .if ::ENABLE_MMC5_EXPANDED
  farcall TnBoundingBoxGate
 .else
  jsr BoundingBoxCore     ;get player's bounding box coordinates
 .endif''')
    # No new resident branch: extend the existing indexed, NMI-safe table.
    edit('src/mmc5.s','.bank(CdArtBegin)\n  .res 136','.bank(CdArtBegin),94,97,91,76,.bank(TnArtStart)\n  .res 136')
    edit('src/kirby_world_palette.s','  cmp #14\n  beq Mario','  cmp #14\n  beq Mario\n  cmp #CHARACTER_TMNT\n  beq Mario')
    edit('src/expanded_audio.s','  cmp #CHARACTER_KIRBY\n  bcc Done','''  cmp #CHARACTER_TMNT
  bne :+
  lda #CHARACTER_RYGAR
  rts
: cmp #CHARACTER_KIRBY
  bcc Done''')
    edit('src/x5_palette.s','  cmp #14\n','''  cmp #CHARACTER_TMNT
  bne :+
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  farcall TnQueuePalette,jmp
: lda SelectedCharacter
  cmp #14
''')
    edit('src/protoman_cold.s','  lda SelectedCharacter\n  cmp #CHARACTER_KIRBY','''  lda SelectedCharacter
  cmp #CHARACTER_TMNT
  bne :+
  lda TnVariant
  clc
  adc #16
  jmp NameIndex
:
  cmp #CHARACTER_KIRBY''')
    edit('src/protoman_cold.s','"KIRBY  "','"KIRBY  ","LEO    ","RAPH   ","MIKE   ","DON    "')
    edit('src/character_select.s','CheckDirection:\n','''CheckDirection:
.if ::ENABLE_MMC5_EXPANDED
  lda SelectedCharacter
  cmp #CHARACTER_TMNT
  bne TnNoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq TnNoToggle
  inc TnVariant
  lda TnVariant
  and #3
  sta TnVariant
  lda CrossoverMenuIndex
  jmp Changed
TnNoToggle:
.endif
''')
    edit('src/character_select.s','  .byte 120,120\n.endif\n.endproc','  .byte 120,120,120,120,120,120,120\n.endif\n.endproc')
    edit('src/character_select.s','  cmp #14\n  bne CdNoHint','  cmp #CHARACTER_TMNT\n  bne TnNoHint\n  lda TnHint,y\n  jmp Put\nTnNoHint:\n  cmp #14\n  bne CdNoHint')
    edit('src/character_select.s','CdHint: .byte','TnHint: .byte "SELECT - TURTLES    "\nCdHint: .byte')
    edit('src/character_select.s','  cmp #14\n  bne CdOtherName','''  cmp #CHARACTER_TMNT
  bne :+
  lda TnVariant
  clc
  adc #20
  jmp NameIndex
:
  cmp #14
  bne CdOtherName''')
    edit('src/character_select.s','"     DALE       "','"     DALE       ","   LEONARDO     ","   RAPHAEL      "," MICHELANGELO   ","   DONATELLO    "')
    edit('smb1base-mmc5-expanded.cfg','X5_NEW_58: start=$a000','X5_NEW_58: start=$c000')
    edit('smb1base-mmc5-expanded.cfg','CD_CHR_TAIL: start=$73000,size=$8d000,type=ro,fill=yes,file=%O,fillval=$00;','''CD_CHR_TAIL: start=$73000,size=$24000,type=ro,fill=yes,file=%O,fillval=$00;
    TMNT_CHR_MEM: start=$97000,size=$10000,type=ro,fill=yes,file=%O,fillval=$00;
    TMNT_CHR_TAIL: start=$a7000,size=$59000,type=ro,fill=yes,file=%O,fillval=$00;''')
    edit('smb1base-mmc5-expanded.cfg','SEGMENTS {','''SEGMENTS {
    TMNT_CORE:load=X5_NEW_57,type=ro;
    TMNT_GFX:load=X5_NEW_58,type=ro;
    TMNT_COMBAT:load=X5_NEW_59,type=ro;
    TMNT_CHR:load=TMNT_CHR_MEM,type=ro;
''')
    O.mkdir(parents=True)
    spec=json.loads((R/'build/verification/chip-dale-candidate-agent/menu-input.json').read_text())
    spec['portraits'].append(dict(slot=18,character=19,image=str(D/'art/tmnt-portrait.png')))
    (O/'menu-input.json').write_text(json.dumps(spec,indent=2)+'\n')
    subprocess.run([sys.executable,str(R/'tools/reference/build_x5_menu.py'),'--manifest',str(O/'menu-input.json'),'--output',str(O/'menu')],check=True)
    texts['src/x5_menu_layout.inc']=(O/'menu/x5-menu-layout.inc').read_text()
    for name in common:
        backup=O/'before'/name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,backup)
    for name,text in {**texts,**owned}.items():(R/name).write_text(text)
    shutil.copyfile(D/'chr/characters/tmnt.chr',R/'chr/characters/tmnt.chr')
    shutil.copyfile(O/'menu/x5-menu.bin',R/'chr/raw/x5-character-select.bin')
    packed=bytearray((R/'chr/characters/packed-mmc5-expanded.chr').read_bytes())
    packed[4096:8192]=(O/'menu/x5-menu.chr').read_bytes()
    (R/'chr/characters/packed-mmc5-expanded.chr').write_bytes(packed)
    report=dict(parent='chip-roster-mj',packet_sha256=sha(D/'manifest.json'),
                before={n:sha(O/'before'/n) for n in common},after={n:sha(R/n) for n in common},
                owned={n:sha(R/n) for n in owned},art_sha256=sha(R/'chr/characters/tmnt.chr'),
                changes='Outer ID19 guards preserve Chip/Kirby; menu names20..23; indexed resident C table; PLAYER+15B source bbox.')
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(evidence=str(O),owned=len(owned),shared=len(common))))


if __name__=='__main__':main()
