; Rogue Dawn1.21 source-derived weapon component; source-control receiptv1.
; Does not read/construct Metroid worldRAM. The host consumes explicit rendering,
; terrain and motion boundary outputs at the original call ordering.
.include "rogue_dawn_state.inc"
; Native source slot offsetsD0/E0/F0 remain real API indices. These INDEXED bases
; are arithmetic only: every admitted main-record access lands inside5C40..6F.
; Wave metadata is packed separately at70..78 with genuine index conversion.
RdWAction=$5b70                 ; source0300+X
RdWRadiusY=$5b71
RdWRadiusX=$5b72
RdWFrame=$5b73
RdWDelay=$5b74
RdWReset=$5b75
RdWAnim=$5b76
RdWVY=$5b78
RdWVX=$5b79
RdWHit=$5b7a
RdWOnScreen=$5b7b
RdWHi=$5b7c
RdWY=$5b7d
RdWX=$5b7e
RdWAge=$5b7f
RdWPhase=$5c70                  ; packed0/3/6, NOT nativeD0/E0/F0 index
RdWPhaseClock=$5c71
RdWDirection=$5c72
RdMetaIndex=$5c35
RdWaveDirectionTemp=$5c36
RdMetaNativeY=$5c37
RdWeaponDrawClass=$5c3a          ; native draw class1beam/3bomb; host renders
RdBombTerrainPhase=$5c3b         ; age1center,2up16,3down16,4left16,5right16
RdWeaponColor=$5c3c              ; source6B override81 forIce
RdWeaponUpdating=$5c3d           ; source71 update-in-progress image
RdWeaponSpawnDX=$5c3e            ; source05 spawn offset, host consumes
RdWeaponSpawnDY=$5c3f            ; source04 spawn offset, host consumes
RdBeamSfx=$5c7a                 ; source061F original combined sound image
RdGrabbed=$5c7b                 ; source92 Metroid-on-player firing admission
RdColorRequest=$5c7c            ; source1C palette request, host consumes
RdSourceAltPalette=$5c7d         ; source69B3 alternate costume owner
.pushseg
.segment "ROGUE_DAWN_CORE"
.export RdBombAllocate,RdBombInitialize,RdBombFuseStep
.export RdBombExplosionBegin,RdBombExplosionFinish
.export RdInitProjectile,RdInitWaveHorizontal,RdInitWaveUp,RdInitIce
.export RdSetProjectileAnimation,RdWaveKinematics
.export RdProjectileImpact,RdProjectileExplosion,RdFindProjectileSlot
.export RdProjectileTerrainImpact
.export RdFinishProjectileRender,RdCheckProjectileOnScreen,RdProjectileMotionDelta
.export RdIceUpdateAdmission
.export RdAnimateProjectile,RdBombStepBegin,RdBombStepFinish
.export RdPrepareHorizontalShot,RdPrepareUpShot,RdFireHorizontalFinish,RdFireUpFinish
.export RdApplyHorizontalMissile,RdApplyUpMissile,RdToggleMissile
.export RdAttackAdmission
.export RdClearProjectileColor
.export RdWeaponDrawClass,RdBombTerrainPhase,RdWeaponColor,RdBeamSfx

.proc RdBombAllocate             ; complete native62:D150..D197
    lda RdGear
    lsr a
    bcc Done
    lda RdFresh
    ora RdRepeat
    asl a
    bpl Done
    lda #0
    nop
    ora RdElevator
    bne Done
    ldx #$d0
    lda RdWAction,x
    beq Allocate
    ldx #$e0
    lda RdWAction,x
    beq Allocate
    ldx #$f0
    lda RdWAction,x
    bne Done
Allocate:
    lda RdRoomHi
    sta RdWHi,x
    lda RdX
    sta RdWX,x
    lda RdY
    clc
    adc #4
    sta RdWY,x
    lda #8
    sta RdWAction,x
    jsr BombRequest
Done:
    rts
.endproc

.proc RdBombInitialize           ;62:D65E prefix, then explicit draw class3
    lda #$7f
    jsr RdSetProjectileAnimation
    lda #12
    sta RdWAge,x
    inc RdWAction,x
    lda #3
    sta RdWeaponDrawClass
    rts
.endproc

.proc RdBombFuseStep             ;62:D670..D68E; original anim/state/SFX
    lda RdClock
    lsr a
    bcc Draw
    dec RdWAge,x
    bne Draw
    lda #$37
    ldy RdWAction,x
    cpy #9
    bne SetAnim
    lda #$82
