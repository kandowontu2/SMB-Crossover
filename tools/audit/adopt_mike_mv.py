"""Compose frozen Mike M through the current MU cold dispatch chain."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/mike-kd-private/handoff-Mike-core-m'
O=R/'build/verification/mike-adoption-mv'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    assert sha(D/'manifest.json')=='e0faeea7fa9f3f7eaff5d4af30141a6482fac4bbf2bedc738553b85c645070c0'
    packet=json.loads((D/'manifest.json').read_text())
    for x in packet['files']:
        assert sha(D/x['path'])==x['sha256'],x['path']
    parent=json.loads((R/'build/checkpoints/smb3-roster-mu/manifest.json').read_text())
    shared=set(packet['common_context_files'])-{'src/mmc5.s'}
    shared.add('chr/characters/packed-mmc5-expanded.chr')
    for n in shared:assert sha(R/n)==parent['source_files'][n],n
    texts={n:(R/n).read_text() for n in shared if not n.endswith(('.chr','.bin'))}
    owned={x['path'][6:]:(D/x['path']).read_text() for x in packet['files'] if x['path'].startswith('owned/src/')}
    assert all(not(R/n).exists() for n in owned)
    def edit(n,old,new,count=1):
        assert texts[n].count(old)==count,(n,old[:80],texts[n].count(old))
        texts[n]=texts[n].replace(old,new)
    fallbacks={
        'CdMovementDispatch':'M3MovementDispatch','CdGraphicsDispatch':'M3GraphicsDispatch',
        'CdPortraitDispatch':'M3PortraitDispatch','CdWeaponsDispatch':'M3WeaponsDispatch',
        'CdDeathDispatch':'M3DeathDispatch','CdInjuryStartDispatch':'M3InjuryDispatch',
        'CdInjuryStatusDispatch':'M3InjuryStatusDispatch','Z2PreparePickupGate':'M3PreparePickup',
        'DwPrivatePickup':'M3PrivatePickup','DwRisePickup':'M3RisePickup',
        'DwPickupCollision':'M3PickupCollision','CdNewDrawDispatch':'M3NewDrawDispatch',
        'CdResetDispatch':'M3ResetDispatch','CdInventoryDeathDispatch':'M3InventoryDeathDispatch',
        'CdPickupDispatch':'M3CollectPickup','CdBodyDispatch':'M3BodyDispatch',
        'CdAdderDispatch':'M3AdderDispatch','CdBoxDispatch':'M3BoxDispatch',
        'KbHeadDispatch':'M3HeadDispatch','Z2SpecialDrawGate':'M3SpecialDrawGate',
        'DwPlayerVisible':'M3VisibleDispatch','Z2EnemyDropGate':'Cv3EnemyDropGate',
        'CdStatusNameDispatch':'M3StatusNameDispatch'}
    name='src/mike_jones_dispatch.s'
    for old,new in fallbacks.items():
        assert owned[name].count('farcall '+old)==1,(old,owned[name].count(old))
        owned[name]=owned[name].replace('farcall '+old,'farcall '+new)
    edit('src/entrypoint.s','.include "x5_palette.s"','.include "mike_jones_state.inc"\n.include "mike_jones.s"\n.include "x5_palette.s"')
    for n,old,new in (
        ('src/player.s','M3GraphicsDispatch','JnGraphicsDispatch'),('src/player.s','M3MovementDispatch','JnMovementDispatch'),('src/player.s','M3DeathDispatch','JnDeathDispatch'),
        ('src/object.s','M3WeaponsDispatch','JnWeaponsDispatch'),('src/object.s','M3RisePickup','JnRiseDispatch'),('src/object.s','M3PickupCollision','JnCollisionDispatch'),
        ('src/screen_render.s','M3PortraitDispatch','JnPortraitDispatch'),('src/characters.s','M3StatusNameDispatch','JnStatusName'),
        ('src/collision.s','M3InjuryDispatch','JnInjuryStartDispatch'),('src/collision.s','M3CollectPickup','JnPickupDispatch'),
        ('src/guest_body_contact.s','M3BodyDispatch','JnBodyDispatch'),('src/guest_body_contact.s','M3InjuryStatusDispatch','JnInjuryStatusDispatch'),
        ('src/guest_injury.s','M3VisibleDispatch','JnVisibleDispatch'),('src/kirby_draw.s','M3NewDrawDispatch','JnDrawDispatch'),
        ('src/expanded.s','M3AdderDispatch','JnAdderDispatch'),('src/expanded.s','M3BoxDispatch','JnBoxDispatch'),('src/expanded.s','M3HeadDispatch','JnHeadDispatch'),
        ('src/metasprite_engine.s','M3SpecialDrawGate','JnSpecialDrawDispatch'),('src/megaman_death.s','M3InventoryDeathDispatch','JnInventoryDeathDispatch'),
        ('src/roster.s','M3ResetDispatch','JnResetDispatch'),('src/inventory_drops.s','Cv3EnemyDropGate','JnDropDispatch'),
        ('src/sprite_render.s','M3PrivatePickup','JnPrivateDispatch'),('src/union_rare.s','M3PreparePickup','JnPrepareDispatch'),('src/level_tiles.s','M3PreparePickup','JnPrepareDispatch')):edit(n,old,new)
    edit('src/kirby_world_palette.s','  cmp #14\n  beq Mario','  cmp #14\n  beq Mario\n  cmp #CHARACTER_MIKE\n  beq Mario')
    edit('src/x5_palette.s','.proc X5GetPlayerColors\n  lda SelectedCharacter\n','.proc X5GetPlayerColors\n  lda SelectedCharacter\n  cmp #CHARACTER_MIKE\n  bne :+\n  farcall JnGetColors,jmp\n:\n')
    cfg='smb1base-mmc5-expanded.cfg'
    edit(cfg,'X5_NEW_61: start=$a000','X5_NEW_61: start=$c000')
    edit(cfg,'TMNT_CHR_TAIL: start=$a7000,size=$59000,type=ro,fill=yes,file=%O,fillval=$00;',
         'MIKE_CHR_PRE: start=$a7000,size=$a000,type=ro,fill=yes,file=%O,fillval=$00;\n    MIKE_CHR_MEM: start=$b1000,size=$c000,type=ro,fill=yes,file=%O,fillval=$00;\n    TMNT_CHR_TAIL: start=$bd000,size=$43000,type=ro,fill=yes,file=%O,fillval=$00;')
    edit(cfg,'SEGMENTS {','SEGMENTS {\n    MIKE_CORE:load=X5_NEW_60,type=ro;\n    MIKE_GFX:load=X5_NEW_61,type=ro;\n    MIKE_COMBAT:load=X5_NEW_62,type=ro;\n    MIKE_CHR:load=MIKE_CHR_MEM,type=ro;\n')
    edit('src/character_select.s','.proc QueueSelectName\n  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED',
         '.proc QueueSelectName\n  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED\n  cmp #CHARACTER_MIKE\n  bne JnOtherName\n  lda #31\n  jmp NameIndex\nJnOtherName:')
    edit('src/character_select.s','"   SMB3 LUIGI   "','"   SMB3 LUIGI   ","                ","   MIKE JONES   "')
    O.mkdir(parents=True)
    spec=json.loads((R/'build/verification/smb3-adoption-mu/menu-input.json').read_text())
    spec['portraits'].append(dict(slot=15,character=16,image=str(D/'art/mike-portrait.png')))
    (O/'menu-input.json').write_text(json.dumps(spec,indent=2)+'\n')
    subprocess.run([sys.executable,str(R/'tools/reference/build_x5_menu.py'),'--manifest',str(O/'menu-input.json'),'--output',str(O/'menu')],check=True)
    texts['src/x5_menu_layout.inc']=(O/'menu/x5-menu-layout.inc').read_text()
    for n in shared:
        p=O/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    for n,t in {**texts,**owned}.items():(R/n).write_text(t)
    shutil.copyfile(D/'owned/chr/characters/mike-jones.chr',R/'chr/characters/mike-jones.chr')
    shutil.copyfile(O/'menu/x5-menu.bin',R/'chr/raw/x5-character-select.bin')
    packed=bytearray((R/'chr/characters/packed-mmc5-expanded.chr').read_bytes());packed[4096:8192]=(O/'menu/x5-menu.chr').read_bytes()
    (R/'chr/characters/packed-mmc5-expanded.chr').write_bytes(packed)
    report=dict(parent='smb3-roster-mu',packet_sha256=sha(D/'manifest.json'),before={n:sha(O/'before'/n) for n in sorted(shared)},after={n:sha(R/n) for n in sorted(shared)},owned={n:sha(R/n) for n in sorted(owned)},asset_sha256=sha(R/'chr/characters/mike-jones.chr'),fallbacks= fallbacks,name_index=31)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(evidence=str(O),owned=len(owned)+1,shared=len(shared))))

if __name__=='__main__':main()
