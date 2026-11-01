; Thomas-only1-1 accommodations listed before edits in the camera checkpoint.
; These are ordinary native vertical platforms, never custom painted geometry.
.setcpu "6502"
.macpack longbranch
.import InitEnemyObject,TimerControl,WorldNumber,LevelNumber,AreaAddrsLOffset
.import SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon
.importzp Player_X_Position,Player_PageLoc,ObjectOffset,R0
.importzp Enemy_Flag,Enemy_ID,Enemy_X_Position,Enemy_PageLoc,Enemy_Y_Position,Enemy_Y_HighPos
.export ThLiftTick,ThLiftReset,ThLiftSeen
; Own selected C2 boundary gap: HostTemp836..837; next context starts840.
ThLiftSeen=$c838
ThLiftOldObject=$c839
.segment "THOMAS_KERNEL"
ThLiftReset:
 lda #0
 sta ThLiftSeen
 rts
ThLiftTick:
 lda TimerControl
 jne Done
 lda WorldNumber
 ora LevelNumber
 jne Done
 lda AreaAddrsLOffset
 cmp #5
 jne Done
 ldy #0
Scan:
 lda ThLiftSeen
 and Bits,y
 jne Next
 ; Signed16 distance from the native platform's authored world position.
 ; Spawn at most112px ahead; skip a pipe already passed after room return.
 lda Player_X_Position
 sec
 sbc XLo,y
 sta R0
 lda Player_PageLoc
 sbc XHi,y
 beq Right
 jpl Mark
 cmp #$ff
 bne Next
 lda R0
 cmp #$90
 bcc Next
 bcs Ready
Right:
 lda R0
 cmp #80
 bcs Mark
Ready:
 ldx #5
Free:
 lda Enemy_Flag,x
 beq Found
 dex
 bpl Free
 rts                         ; retry later; native actors always have priority
Found:
 lda ObjectOffset
 sta ThLiftOldObject
 stx ObjectOffset
 lda XLo,y
 sta Enemy_X_Position,x
 lda XHi,y
 sta Enemy_PageLoc,x
 lda #192
 sta Enemy_Y_Position,x
 lda #1
 sta Enemy_Flag,x
 sta Enemy_Y_HighPos,x
 lda #$25
 sta Enemy_ID,x
 lda ThLiftSeen
 ora Bits,y
 sta ThLiftSeen
 ; Full existing native initialization, including shared contact teardown.
 sta SafecallA_SMC+1
 lda #<InitEnemyObject
 sta FarcallJmpTarget_SMC+1
 lda #>InitEnemyObject
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(InitEnemyObject)|$80)
 jsr FarCallCommon
 lda ThLiftOldObject
 sta ObjectOffset
 rts
Mark:
 lda ThLiftSeen
 ora Bits,y
 sta ThLiftSeen
Next:
 iny
 cpy #4
 jne Scan
Done:
 rts
XLo:.byte $90,$30,$b0,$60
XHi:.byte 1,2,2,3
Bits:.byte 1,2,4,8