SetAnim:
    jsr RdSetProjectileAnimation
    inc RdWAction,x
    jsr BombExplodeRequest
Draw:
    lda #3
    sta RdWeaponDrawClass
    rts
.endproc

.proc RdBombExplosionBegin       ;62:D691, nativeD6A7 call delegated as event
    inc RdWAge,x
    lda RdWAge,x
    cmp #6
    bcc Terrain
    lda #0
Terrain:
    sta RdBombTerrainPhase
    rts
.endproc
; REQUIRED: host handles source terrain phase before this continuation, with
; original legal breakable-tile admission. No global enemy damage is implied.
.proc RdBombExplosionFinish      ; genuine62:D697..D6A4 continuation
    ldx RdSlot
    lda RdWFrame,x
    sec
    sbc #$f7
    bne Draw
    sta RdWAction,x
Draw:
    lda #3
    sta RdWeaponDrawClass
    rts
.endproc

; Complete bomb state/animation protocol. Host MUST consume the terrain event
; between Begin(C=1) and Finish, before drawing. C=0 means state/animation ready
; for the renderer. Native frameF7 emits no parts, even on the final draw call.
.proc RdBombStepBegin
    stx RdSlot
    lda #0
    sta RdBombTerrainPhase
    lda RdWAction,x
    cmp #8
    beq Initialize
    cmp #9
    beq Fuse
    cmp #10
    beq Explosion
    lda #0
    sta RdWeaponDrawClass
    clc
    rts
Initialize:
    jsr RdBombInitialize
    jmp DrawReady
Fuse:
    jsr RdBombFuseStep
DrawReady:
    lda #3
    jsr RdAnimateProjectile
    clc
    rts
Explosion:
    jsr RdBombExplosionBegin
    sec
    rts
.endproc
.proc RdBombStepFinish
    jsr RdBombExplosionFinish
    lda #3
    jsr RdAnimateProjectile
    rts
.endproc

.proc RdAnimateProjectile        ; complete62:DC8F..DCB6, weapon-only data
    ldx RdSlot
    ldy RdWDelay,x
    beq Next
    dec RdWDelay,x
    bne Done
Next:
    sta RdWDelay,x
    ldy RdWAnim,x
Read:
    cpy #$7d
    bcs High
    lda WeaponAnimationLow-$1b,y
    jmp Decoded
High:
    lda WeaponAnimationHigh-$7d,y
Decoded:
    cmp #$ff
    beq Reset
    sta RdWFrame,x
    iny
    tya
    sta RdWAnim,x
Done:
    rts
Reset:
    ldy RdWReset,x
    jmp Read
.endproc
; Exactly physical02/04/06/08/0A:8572+native index; no invented durations.
; Valid animations1B,1D,7D,7F,82,8B,8D,8F,91 and their real continuations.
WeaponAnimationLow: .byte $28,$ff,$2a,$f7,$ff
WeaponAnimationHigh:
    .byte $4b,$ff,$4e,$4f,$ff,$3c,$4a,$49,$4a,$4d,$4a,$4d,$f7,$ff
    .byte $26,$ff,$25,$ff,$27,$ff,$67,$67,$67,$68,$68,$69,$f7,$ff

.proc RdInitProjectile           ;62:D2EB..D305, Y=D0/E0/F0 fromrealallocator
    tya
    tax
    inc RdWAction,x
    lda #2
    sta RdWRadiusY,y
    sta RdWRadiusX,y
    lda #$1b
    jmp RdSetProjectileAnimation
.endproc
.proc RdSetProjectileAnimation   ;62:D2FA..D305
    sta RdWReset,x
    sta RdWAnim,x
    lda #0
    sta RdWDelay,x
    rts
.endproc

.proc RdFindProjectileSlot       ; complete62:D1F7..D20F
    ldy #$d0
Try:
    lda RdWAction,y
    beq Found
    tya
    clc
    adc #$10
    tay
    bne Try
    iny
    rts
Found:
    sta RdWHit,y
    lda RdMissileMode
    beq Done
    lda #0
Done:
    rts
.endproc

