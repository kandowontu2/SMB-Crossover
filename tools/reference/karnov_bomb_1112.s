; The native options controller has one activation caller. Its real ownership
; test and original EB19 activation, stock helper and timer scheduler remain.
.setcpu "6502"
.segment "CONTROL_GATE"
    jsr KrBombAllowed
    bcc KrOptionsUnhandled

.segment "LADDER_LOAN"
KrBombAllowed:
    cmp #0
    beq KrBombAllow
    cmp #1
    beq KrBombAllow
    cmp #3
    beq KrBombAllow
    cmp #7
    beq KrBombAllow
    clc
    rts
KrBombAllow:
    sec
    rts

; Native Select follows the same owned-item cycle, now including Bomb1.
KrBombCycle:
    ldx #0
    lda $c08e
KrBombFind:
    cmp KrBombIds,x
    beq KrBombNext
    inx
    cpx #5
    bne KrBombFind
    ldx #4
KrBombNext:
    inx
    cpx #5
    bcc KrBombHaveIndex
    ldx #0
KrBombHaveIndex:
    lda KrBombIds,x
    bmi KrBombChoose
    lda $c08f
    and KrBombMasks,x
    beq KrBombNext
    lda KrBombIds,x
KrBombChoose:
    sta $c08e
    rts
KrBombIds:
    .byte $00,$01,$03,$07,$ff
KrBombMasks:
    .byte $01,$02,$08,$80

; Original AE3D..AE81 selects the same three timed phases. The SMB host has
; no donor stage3/5/7/8 scripted tile list following original AE81.
; Capture the camera from the existing actor rebase owner, before spawning.
KrBombTick:
    lda $c0c0
    bpl KrBombRemove
    lda $c0c1
    cmp #8
    bcc KrBombRemove
    cmp #248
    bcs KrBombRemove
    ; Donor foreground actor coordinates are 32 below native Y. Its normal
    ; stage floor is above the original C0 lower viewport bound. Native SMB
    ; floor actors stand at source D0, so extend the lower viewport bound by
    ; the exact 32-pixel host coordinate shift without moving the anchor.
    lda $c0c2
    cmp #32
    bcc KrBombRemove
    cmp #224
    bcs KrBombRemove
    lda $c0c0
    and #15
    beq KrBombTickDone
    cmp #1
    beq KrBombStageOne
    cmp #2
    beq KrBombStageTwo
    dec $c0c3
    bne KrBombTickDone
KrBombRemove:
    lda #0
    sta $c0c0
KrBombTickDone:
    rts
KrBombStageOne:
    inc $c0c0
    rts
KrBombStageTwo:
    dec $c0c3
    bne KrBombTickDone
    inc $c0c0
    lda #16
    sta $c0c3
    rts

.segment "SELECTION_LOAN"
; Active-update order is original Bomb object first, timer second. The
; movement caller has already accepted exactly one native epoch.
KrBombThenTimer:
    jsr KrBombTick
    jmp KrOptionsNativeTimers

; Original camera rebase subtracts the signed camera step from the parked
; Bomb anchor. Form it in 16 bits so an offscreen object cannot wrap back in.
KrBombRebaseShots:
    lda $c0c0
    bpl KrBombRebaseDone
    lda KrCameraLo
    clc
    adc $c0c1
    sta R0
    lda KrCameraHi
    adc #0
    sta R1
    lda R0
    sec
    sbc ScreenLeft_X_Pos
    sta $c0c1
    lda R1
    sbc ScreenLeft_PageLoc
    beq KrBombRebaseDone
    lda #0
    sta $c0c0
KrBombRebaseDone:
    jmp KrRebaseShots

; Same-life scene transfer cancels this world object. Source stock and the
; rest of the original options/timer state retain their existing lifetime.
KrBombSceneClear:
    lda #0
    sta $c0c0
    jmp KrClearSourceShots

; Native player Draw already owns AXYP and foreground scratch. Emit the
; original one/two sprite records, in native packet order, through its
; existing metasprite renderer and projectile CHR page.
.segment "DRAW_LOAN"
KrBombDrawWithShots:
    jsr KrDrawShots
    lda $c0c0
    bmi KrBombDrawActive
    rts
KrBombDrawActive:
    and #15
    beq KrBombArmedArt
    tax
    lda KrBombRightTiles,x
    sta KrShotPacket+1
    lda KrBombLeftTiles,x
    sta KrShotPacket+5
    lda #0
    sta KrShotPacket+2
    sta KrShotPacket+3
    sta KrShotPacket+6
    sta KrShotPacket+7
    sta KrShotPacket+8
    lda #8
    sta KrShotPacket
    sta KrShotPacket+4
    bne KrBombExplosionAnchor
KrBombArmedArt:
    lda $c0e8
    and #8
    beq KrBombArmedFirst
    lda #$c4
    bne KrBombArmedTile
KrBombArmedFirst:
    lda #$c2
KrBombArmedTile:
    sta KrShotPacket+1
    lda #0
    sta KrShotPacket+2
    sta KrShotPacket+3
    sta KrShotPacket+4
    lda #4
    sta KrShotPacket
    bne KrBombDrawAnchor
KrBombExplosionAnchor:
    lda #8
