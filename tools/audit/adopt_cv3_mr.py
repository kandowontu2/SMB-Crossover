"""Contextual CV3 adoption over MQ; keep all newer character dispatch chains."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
D=R/'build/player-guide-agent/cv3-private/adoption-packet'
O=R/'build/verification/cv3-adoption-mr'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    packet=json.loads((D/'manifest.json').read_text())
    for item in packet['files']:assert sha(D/item['path'])==item['sha256'],item['path']
    parent=json.loads((R/'build/checkpoints/palette-roster-mq/manifest.json').read_text())
    names=set(packet['shared_files_for_contextual_merge'])|{'src/vic_dispatch.s','src/chip_dale_dispatch.s','src/x5_palette.s'}
    for n in names:assert sha(R/n)==parent['source_files'][n],n
    texts={n:(R/n).read_text() for n in names}
    owned={n:(D/'source'/n).read_text() for n in packet['new_files'] if n.startswith('src/')}
    assert all(not (R/n).exists() for n in packet['new_files'])
    def edit(n,old,new,count=1):
        assert texts[n].count(old)==count,(n,old[:100],texts[n].count(old))
        texts[n]=texts[n].replace(old,new)
    edit('src/entrypoint.s','.include "kirby_state.inc"','.include "kirby_state.inc"\n.include "cv3_state.inc"')
    edit('src/entrypoint.s','.include "vic_viper.s"','.include "vic_viper.s"\n.include "cv3.s"')
    for n,old,new in (
        ('src/player.s','farcall Z2MovementGate','farcall Cv3MovementGate'),
        ('src/megaman_environment.s','farcall Z2MovementGate','farcall Cv3MovementGate'),
        ('src/player.s','farcall Z2GraphicsGate','farcall Cv3GraphicsGate'),
        ('src/object.s','farcall Z2WeaponsGate','farcall Cv3WeaponsGate'),
        ('src/screen_render.s','farcall Z2PortraitGate','farcall Cv3PortraitGate'),
        ('src/roster.s','farcall VvResetDispatch','farcall Cv3ResetGate'),
        ('src/collision.s','farcall VvInjuryDispatch','farcall Cv3InjuryStartGate'),
        ('src/guest_body_contact.s','farcall VvInjuryStatusDispatch','farcall Cv3InjuryStatusGate'),
        ('src/guest_body_contact.s','farcall VvBodyDispatch','farcall Cv3BodyGate'),
        ('src/vic_dispatch.s','farcall Z2PreparePickupGate','farcall Cv3PreparePickupGate'),
        ('src/mario_source.s','farcall Z2CollectPickupGate','farcall Cv3CollectPickupGate'),
        ('src/sprite_render.s','farcall DwPrivatePickup','farcall Cv3PrivatePickupGate'),
        ('src/chip_dale_dispatch.s','farcall DwStatusName','farcall Cv3StatusNameGate'),
        ('src/inventory.s','farcall Z2InventorySupportedGate','farcall Cv3SupportedGate'),
        ('src/inventory.s','farcall Z2InventoryLegacyClassicGate','farcall Cv3LegacyGate'),
        ('src/inventory_drops.s','farcall Z2EnemyDropGate','farcall Cv3EnemyDropGate'),
        ('src/vic_dispatch.s','farcall Z2UiTickGate','farcall Cv3UiGate'),
        ('src/object.s','farcall DwRisePickup','farcall Cv3RisePickupGate')):edit(n,old,new)
    for n,old,new in (
        ('src/cv3_core.s','farcall KbResetDispatch','farcall VvResetDispatch'),
        ('src/cv3_pickups.s','Cv3Gate KbInjuryStatusDispatch','Cv3Gate VvInjuryStatusDispatch'),
        ('src/cv3_pickups.s','Cv3Gate KbInjuryStartDispatch','Cv3Gate VvInjuryDispatch'),
        ('src/cv3_combat.s','farcall KbBodyDispatch','farcall VvBodyDispatch')):
        assert owned[n].count(old)==1;owned[n]=owned[n].replace(old,new)
    n='src/cv3_draw.s';a=owned[n].index('.proc Cv3DrawDispatch');b=owned[n].index('.endproc',a)+len('.endproc')
    owned[n]=owned[n][:a]+'''.proc Cv3DrawDispatch
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 bcc Check
 farcall VvDrawDispatch,jmp
Check:
 farcall Cv3IsActive
 bcs Native
 farcall RosterDrawShots,jmp
Native:jmp Cv3DrawShots
.endproc'''+owned[n][b:]
    # Independent targets avoid another farcall on every newer-profile draw.
    # Fifty bytes fit BFCC..BFFD; no later entry or original code moves.
    edit('src/kirby_draw.s','  jcc Legacy\n  farcall VvDrawDispatch,jmp','  bcc CheckSimon\n  farcall VvDrawDispatch,jmp\nCheckSimon:\n  cmp #CHARACTER_SIMON\n  bne Legacy\n  farcall Cv3DrawDispatch,jmp')
    edit('src/kirby_draw.s','  jmp Z2DrawGuard\n.endproc','  jmp Z2DrawGuard\n  .assert *-KbDrawDispatch=50,error,"Expanded draw gate fits bank4 tail"\n.endproc')
    staged=(D/'source/src/mmc5.s').read_text();a=staged.index('::Cv3ResidentRosterBank:');b=staged.index('  .res 136-',a)
    edit('src/mmc5.s','  .res 136-(*-StartPublication),$ea',staged[a:b]+'  .res 136-(*-StartPublication),$ea')
    staged=(D/'source/src/expanded.s').read_text();a=staged.index('::Cv3ResidentBox:');b=staged.index('  .assert *-ExpandedCollisionBox',a)
    edit('src/expanded.s','  .res 37,$ea\n',staged[a:b])
    edit('src/roster.s','  lda Banks,x\n.if ::MAPPER_MMC5',' .if ::ENABLE_MMC5_EXPANDED\n  jsr Cv3ResidentRosterBank\n .else\n  lda Banks,x\n .endif\n.if ::MAPPER_MMC5')
    edit('src/roster.s','Banks:\n  .byte .bank(RgBILL0_STANDRight)','Banks:\n.if ::ENABLE_MMC5_EXPANDED\n::Cv3LegacyBanks:\n.endif\n  .byte .bank(RgBILL0_STANDRight)')
    for proc,gate,bill,other in [('MegaManCollisionAdder','Cv3ResidentAdder',4,8),('MegaManCollisionBox','Cv3ResidentBox',4,10)]:
        n='src/megaman_weapons.s';a=texts[n].index('.proc '+proc+'\n');b=texts[n].index('.endproc',a);sub=texts[n][a:b]
        old='Roster:\n  cmp #CHARACTER_BILL\n  bne :+';assert sub.count(old)==1
        suffix='Adder' if proc.endswith('Adder') else 'Box'
        new=f'Roster:\n .if ::ENABLE_MMC5_EXPANDED\n::Cv3Legacy{suffix}Bill=Roster+{bill}\n::Cv3Legacy{suffix}Other=Roster+{other}\n  jmp {gate}\n  nop\n .else\n  cmp #CHARACTER_BILL\n  bne :+\n .endif'
        texts[n]=texts[n][:a]+sub.replace(old,new)+texts[n][b:]
    staged=(D/'source/src/character_select.s').read_text()
    a=staged.index('Z2NoToggle:')+len('Z2NoToggle:\n');b=staged.index('Cv3NoToggle:',a)+len('Cv3NoToggle:\n')
    edit('src/character_select.s','Z2NoToggle:\n','Z2NoToggle:\n'+staged[a:b])
    edit('src/character_select.s','Z2OriginalName:\n','''Z2OriginalName:
  cmp #CHARACTER_SIMON
  bne Cv3OriginalName
  ldx Cv3Variant
  beq NameIndex
  cpx #4
  bcs Cv3OriginalName
  txa
  clc
  adc #24
  jmp NameIndex
Cv3OriginalName:
  lda SelectedCharacter
''')
    edit('src/character_select.s','"   VIC VIPER    "','"   VIC VIPER    ","     GRANT      ","     SYPHA      ","    ALUCARD     "')
    edit('src/character_select.s','Z2NoHint:\n','''Z2NoHint:
  cmp #CHARACTER_SIMON
  bne Cv3NoHint
  lda Cv3Hint,y
  jmp Put
Cv3NoHint:
''')
    edit('src/character_select.s','ProtoHint: .byte','Cv3Hint: .byte "SELECT - CV3 HEROES "\nProtoHint: .byte')
    # Force the correct body palette when native GetPlayerColors overwrites it
    # on a power/status transition. Graphics otherwise stays change-only.
    edit('src/x5_palette.s','  cmp #CHARACTER_SCROOGE\n','''  cmp #CHARACTER_SIMON
  bne :+
  lda Cv3Variant
  beq Cv3Ordinary
  cmp #4
  bcs Cv3Ordinary
  farcall QueueMegaManFacePalette
  farcall QueueGuestWeaponPalette
  jsr X5QueueAreaBackdrop
  farcall Cv3ForcePalette,jmp
Cv3Ordinary:
  jmp X5LegacyGetPlayerColors
:
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
''')
    owned['src/cv3_render.s']+='''\n.pushseg
.segment "CV3_CORE"
.proc Cv3ForcePalette
 lda #0
 sta Cv3LastPalette
 jmp Cv3QueuePalette
.endproc
.popseg
'''
    cfg='smb1base-mmc5-expanded.cfg'
    for bank in ('53','55'):edit(cfg,'X5_NEW_'+bank+': start=$a000','X5_NEW_'+bank+': start=$c000')
    edit(cfg,'    CD_CHR_TAIL: start=$73000,size=$24000,type=ro,fill=yes,file=%O,fillval=$00;','    CV3_CHR_MEM: start=$73000,size=$10000,type=ro,fill=yes,file=%O,fillval=$00;\n    CV3_CHR_AFTER: start=$83000,size=$14000,type=ro,fill=yes,file=%O,fillval=$00;')
    edit(cfg,'SEGMENTS {','''SEGMENTS {
    CV3_CORE:load=X5_NEW_52,type=ro;
    CV3_GFX_83:load=X5_NEW_53,type=ro;
    CV3_COMBAT:load=X5_NEW_54,type=ro;
    CV3_GFX_85:load=X5_NEW_55,type=ro;
    CV3_CHR:load=CV3_CHR_MEM,type=ro;
''')
    O.mkdir(parents=True)
    for n in names:
        p=O/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    for n,t in {**texts,**owned}.items():(R/n).write_text(t)
    shutil.copyfile(D/'source/chr/characters/cv3.chr',R/'chr/characters/cv3.chr')
    report=dict(parent='palette-roster-mq',packet_sha256=sha(D/'manifest.json'),before={n:sha(O/'before'/n) for n in sorted(names)},after={n:sha(R/n) for n in sorted(names)},owned={n:sha(R/n) for n in packet['new_files']},menu_names=[25,26,27],bank4_tail_growth_bytes=19)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(evidence=str(O),files=len(names)+len(owned)+1)))

if __name__=='__main__':main()
