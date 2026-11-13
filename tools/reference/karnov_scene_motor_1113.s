; Existing 12-byte KrConstruct facing publication, A3/B0D4..B0DF.
; Native PlayerFacingDir is the direction mask right1/left2. Every same-life
; scene must publish a fresh original stand selector after clearing the old
; action timer, regardless of the previous source actor selector.
.segment "SCENE_FACING"
KrSceneMotorFacing:
 lda PlayerFacingDir
 and #2
 beq KrSceneMotorWrite
 lda #$80
KrSceneMotorWrite:
 sta KrState62

