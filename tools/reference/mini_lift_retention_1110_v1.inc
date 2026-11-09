; Existing authenticated Mini lift allocator. Camera page is the native
; constructor's world page. Every live actor retains its own native slot.
.segment "CODE"
.export MiniLiftAllocate
MiniLiftAllocate:
    ldx #5
@scan:
    lda $10,x
    beq @construct
    dex
    bpl @scan
    sec
    rts
@construct:
    ldy $071e
    jmp $bfe3

; This branch is inserted in the owned Mini kernel by its packing recipe.
; C30B still means at least one helper was constructed this life.
; C30D remains one-based, and names the lift actually under Mini's feet.
