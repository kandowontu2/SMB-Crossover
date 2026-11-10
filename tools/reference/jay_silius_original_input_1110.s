; Journey to Silius (USA), physical 16 KiB PRG bank 6, $8093..<$81D2.
; Initial control update from the real $8048 JSR. The following two
; donor helpers are kept external. The parity test invokes both real helpers.
; $14/$15 are signed horizontal/vertical velocity in sixteenths of a pixel.
; $0162 holds native buttons and $0163 holds the previous sample.
; $19/$1C are actor state and animation/control bits. $51 owns the jump hold.
.setcpu "6502"
OriginalWeaponInput = $81d2
OriginalFreshButtons = $c86e
.segment "INPUT"
JayOriginalInput:
 jsr JumpInput
 jsr OriginalWeaponInput
 lda $0162
 and #$0f
 beq NeutralDirection
 and #$04
 beq OrdinaryDirection
 lda $19
 and #$04
 bne OrdinaryDirection
 jmp CrouchInput
OrdinaryDirection:
 lda $19
 and #$08
 bne NeutralDirection
 lda $1c
 and #$38
 bne LockedHorizontal
 lda $0162
 and #$03
 cmp #$01
 beq RightInput
 cmp #$02
 bne InputDone
 lda $19
 and #$02
 bne L80E6
 lda $051c
 bne L80E6
 lda #$04
 sta $051c
 lda $1c
 ora #$08
 sta $1c
 lda $19
 and #$04
 bne L80E6
 lda #$00
 beq StoreHorizontalVelocity
L80E6:
 lda $14
 cmp #$e8
 bcs L80F4
 cmp #$40
 bcc L80F4
 lda #$ea
 bne StoreHorizontalVelocity
L80F4:
 lda $19
 and #$04
 bne L80FE
 lda #$fc
 bne ApplyHorizontalDelta
L80FE:
 lda #$ff
ApplyHorizontalDelta:
 clc
 adc $14
StoreHorizontalVelocity:
 sta $14
InputDone:
 rts
LockedHorizontal:
 lda $19
 and #$04
 bne L8110
 lda #$00
 sta $14
L8110:
 rts
NeutralDirection:
 lda $19
 and #$04
 bne InputDone
 lda $19
 and #$08
 beq StopHorizontal
 lda $1c
 and #$38
 bne StopHorizontal
 lda #$04
 sta $051c
 lda $1c
 ora #$10
 sta $1c
StopHorizontal:
 lda #$00
 beq StoreHorizontalVelocity
RightInput:
 lda $19
 and #$02
 beq L8152
 lda $051c
 bne L8152
 lda #$04
 sta $051c
 lda $1c
 ora #$08
 sta $1c
 lda $19
 and #$04
 bne L8152
 lda #$00
 beq StoreHorizontalVelocity
L8152:
 lda $14
 cmp #$18
 bcs L8166
L8158:
 lda $19
 and #$04
 bne L8162
 lda #$04
 bne ApplyHorizontalDelta
L8162:
 lda #$01
 bne ApplyHorizontalDelta
L8166:
 cmp #$c0
 bcs L8158
 lda #$16
 bne StoreHorizontalVelocity
CrouchInput:
 lda $19
 and #$08
 bne L8185
 lda $1c
 and #$38
 bne L8185
 lda $1c
 ora #$10
 sta $1c
 lda #$04
 sta $051c
L8185:
 lda #$00
 sta $14
 rts
JumpInput:
 lda $19
 and #$04
 beq L81A6
 lda $51
 bpl JumpDone
 lda $0162
 bpl ReleaseJump
 lda $51
 and #$7f
 cmp #$0b
 beq JumpDone
 inc $51
 jmp ApplyJumpVelocity
L81A6:
 lda $1c
 and #$38
 bne JumpDone
 jsr OriginalFreshButtons
 and #$80
 beq JumpDone
 lda #$10
 sta $017a
 lda $1c
 and #$01
 beq L81C4
 lda $1c
 and #$fe
 sta $1c
L81C4:
 lda #$80
 sta $51
ApplyJumpVelocity:
 lda #$cc
 sta $15
JumpDone:
 rts
ReleaseJump:
 lda #$00
 sta $51
 rts
