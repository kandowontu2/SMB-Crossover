"""Compose the frozen Zelda II packet with adopted Darkwing, without replacing its hooks."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/zelda2-link-candidate-agent'
O=R/'build/verification/zelda2-adoption-mc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
norm=lambda b:b.decode().replace('\r','')


def main():
    assert not O.exists()
    packet=json.loads((D/'incremental-merge-manifest.json').read_text())
    assert packet['candidate_ROM_SHA256']==sha(D/'zelda2-private.nes')
    with zipfile.ZipFile(R/'build/checkpoints/expanded-profiles-lr/source.zip') as z:
        base={n:z.read(n) for n in z.namelist()}
    texts={}
    for change in packet['changes']:
        name=change['path'];stage=D/'merge-staging'/name
        assert sha(stage)==change['after_SHA256'],name
        if change['before_SHA256']:
            assert hashlib.sha256(base[name]).hexdigest()==change['before_SHA256']
            texts[name]=norm((R/name).read_bytes())
        else:assert not (R/name).exists(),name
    # Work entirely in memory until every contextual replacement succeeds.
    def edit(name,old,new,count=1):
        name='src/'+name if name.endswith(('.s','.inc')) and '/' not in name else name
        assert texts[name].count(old)==count,(name,old[:100],texts[name].count(old))
        texts[name]=texts[name].replace(old,new)
    def wrap(name,old,new,count=1):
        edit(name,old,'.if ::ENABLE_MMC5_EXPANDED\n'+new+'\n.else\n'+old+'\n.endif',count)
    own={v['path']:norm((D/'merge-staging'/v['path']).read_bytes())
         for v in packet['changes'] if v['before_SHA256'] is None and v['path'].startswith('src/')}
    # Uncontested files retain the exact reviewed packet implementation.
    for name in list(texts):
        if (R/name).read_bytes()==base[name]:
            texts[name]=norm((D/'merge-staging'/name).read_bytes())
    edit('characters.s','  farcall DwGlobalInit','  farcall Z2GlobalInit')
    edit('collision.s','          farcall DwInjuryStart','          farcall Z2InjuryStartGate')
    ep='src/entrypoint.s'
    original=norm(base[ep]);staged=norm((D/'merge-staging'/ep).read_bytes())
    added=staged[staged.index('.include "zelda2_link_state.inc"'):]
    assert added.endswith('.endif\n')
    added=added[:-len('.endif\n')]
    edit(ep,'.include "x5_profiles.s"\n','.include "x5_profiles.s"\n'+added)
    edit('guest_body_contact.s','  farcall DwInjuryStatus,jmp','  farcall Z2InjuryStatusGate,jmp')
    wrap('guest_body_contact.s','  farcall LinkDeferredThrust','  farcall Z2DeferredThrustGate')
    wrap('guest_body_contact.s','  farcall LinkBodyContact','  farcall Z2BodyContactGate')
    # Three equal-size inventory leaves; preserve unrelated Darkwing drop/refill hooks.
    inv='src/inventory.s';staged=norm((D/'merge-staging'/inv).read_bytes())
    for proc in ('InventoryLegacyClassic','InventorySupported','InventoryHurt'):
        marker='.proc '+proc+'\n'
        start=texts[inv].index(marker);end=texts[inv].index('.endproc',start)+len('.endproc')
        a=staged.index(marker);b=staged.index('.endproc',a)+len('.endproc')
        texts[inv]=texts[inv][:start]+staged[a:b]+texts[inv][end:]
    wrap('inventory_drops.s','  farcall InventoryEnemyDrop','  farcall Z2EnemyDropGate')
    for name in ('union_rare.s','level_tiles.s'):
        edit(name,'  farcall DwPreparePickup','  farcall Z2PreparePickupGate')
    edit('mario_source.s','      farcall DwCollectPickup','      farcall Z2CollectPickupGate')
    edit('metasprite_engine.s','  jsr DwDrawGuard','  jsr Z2DrawGuard')
    wrap('metasprite_engine.s','  farcall SpecialDrawShots','  farcall Z2SpecialDrawGate')
    wrap('object.s','  farcall InventoryUpdateDrops','  farcall Z2UpdateDropsGate')
    wrap('object.s','  farcall RemainingWeapons','  farcall Z2RemainingWeaponsGate')
    wrap('object.s','    farcall RosterWeapons','    farcall Z2WeaponsGate')
    wrap('screen_render.s','    farcall RosterPortrait','    farcall Z2PortraitGate')
    # Scrooge15, Z2 Link16; new raw IDs will get separate later name entries.
    edit('character_select.s','ProtoNoToggle:\n','''ProtoNoToggle:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Z2NoToggle
  lda CrossoverMenuPressed
  and #Select_Button
  beq Z2NoToggle
  lda Z2Variant
  eor #1
  sta Z2Variant
  lda CrossoverMenuIndex
  jmp Changed
Z2NoToggle:
''')
    edit('character_select.s','  jsr ProtoMenuPrepare','  farcall Z2MenuPrepare')
    edit('character_select.s','ProtoNoHint:\n','''ProtoNoHint:
  cmp #CHARACTER_LINK
  bne Z2NoHint
  lda Z2Hint,y
  jmp Put
Z2NoHint:
''')
    edit('character_select.s','ProtoHint: .byte "SELECT - MEGA/PROTO "',
         'Z2Hint: .byte "SELECT - LINK/Z2    "\nProtoHint: .byte "SELECT - MEGA/PROTO "')
    edit('character_select.s','ProtoOriginalName:\n','''ProtoOriginalName:
  cmp #CHARACTER_LINK
  bne Z2OriginalName
  ldx Z2Variant
  beq NameIndex
  lda #16
  bne NameIndex
Z2OriginalName:
''')
    edit('character_select.s','" DARKWING DUCK  "','" DARKWING DUCK  ", " ZELDA II LINK  "')
    cfg='smb1base-mmc5-expanded.cfg'
    edit(cfg,'X5_NEW_46: start=$a000','X5_NEW_46: start=$c000')
    edit(cfg,'X5_CHR_MORE: start=$40000, size=$c0000, type=ro, fill=yes, file=%O, fillval=$00;',
         'X5_CHR_MORE: start=$40000, size=$d000, type=ro, fill=yes, file=%O, fillval=$00;\n'
         '    Z2_CHR_MEM: start=$4d000, size=$8000, type=ro, fill=yes, file=%O, fillval=$00;\n'
         '    X5_CHR_TAIL: start=$55000, size=$ab000, type=ro, fill=yes, file=%O, fillval=$00;')
    edit(cfg,'SEGMENTS {','''SEGMENTS {
    Z2_LOGIC: load=X5_NEW_45,type=ro;
    Z2_GFX: load=X5_NEW_46,type=ro,optional=yes;
    Z2_COLD: load=X5_NEW_47,type=ro,optional=yes;
    Z2_CHR: load=Z2_CHR_MEM,type=ro;
    Z2_DRAW_GATE: load=PRGA_04,type=ro,start=$bfa9;
''')
    # Inactive gates must preserve the already-installed Darkwing behavior.
    def owned(name,old,new,count=1):
        key='src/'+name
        assert own[key].count(old)==count,(name,old)
        own[key]=own[key].replace(old,new)
    owned('zelda2_link_motion.s',' farcall ProtoGlobalInit',' farcall DwGlobalInit')
    owned('zelda2_link_damage.s',' farcall GuestInjuryStart,jmp',' farcall DwInjuryStart,jmp')
    key='src/zelda2_link_damage.s';a=own[key].index('Original:\n');b=own[key].index('.endproc',a)
    own[key]=own[key][:a]+'Original:\n farcall DwInjuryStatus,jmp\n'+own[key][b:]
    owned('zelda2_link_rewards.s',' farcall InventoryPreparePickup,jmp',' farcall DwPreparePickup,jmp')
    owned('zelda2_link_rewards.s',' farcall InventoryCollect,jmp',' farcall DwCollectPickup,jmp')
    # The packet's reserved35B guard currently tails to the pre-Darkwing guard.
    for key,text in own.items():
        if '.proc Z2DrawGuard' in text:
            assert text.count('jmp RosterDrawShots')==1
            own[key]=text.replace('jmp RosterDrawShots','jmp DwDrawGuard')
    before={n:sha(R/n) for n in texts}
    O.mkdir(parents=True)
    for name,text in texts.items():
        dest=O/'before'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(R/name,dest)
        (R/name).write_text(text)
    for change in packet['changes']:
        name=change['path']
        if change['before_SHA256'] is None:
            target=R/name;target.parent.mkdir(parents=True,exist_ok=True)
            if name in own:target.write_text(own[name])
            else:shutil.copyfile(D/'merge-staging'/name,target)
    names=list(texts)+list(own)+[v['path'] for v in packet['changes'] if v['path'].startswith('chr/')]
    report=dict(status='COMPOSED_SOURCE_PENDING_BUILD_AND_NATIVE_CHECKS',
        packet_sha256=sha(D/'incremental-merge-manifest.json'),before=before,
        after={n:sha(R/n) for n in names},
        limitations=['Zelda I audio inherited; original death-scene and fairy/item palette polish remain.'],goal_complete=False)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'])


if __name__=='__main__':main()
