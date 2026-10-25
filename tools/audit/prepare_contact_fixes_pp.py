"""Stage reported contact repairs on the frozen PM source, without adoption."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-contact-pp/candidate-v5')
PARENT=ROOT/'build/checkpoints/grant-grip-pm'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=False)
    source=OUT/'source'
    with zipfile.ZipFile(PARENT/'source.zip') as z:
        assert z.testzip() is None
        assert all((source/n).resolve().is_relative_to(source) for n in z.namelist())
        z.extractall(source)
    changes={}
    def replace(n,old,new):
        p=source/n;before=sha(p);s=p.read_text();assert s.count(old)==1,(n,s.count(old))
        p.write_text(s.replace(old,new));changes[n]=dict(before=before,after=sha(p))
    # R6 is the still-live contacted block-buffer column. The old initializer
    # derives X from player+8, which is wrong for an off-center head sample.
    replace('src/bill_native_rare.s',
        '  lda SelectedCharacter\n  cmp #CHARACTER_SOPHIA\n  jne InitBlock_XY_Pos\n  jsr InitBlock_XY_Pos\n  php\n  pha\n  lda MmBlockAttack\n  bne Done\n  bit SmCeilingHit\n  bpl Done\n  lda RgTempX\n  and #$f0\n  sta Block_X_Position,x\n  lda RgTempPage\n  sta Block_PageLoc,x\n  sta Block_PageLoc2,x\nDone:\n  pla\n  plp\n  rts',
        '''.if ::ENABLE_MMC5_EXPANDED
  jsr InitBlock_XY_Pos
  php
  pha
  lda SelectedCharacter
  beq Done
  lda R6
  sec
  sbc #<Block_Buffer_1
  and #$0f
  asl
  asl
  asl
  asl
  sta Block_X_Position,x
  lda Player_PageLoc
  sta Block_PageLoc,x
  sta Block_PageLoc2,x
  ; The two buffers encode world-page parity. A head/proxy can only sample
  ; the player's page or one neighbor, including a left-edge page carry.
  lda R6
  sec
  sbc #<Block_Buffer_1
  and #$10
  lsr
  lsr
  lsr
  lsr
  eor Player_PageLoc
  and #1
  beq Done
  lda Player_X_Position
  bmi NextPage
  dec Block_PageLoc,x
  dec Block_PageLoc2,x
  jmp Done
NextPage:
  inc Block_PageLoc,x
  inc Block_PageLoc2,x
Done:
  pla
  plp
  rts
.else
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  jne InitBlock_XY_Pos
  jsr InitBlock_XY_Pos
  php
  pha
  lda MmBlockAttack
  bne Done
  bit SmCeilingHit
  bpl Done
  lda RgTempX
  and #$f0
  sta Block_X_Position,x
  lda RgTempPage
  sta Block_PageLoc,x
  sta Block_PageLoc2,x
Done:
  pla
  plp
  rts
.endif''')
    replace('src/megaman_weapons.s',
        'SmallHead:\n    ldy #1\nDone:\n  plp\n  rts',
        '''SmallHead:
.if ::ENABLE_MMC5_EXPANDED
  ; Every linked caller is NativeRarePlayerHeadCollisionCore in bank9.
  ; Keep this resident span exact; the cold leaf releases our saved P.
  jmp CrossoverSmallHeadCold
  nop
.else
    ldy #1
Done:
  plp
  rts
.endif
 .if ::ENABLE_MMC5_EXPANDED
Done:
  plp
  rts
 .endif''')
    # Reclaim the redundant branch to the immediately following SmallHead;
    # pad at the end, keeping this entire resident routine and later PCs exact.
    p=source/'src/megaman_weapons.s';s=p.read_text()
    s=s.replace('  jmp CrossoverSmallHeadCold\n  nop\n','  jmp CrossoverSmallHeadCold\n')
    s=s.replace('  bne SmallHead                 ; Bill/Link/Simon break with weapons, not heads.',
        '.if .not ::ENABLE_MMC5_EXPANDED\n  bne SmallHead                 ; Bill/Link/Simon break with weapons, not heads.\n.endif')
    s=s.replace('  ldy #0\n  beq Done\n.endproc\n.proc MegaManResetBlockHealth',
        '  ldy #0\n  beq Done\n.if ::ENABLE_MMC5_EXPANDED\n  nop\n.endif\n.endproc\n.proc MegaManResetBlockHealth')
    p.write_text(s);changes['src/megaman_weapons.s']['after']=sha(p)
    p=source/'src/bill_native_rare.s';s=p.read_text()
    s+='''
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "BILL_BODY_COLD"
.proc CrossoverSmallHeadCold
  ldy #1
  lda SelectedCharacter
  cmp #CHARACTER_MIKE
  bne Done
  ldy #0
Done:
  plp
  rts
.endproc
.popseg
.endif
'''
    p.write_text(s);changes['src/bill_native_rare.s']['after']=sha(p)
    # Reuse the existing exact-cell adapter, with the actual yo-yo/projectile
    # tip. It admits only authored bricks/question blocks, never foundation.
    replace('src/mike_jones_weapons.s',
        ' lda JnShotY,x\n clc\n adc #8\n jsr JnReadCell\n tay\n lda MTileAttribute,y\n and #MTILE_SOLID|MTILE_CLIMB\n cmp #MTILE_SOLID\n jne Done',
        ''' lda JnQueryX
 sta MmProbeX
 lda JnQueryPage
 sta MmProbePage
 lda JnShotY,x
 clc
 adc #8
 sta MmProbeY
 farcall Cv3BlockPoint
 jcc Done''')
    replace('src/mike_jones_dispatch.s','Own:jmp BlockBufferColli_Head',
        '''Own:
 jsr BlockBufferColli_Head
 pha
 beq Done
 cmp #$c2
 beq Done
 cmp #$c3
 beq Done
 ldy Player_Y_Speed
 bpl Done
 ldy R3
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne Done
 ; The fixed grid-jump table would otherwise resume its8px rise through
 ; the temporary bumped-block cell and repeatedly trigger side separation.
 ; Separate the head at the actual tile bottom and end that jump arc.
 lda R2
 clc
 adc #48
 sec
 sbc #4
 sta Player_Y_Position
 and #15
 sta R4
 lda #0
 sta JnJump
 sta JnVY
 sta JnFallFrac
Done:
 pla
 rts''')
    # Inhale uses the same mouth cone for suction and body protection. Pull
    # enemy centers toward mouth height, rather than pushing their origins
    # below the floor. Pause native gravity for the captured target update.
    replace('src/kirby_weapons.s',
        '  lda Enemy_Y_Position,x\n  sec\n  sbc Player_Y_Position\n  clc\n  adc #4\n  cmp #41\n  jcs PullNext',
        '  jsr KbInhaleVertical\n  jcc PullNext')
    replace('src/kirby_weapons.s',
        'PullY:\n  lda Player_Y_Position\n  clc\n  adc #16\n  cmp Enemy_Y_Position,x',
        '''PullY:
  lda #0
  sta Enemy_Y_Speed,x
  sta Enemy_Y_MoveForce,x
  jsr KbInhaleTargetY
  cmp Enemy_Y_Position,x''')
    replace('src/kirby_weapons.s',
        '  lda KbAction\n  cmp #5\n  jeq Defeat\n  cmp #4\n  jne No',
        '''  lda KbVariant
  jne OrdinaryAttack
  lda KbAction
  cmp #1
  jne OrdinaryAttack
  ; Only an edible enemy in front of an active mouth is protected. Back,
  ; startup, released-B, hazard and Meta Knight contacts remain ordinary.
  lda KbActionAge
  jne No
  lda SavedJoypadBits
  and #B_Button
  jeq No
  jsr KbInhaleVertical
  jcc No
  lda Enemy_X_Position,x
  sec
  sbc Player_X_Position
  sta KbTempX
  lda Enemy_PageLoc,x
  sbc Player_PageLoc
  sta KbTempPage
  lda PlayerFacingDir
  cmp #1
  jeq MouthFront
  sec
  lda #0
  sbc KbTempX
  sta KbTempX
  lda #0
  sbc KbTempPage
  sta KbTempPage
MouthFront:
  lda KbTempPage
  jne No
  lda KbTempX
  cmp #57
  jcs No
  sec
  rts
OrdinaryAttack:
  lda KbAction
  cmp #5
  jeq Defeat
  cmp #4
  jne No''')
    # Enemy body coordinates are native SMB origins, not sprite-top pixels.
    # Native goomba/beetle/bill/fish height16; tall koopas/hammerbro/plant24.
    p=source/'src/kirby_weapons.s';s=p.read_text();before=sha(p)
    s+='''
.pushseg
.segment "KIRBY_ABILITIES"
.proc KbInhaleTargetY
  ; Native ground enemies share the origin+24 foot even when the artwork
  ; is taller. Kirby's foot is origin+32. Keep their feet level: deriving
  ; this from sprite height would bury tall Koopas four pixels in the floor.
  lda #8
  clc
  adc Player_Y_Position
  rts
.endproc
.proc KbInhaleVertical
  jsr KbInhaleTargetY
  sta KbTempY
  lda Enemy_Y_HighPos,x
  cmp #1
  bne No
  lda Enemy_Y_Position,x
  sec
  sbc KbTempY
  clc
  adc #12
  cmp #25
  bcs No
  sec
  rts
No:
  clc
  rts
.endproc
.popseg
'''
    p.write_text(s);changes['src/kirby_weapons.s']['after']=sha(p)
    # Copied SMB shot records use top-left origins; native Kirby effects use
    # centers. Normalize the copied records to the existing center+8 floor.
    replace('src/kirby_draw.s',
        '  lda KbShotY,x\n  sta R6\n  jsr Draw\nNext:',
        '''  lda KbShotY,x
  sta R6
  lda KbShotType,x
  cmp #3
  bne ShotReady
  lda KbShotKind,x
  cmp #2
  beq CenterNative
  cmp #3
  beq CenterNative
  cmp #5
  beq CenterNative
  cmp #11
  bne ShotReady
CenterNative:
  sec
  lda R4
  sbc #8
  sta R4
  lda R5
  sbc #0
  sta R5
  sec
  lda R6
  sbc #8
  sta R6
ShotReady:
  jsr Draw
Next:''')
    # Sypha's doubled integer source-table displacement has 10px launch and
    # 12px terminal drops. Use a fractional SMB traversal arc for Sypha only;
    # keep her fixed launch direction, source attacks and all outside impulses.
    replace('src/cv3_core.s','Live:\n  ; A native head bump',
        '''Live:
  lda Cv3Variant
  cmp #2
  jne OriginalJump
  jmp Cv3SyphaArc
OriginalJump:
  ; A native head bump''')
    p=source/'src/cv3_core.s';s=p.read_text()
    s+='''
.pushseg
.segment "CV3_CORE"
.proc Cv3SyphaArc
  lda Cv3JumpPhase
  bne Step
  lda Cv3JumpIndex
  cmp #9
  bne Head
  inc Cv3JumpIndex
  lda #0
  sta Cv3VyLo
  sta MmYFraction+1
  lda #$fa
  sta Cv3VyHi
  rts
Head:
  lda Player_Y_Speed
  bmi Step
  lda Cv3VyHi
  bpl Step
  lda #0
  sta Cv3VyLo
  sta Cv3VyHi
  sta MmYFraction+1
Step:
  clc
  lda Cv3VyLo
  adc #$40
  sta Cv3VyLo
  lda Cv3VyHi
  adc #0
  sta Cv3VyHi
  bmi Done
  lda #1
  sta Cv3JumpPhase
  lda Cv3VyHi
  cmp #6
  bcc Done
  lda #6
  sta Cv3VyHi
  lda #0
  sta Cv3VyLo
Done:
  rts
.endproc
.popseg
'''
    p.write_text(s);changes['src/cv3_core.s']['after']=sha(p)
    replace('src/x5_bounce.s','  asl Cv3VyLo\n  rol Cv3VyHi',
        '''  lda Cv3Variant
  cmp #2
  beq Restore                 ; Sypha owns a smooth fractional traversal arc.
  asl Cv3VyLo
  rol Cv3VyHi''')
    command=[sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(OUT/'candidate.nes')]
    z=subprocess.run(command,cwd=source,capture_output=True,text=True)
    (OUT/'build.log').write_text(z.stdout+z.stderr)
    (OUT/'preparation.json').write_text(json.dumps(dict(prepared=z.returncode==0,accepted=False,
        parent_ROM_sha256=sha(PARENT/'candidate.nes'),changes=changes),indent=2)+'\n')
    assert z.returncode==0,(z.stdout+z.stderr)[-3500:]
    print(sha(OUT/'candidate.nes'))

if __name__=='__main__':main()
