; Replacement for the native narrow enemy-box query only. Source shot bounds,
; phase, world-page prefilter, victim exclusions and native damage remain owned
; by shinobi_native_combat_1101_v1.inc. No original shot coordinates are moved.
; NativeEnemyBounds in megaman_weapons.s uses this same full visible16x16 box.
; ObjectOffset is set only on a hit; HandleEnemyFBallCol computes relative
; position itself. The removed offscreen query existed for GetEnemyBoundBox.
 lda Enemy_Y_HighPos,x
 cmp #1
 jne ShShotNext
 lda Enemy_Y_Position,x
 cmp #232
 jcs ShShotNext             ; avoid a wrapped Y+24 rectangle near bottom
 ; Two disposable native weapon boxes28..35 are saved before construction.
 ; Never widen the real enemy box used by later native body collision.
 ldy #7
ShSaveContactBoxes:
 lda BoundingBox_UL_Corner+28,y
 sta ShContactBox,y
 dey
 bpl ShSaveContactBoxes
 ldy #32
 lda Enemy_X_Position,x
 sec
 sbc ScreenLeft_X_Pos
 sta BoundingBox_UL_Corner,y
 clc
 adc #16
 sta BoundingBox_LR_Corner,y
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta BoundingBox_UL_Corner+1,y
 clc
 adc #16
 sta BoundingBox_LR_Corner+1,y
 tya
 tax
