.setcpu "6502"
.export GiantResidentEntry, GiantResidentLegacy, GiantRogueRead, GiantRogueMux, GiantHostAdapter
.export GiantRogueMapRead, GiantRogueUpper, GiantRogueDirect

.segment "GIANT_ADAPTER"

; Same source classifications as the c8 compound dispatcher. All existing
; entries reach this via FarCallCommon, which has already loaded the saved
; A from $016a. No instruction in this classifier modifies that byte.
GiantHostAdapter:
    php
    pha
    lda SelectedCharacter
    beq Mario
    cmp #$02
    beq ExistingOwner
    cmp #$1a
    beq ExistingOwner
    cmp #$1c
    beq ExistingOwner
    cmp #$20
    beq ExistingOwner
    cmp #$09
    bne Stock
    lda $5fe5
    and #$20
    beq Stock
ExistingOwner:
    lda #$bf
SetTag:
    sta $0162
    pla
    plp
    lda #$44
    sta $016c
    lda #$b7
    sta $016d
    pla
    pla
    jmp $0161
Mario:
    lda MarioVariant
    cmp #2
    beq ExistingOwner
    cmp #9
    bne Stock
    lda #$da
    bne SetTag
Stock:
    pla
    plp
    jmp $bff8

.segment "GIANT_RESIDENT"

; This PRG90 leaf shares the existing PRG63 entry PC. Only variant 9
; takes the former path through the unchanged bank1 farcall packet.
GiantResidentEntry:
    php
    pha
    jmp GiantMarioRoute
GiantResidentLegacy:
    pla
    plp
    lda #$f8
    sta $016c
    lda #$bf
    sta $016d
    lda #$dd
    sta $0162
    ; Discard the existing SMC JSR return. The original map remains on
    ; its stack frame and the native tail restores it after the old call.
    pla
    pla
    jmp $0161

.segment "GIANT_AUDIO_VIEW"

; Only the original mapped Rogue DA view enters here. This preserves the
; byte-complete source audio image while making three source-zero intervals
; available to the selected Mario worker in a different owner context.
GiantRogueRead:
    php
    lda $e9
    cmp #$b0
    beq ZeroB0
    cmp #$b1
    beq ZeroB1
    cmp #$b7
    beq ZeroB7
    cmp #$b8
    beq ZeroB8
    cmp #$bc
    bne Original
    lda #$3f
    bne CheckAfter
ZeroB0:
    lda #$9d
    bne CheckAfter
ZeroB7:
    lda #$04
CheckAfter:
    cmp $e8
    bcc ReturnZero
    bcs Original
ZeroB1:
    lda #$7f
    bne CheckBefore
ZeroB8:
    lda #$8f
CheckBefore:
    cmp $e8
    bcs ReturnZero
Original:
    plp
    lda ($e8),y
    rts
ReturnZero:
    plp
    lda #0
    rts

.segment "GIANT_AUDIO_MAP"

; All ordinary table tags have bit 7 set. Only the five exact Rogue
; lower rows intersecting repurposed storage have the private tag $5a.
GiantRogueMapRead:
    .byte $10,$c469-$c42e       ; BPL into the separate fixed-address mux
GiantRogueDirect:
    sta $0145
    sta $5115
    ldy #0
    lda ($e8),y
GiantRogueStore:
    sta $7051
    lda #$be
    sta $0145
    sta $5115
    rts
GiantRogueUpper:
    ; The sole caller branches here with C set from CMP #$a0. Valid
    ; upper source pages retain C through the table loads into MapRead.
    sbc #$a0
    tax
    lda $be5f,x
    sta $e9
    lda $be3f,x
    bcs GiantRogueMapRead

.segment "GIANT_AUDIO_MUX"

; Never map the private tag as RAM. The driver and ISR see exactly the
; original physical $da window and its existing $be restoration.
GiantRogueMux:
    .assert GiantRogueMapRead=$c42c .and GiantRogueMux=$c469,lderror,"Rogue read branch moved"
    lda #$da
    sta $0145
    sta $5115
    ldy #0
    jsr GiantRogueRead
    jmp GiantRogueStore
