; Source fragments for the existing Mini kernel. All public entries stay fixed.

; === pad
    ; A still holds MiniHeld after publishing MiniPrevious.
    lsr a
    and #1
    bcc :+
    ora #2
:
    sta buttons
    lda MiniHeld
    and #$40
    beq :+
    lda buttons
    ora #4
    sta buttons
:
    lda MiniHeld
    asl a
    lda #0
    rol a
    sta ybuttons
    lda MiniHeld
    and #8
    beq :+
    lda ybuttons
    ora #2
    sta ybuttons
:
    lda #0
    sta MiniContacts
    sta MiniHeadPending
    sta MiniFault

; === states
@unattached:
    lda MiniCurrent
    beq @fallinit
    cmp #3
    beq @groundinit
    cmp #6
    beq @crouchinit
    cmp #9
    beq @skidinit
    cmp #12
    bne @dispatch
    lda #13
    sta queued
    lda #1
    sta hold
    lda #0
    sta attached
    sta yvel
    sta yvel+1
    sta MiniBuffer
    sta MiniCoyote
    sta MiniCrouched
    beq @dispatch
@fallinit:
    lda #1
    sta queued
    lda #0
    sta MiniCrouched
    beq @dispatch
@groundinit:
    lda #4
    sta queued
    lda #2
    sta MiniCoyote
    lda #0
    sta bounce
    sta MiniCrouched
    beq @dispatch
@crouchinit:
    lda #7
    sta queued
    lda #1
    sta MiniTop
    sta MiniCrouched
    bne @dispatch
@skidinit:
    lda #10
    sta queued
@dispatch:

; === step_pad
    .res $188-(*-MiniStep),$ea ; Preserve MiniCrouchInput and all later entries.

; === aligned
MiniAddAligned:
    ldx #0
    cmp #$80
    bcc :+
    dex
:
    clc
    adc MiniCoord
    and #$f8                 ; AND preserves the low-byte addition carry.
    sta MiniCoord
    txa
    adc MiniCoord+1
    sta MiniCoord+1
    lda MiniCoord            ; Original A/NZ and high-byte C/V.
    rts
    .res $22-(*-MiniAddAligned),$ea

; === tile
MiniNativeTile:
    lda MiniQueryY+1
    bne Tile_Invalid
    lda MiniQueryY
    cmp #32
    bcc Tile_Invalid
    cmp #240
    bcs Tile_Invalid
    txa
    pha
    lda #0
    sta MiniQueryKind
    lda MiniQueryX
    lsr a
    lsr a
    lsr a
    lsr a
    sta MiniQueryColumn
    lda MiniQueryY
    and #$f0
    sec
    sbc #32
    ora MiniQueryColumn
    tax                      ; The same X indexes both buffer and attributes.
    lda MiniQueryX+1
    lsr a
    bcs Tile_Buffer2
    stx MiniQueryAddress
    lda #>Block_Buffer_1
    sta MiniQueryAddress+1
    lda Block_Buffer_1,x
    jmp Tile_Classify
Tile_Buffer2:
    txa
    clc
    adc #<Block_Buffer_2
    sta MiniQueryAddress
    lda #>Block_Buffer_2
    adc #0
    sta MiniQueryAddress+1
    lda Block_Buffer_2,x
Tile_Classify:
    sta MiniQueryTile
    tax
    lda MiniTileAttributes,x
    lsr a
    lsr a
    sta MiniQueryFlags
    cmp #16
    bne Tile_Restore
    lda #151
    sta MiniQueryKind
Tile_Restore:
    pla
    tax
    lda MiniQueryFlags
    cmp #15
    beq Tile_Return
    clc
Tile_Return:
    rts
    .res $7b-(*-MiniNativeTile),$ea
