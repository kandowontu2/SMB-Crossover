"""Compose authentic Kirby H with the integrated alternate profiles."""
from pathlib import Path
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
D=R/'build/kirby-kd-private/handoff'
O=R/'build/verification/kirby-adoption-me'
norm=lambda b:b.decode().replace('\r','')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    packet=json.loads((D/'manifest.json').read_text())
    files=packet['files']
    for path,info in files.items():assert sha(D/path)==info['sha256'],path
    owned={p.name:norm(p.read_bytes()) for p in (D/'src').iterdir()}
    assert all(not (R/'src'/n).exists() for n in owned)
    names=('entrypoint.s','player.s','screen_render.s','object.s','characters.s','collision.s',
           'guest_body_contact.s','metasprite_engine.s','roster.s','expanded.s',
           'megaman_environment.s','expanded_audio.s','world_sprite_palette.s','character_select.s',
           'mmc5.s','protoman_cold.s')
    texts={'src/'+n:norm((R/'src'/n).read_bytes()) for n in names}
    texts['smb1base-mmc5-expanded.cfg']=norm((R/'smb1base-mmc5-expanded.cfg').read_bytes())
    def edit(name,old,new,count=1):
        if '/' not in name and name.endswith(('.s','.inc')):name='src/'+name
        assert texts[name].count(old)==count,(name,old[:100],texts[name].count(old))
        texts[name]=texts[name].replace(old,new)
    def wrap(name,old,new,count=1):
        edit(name,old,'.if ::ENABLE_MMC5_EXPANDED\n'+new+'\n.else\n'+old+'\n.endif\n',count)
    edit('entrypoint.s','.include "memory.s"','.include "memory.s"\n.if ::ENABLE_MMC5_EXPANDED\n.include "kirby_state.inc"\n.endif')
    edit('entrypoint.s','.include "zelda2_link_menu.s"','.include "zelda2_link_menu.s"\n.include "kirby.s"')
    wrap('entrypoint.s','.incbin "chr/characters/packed-mmc5.chr"','.incbin "chr/characters/packed-mmc5-expanded.chr"')
    for filename,original,new in (
        ('player.s','    farcall ExpandedGraphics','    farcall KbGraphicsDispatch'),
        ('player.s','    farcall ExpandedDeathUpdate','    farcall KbDeathDispatch'),
        ('player.s','    farcall ExpandedMovement','    farcall KbMovementDispatch'),
        ('object.s','    farcall ExpandedWeapons','    farcall KbWeaponsDispatch'),
        ('roster.s','  farcall SpecialRosterClear','  farcall KbResetDispatch')):
        wrap(filename,original,new)
    edit('screen_render.s','    farcall DwExpandedPortrait','    farcall KbPortraitDispatch')
    edit('characters.s','  farcall Z2GlobalInit','  farcall KbGlobalInit')
    edit('collision.s','          farcall Z2InjuryStartGate','          farcall KbInjuryStartDispatch')
    wrap('collision.s','      farcall MarioSourcePowerupCollision, jmp','      farcall KbPickupDispatch, jmp')
    wrap('guest_body_contact.s','  farcall GuestBodyContact\n','  farcall KbBodyDispatch\n')
    edit('guest_body_contact.s','  farcall Z2InjuryStatusGate,jmp','  farcall KbInjuryStatusDispatch,jmp')
    edit('metasprite_engine.s','  jsr Z2DrawGuard','  jsr KbDrawDispatch')
    # Resident NMI-safe table already belongs to Darkwing. Only append Kirby.
    marker='.bank(XgSCROOGE_STANDRight)\n  .res 136-(*-StartPublication)'
    edit('mmc5.s',marker,'.bank(XgSCROOGE_STANDRight),.bank(KbArtStart)\n  .res 136-(*-StartPublication)')
    # Reuse exact legacy leaf spans; head query bridge lives in unused adder tail.
    exp='src/expanded.s'
    for proc,new,span in (
        ('ExpandedCollisionAdder','  farcall KbAdderDispatch,jmp\n::KbNativeHeadBridge:\n  farcall KbHeadDispatch,jmp\n  .res 21,$ea',57),
        ('ExpandedCollisionBox','  farcall KbBoxDispatch,jmp\n  .res 37,$ea',55)):
        a=texts[exp].index('.proc '+proc+'\n');b=texts[exp].index('.endproc',a)+len('.endproc')
        old=texts[exp][a:b]
        newproc='.proc '+proc+'\n'+new+'\n  .assert *-'+proc+'='+str(span)+',error,"Original collision leaf span"\n.endproc'
        texts[exp]=texts[exp][:a]+'.if ::ENABLE_MMC5_EXPANDED\n'+newproc+'\n.else\n'+old+'\n.endif'+texts[exp][b:]
    wrap('megaman_environment.s','  jmp BlockBufferColli_Head\nRyu:','  jmp KbNativeHeadBridge\nRyu:')
    # This helper runs in its own audio C bank, including when entered by NMI.
    wrap('expanded_audio.s','  lda SelectedCharacter','  jsr KbAudioFamily',4)
    texts['src/expanded_audio.s']+='''
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "XG_AUDIO"
.proc KbAudioFamily
  lda SelectedCharacter
  cmp #CHARACTER_KIRBY
  bne Done
  lda #CHARACTER_PIT
Done:rts
.endproc
.popseg
.endif
'''
    # Preserve the20B world-palette selector with a cold main-thread wrapper.
    world='src/world_sprite_palette.s'
    original=texts[world]
    body=original[original.index('.proc GuestWorldPaletteIndex'):original.index('.assert * <=')]
    owned['kirby_world_palette.s']='.pushseg\n.segment "KIRBY_CORE"\n'+body.replace('GuestWorldPaletteIndex','KbWorldPaletteIndex').replace('  beq Mario\n','  beq Mario\n  cmp #CHARACTER_KIRBY\n  beq Mario\n',1)+'.popseg\n'
    edit('characters.s','  jsr GuestWorldPaletteIndex\n  jmp Guest',
         '.if ::ENABLE_MMC5_EXPANDED\n  farcall KbWorldPaletteIndex\n.else\n  jsr GuestWorldPaletteIndex\n  jmp Guest\n.endif')
    # Compose already-active variants rather than replacing the newer front end.
    menu='src/character_select.s'
    a=texts[menu].index('Navigation:\n')+len('Navigation:\n');b=texts[menu].index('Changed:\n',a)
    old=texts[menu][a:b]
    new='''  lda CrossoverMenuPressed
  and #Left_Dir|Right_Dir|Up_Dir|Down_Dir
  jeq NotReady
  lda #$24
  jsr QueueCursor
  ldx CrossoverMenuIndex
  lda CrossoverMenuPressed
  and #Up_Dir
  beq :+
  lda X5MenuUp,x
  jmp Changed
: lda CrossoverMenuPressed
  and #Down_Dir
  beq :+
  lda X5MenuDown,x
  jmp Changed
: lda CrossoverMenuPressed
  and #Left_Dir
  beq :+
  lda X5MenuLeft,x
  jmp Changed
: lda X5MenuRight,x
  jmp Changed
'''
    texts[menu]=texts[menu][:a]+'.if ::ENABLE_MMC5_EXPANDED\n'+new+'.else\n'+old+'.endif\n'+texts[menu][b:]
    wrap('character_select.s','  lda MenuCharacters,x','  lda X5MenuCharacters,x')
    wrap('character_select.s','  lda CursorLow,y','  lda X5MenuCursorLo,y')
    wrap('character_select.s','  lda CursorHigh,y','  lda X5MenuCursorHi,y')
    edit('character_select.s','    farcall DwInventoryInit','    farcall KbFreshGameInit')
    edit('character_select.s','  .byte 120,120,120,121,120,120','  .byte 120,120,120,121,120,120\n.if ::ENABLE_MMC5_EXPANDED\n  .byte 120\n.endif')
    edit('character_select.s','.proc QueueSelectName\n  lda SelectedCharacter','.proc QueueSelectName\n  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED\n  cmp #CHARACTER_KIRBY\n  bne :+\n  lda #17\n  jmp NameIndex\n:\n.endif')
    edit('character_select.s','" ZELDA II LINK  "','" ZELDA II LINK  ", "     KIRBY      "')
    wrap('character_select.s','  .incbin "chr/raw/character-select.bin"','  .incbin "chr/raw/x5-character-select.bin"')
    texts[menu]+='\n.if ::ENABLE_MMC5_EXPANDED\n.pushseg\n.segment "PROTO_MENU"\n.include "x5_menu_layout.inc"\n.popseg\n.endif\n'
    # Kirby HUD name has its own entry, preserving Proto/Lance name indices.
    edit('protoman_cold.s','  lda SelectedCharacter\n  beq Restore','  lda SelectedCharacter\n  cmp #CHARACTER_KIRBY\n  bne :+\n  lda #15\n  jmp NameIndex\n:\n  beq Restore')
    edit('protoman_cold.s','"LANCE  ","PROTO  "','"LANCE  ","PROTO  ","KIRBY  "')
    # Own wrappers chain into the integrated alternates.
    owned['kirby_core.s']=owned['kirby_core.s'].replace('farcall ProtoGlobalInit','farcall Z2GlobalInit')
    disp=owned['kirby_dispatch.s']
    disp=disp.replace('farcall ExpandedPortrait,jmp','farcall DwExpandedPortrait,jmp')
    disp=disp.replace('farcall GuestInjuryStart,jmp','farcall Z2InjuryStartGate,jmp')
    a=disp.index('.proc KbInjuryStatusDispatch\n');b=disp.index('.proc KbInjuryStartDispatch',a)
    disp=disp[:a]+'''.proc KbInjuryStatusDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 jeq Kirby
 farcall Z2InjuryStatusGate,jmp
Kirby:jmp KbInjuryStatus
.endproc
'''+disp[b:]
    disp=disp.replace(' farcall InventoryInit\n jmp KbGlobalInit::ClearEntry',' farcall DwInventoryInit\n jmp KbGlobalInit::ClearEntry')
    owned['kirby_dispatch.s']=disp
    draw=owned['kirby_draw.s'].replace('.segment "METASPRITE"','.segment "X5_DRAW_GATE"').replace('jmp RosterDrawShots','jmp Z2DrawGuard')
    owned['kirby_draw.s']=draw
    owned['kirby.s']+='.include "kirby_world_palette.s"\n'
    cfg='smb1base-mmc5-expanded.cfg'
    edit(cfg,'X5_NEW_49: start=$a000','X5_NEW_49: start=$c000')
    edit(cfg,'X5_CHR_TAIL: start=$55000, size=$ab000','KIRBY_CHR_MEM: start=$55000, size=$a000, type=ro, fill=yes, file=%O, fillval=$00;\n    X5_CHR_TAIL: start=$5f000, size=$a1000')
    edit(cfg,'SEGMENTS {','''SEGMENTS {
    KIRBY_CORE: load=X5_NEW_48,type=ro;
    KIRBY_GFX: load=X5_NEW_49,type=ro;
    KIRBY_ABILITIES: load=X5_NEW_4A,type=ro;
    KIRBY_CHR: load=KIRBY_CHR_MEM,type=ro;
''')
    edit(cfg,'    Z2_DRAW_GATE: load=PRGA_04,type=ro,start=$bfa9;','    Z2_DRAW_GATE: load=PRGA_04,type=ro,start=$bfa9;\n    X5_DRAW_GATE: load=PRGA_04,type=ro,start=$bfcc;')
    before={n:sha(R/n) for n in texts}
    O.mkdir(parents=True)
    for name,text in texts.items():
        dest=O/'before'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,dest)
        (R/name).write_text(text)
    for name,text in owned.items():(R/'src'/name).write_text(text)
    shutil.copyfile(D/'chr/kirby.chr',R/'chr/characters/kirby.chr')
    packed=R/'build/verification/third-row-lp/menu-kirby-layout/packed'
    shutil.copyfile(packed/'x5-menu-layout.inc',R/'src/x5_menu_layout.inc')
    shutil.copyfile(packed/'x5-menu.bin',R/'chr/raw/x5-character-select.bin')
    data=bytearray((R/'chr/characters/packed-mmc5.chr').read_bytes())
    data[4096:8192]=(packed/'x5-menu.chr').read_bytes()
    (R/'chr/characters/packed-mmc5-expanded.chr').write_bytes(data)
    report=dict(status='COMPOSED_KIRBY_PENDING_BUILD_AND_NATIVE_CHECKS',
        packet_sha256=sha(D/'manifest.json'),before=before,
        new_sources=list(owned)+['x5_menu_layout.inc'],character_id=13,name_index=17,
        limitations=['Kirby currently inherits Pit music; enemy copies are authored SMB adaptations.'],goal_complete=False)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'])


if __name__=='__main__':main()
