"""Compose the frozen Mac packet through MV without widening legacy routes."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/player-guide-agent/little-mac-private/adoption-packet'
O=R/'build/verification/mac-adoption-mw'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    assert sha(D/'manifest.json')=='718d0d953cf95ccd5856dcaba45ff474b9ca9627033a90a3f6a3bfdd7b0ef266'
    packet=json.loads((D/'manifest.json').read_text())
    assert packet['components']['passed'] and packet['native']['passed']
    assert sha(D/'little-mac-mr-private.nes')==packet['private_rom_sha256']==packet['components']['sha256']
    for f in packet['owned']+packet['contextual']:assert sha(D/'source'/f['path'])==f['sha256'],f['path']
    parent=json.loads((R/'build/checkpoints/mike-roster-mv/manifest.json').read_text())
    shared={f['path'] for f in packet['contextual']}|{'src/kirby_world_palette.s'}
    shared.discard('src/cv3_draw.s');shared.discard('src/megaman_environment.s')
    for n in shared:assert sha(R/n)==parent['source_files'][n],n
    texts={n:(R/n).read_text() for n in shared if not n.endswith(('.chr','.bin'))}
    owned={f['path']:(D/'source'/f['path']).read_text() for f in packet['owned'] if f['path'].startswith('src/')}
    assert all(not(R/n).exists() for n in owned)
    def edit(n,old,new,count=1):
        assert texts[n].count(old)==count,(n,old[:80],texts[n].count(old))
        texts[n]=texts[n].replace(old,new)
    fallback={
      'Cv3ResetGate':'JnResetDispatch','Cv3MovementGate':'JnMovementDispatch',
      'Cv3InjuryStartGate':'JnInjuryStartDispatch','Cv3InjuryStatusGate':'JnInjuryStatusDispatch',
      'Cv3BodyGate':'JnBodyDispatch','VvDeathStartDispatch':'JnInventoryDeathDispatch',
      'VvDeathDispatch':'JnDeathDispatch','VvAdderDispatch':'JnAdderDispatch','VvBoxDispatch':'JnBoxDispatch',
      'TnVisibleDispatch':'JnVisibleDispatch','VvStatusName':'JnStatusName',
      'VvPrepareDispatch':'JnPrepareDispatch','Cv3PrivatePickupGate':'JnPrivateDispatch',
      'Cv3RisePickupGate':'JnRiseDispatch','Cv3GraphicsGate':'JnGraphicsDispatch',
      'Cv3PortraitGate':'JnPortraitDispatch','VvDrawDispatch':'JnDrawDispatch',
      'VvBoundingBoxGate':'M3BoundingBoxGate','TnHeadDispatch':'JnHeadDispatch',
      'Cv3WeaponsGate':'JnWeaponsDispatch'}
    for old,new in fallback.items():
        found=0
        for n,t in list(owned.items()):
            count=t.count(old)
            if count:owned[n]=t.replace(old,new);found+=count
        assert found==1,(old,found)
    # The old private side fallback is superseded by the later SMB3 hull.
    n='src/little_mac_terrain.s';assert owned[n].count(' jmp LmSideLegacy')==1
    owned[n]=owned[n].replace(' jmp LmSideLegacy',' farcall M3SideDispatch,jmp')
    edit('src/entrypoint.s','.include "cv3_state.inc"','.include "cv3_state.inc"\n.include "little_mac_state.inc"')
    edit('src/entrypoint.s','.include "cv3.s"','.include "cv3.s"\n.include "little_mac.s"')
    for n,old,new in (
      ('src/player.s','JnGraphicsDispatch','LmGraphicsGate'),('src/player.s','JnMovementDispatch','LmMovementGate'),('src/player.s','JnDeathDispatch','LmDeathGate'),('src/player.s','M3BoundingBoxGate','LmBoundingBoxGate'),
      ('src/object.s','JnWeaponsDispatch','LmWeaponsGate'),('src/object.s','JnRiseDispatch','LmRiseGate'),
      ('src/screen_render.s','JnPortraitDispatch','LmPortraitGate'),('src/characters.s','JnStatusName','LmStatusNameGate'),
      ('src/collision.s','JnInjuryStartDispatch','LmInjuryGate'),
      ('src/guest_body_contact.s','JnBodyDispatch','LmBodyGate'),('src/guest_body_contact.s','JnInjuryStatusDispatch','LmInjuryStatusGate'),
      ('src/guest_injury.s','JnVisibleDispatch','LmVisibleGate'),('src/kirby_draw.s','JnDrawDispatch','LmDrawGate'),
      ('src/expanded.s','JnAdderDispatch','LmAdderGate'),('src/expanded.s','JnBoxDispatch','LmBoxGate'),('src/expanded.s','JnHeadDispatch','LmHeadGate'),
      ('src/megaman_death.s','JnInventoryDeathDispatch','LmDeathStartGate'),('src/roster.s','JnResetDispatch','LmResetGate'),
      ('src/inventory.s','Cv3LegacyGate','LmLegacyGate'),('src/inventory.s','Cv3SupportedGate','LmSupportedGate'),
      ('src/mario_source.s','Cv3CollectPickupGate','LmCollectGate'),
      ('src/sprite_render.s','JnPrivateDispatch','LmPrivateGate'),('src/union_rare.s','JnPrepareDispatch','LmPrepareGate'),('src/level_tiles.s','JnPrepareDispatch','LmPrepareGate'),
      ('src/game.s','VvUiDispatch','LmUiGate'),('src/characters.s','M3SideDispatch','LmSideGate')):edit(n,old,new)
    edit('src/samus.s','  farcall CrossoverSourceWallDispatch, jmp',
      '  .if ::ENABLE_MMC5_EXPANDED\n    farcall LmWallGate,jmp\n  .else\n    farcall CrossoverSourceWallDispatch,jmp\n  .endif')
    edit('src/kirby_world_palette.s','  cmp #14\n  beq Mario','  cmp #14\n  beq Mario\n  cmp #15\n  beq Mario')
    edit('src/x5_palette.s','.proc X5GetPlayerColors\n  lda SelectedCharacter\n',
      '.proc X5GetPlayerColors\n  lda SelectedCharacter\n  cmp #15\n  bne :+\n  farcall QueueMegaManFacePalette\n  farcall QueueGuestWeaponPalette\n  jsr X5QueueAreaBackdrop\n  farcall LmForcePalette,jmp\n:\n  lda SelectedCharacter\n')
    cfg='smb1base-mmc5-expanded.cfg'
    edit(cfg,'X5_NEW_5E: start=$a000','X5_NEW_5E: start=$c000')
    edit(cfg,'MIKE_CHR_PRE: start=$a7000,size=$a000','LM_CHR_MEM: start=$a7000,size=$a000')
    edit(cfg,'SEGMENTS {','SEGMENTS {\n    LM_CORE:load=X5_NEW_5D,type=ro;\n    LM_GFX:load=X5_NEW_5E,type=ro;\n    LM_COMBAT:load=X5_NEW_5F,type=ro;\n    LM_CHR:load=LM_CHR_MEM,type=ro;\n')
    edit('src/character_select.s','  lda #152\n  sta Player_Y_Position',
      '  lda #152\n.if ::ENABLE_MMC5_EXPANDED\n  ldx SelectedCharacter\n  cpx #15\n  bne :+\n  lda #160\n:\n.endif\n  sta Player_Y_Position')
    edit('src/character_select.s','.proc QueueSelectName\n  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED',
      '.proc QueueSelectName\n  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED\n  cmp #15\n  bne LmOtherName\n  lda #30\n  jmp NameIndex\nLmOtherName:')
    edit('src/character_select.s','"                ","   MIKE JONES   "','"   LITTLE MAC   ","   MIKE JONES   "')
    O.mkdir(parents=True)
    spec=json.loads((R/'build/verification/mike-adoption-mv/menu-input.json').read_text())
    spec['portraits'].append(dict(slot=14,character=15,image=str(D.parent/'mac-portrait.png')))
    (O/'menu-input.json').write_text(json.dumps(spec,indent=2)+'\n')
    subprocess.run([sys.executable,str(R/'tools/reference/build_x5_menu.py'),'--manifest',str(O/'menu-input.json'),'--output',str(O/'menu')],check=True)
    texts['src/x5_menu_layout.inc']=(O/'menu/x5-menu-layout.inc').read_text()
    for n in shared:
        p=O/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    for n,t in {**texts,**owned}.items():(R/n).write_text(t)
    shutil.copyfile(D/'source/chr/characters/little-mac.chr',R/'chr/characters/little-mac.chr')
    shutil.copyfile(O/'menu/x5-menu.bin',R/'chr/raw/x5-character-select.bin')
    packed=bytearray((R/'chr/characters/packed-mmc5-expanded.chr').read_bytes());packed[4096:8192]=(O/'menu/x5-menu.chr').read_bytes()
    (R/'chr/characters/packed-mmc5-expanded.chr').write_bytes(packed)
    report=dict(parent='mike-roster-mv',packet_sha256=sha(D/'manifest.json'),before={n:sha(O/'before'/n) for n in sorted(shared)},after={n:sha(R/n) for n in sorted(shared)},owned={n:sha(R/n) for n in sorted(owned)},asset_sha256=sha(R/'chr/characters/little-mac.chr'),fallbacks=fallback,name_index=30,preserved_low3_to5_direct_CV3_routes=True)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(evidence=str(O),owned=len(owned)+1,shared=len(shared))))

if __name__=='__main__':main()
