; Source port of Mini PlatformerPlus ground/fall/crouch/jump bodies.
; Private proposed ABI only. Original tile_x is extended to 16 bits for SMB.
; Motion prefix supplies ground_x/air_x/air_y and C200..C230 symbols.
.export MiniStep, MiniInit, MiniWorldEnd
MiniCurrent = $C240
MiniCoyote = $C241
MiniBuffer = $C242
MiniCrouched = $C243
MiniTier = $C244
MiniFacing = $C245
MiniClass = $C246
MiniFault = $C247
MiniHeld = $C248
MiniPrevious = $C249
MiniFresh = $C24A
MiniFamily = $C24B
MiniContacts = $C24C
MiniAnimation = $C24D
MiniMoving = $C24E
MiniX = $C250
MiniY = $C252
MiniLeft = $C254
MiniRight = $C255
MiniTop = $C256
MiniBottom = $C257
MiniEdgeLeft = $C258
MiniEdgeRight = $C25A
MiniHeadPending = $C25C
MiniHeadX = $C25D
MiniHeadY = $C25F
MiniHeadTile = $C261
MiniHeadAddress = $C262
MiniUpCacheX = $C264
MiniUpCacheY = $C266
MiniTemp = $C270
MiniCoord = $C272
MiniScanX = $C274
MiniScanY = $C276
MiniEnd = $C278
MiniBound = $C27A
MiniMask = $C27B
MiniNegative = $C27C
MiniAxis = $C27D
MiniSaved = $C27E
MiniLastWall = $C280

; Init clears only the source motion/world storage. Root supplies position,
; bounds and viewport edges after Init, before the first Step.
MiniInit:
    lda #0
    ldx #$80
@clear:
    sta $C200,x
    dex
    bpl @clear
    lda #$02
    sta holdgrav+1
    lda #$0F
    sta yvel+1
    lda #$A0
    sta yvel
    lda #1
    sta MiniFacing
    lda #$F0
    sta MiniEdgeRight
    lda #$FF
    sta MiniEdgeRight+1
    rts

MiniStep:
    ; Native NES bits A80 B40 Down04 Up08 Left02 Right01.
    lda MiniPrevious
    eor #$FF
    and MiniHeld
    sta MiniFresh
    lda MiniHeld
    sta MiniPrevious
    lda #0
    sta buttons
    sta ybuttons
    sta MiniContacts
    sta MiniHeadPending
    sta MiniFault
    lda MiniHeld
    and #2
    lsr a
    sta buttons
    lda MiniHeld
    and #1
    asl a
    ora buttons
    sta buttons
    lda MiniHeld
    and #$40
    beq @norun
    lda buttons
    ora #4
    sta buttons
@norun:
    lda MiniHeld
    and #$80
    beq @nob
    inc ybuttons
@nob:
    lda MiniHeld
    and #8
    beq @noup
    lda ybuttons
    ora #2
    sta ybuttons
@noup:
    lda #7
    sta anim
    lda queued
    sta MiniCurrent
    cmp #15
    bcc @normal
    ; Extended climb/swim/blank bodies are not admitted by this first slice.
    lda #1
    sta MiniFault
    rts
@normal:
    lda attached
    beq @unattached
    lda #2
    sta MiniFault
    rts
@unattached:
    lda MiniCurrent
    cmp #0
    bne @notfallinit
    lda #1
    sta queued
    lda #0
    sta MiniCrouched
@notfallinit:
    lda MiniCurrent
    cmp #3
    bne @notgroundinit
    lda #4
    sta queued
    lda #2
    sta MiniCoyote
    lda #0
    sta bounce
    sta MiniCrouched
@notgroundinit:
    lda MiniCurrent
    cmp #6
    bne @notcrouchinit
    lda #7
    sta queued
    lda #1
    sta MiniTop
    sta MiniCrouched
@notcrouchinit:
    lda MiniCurrent
    cmp #9
    bne @notskidinit
    lda #10
    sta queued
