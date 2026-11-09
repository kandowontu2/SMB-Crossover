.setcpu "6502"

; CHR967 contains the sprite frames and these cold-only source packets.
; Copy the small workers into Mini's authenticated C2/A3 pair before
; rebuilding the exact runtime metatile table over the CHR staging bytes.
.import __RESTORE_LOAD__, __RESTORE_RUN__, __RESTORE_SIZE__
.import __PHASE_LOAD__, __PHASE_RUN__, __PHASE_SIZE__
.export MiniFireballArtBoot, MiniFireballPose

.segment "ART_BOOT"
MiniFireballArtBoot:
 ldx #.lobyte(__PHASE_SIZE__-1)
@phase:
 lda __PHASE_LOAD__,x
 sta __PHASE_RUN__,x
 dex
 bpl @phase
 ldx #.lobyte(__RESTORE_SIZE__-1)
@restore:
 lda __RESTORE_LOAD__,x
 sta __RESTORE_RUN__,x
 dex
 bpl @restore
 jmp __RESTORE_RUN__

.segment "RESTORE"
 ldx #0
@attribute:
 lda $ef36,x                ; Native resident MTileAttribute.
 and #3
 cpx #$c2
 beq @store
 cpx #$c3
 beq @store
 cmp #1
 bne @vine
 ora #$3c
 bne @store
@vine:
 cpx #$26
 bne @store
 ora #$40
@store:
 sta $d300,x                ; The identical pre-art Mini runtime table.
 inx
 bne @attribute
 sec
 rts

.segment "PHASE"
; X is the physical OAM slot. Y is the live Mini fireball slot.
; Called only after clipping, sprite capacity and rotation are decided.
MiniFireballPose:
 lda $25,y
 cmp #1
 bne @impact
 lda $c324,y
 and #3
 lsr a                      ; Carry selects the second moving source tile.
 pha                         ; A=1 for the donor's H+V phases.
 lda #$6f
 bcc @tile
 lda #$7f
@tile:
 sta $0201,x
 pla
 beq @normal
 lda #$c2
 sta $0202,x
 lda $c4,y
 sec
 sbc #7                     ; Compensate for the 8x16 vertical flip.
 sta $0200,x
 rts
@impact:
 and #2
 beq @impactA
 lda #$7d
 bne @impactTile
@impactA:
 lda #$7b
@impactTile:
 sta $0201,x
@normal:
 lda #2
 sta $0202,x
 lda $c4,y
 clc
 adc #1
 sta $0200,x
 rts
