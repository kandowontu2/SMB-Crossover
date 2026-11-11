; Steve's physical token actor retains the native block and pickup lifecycle.
.setcpu "6502"

.segment "NATIVE_GATE"
StevePrepareBridge:
    sta InvPickup,x                  ; displaced stock publish
SteveCollectBridge:
    stx JnPickupSlot                  ; displaced stock collection prologue
    bit $730b                        ; Mike and Jay retain their native paths
    bvc StevePickupNativeReturn
    jsr $afed                        ; existing argument store and dual-header farcall
    lda InvPickup,x
StevePickupNativeReturn:
    rts

.segment "TOKEN_INGRESS"
SteveTokenDispatch:
    cpy #$e2
    bne SteveTokenOtherCaller
    cmp #$ff
    beq SteveTokenAttack
    cmp #$81
    bcc SteveTokenDraw
    cmp #$8e
    bcs SteveTokenDraw
    ; Two nested native farcalls keep the PRG98 JSR return 16 bytes above
    ; SP here. Accept its full address so an OAM offset cannot claim a token.
    tsx
    ldy $0111,x
    cpy #$a6
    beq SteveTokenPrepareSite
    cpy #$a7
    bne SteveTokenDraw
    ldy $0110,x
    cpy #$47
    bne SteveTokenDraw
    jmp SteveCollectToken
SteveTokenPrepareSite:
    ldy $0110,x
    cpy #$83
    bne SteveTokenDraw
    jmp StevePrepareToken
SteveTokenAttack:
    jsr SteveTokenEpoch
    jmp NativeAttack
SteveTokenDraw:
    jmp NativeDraw
SteveTokenOtherCaller:
    jmp NativeOther

StevePrepareToken:
    jsr SteveTokenPlayable
    bcc SteveTokenReturn
    ldx JnPickupSlot
    lda Enemy_ID,x
    cmp #$2e
    bne SteveTokenReturn
    lda SteveTokenStamp
    ora SteveTokenMasks,x
    sta SteveTokenStamp
    lda #$8c
    sta InvPickup,x
SteveTokenReturn:
    sec
    rts

SteveCollectToken:
    jsr SteveTokenPlayable
    bcc SteveTokenReturn
    ldx JnPickupSlot
    jsr SteveTokenOwned
    bcc SteveTokenReturn
    lda SteveTokenPending
    beq StevePreviewNew
    ; The host has a single ordinary power-up object. If another is earned
    ; before the first flight ends, finish the prior preview in slot order.
    sta SteveTokenPattern
    lda #0
    sta SteveTokenPending
StevePreviewNew:
    lda InvPickup,x
    and #1
    adc #0                          ; SteveTokenOwned left carry set.
    jsr SteveTokenPreview
    bcc SteveNoPreview
    sta SteveTokenPending
    ldx JnPickupSlot
    lda Enemy_X_Position,x
    sec
    sbc ScreenLeft_X_Pos
    clc
    adc #8
    sta SteveTokenFlightX
    lda Enemy_Y_Position,x
    clc
    adc #8
    sta SteveTokenFlightY
SteveNoPreview:
    ldx JnPickupSlot
    lda SteveTokenStamp
    eor SteveTokenMasks,x            ; this claim has already verified the bit
    sta SteveTokenStamp
    ; Zero skips Mike's heart, tier and weapon handlers. The native
    ; collector still owns object erasure and ordinary pickup feedback.
    lda #0
    sta InvPickup,x
    sec
    rts

SteveTokenOwned:
    ; X is the stock object slot. This leaf is called with raw2 authenticated.
    lda Enemy_Flag,x
    beq SteveTokenUnowned
    bmi SteveTokenUnowned
    lda Enemy_ID,x
    cmp #$2e
    bne SteveTokenUnowned
    lda InvPickupOwner,x
    cmp #16
    bne SteveTokenUnowned
    lda SteveTokenStamp
    and SteveTokenMasks,x
    beq SteveTokenUnowned
    lda InvPickup,x
    and #$fe
    cmp #$8c
    bne SteveTokenUnowned
    rts
SteveTokenUnowned:
    clc
    rts

StevePunchToken:
    ldx #5                          ; GetEmptySlot searches the same six slots
StevePunchSlot:
    jsr SteveTokenOwned
    bcc SteveNextToken
    lda Enemy_State,x
    bpl SteveNextToken
    lda SteveHitHigh
    cmp Enemy_Y_HighPos,x
    bne SteveNextToken
    cmp #1
    bne SteveNextToken
    lda Enemy_X_Position,x
    clc
    adc #22
    sta $03
    lda Enemy_PageLoc,x
    adc #0
    tay
    lda $03
    sec
    sbc SteveHitX
    sta $03
    tya
    sbc SteveHitPage
    bne SteveNextToken
    lda $03
    cmp #29
    bcs SteveNextToken
    lda Enemy_Y_Position,x
    clc
    adc #26
    bcs SteveNextToken
    sec
    sbc SteveHitY
    cmp #37
    bcs SteveNextToken
    lda InvPickup,x
    eor #1
    sta InvPickup,x
    lda #1
    sta SteveHitLife
    rts
SteveNextToken:
    dex
    bpl StevePunchSlot
    jmp NativeHitEnemy

SteveTokenMasks: .byte 1,2,4,8,16,32

; Project original $AA15's half-tile steps to the host's pixel coordinates.
; The original reaches the HUD height first, then snaps in its three-tile X band.
SteveTokenEpoch:
    lda SteveTokenPending
    beq SteveTokenEpochDone
    ; The authenticated attack caller already admitted ordinary engine 8.
    lda GamePauseStatus
    lsr a
    bcs SteveTokenEpochDone
    lda SteveTokenFlightY
    cmp #48
    bcc SteveTokenAcross
    sbc #8
    sta SteveTokenFlightY
    rts
SteveTokenAcross:
    lda #32
    sta SteveTokenFlightY
    lda SteveTokenFlightX
    cmp #112
    bcc SteveTokenFlightRight
    cmp #160
    bcs SteveTokenFlightLeft
    lda SteveTokenPending
    sta SteveTokenPattern
    lda #0
    sta SteveTokenPending
SteveTokenEpochDone:
    rts
SteveTokenFlightRight:
    adc #8
    bcc SteveSaveFlightX             ; admitted X < 112, so no wrap
SteveTokenFlightLeft:
    sbc #8
SteveSaveFlightX:
    sta SteveTokenFlightX
    rts

SteveTokenPlayable:
    lda OperMode
    cmp #1
    bne SteveTokenInactive
    lda OperMode_Task
    cmp #3
    bne SteveTokenInactive
    lda GameEngineSubroutine
    cmp #8
    beq SteveTokenEpochDone
SteveTokenInactive:
    clc
    rts