@notskidinit:
    lda MiniCurrent
    cmp #12
    bne @notjumpinit
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
@notjumpinit:
    lda MiniCurrent
    cmp #2
    beq @end
    cmp #5
    beq @end
    cmp #8
    beq @end
    cmp #11
    beq @end
    cmp #14
    beq @end
    cmp #6
    beq @crouch
    cmp #7
    beq @crouch
    cmp #3
    beq @ground
    cmp #4
    beq @ground
    cmp #9
    beq @ground
    cmp #10
    beq @ground
    lda #0
    sta MiniFamily
    lda MiniCurrent
    cmp #12
    bcc @air
    lda #1
    sta MiniFamily
@air:
    jsr MiniCrouchInput
    lda MiniFamily
    sta ymode
    jsr air_y
    jsr air_x
    jmp MiniCollisions
@ground:
    lda #2
    sta MiniFamily
    jsr MiniCrouchInput
    jsr MiniGroundGravity
    jsr ground_x
    jmp MiniCollisions
@crouch:
    lda #3
    sta MiniFamily
    jsr MiniGroundGravity
    ; Original crouch deceleration plat_dec >> 1 = 128.
    lda vel+1
    bmi @cnegative
    ora vel
    beq @cintegrate
    sec
    lda vel
    sbc #128
    sta vel
    lda vel+1
    sbc #0
    sta vel+1
    bpl @cintegrate
    jmp @czero
@cnegative:
    clc
    lda vel
    adc #128
    sta vel
    lda vel+1
    adc #0
    sta vel+1
    bmi @cintegrate
@czero:
    lda #0
    sta vel
    sta vel+1
@cintegrate:
    lda #0
    sta stage
    lda vel+1
    jsr MiniAddDeltaX
    jmp MiniCollisions
@end:
    rts

MiniCrouchInput:
    lda MiniHeld
    and #4
    beq @up
    lda MiniCrouched
    bne @done
    lda #1
    sta MiniTop
    sta MiniCrouched
    rts
@up:
    lda MiniCrouched
    beq @done
    lda MiniTier
    beq @small
    lda #$F9
    sta MiniTop
@small:
    lda #0
    sta MiniCrouched
@done:
    rts

MiniGroundGravity:
    lda nocollide
    beq @normal
    lda #<$1B58
    sta yvel
    lda #>$1B58
    sta yvel+1
    jmp @integrate
@normal:
    clc
    lda yvel+1
    adc #8
    sta yvel+1
    lda #0
    sta queued
@integrate:
    lda yvel+1
    ldx #0
    cmp #$80
    bcc @positive
    dex
@positive:
    clc
    adc ydelta
    sta ydelta
    txa
    adc ydelta+1
    sta ydelta+1
    rts

MiniAddDeltaX:
    ldx #0
    cmp #$80
    bcc @positive
    dex
@positive:
    clc
    adc delta
    sta delta
    txa
    adc delta+1
    sta delta+1
    rts

MiniCollisions:
    lda #0
    sta MiniAxis
    jsr MiniClampDeltaX
    clc
    lda MiniX
    adc delta
    sta MiniTemp
    lda MiniX+1
    adc delta+1
    sta MiniTemp+1
    jsr MiniEdges
    lda MiniFamily
    cmp #1
    beq @right
    lda MiniTemp+1
    cmp MiniX+1
    bne @xdirection
    lda MiniTemp
    cmp MiniX
    beq @xfinished
@xdirection:
    bcs @right
    lda #1
    sta MiniNegative
    lda #8
    sta MiniMask
    lda MiniLeft
    jmp @xbound
@right:
    lda #0
    sta MiniNegative
    lda #4
    sta MiniMask
    lda MiniRight
@xbound:
    sta MiniBound
    jsr MiniTempPixel
    jsr MiniAddBound
    jsr MiniAlign
    lda MiniCoord
    sta MiniScanX
    lda MiniCoord+1
    sta MiniScanX+1
    lda MiniY
    sta MiniCoord
    lda MiniY+1
    sta MiniCoord+1
    jsr MiniToPixel
    lda MiniBottom
    jsr MiniAddSigned
    jsr MiniAlign
    lda MiniCoord
    sta MiniEnd
    lda MiniCoord+1
    sta MiniEnd+1
    lda MiniY
    sta MiniCoord
    lda MiniY+1
    sta MiniCoord+1
    jsr MiniToPixel
    lda MiniTop
    jsr MiniAddSigned
    jsr MiniAlign
    lda MiniCoord
    sta MiniScanY
    lda MiniCoord+1
    sta MiniScanY+1