; Split at native D306 coordinate call. On admitted spawn, DrawClass1 identifies
; a new record and nativeY is its D0/E0/F0 index. The host applies exact signed
; SpawnDX/DY relative to player with its real world/collision ownership, then
; calls the matching Finish. Denied attempts already finish native actor pose.
.proc RdPrepareHorizontalShot    ;62:D210..D24D before JSRD306
    lda #0
    sta RdWeaponDrawClass
    lda RdGrabbed
    bne Denied
    jsr RdFindProjectileSlot
    bne Denied
    jsr RdInitProjectile
    jsr RdInitWaveHorizontal
    jsr RdInitIce
    lda #12
    sta RdWAge,y
    ldx RdFacing
    lda HorizontalVelocity,x
    sta RdWVX,y
    lda #0
    sta RdWVY,y
    lda #1
    sta RdWOnScreen,y
    jsr RdApplyHorizontalMissile
    lda #1
    sta RdWeaponDrawClass
    lda RdWAction,y
    asl a
    ora RdFacing
    and #3
    tax
    lda HorizontalOffset,x
    sta RdWeaponSpawnDX
    lda #$fa
    sta RdWeaponSpawnDY
    rts
Denied:
    jmp FirePose9
.endproc
.proc RdPrepareUpShot            ;62:D275..D2AF before JSRD306
    lda #0
    sta RdWeaponDrawClass
    lda RdGrabbed
    bne Denied
    jsr RdFindProjectileSlot
    bne Denied
    jsr RdInitProjectile
    jsr RdInitWaveUp
    jsr RdInitIce
    lda #12
    sta RdWAge,y
    lda #$fc
    sta RdWVY,y
    lda #0
    sta RdWVX,y
    lda #1
    sta RdWOnScreen,y
    jsr RdApplyUpMissile
    lda #1
    sta RdWeaponDrawClass
    ldx RdFacing
    lda UpOffsetX,x
    sta RdWeaponSpawnDX
    lda RdWAction,y
    and #1
    tax
    lda UpOffsetY,x
    sta RdWeaponSpawnDY
    rts
Denied:
    jmp FinishUpPose
.endproc
.proc RdFireHorizontalFinish     ;62:D251..D26E after host native-offset move
    jsr LongRequestImage
    ldx RdWAction,y
    dex
    bne FirePose9
    jsr IceRequest              ; authentic CBB4 bit10 also normal fire request
    jmp FirePose9
.endproc
.proc RdFireUpFinish             ;62:D2B3..D2E2 after host native-offset move
    jsr LongRequestImage
    lda RdWAction,y
    cmp #1
    bne Pose
    jsr IceRequest
Pose:
    jmp FinishUpPose
.endproc
.proc FinishUpPose
    ldx RdFacing
    ldy #$26
    lda RdGravity
    beq Pose
    ldy #$34
Pose:
    lda RdAction
    cmp #1
    beq Done
    tya
    jmp PlayerFirePose
Done:
    rts
.endproc
.proc FirePose9
    ldy #9
    tya
    jmp PlayerFirePose
.endproc
.proc PlayerFirePose             ; source62:CF6E..CF76, does NOT reset0305
    sta RdAnimIndex
    lda #0
    sta RdAnimDelay
    rts
.endproc
.proc LongRequestImage           ; sourceD251..D25F /D2B3..D2C1
    nop
    lda #4
    and #4
    lsr a
    lsr a
    lsr a
    ror a
    ora RdBeamSfx
    sta RdBeamSfx
    rts
.endproc
.proc RdApplyHorizontalMissile   ; complete source62:D315..D358
    lda RdMissileMode
    beq Done
    cpy #$d0
    nop
    nop
    ldx RdFacing
    lda MissileAnimation,x
    jmp MissileCommit
Done:
    rts
.endproc
.proc RdApplyUpMissile           ; complete source62:D340..D358
    lda RdMissileMode
    beq Done
    cpy #$d0
    nop
    nop
    lda #$8f
    bne MissileCommit
Done:
    rts
.endproc
.proc MissileCommit              ; sourceD323 shared continuation
    jsr SetProjectileAnimationY
    jsr MissileRequest
    lda #11
    sta RdWAction,y
    lda #$ff
    sta RdWAge,y
    dec RdMissiles
    bne Done
    dec RdMissileMode
    jmp PaletteRequest
Done:
    rts
.endproc
.proc RdToggleMissile            ; complete actual61:A22A..A242
    lda RdMissiles
    beq Done
    lda RdFresh
    ora RdRepeat
    and #$20
    beq Done
    lda RdMissileMode
    eor #1
    sta RdMissileMode
    jmp PaletteRequest
Done:
    rts
.endproc
.proc PaletteRequest             ; exact source62:CB73..CB8D private image
    tya
    pha
    lda RdGear
    asl a
    asl a
    asl a
    lda RdMissileMode
    rol a
    adc #2
    ldy RdSourceAltPalette
    beq Store
    clc
    adc #$17
Store:
    sta RdColorRequest
    pla
    tay
    rts
.endproc
.proc MissileRequest
    lda #$20
    ldx #0
    ora RdSfx,x
    sta RdSfx,x
    rts
.endproc
HorizontalVelocity: .byte $04,$fc
HorizontalOffset: .byte $0c,$f4,$08,$f8
UpOffsetX: .byte $01,$ff
UpOffsetY: .byte $ec,$f0
MissileAnimation: .byte $8d,$8b

.proc RdInitWaveHorizontal       ;62:D359 entry
    lda RdFacing
    jmp RdWaveInitialize
.endproc
.proc RdInitWaveUp               ;62:D38A entry
    lda #2
    jmp RdWaveInitialize
.endproc
.proc RdWaveInitialize           ;62:D35B..D389
    jsr MetaIndexY
    sta RdWDirection,y
    ldy RdMetaNativeY
    bit RdGear
    bvc Done
    lda RdMissileMode
    bne Done
    lda #0
    jsr MetaIndexY
    sta RdWPhaseClock,y
    ldy RdMetaNativeY
    sta RdWDelay,y
    tya
    jsr Divide32
    lda #0
    bcs Phase
    lda #12
Phase:
    jsr MetaIndexY
    sta RdWPhase,y
    ldy RdMetaNativeY
    lda #2
    sta RdWAction,y
    lda #$7d
    jsr SetProjectileAnimationY
    jsr WaveRequest
Done:
    rts
.endproc
.proc RdInitIce                  ; complete62:D38E..D3A7
    lda RdMissileMode
    bne Done
    lda RdGear
    bpl Done
    lda #3
    sta RdWAction,y
    lda RdBeamSfx
    ora #1
    sta RdBeamSfx
    jsr IceRequest
Done:
    rts
.endproc
.proc SetProjectileAnimationY    ;62:D34D..D358, distinct Y-index owner
    sta RdWAnim,y
    sta RdWReset,y
    lda #0
    sta RdWDelay,y
    rts
.endproc

.proc RdWaveKinematics           ; source62:D536..D57F, before nextworldcheck
    txa
    tay
    jsr MetaIndexY
    lda RdWDirection,y
    sta RdWaveDirectionTemp
ReadPhase:
    ldy RdMetaIndex
    lda RdWPhase,y
    tay
    jsr ReadWave
    cmp #$ff
    bne Count
    ldy RdMetaIndex
    sta RdWPhase,y
One:
    php                         ; native INC preserves C/V
    lda RdWPhase,y
    clc
    adc #1
    sta RdWPhase,y
    plp
    lda #0
    sta RdWPhaseClock,y
    beq ReadPhase
Count:
    sty RdMetaNativeY
    ldy RdMetaIndex
    cmp RdWPhaseClock,y
    bne Decode
    php
    lda RdWPhase,y
    clc
    adc #1
    sta RdWPhase,y
    plp
    jmp One
Decode:
    php
    lda RdWPhaseClock,y
    clc
    adc #1
    sta RdWPhaseClock,y
    plp
    ldy RdMetaNativeY
    iny
    jsr ReadWave
    jsr DecodeVertical
    ldx RdSlot
    sta RdWVY,x
    jsr ReadWave
    jsr DecodeHorizontal
    ldx RdSlot
    sta RdWVX,x
    tay
    lda RdWaveDirectionTemp
    lsr a
    bcc Done
    tya
    jsr Negate
    sta RdWVX,x
Done:
    rts
ReadWave:
    lda RdWaveDirectionTemp
    and #$fe
    bne Vertical
    lda WaveHorizontal,y
    rts
Vertical:
    lda WaveVertical,y
    rts
.endproc

.proc MetaIndexY                 ; nativeY D0/E0/F0 -> packedY0/3/6
    php                         ; preserve actual inputCarry and BITflags
    pha
    tya
    sta RdMetaNativeY
    sec
    sbc #$d0
    lsr a
    lsr a
    lsr a
    lsr a
    sta RdMetaIndex
    asl a
    clc
    adc RdMetaIndex
    sta RdMetaIndex
    tay
    pla
    plp
    rts
.endproc

.proc RdProjectileImpact         ; complete62:D5DA..D5FB
    lda RdWHit,x
    beq Done
    lda #0
    sta RdWHit,x
    jmp RdProjectileTerrainImpact