KrBombDrawAnchor:
    jmp KrBombAnchorFields
KrBombLeftTiles:
    .byte $00,$c6,$c6,$fc
KrBombRightTiles:
    .byte $00,$fa,$fa,$fe

.segment "DRAW_ANCHOR_LOAN"
KrBombAnchorFields:
    sta R2
    lda $c0c1
    sec
    sbc R2
    sta R4
    lda #0
    sbc #0
    sta R5
    lda R4
    sec
    sbc KrRenderCameraLo
    sta R4
    lda R5
    sbc KrRenderCameraHi
    sta R5
    lda $c0c2
    sec
    sbc #16
    sta R6
    lda #1
    sta R7
    lda #0
    sta R3
    lda #<KrShotPacket
    sta R0
    lda #>KrShotPacket
    sta R1
    sta $016a
    lda #<MetaspriteRenderLoop
    sta $016c
    lda #>MetaspriteRenderLoop
    sta $016d
    lda #$84
    jmp $015a

.segment "CLAPPER_LOAN"
; Native enemy contact keeps donor CCFC's unsigned asymmetric 32x16
; rectangle and active-phase test. The existing shot contact loop owns its
; authenticated once-per-epoch frame. Native actors use their own damage,
; death and score receiver. Reject actors outside that receiver's contract.
KrBombContactWithShots:
    lda $c0c0
    bpl KrBombOrdinaryShots
    and #15
    beq KrBombOrdinaryShots
    ldx #5
KrBombEnemyLoop:
    stx KCEnemy
    lda Enemy_Flag,x
    beq KrBombEnemyNext
    bmi KrBombEnemyNext
    lda Enemy_Y_HighPos,x
    cmp #1
    bne KrBombEnemyNext
    lda Enemy_State,x
    and #$20
    bne KrBombEnemyNext
    lda Enemy_ID,x
    cmp #6
    bne KrBombEnemyKind
    lda Enemy_State,x
    cmp #2
    bcs KrBombEnemyNext
    lda Enemy_ID,x
KrBombEnemyKind:
    cmp #$15
    bcc KrBombEnemyGeometry
    bcs KrBombEnemyNext
KrBombEnemyGeometry:
    lda Enemy_X_Position,x
    sec
    sbc KrCameraLo
    sta R0
    lda Enemy_PageLoc,x
    sbc KrCameraHi
    bne KrBombEnemyNext
    lda $c0c1
    clc
    ; Donor 0652 is the horizontal center. Native ordinary enemies store
    ; their left edge; fold its +8 conversion into Bomb's original +16.
    adc #8
    sec
    sbc R0
    cmp #32
    bcs KrBombEnemyNext
    jmp KrBombEnemyVertical
KrBombEnemyNext:
    dex
    bpl KrBombEnemyLoop
KrBombOrdinaryShots:
    lda $c065
    jmp KrCombatOrdinary

.segment "CONTACT_TAIL"
KrBombEnemyVertical:
    lda Enemy_Y_Position,x
    clc
    ; Donor 0653 and Bomb C2 share the bottom/feet anchor. A native
    ; Goomba's two 8x16 cells start at native Y+8 and end at Y+24.
    adc #24
    sta R0
    lda $c0c2
    sec
    sbc R0
    cmp #16
    bcs KrBombEnemyReturn
    stx ObjectOffset
    stx R1
    jsr HandleEnemyFBallCol
    ldx KCEnemy
KrBombEnemyReturn:
    jmp KrBombEnemyNext

.segment "SHIELD_LOAN"
; Map the native HUD to four real equipment indices, then the existing FIRE
; default. Original three icon and BCD paths stay intact.
KrBombHudChoice:
    ldx #0
    lda $c08e
    beq KrBombHudOwned
    inx
    cmp #3
    beq KrBombHudOwned
    inx
    cmp #7
    beq KrBombHudOwned
    ldx #4
    cmp #1
    bne KrBombHudFire
KrBombHudOwned:
    lda $c08f
    and KrBombHudMasks,x
    bne KrBombHudDone
KrBombHudFire:
    ldx #3
KrBombHudDone:
    jmp KrHudHaveIndex
KrBombHudMasks:
    .byte $01,$08,$80,$00,$02
KrBombHudStocks:
    .byte $bd,$be,$bf,$00,$bb
KrBombHudTiles:
    .byte $30,$34,$38,$00,$3c
KrBombHudNames:
    .byte $00,$09,$12,$1b,$24

.segment "HUD_NAME_TAIL"
KrBombHudNameStart:
    tay
    ldx #0
KrBombHudNameCopy:
    cpy #36
    bcc KrBombHudNameOld
    lda KrBombHudNewName,y
    bne KrBombHudNameStore
KrBombHudNameOld:
    lda KrHudOriginalNames,y
KrBombHudNameStore:
    sta KrHudNameCell,x
    iny
    inx
    cpx #9
    bne KrBombHudNameCopy
    jmp KrHudAfterName

.segment "HUD_TAIL"
KrBombHudHint:
    lda KrHudDownB,y
    cpy #4
    bne KrBombHudHintStore
    lda #$24
KrBombHudHintStore:
    sta VRAM_Buffer1+18,y
    dey
    bpl KrBombHudHint
    jmp KrHudLease