@xloop:
    jsr MiniQuery
    and MiniMask
    bne @xhit
    lda MiniScanY+1
    cmp MiniEnd+1
    bne @xnext
    lda MiniScanY
    cmp MiniEnd
    beq @xfinished
@xnext:
    clc
    lda MiniScanY
    adc #8
    sta MiniScanY
    bcc @xloop
    inc MiniScanY+1
    jmp @xloop
@xhit:
    lda MiniScanX
    sta MiniCoord
    lda MiniScanX+1
    sta MiniCoord+1
    jsr MiniSnap
    lda #0
    sta vel
    sta vel+1
    lda MiniNegative
    beq @rwall
    lda #$FF
    sta MiniLastWall
    lda #4
    bne @wall
@rwall:
    lda #1
    sta MiniLastWall
    lda #8
@wall:
    ora MiniContacts
    sta MiniContacts
@xfinished:
    ; Original jump_state scans right then left even with zero/left motion.
    lda MiniFamily
    cmp #1
    bne @xcommit
    lda MiniAxis
    bne @xcommit
    lda #2
    sta MiniAxis
    lda #1
    sta MiniNegative
    lda #8
    sta MiniMask
    lda MiniLeft
    jmp @xbound
@xcommit:
    lda MiniTemp
    sta MiniX
    lda MiniTemp+1
    sta MiniX+1
    ; Source actor-collision stage clears both accumulated deltas after Y.
    lda #1
    sta MiniAxis
    jsr MiniClampDeltaY
    clc
    lda MiniY
    adc ydelta
    sta MiniTemp
    lda MiniY+1
    adc ydelta+1
    sta MiniTemp+1
    lda ydelta
    ora ydelta+1
    bne @ymoving
    jmp MiniFinish
@ymoving:
    lda ydelta+1
    bmi @up
    lda #0
    sta MiniNegative
    lda #1
    sta MiniMask
    lda MiniBottom
    sta MiniBound
    jmp @yscan
@up:
    lda #1
    sta MiniNegative
    lda #2
    sta MiniMask
    lda MiniTop
    sta MiniBound
@yscan:
    jsr MiniTempPixel
    jsr MiniAddBound
    jsr MiniAlign
    lda MiniCoord
    sta MiniScanY
    lda MiniCoord+1
    sta MiniScanY+1
    lda MiniX
    sta MiniCoord
    lda MiniX+1
    sta MiniCoord+1
    jsr MiniToPixel
    ; Ground's original running probes extend the opposite side by 3 pixels.
    lda MiniRight
    sta MiniSaved
    lda MiniFamily
    cmp #2
    bne @rightbound
    lda vel+1
    bpl @rightbound
    cmp #$F1
    bcc @extendright
    bne @rightbound
    lda vel
    cmp #$AF
    bcs @rightbound
@extendright:
    clc
    lda MiniSaved
    adc #3
    sta MiniSaved
@rightbound:
    lda MiniSaved
    jsr MiniAddSigned
    jsr MiniAlign
    lda MiniCoord
    sta MiniEnd
    lda MiniCoord+1
    sta MiniEnd+1
    lda MiniX
    sta MiniCoord
    lda MiniX+1
    sta MiniCoord+1
    jsr MiniToPixel
    lda MiniLeft
    sta MiniSaved
    lda MiniFamily
    cmp #2
    bne @leftbound
    lda vel+1
    cmp #$0E
    bcc @leftbound
    bne @extendleft
    lda vel
    cmp #$52
    bcc @leftbound
@extendleft:
    sec
    lda MiniSaved
    sbc #3
    sta MiniSaved
