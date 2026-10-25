.pushseg
.segment "Z2_COLD"
.proc Z2NativeSmallPlatformCollision
      lda TimerControl             ;if master timer control set,
      bne ExSPC                    ;branch to leave
      sta PlatformCollisionFlag,x  ;otherwise initialize collision flag
      jsr CheckPlayerVertical      ;do a sub to see if player is below a certain point
      bcs ExSPC                    ;or entirely offscreen, and branch to leave if true
      lda #$02
      sta R0                       ;load counter here for 2 bounding boxes

ChkSmallPlatLoop:
      ldx ObjectOffset           ;get enemy object offset
      jsr GetEnemyBoundBoxOfs    ;get bounding box offset in Y
      and #%00000010             ;if d1 of offscreen lower nybble bits was set
      bne ExSPC                  ;then branch to leave
      lda BoundingBox_UL_YPos,y  ;check top of platform's bounding box for being
      cmp #$20                   ;above a specific point
      bcc MoveBoundBox           ;if so, branch, don't do collision detection
      jsr PlayerCollisionCore    ;otherwise, perform player-to-platform collision detection
      jcs ProcSPlatCollisions    ;skip ahead if collision

MoveBoundBox:
       lda BoundingBox_UL_YPos,y  ;move bounding box vertical coordinates
.if ::ENABLE_CROSSOVER
       farcall CrossoverLiftSecondY
.else
       clc                        ;128 pixels downwards
       adc #$80
.endif
       sta BoundingBox_UL_YPos,y
       lda BoundingBox_DR_YPos,y
.if ::ENABLE_CROSSOVER
       farcall CrossoverLiftSecondY
.else
       clc
       adc #$80
.endif
       sta BoundingBox_DR_YPos,y
       dec R0                     ;decrement counter we set earlier
       bne ChkSmallPlatLoop       ;loop back until both bounding boxes are checked
ExSPC: ldx ObjectOffset           ;get enemy object buffer offset, then leave
       rts
.endproc
.popseg
