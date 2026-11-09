.setcpu "6502"
.segment "GOOMBA_SEAM"

EnemyX=$76
EnemyDirection=$053f
Native=$bf5a
Query=$bf5d

.org $bf45
SeamAdmission:
    ; The existing low-nibble arithmetic works from X=0 as well. Only
    ; X>=240 could put X+16 on a different block-buffer page.
    lda EnemyX,x
    cmp #$f0
    bcs Native
    lda EnemyDirection,x
    cmp #1
    beq Query
    cmp #2
    beq Query
    bne Native
.assert *-SeamAdmission <= $15,error,"Existing native fallback stays fixed"
.res $15-(*-SeamAdmission),$ea