@leftbound:
    lda MiniSaved
    jsr MiniAddSigned
    jsr MiniAlign
    lda MiniCoord
    sta MiniScanX
    lda MiniCoord+1
    sta MiniScanX+1
    ; Jump ascent checks only the head center, unlike fall/ground/crouch.
    lda MiniFamily
    cmp #1
    bne @yloop
    lda MiniNegative
    beq @yloop
    clc
    lda MiniLeft
    adc MiniRight
    cmp #$80
    ror a
    sta MiniSaved
    lda MiniX
    sta MiniCoord
    lda MiniX+1
    sta MiniCoord+1
    jsr MiniToPixel
    lda MiniSaved
    jsr MiniAddSigned
    jsr MiniAlign
    lda MiniCoord
    sta MiniScanX
    sta MiniEnd
    lda MiniCoord+1
    sta MiniScanX+1
    sta MiniEnd+1
@yloop:
    lda MiniNegative
    bne @yquery
    lda nocollide
    beq @yquery
    jmp @yfinished
@yquery:
    jsr MiniQuery
    and MiniMask
    bne @yhit
    lda MiniScanX+1
    cmp MiniEnd+1
    bne @ynext
    lda MiniScanX
    cmp MiniEnd
    beq @yfinished
@ynext:
    clc
    lda MiniScanX
    adc #8
    sta MiniScanX
    bcc @yloop
    inc MiniScanX+1
    jmp @yloop
@yhit:
    lda MiniScanY
    sta MiniCoord
    lda MiniScanY+1
    sta MiniCoord+1
    jsr MiniSnap
    lda MiniNegative
    bne @headhit
    lda #0
    sta attached
    lda MiniContacts
    ora #1
    sta MiniContacts
    lda MiniFamily
    cmp #3
    beq @crouchland
    lda MiniCurrent
    cmp #4
    beq @landvelocity
    cmp #3
    beq @groundland
    lda #3
    bne @landstate
@groundland:
    lda #4
    bne @landstate
@landvelocity:
    lda #0
    sta yvel
    lda MiniFamily
    cmp #0
    beq @zerovelocity
    lda #1
@zerovelocity:
    sta yvel+1
    lda #4
    bne @landstate
@crouchland:
    lda MiniCurrent
    cmp #7
    bne @crouchinitland
    lda #0
    sta yvel
    lda #1
    sta yvel+1
    lda #7
    bne @landstate
@crouchinitland:
    cmp #6
    beq @crouchstay
    lda #6
    bne @landstate
@crouchstay:
    lda #7
@landstate:
    sta queued
    jmp @yfinished
@headhit:
    lda #0
    sta yvel
    sta yvel+1
    sta MiniCoyote
    sta queued
    sta attached
    lda MiniContacts
    ora #2
    sta MiniContacts
    jsr MiniHeadEvent
@yfinished:
    lda MiniTemp
    sta MiniY
    lda MiniTemp+1
    sta MiniY+1
    lda MiniNegative
    bne MiniFinish
    lda #0
    sta MiniUpCacheX
    sta MiniUpCacheX+1
    sta MiniUpCacheY
    sta MiniUpCacheY+1
MiniFinish:
    lda #0
    sta delta
    sta delta+1
    sta ydelta
    sta ydelta+1
    sta MiniMoving
    lda MiniFamily
    sta MiniClass
    cmp #2
    beq MiniGroundFinish
    cmp #3
    beq MiniCrouchFinish
    ; Air turning is disabled by the source default, so facing is latched.
    lda MiniFacing
    cmp #3
    beq @airleft
    lda #2
    bne @airanim
@airleft:
    lda #0
@airanim:
    sta MiniAnimation
    lda MiniFamily
    bne @jumpfinish
    lda MiniFresh
    and #$80
    beq @fallend
    lda MiniCoyote
    beq @buffer
    lda #12
    sta queued
    bne @fallend
@buffer:
    lda #2
    sta MiniBuffer
@fallend:
    lda queued
    cmp #1
    beq @fallcounter
    lda #2
    sta MiniCurrent
@fallcounter:
    lda MiniBuffer
    beq @ct
    dec MiniBuffer
