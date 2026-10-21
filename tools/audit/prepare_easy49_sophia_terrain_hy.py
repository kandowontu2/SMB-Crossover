"""Private normal Sophia head/side consumers on frozen body stage HS."""
from pathlib import Path
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
P=V/'root49-sophia-source-body-hs'
D=V/'root49-sophia-source-terrain-hy'
S=D/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def edit(n,a,b):
    p=S/n;raw=p.read_bytes();eol='\r\n'if b'\r\n'in raw else'\n'
    aa,bb=(x.replace('\n',eol).encode()for x in [a,b])
    assert raw.count(aa)==1,(n,a[:60]);p.write_bytes(raw.replace(aa,bb))


def main():
    assert not D.exists()
    frozen=P/'implementation-stage-freeze-hx.json'
    assert sha(frozen)=='5cf6053ae918b693f67df7d7167089c8508314c93cdc087d5f16b5570d4e865e'
    catalog=json.loads(frozen.read_text())['source_catalog']
    for n,h in catalog.items():
        assert sha(P/'source'/n)==h,n
        p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
    shutil.copytree(P/'source/build/generated',S/'build/generated')
    edit('src/characters.s', '''  cmp #CHARACTER_RYU
  beq Ryu
  cmp #CHARACTER_SAMUS
  beq Guest
  cmp #CHARACTER_SCROOGE
  bne Native
Guest:''','''  cmp #CHARACTER_RYU
  bcs HighGuest
  cmp #CHARACTER_SAMUS
  bne Native
Guest:''')
    edit('src/characters.s','Return:\n  rts\nNative:\n  jmp BlockBufferColli_Head',
         'Return:\n  rts\nHighGuest:\n  beq Ryu\n  cmp #CHARACTER_COUNT\n  bcc Guest\nNative:\n  jmp BlockBufferColli_Head')
    edit('src/characters.s','  nop\n  nop ; Preserve all subsequent resident PCs; blank queries need source width.','  ; New high-ID dispatch consumes the former two NOP bytes.')
    edit('src/characters.s','''  cmp #CHARACTER_SAMUS
  beq Samus
  jmp ScroogeHeadProbe''','''  cmp #CHARACTER_SOPHIA
  beq Sophia
  cmp #CHARACTER_SAMUS
  beq Samus
  jmp ScroogeHeadProbe
Sophia:
  farcall SophiaSourceHeadProbe, jmp''')
    edit('src/characters.s','''CharacterNames:
  .byte "MARIO  ", "MEGAMAN", "SAMUS  ", "BILL   ", "LINK   ", "SIMON  "
  .byte "PIT    ",''','''; Only the existing bank3 status-text producer reads these42 bytes.
.pushseg
.segment "RENDER"
CharacterNamesPrefix:
  .byte "MARIO  ", "MEGAMAN", "SAMUS  ", "BILL   ", "LINK   ", "SIMON  "
.popseg
CharacterNames:
  .byte "PIT    ",''')
    edit('src/characters.s','  lda CharacterNames,x\nWriteName:',
         '  cpx #42\n  bcc Prefix\n  lda CharacterNames-42,x\n  jmp WriteName\nPrefix:\n  lda CharacterNamesPrefix,x\nWriteName:')
    edit('src/characters.s','.proc GuestFootContactSide', '''.proc CrossoverSourceSideProbe
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne Native
  farcall SophiaSourceSideProbe, jmp
Native:
  jmp BlockBufferColli_Side
.endproc

.proc SophiaHeadWithinTerrain
  lda MmYFraction+1
  asl
  lda Player_Y_Position
  adc #16
  cmp #32
  rts
.endproc

.proc GuestFootContactSide''')
    edit('src/collision.s','''  cmp #CHARACTER_LUIGI
  beq Native
  ; Guest head adders''','''  cmp #CHARACTER_LUIGI
  beq Native
  cmp #CHARACTER_SOPHIA
  beq SophiaHeadWithinTerrain
  ; Guest head adders''')
    p=S/'src/collision.s';raw=p.read_bytes();a=b'jsr BlockBufferColli_Side';assert raw.count(a)==2
    raw=raw.replace(a,b'jsr CrossoverSourceSideProbe');p.write_bytes(raw)
    edit('src/samus.s','  farcall SamusStopAtWallBanked, jmp','  farcall CrossoverSourceWallDispatch, jmp')
    edit('src/samus.s','.proc SamusStopAtWallBanked','''.proc CrossoverSourceWallDispatch
  cmp #CHARACTER_SOPHIA
  beq Sophia
  jmp SamusStopAtWallBanked
Sophia:
  farcall SophiaSourceWall, jmp
.endproc
.proc SamusStopAtWallBanked''')
    edit('src/sophia_source_body.s','Sophia:\n  jmp SophiaSourceBodyBox',
         'Sophia:\n  jsr SophiaSourceAfterTerrain\n  jmp SophiaSourceBodyBox')
    edit('src/source_motion.s','.proc SophiaAbilities\n  lda XgCeiling', '''.proc SophiaAbilities
  ; Sophia owns these otherwise dormant Ryu cache cells for this update.
  lda #0
  sta RyWallSupported
  lda Player_State
  bne AirFlag
  sta RgDoubleJump
AirFlag:
  lda XgRise
  beq Cache
  lda #1
  sta RgDoubleJump
Cache:
  lda Player_X_Position
  sta RyWallOldX
  lda Player_PageLoc
  sta RyWallOldPage
  lda MmXFraction
  sta RyWallOldXFine
  lda MmXFraction+1
  sta RyWallOldXFrac
  lda Player_Y_Position
  sta RyWallOldY
  lda MmYFraction
  sta RyWallOldYFine
  lda MmYFraction+1
  sta RyWallOldYFrac
  lda #1
  sta RyWallSupported
  lda XgCeiling''')
    edit('src/megaman_environment.s','.segment "TITLE"\n.proc MegaManSpringVelocityModes',
         '.segment "SOPHIA_BODY_COLD"\n.proc MegaManSpringVelocityModes')
    edit('src/megaman_environment.s','''  lda #1
  sta Player_State
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
Done:
  plx''','''  lda #1
  sta Player_State
  ldx SelectedCharacter
  cpx #CHARACTER_SOPHIA
  bne :+
    sta RgDoubleJump             ; Source SpringObj.springLaunch sets jumped.
  :
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
Done:
  plx''')
    # The net resident +2 consumes only old spare spring bytes. Audio/fixed
    # continuations remain at the old address; actual layout checks bind this.
    edit('src/megaman_environment.s','  .repeat 4\n    .byte $ea','  .repeat 2\n    .byte $ea')
    edit('src/megaman_environment.s','  .repeat 26\n    .byte $ea','  .repeat 24\n    .byte $ea')
    edit('src/entrypoint.s','.include "sophia_source_body.s"',
         '.include "sophia_source_body.s"\n.include "sophia_source_terrain.s"')
    template=R/'tools/audit/templates/sophia_source_terrain_hy.s'
    shutil.copyfile(template,S/'src/sophia_source_terrain.s')
    driver=(P/'build-driver.py').read_text();assert driver.count(repr(str(P/'source')))==1
    (D/'build-driver.py').write_text(driver.replace(repr(str(P/'source')),repr(str(S))))
    names=list(catalog)+['src/sophia_source_terrain.s']
    record=dict(status='PRIVATE_NORMAL_TERRAIN_PREPARED_UNBUILT_NOT_ADMITTED',
        parent=sha(frozen),source_sha256={n:sha(S/n)for n in names},
        changes=[n for n,h in catalog.items()if sha(S/n)!=h],new=['src/sophia_source_terrain.s'],
        script_sha256=sha(__file__),template_sha256=sha(template),RAM_added=0,
        phase_ceiling_bytes=500000000,workspace_ceiling_bytes=60000000000,
        scope='Normal flat head-span queries, direct-below canonical ceiling response, interior side queries and source half-pixel wall clamps. Source prior cache is character-owned existing Ryu storage; jumped uses dormant Sophia RgDoubleJump. Rotated/vine/corner calcAxis/fullfootspan and all-arsenal remain open. Not a source-perfect or final-route claim.',
        main_changed=False)
    (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(status=record['status'],sources=len(names),changes=record['changes'])))


if __name__=='__main__':main()
