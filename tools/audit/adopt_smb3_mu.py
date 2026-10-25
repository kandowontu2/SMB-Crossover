"""Contextual SMB3 forms adoption over the newer, verified MT roster."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/verification/smb3-mario-candidate-agent'
O=R/'build/verification/smb3-adoption-mu'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    packet=json.loads((D/'incremental-merge-manifest.json').read_text())
    for x in packet['changes']:assert sha(D/'merge-staging'/x['path'])==x['staged_SHA256'],x['path']
    parent=json.loads((R/'build/checkpoints/cv3-blocks-mt/manifest.json').read_text())
    shared={x['path'] for x in packet['changes'] if x['before_SHA256'] is not None}
    shared.add('src/vic_dispatch.s')
    for n in shared:assert sha(R/n)==parent['source_files'][n],n
    texts={n:(R/n).read_text() for n in shared if not n.endswith(('.chr','.bin'))}
    owned={x['path']:(D/'merge-staging'/x['path']).read_text() for x in packet['changes'] if x['before_SHA256'] is None and x['path'].startswith('src/')}
    assert all(not(R/n).exists() for n in owned)
    def edit(n,old,new,count=1):
        assert texts[n].count(old)==count,(n,old[:80],texts[n].count(old))
        texts[n]=texts[n].replace(old,new)
    # Each cold inactive branch retains the current full roster, including CV3.
    fallback=json.loads((D/'current-mr-fallback-map.json').read_text())['inactive_fallbacks']
    for name,target in fallback.items():
        found=False
        for n,t in list(owned.items()):
            macro=re.search(r'(?m)^M3Dispatch '+name+r',([^,\n]+),([^\n]+)$',t)
            if macro:
                owned[n]=t[:macro.start()]+f'M3Dispatch {name},{macro[1]},{target}'+t[macro.end():];found=True;break
            mark='.proc '+name+'\n'
            if mark not in t:continue
            a=t.index(mark);b=t.index('.endproc',a);body=t[a:b]
            if name=='M3BoundingBoxGate':
                old='jmp BoundingBoxCore ; Root composes current VvBoundingBoxGate fallback here.'
                assert body.count(old)==1;body=body.replace(old,'farcall VvBoundingBoxGate,jmp')
            else:
                body,count=re.subn(r'Legacy:farcall \w+,jmp',f'Legacy:farcall {target},jmp',body)
                if count==0:
                    body,count=re.subn(r'farcall \w+,jmp',f'farcall {target},jmp',body,count=1)
                assert count==1,(name,body)
            owned[n]=t[:a]+body+t[b:];found=True;break
        assert found,name
    source=(D/'merge-staging/src/entrypoint.s').read_text()
    a=source.index('.include "smb3_mario_state.inc"');b=source.index('.include "x5_palette.s"',a)
    edit('src/entrypoint.s','.include "cv3.s"','.include "cv3.s"\n'+source[a:b].rstrip())
    for n,old,new in (
        ('src/player.s','VvGraphicsDispatch','M3GraphicsDispatch'),('src/player.s','VvMovementDispatch','M3MovementDispatch'),('src/player.s','VvDeathDispatch','M3DeathDispatch'),
        ('src/player.s','VvBoundingBoxGate','M3BoundingBoxGate'),('src/object.s','VvWeaponsDispatch','M3WeaponsDispatch'),
        ('src/screen_render.s','VvPortraitDispatch','M3PortraitDispatch'),('src/characters.s','VvStatusName','M3StatusNameDispatch'),
        ('src/collision.s','Cv3InjuryStartGate','M3InjuryDispatch'),('src/collision.s','VvPickupDispatch','M3CollectPickup'),
        ('src/guest_body_contact.s','Cv3BodyGate','M3BodyDispatch'),('src/guest_body_contact.s','Cv3InjuryStatusGate','M3InjuryStatusDispatch'),
        ('src/guest_injury.s','TnVisibleDispatch','M3VisibleDispatch'),('src/kirby_draw.s','farcall VvDrawDispatch','farcall M3NewDrawDispatch'),
        ('src/expanded.s','VvAdderDispatch','M3AdderDispatch'),('src/expanded.s','VvBoxDispatch','M3BoxDispatch'),('src/expanded.s','TnHeadDispatch','M3HeadDispatch'),
        ('src/metasprite_engine.s','TnSpecialDrawDispatch','M3SpecialDrawGate'),('src/megaman_death.s','VvDeathStartDispatch','M3InventoryDeathDispatch'),
        ('src/roster.s','Cv3ResetGate','M3ResetDispatch'),('src/object.s','Cv3RisePickupGate','M3RisePickup'),('src/object.s','DwPickupCollision','M3PickupCollision'),
        ('src/sprite_render.s','Cv3PrivatePickupGate','M3PrivatePickup'),('src/union_rare.s','VvPrepareDispatch','M3PreparePickup'),('src/level_tiles.s','VvPrepareDispatch','M3PreparePickup')):edit(n,old,new)
    src=(D/'merge-staging/src/characters.s').read_text();a=src.index('.proc CrossoverSourceSideProbe');b=src.index('.endproc',a)+len('.endproc')
    old=texts['src/characters.s'];c=old.index('.proc CrossoverSourceSideProbe');d=old.index('.endproc',c)+len('.endproc')
    texts['src/characters.s']=old[:c]+src[a:b]+old[d:]
    edit('src/kirby_world_palette.s','  cmp #18\n  beq Mario','  cmp #18\n  beq Mario\n  cmp #17\n  beq Mario')
    edit('src/x5_palette.s','.proc X5GetPlayerColors\n  lda SelectedCharacter\n','.proc X5GetPlayerColors\n  lda SelectedCharacter\n  cmp #17\n  bne :+\n  farcall M3GetPlayerColors,jmp\n:\n')
    # The palette file has several independent SelectedCharacter reloads;
    # install only at the public entry without altering their local conditions.
    cfg='smb1base-mmc5-expanded.cfg'
    edit(cfg,'X5_NEW_5B: start=$a000','X5_NEW_5B: start=$c000')
    edit(cfg,'CV3_CHR_AFTER: start=$83000,size=$14000','M3_CHR_MEM: start=$83000,size=$14000')
    edit(cfg,'SEGMENTS {','''SEGMENTS {
    M3_LOGIC:load=X5_NEW_5A,type=ro;
    M3_NATIVE:load=X5_NEW_5C,type=ro;
    M3_GFX:load=X5_NEW_5B,type=ro;
    M3_CHR:load=M3_CHR_MEM,type=ro;
''')
    src=(D/'merge-staging/src/character_select.s').read_text()
    a=src.index('  lda SelectedCharacter\n  cmp #17',src.index('CdNoToggle:'));b=src.index('M3NoToggle:',a)+len('M3NoToggle:\n')
    edit('src/character_select.s','CdNoToggle:\n','CdNoToggle:\n'+src[a:b])
    edit('src/character_select.s','TnNoHint:\n','''TnNoHint:
  cmp #17
  bne M3NoHint
  lda M3Hint,y
  jmp Put
M3NoHint:
''')
    edit('src/character_select.s','ProtoHint: .byte','M3Hint: .byte "SELECT - MARIO/LUIGI"\nProtoHint: .byte')
    edit('src/character_select.s','.proc QueueSelectName\n  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED','.proc QueueSelectName\n  lda SelectedCharacter\n.if ::ENABLE_MMC5_EXPANDED\n  cmp #17\n  bne M3OtherName\n  lda #28\n  clc\n  adc M3Variant\n  jmp NameIndex\nM3OtherName:')
    edit('src/character_select.s','"    ALUCARD     "','"    ALUCARD     ","   SMB3 MARIO   ","   SMB3 LUIGI   "')
    O.mkdir(parents=True)
    spec=json.loads((R/'build/verification/vic-adoption-mp/menu-input.json').read_text())
    spec['portraits'].append(dict(slot=16,character=17,image=str(D/'original-art/smb3-mario-portrait.png')))
    (O/'menu-input.json').write_text(json.dumps(spec,indent=2)+'\n')
    subprocess.run([sys.executable,str(R/'tools/reference/build_x5_menu.py'),'--manifest',str(O/'menu-input.json'),'--output',str(O/'menu')],check=True)
    texts['src/x5_menu_layout.inc']=(O/'menu/x5-menu-layout.inc').read_text()
    for n in shared:
        p=O/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    for n,t in {**texts,**owned}.items():(R/n).write_text(t)
    shutil.copyfile(D/'merge-staging/chr/characters/smb3-mario.chr',R/'chr/characters/smb3-mario.chr')
    shutil.copyfile(O/'menu/x5-menu.bin',R/'chr/raw/x5-character-select.bin')
    packed=bytearray((R/'chr/characters/packed-mmc5-expanded.chr').read_bytes());packed[4096:8192]=(O/'menu/x5-menu.chr').read_bytes()
    (R/'chr/characters/packed-mmc5-expanded.chr').write_bytes(packed)
    report=dict(parent='cv3-blocks-mt',packet_sha256=sha(D/'incremental-merge-manifest.json'),before={n:sha(O/'before'/n) for n in sorted(shared)},after={n:sha(R/n) for n in sorted(shared)},owned={n:sha(R/n) for n in sorted(owned)},asset_sha256=sha(R/'chr/characters/smb3-mario.chr'),name_indices=[28,29],private_PLAYER_trampoline_excluded=True)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(evidence=str(O),own=len(owned)+1,shared=len(shared))))

if __name__=='__main__':main()