@ct:
    lda MiniCoyote
    beq MiniNoCollideCounter
    lda queued
    cmp #4
    beq MiniNoCollideCounter
    dec MiniCoyote
    jmp MiniNoCollideCounter
@jumpfinish:
    lda queued
    cmp #13
    beq @jumpdone
    lda #14
    sta MiniCurrent
@jumpdone:
    rts

MiniGroundFinish:
    jsr MiniGroundDirection
    lda MiniFresh
    and #$80
    ora MiniBuffer
    beq @nojump
    lda nocollide
    bne @nojump
    lda #12
    sta queued
@nojump:
    lda #0
    sta MiniBuffer
    lda MiniHeld
    and #4
    beq @notdown
    lda #6
    sta queued
@notdown:
    lda MiniCurrent
    cmp #9
    bcs @skidend
    lda queued
    cmp #4
    beq MiniNoCollideCounter
    lda #5
    sta MiniCurrent
    bne MiniNoCollideCounter
@skidend:
    lda queued
    cmp #10
    beq MiniNoCollideCounter
    lda #11
    sta MiniCurrent
    bne MiniNoCollideCounter
MiniCrouchFinish:
    jsr MiniGroundDirection
    lda #0
    sta MiniMoving
    lda MiniFresh
    and #$80
    ora MiniBuffer
    beq @nojump
    lda nocollide
    bne @nojump
    lda #12
    sta queued
@nojump:
    lda #0
    sta MiniBuffer
    lda MiniHeld
    and #4
    bne @down
    lda #3
    sta queued
@down:
    lda queued
    cmp #7
    beq MiniNoCollideCounter
    lda MiniTier
    beq @small
    lda #$F9
    sta MiniTop
@small:
    lda #0
    sta MiniCrouched
    lda #8
    sta MiniCurrent
MiniNoCollideCounter:
    lda nocollide
    beq @done
    dec nocollide
@done:
    rts

MiniGroundDirection:
    lda buttons
    and #1
    beq @notleft
    lda #3
    sta MiniFacing
    lda MiniFamily
    cmp #3
    beq @idle
    lda vel+1
    bmi @matching
    ora vel
    beq @matching
    lda #9
    sta queued
    bne @moving
@matching:
    lda MiniCurrent
    cmp #10
    bne @moving
    lda #3
    sta queued
    bne @moving
@notleft:
    lda buttons
    and #2
    beq @velocity
    lda #1
    sta MiniFacing
    lda MiniFamily
    cmp #3
    beq @idle
    lda vel+1
    bpl @matching
    lda #9
    sta queued
    bne @moving
@velocity:
    lda MiniFamily
    cmp #3
    beq @idle
    lda vel+1
    bmi @left
    ora vel
    beq @idle
    lda #1
    bne @face
@left:
    lda #3
@face:
    sta MiniFacing
@moving:
    lda #1
    sta MiniMoving
@idle:
    rts

MiniQuery:
    lda MiniScanX
    sta MiniQueryX
    lda MiniScanX+1
    sta MiniQueryX+1
    lda MiniScanY
    sta MiniQueryY
    lda MiniScanY+1
    sta MiniQueryY+1
    jmp MiniNativeTile

MiniHeadEvent:
    lda MiniScanX
    cmp MiniUpCacheX
    bne @new
    lda MiniScanX+1
    cmp MiniUpCacheX+1
    bne @new
    lda MiniScanY
    cmp MiniUpCacheY
    bne @new
    lda MiniScanY+1
    cmp MiniUpCacheY+1
    beq @done
@new:
    lda MiniScanX
    sta MiniUpCacheX
    sta MiniHeadX
    lda MiniScanX+1
    sta MiniUpCacheX+1
    sta MiniHeadX+1
    lda MiniScanY
    sta MiniUpCacheY
    sta MiniHeadY
    lda MiniScanY+1
    sta MiniUpCacheY+1
    sta MiniHeadY+1
    lda MiniQueryTile
    sta MiniHeadTile
    lda MiniQueryAddress
    sta MiniHeadAddress
    lda MiniQueryAddress+1
    sta MiniHeadAddress+1
    inc MiniHeadPending
@done:
    rts

