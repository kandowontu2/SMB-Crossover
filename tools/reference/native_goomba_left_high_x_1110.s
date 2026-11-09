.setcpu "6502"
.segment "GOOMBA_SEAM"

EnemyX = $76
EnemyDirection = $053f
Native = $bf5a
Query = $bf5d

.org $bf45
GoombaSeamAdmission:
    lda EnemyDirection,x
    cmp #1
    beq Right
    cmp #2
    bne Native
    ; Left probes use X+8 and X, so both are on this page through X=$f7.
    lda #$f7
    bne Compare
Right:
    ; Right probes use X+8 and X+16 and still stop at X=$ef.
    lda #$ef
Compare:
    cmp EnemyX,x
    bcs Query
    ; Every other byte follows the genuine native fallback at $bf5a.
.assert *-GoombaSeamAdmission=$15,error,"Retain both existing continuation PCs"
.reloc