Done:
    rts
.endproc
.proc RdProjectileTerrainImpact  ; genuine62:D5E4..D5FB entry, no fake hitflag
    lda #$1d
    ldy RdWAction,x
    cpy #4
    beq Done
    cpy #11
    bne SetAnim
    lda #$91
SetAnim:
    jsr RdSetProjectileAnimation
    lda #4
    sta RdWAction,x
Done:
    rts
.endproc
.proc RdProjectileExplosion      ;62:D5C8..D5D7, draw class1 output
    lda #1
    sta RdWeaponUpdating
    lda RdWFrame,x
    sec
    sbc #$f7
    bne Draw
    sta RdWAction,x
Draw:
    lda #1
    sta RdWeaponDrawClass
    rts                          ; REQUIRED host renderer then Finish below
.endproc
.proc RdFinishProjectileRender   ; genuine62:D51C..D51E, AFTER actual rendering
    dec RdWeaponUpdating
    rts
.endproc
.proc RdClearProjectileColor     ; genuine62:DF2D..DF31, after real render
    lda #0
    sta RdWeaponColor
    rts
.endproc
.proc RdCheckProjectileOnScreen  ; complete62:D5FC..D604
    lda RdWOnScreen,x
    lsr a
    bcs Done
    lda #0
    sta RdWAction,x
Done:
    rts
.endproc
.proc RdAttackAdmission          ; actual63:F0B4..F0C7 source action filter
    lda RdWAction,x
    beq Denied
    cmp #4
    bcc Allowed
    cmp #7
    beq Allowed
    cmp #10
    beq Allowed
    cmp #11
    bne Denied
Allowed:
    sec                          ; NEW API: eligible class, not geometric hit
    rts
Denied:
    clc
    rts
.endproc
.proc RdProjectileMotionDelta    ;62:D624..D62E, next nativeworldcall delegated
    ldx RdSlot
    lda RdWVX,x
    sta RdWeaponSpawnDX
    lda RdWVY,x
    sta RdWeaponSpawnDY
    rts
.endproc
.proc RdIceUpdateAdmission       ;62:D5C1->DA85 prefix before BEQ atDA8A
    lda #$81
    sta RdWeaponColor
    lda RdGear
    and #$40                     ; zero=normal,nonzero=actualWaveKinematics
    rts
.endproc

.proc DecodeVertical             ; actualphysical02/04/06/08/0A:8296..82A4
    asl a
    php
    jsr Divide32
    plp
    bcc Store
    eor #$ff
    adc #0
Store:
    sta RdDelta
    rts
.endproc
.proc DecodeHorizontal           ; actualphysical02/04/06/08/0A:832F..833E
    tax
    and #8
    php
    txa
    and #7
    plp
    beq Store
    jsr Negate
Store:
    sta RdDelta
    rts
.endproc
.proc Divide32                   ; source62:C2BE..C2C3
    lsr a
    lsr a
    lsr a
    lsr a
    lsr a
    rts
.endproc
.proc Negate                     ; source62:C3D4..C3D9
    eor #$ff
    clc
    adc #1
    rts
.endproc
.proc BombRequest
    lda #1
    ldx #3
    ora RdSfx,x
    sta RdSfx,x
    rts
.endproc
.proc BombExplodeRequest
    lda #$10
    ldx #0
    ora RdSfx,x
    sta RdSfx,x
    rts
.endproc
.proc WaveRequest
    lda #1
    ldx #1
    ora RdSfx,x
    sta RdSfx,x
    rts
.endproc
.proc IceRequest
    lda #$10
    ldx #1
    ora RdSfx,x
    sta RdSfx,x
    rts
.endproc
; Exact actual62:D58F/D5A8 source tables (25bytes each, no approximated sine).
WaveHorizontal:
    .byte $01,$d5,$01,$95,$01,$95,$01,$15,$01,$15,$01,$55
    .byte $01,$55,$01,$15,$01,$15,$01,$95,$01,$95,$01,$d5,$ff
WaveVertical:
    .byte $01,$d5,$01,$d1,$01,$d1,$01,$d9,$01,$d9,$01,$dd
    .byte $01,$dd,$01,$d9,$01,$d9,$01,$d1,$01,$d1,$01,$d5,$ff
.export RdWeaponsEnd
RdWeaponsEnd:
.assert RdWeaponsEnd-RdStartJump <= $1000, lderror, "Rogue CORE exceeds4KB"
.popseg