MiniClampDeltaX:
    ldx #0
    jmp MiniClamp
MiniClampDeltaY:
    ldx #$20
MiniClamp:
    lda delta+1,x
    bmi @negative
    bne @max
    lda delta,x
    cmp #128
    bcc @done
@max:
    lda #127
    sta delta,x
    lda #0
    sta delta+1,x
    rts
@negative:
    cmp #$FF
    bne @min
    lda delta,x
    cmp #129
    bcs @done
@min:
    lda #129
    sta delta,x
    lda #$FF
    sta delta+1,x
@done:
    rts

MiniTempPixel:
    lda MiniTemp
    sta MiniCoord
    lda MiniTemp+1
    sta MiniCoord+1
MiniToPixel:
    ldx #4
@shift:
    lsr MiniCoord+1
    ror MiniCoord
    dex
    bne @shift
    rts
MiniAddBound:
    lda MiniBound
MiniAddSigned:
    ldx #0
    cmp #$80
    bcc @pos
    dex
@pos:
    clc
    adc MiniCoord
    sta MiniCoord
    txa
    adc MiniCoord+1
    sta MiniCoord+1
    rts
MiniAlign:
    lda MiniCoord
    and #$F8
    sta MiniCoord
    rts
MiniSnap:
    lda MiniNegative
    beq @noadd
    clc
    lda MiniCoord
    adc #8
    sta MiniCoord
    bcc @noadd
    inc MiniCoord+1
@noadd:
    lda MiniBound
    eor #$FF
    clc
    adc #1
    jsr MiniAddSigned
    ldx #4
@shift:
    asl MiniCoord
    rol MiniCoord+1
    dex
    bne @shift
    lda MiniNegative
    beq @minusone
    clc
    lda MiniCoord
    adc #1
    sta MiniTemp
    lda MiniCoord+1
    adc #0
    sta MiniTemp+1
    rts
@minusone:
    sec
    lda MiniCoord
    sbc #1
    sta MiniTemp
    lda MiniCoord+1
    sbc #0
    sta MiniTemp+1
    rts

MiniEdges:
    lda MiniTemp+1
    cmp MiniEdgeRight+1
    bne @rightcompare
    lda MiniTemp
    cmp MiniEdgeRight
@rightcompare:
    bcc @leftcheck
    beq @leftcheck
    lda MiniTemp+1
    cmp MiniX+1
    bne @rightdir
    lda MiniTemp
    cmp MiniX
@rightdir:
    bcs @stop
    sec
    lda MiniX
    sbc MiniEdgeRight
    sta MiniCoord
    lda MiniX+1
    sbc MiniEdgeRight+1
    bne @rightpush16
    lda MiniCoord
    cmp #16
    bcc @rightpush
@rightpush16:
    lda #16
@rightpush:
    sta MiniCoord
    sec
    lda MiniX
    sbc MiniCoord
    sta MiniTemp
    lda MiniX+1
    sbc #0
    sta MiniTemp+1
    rts
@leftcheck:
    lda MiniTemp+1
    cmp MiniEdgeLeft+1
    bne @leftcompare
    lda MiniTemp
    cmp MiniEdgeLeft
@leftcompare:
    bcs @done
    lda delta+1
    bmi @stop
    ; Original left push includes the 8px overflow buffer; native min0 legal.
    clc
    lda MiniEdgeLeft
    adc #128
    sta MiniCoord
    lda MiniEdgeLeft+1
    adc #0
    sta MiniCoord+1
    sec
    lda MiniCoord
    sbc MiniX
    sta MiniCoord
    lda MiniCoord+1
    sbc MiniX+1
    bne @leftpush16
    lda MiniCoord
    cmp #16
    bcc @leftpush
@leftpush16:
    lda #16
@leftpush:
    clc
    adc MiniX
    sta MiniTemp
    lda MiniX+1
    adc #0
    sta MiniTemp+1
    rts
@stop:
    lda MiniX
    sta MiniTemp
    lda MiniX+1
    sta MiniTemp+1
    lda #0
    sta vel
    sta vel+1
@done:
    rts
MiniWorldEnd:
