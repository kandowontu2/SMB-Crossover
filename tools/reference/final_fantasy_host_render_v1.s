; Typed FF early weapon draw: native DrawAll subsequently reserves/draws body0.
; All additional source body chunks and every spell chunk remain reachable.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,CurrentOAMOffset,CurrentBankC,RgDrawFirst
.import PlayerFacingDir,GuestPowerupActive,GuestPowerupDisplay,MmDeathFlag
.import ObjectMetasprite,ScreenLeft_X_Pos,ScreenLeft_PageLoc
.import SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon
.import MetaspriteRenderLoop
.importzp FfNativeRendererBank
.importzp Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.import FfHostGraphics,FfGraphicsBank,FfRenderChunk,FfPublishChunk
.import FfProjectileEntry,FfEntryRecord,FfRecordLo,FfRecordHi
.import FfRenderBuffer,FfRenderYOffset,FfProjectile,FfSlot,FfTemp
.import FfPower,FfVariant,FfPose,FfTargetX,FfTargetPage,FfTargetY
.import FfTargetW,FfTargetH,FfDamage,FfRectX,FfRectPage,FfRectY,FfRectW,FfRectH,FfEnemyBit
.export FfHostDrawShots,FfHostRenderChunk,FfHostCompact,FfHostRenderBegin,FfHostRenderEnd

; Combat's existing transient output bytes are dead during this draw. This
; adapter uses no new addresses and restores the real body descriptor at exit.
HEntry=FfTargetX
HChunk=FfTargetPage
HWindow=FfTargetY
HSlot=FfTargetW
HCount=FfTargetH
HLeft=FfDamage
HTotal=FfRectPage
HStart=FfRectW
HBytes=FfRectH
HFirst=FfEnemyBit

.segment "FF_HOST_RENDER"
FfHostRenderBegin:
.proc FfHostDrawShots
 lda SelectedCharacter
 cmp #22
 jne Foreign
 lda CurrentBankC
 pha
 jsr FfHostGraphics
 lda ObjectMetasprite
 beq Effects
 lda #$ff
 sta HSlot
 lda #0
 sta HWindow
 ldx FfVariant
 lda ClassBase,x
 sta HEntry
 lda FfPower
 ldx GuestPowerupActive
 beq :+
 lda GuestPowerupDisplay
:cmp #2
 bcc :+
 lda HEntry
 clc
 adc #18
 sta HEntry
:lda HEntry
 clc
 adc FfPose
 sec
 sbc #1
 sta HEntry
 lda #1
 sta HChunk
Body:
 lda PlayerFacingDir
 sta FfSlot
 lda HEntry
 ldx HChunk
 ldy #0
 jsr FfRenderChunk
 bcc Effects
 jsr BodyOrigin
 jsr FfHostRenderChunk
 inc HChunk
 lda HChunk
 cmp #8
 bcc Body
Effects:
 lda MmDeathFlag
 jne Restore
 inc RgDrawFirst
 lda RgDrawFirst
SlotModulo:cmp #3
 bcc SlotReady
 sec
 sbc #3
 bcs SlotModulo
SlotReady:tax
 lda Slots,x
 sta HSlot
 lda #3
 pha
Actor:
 jsr DrawActor
 pla
 sec
 sbc #1
 beq Restore
 pha
 lda HSlot
 clc
 adc #12
 cmp #36
 bcc :+
 lda #0
:sta HSlot
 jmp Actor
Restore:
 ; Native Hp pointer snapshot already points at this same RAM descriptor.
 ; Rebuilding chunk0 also restores its exact pose/frozen-display palette role.
 jsr FfHostGraphics
 lda ObjectMetasprite
 beq Return
 jsr FfPublishChunk
Return:
 pla
 sta CurrentBankC
 sta $5116
Foreign:rts
ClassBase:.byte 0,36,72,108
Slots:.byte 0,12,24
.endproc

.proc DrawActor
 ldx HSlot
 jsr FfProjectileEntry
 jcc Done
 sta HEntry
 lda FfProjectile+8,x
 sta FfSlot
 ; Read the genuine source record's chunk count, without rendering every
 ; chunk twice. The metadata exports add no source instructions or data.
 jsr FfGraphicsBank
 ldx HEntry
 lda FfEntryRecord,x
 tax
 lda FfRecordLo,x
 sta R0
 lda FfRecordHi,x
 sta R1
 ldy #1
 lda (R0),y
 sta HCount
 sta HLeft
 jeq Done
 cmp #9
 jcs Done
 ldx HSlot
 ; Original source records reserve bytes2/3 as zero. These two FF-owned
 ; bytes now hold per-draw chunk/part cursors, reset by genuine allocation.
 lda FfProjectile+2,x
Modulo:cmp HCount
 bcc Ready
 sec
 sbc HCount
 bcs Modulo
Ready:sta HChunk
 clc
 adc #1
 cmp HCount
 bcc :+
 lda #0
:sta FfProjectile+2,x
 inc FfProjectile+3,x
 lda HSlot
 ldy #1
Window:cmp #12
 bcc WindowReady
 sec
 sbc #12
 iny
 bne Window
WindowReady:sty HWindow
Chunk:
 lda HEntry
 ldx HChunk
 ldy HWindow
 jsr FfRenderChunk
 bcc Next
 jsr ShotOrigin
 jsr FfHostRenderChunk
Next:
 inc HChunk
 lda HChunk
 cmp HCount
 bcc :+
 lda #0
 sta HChunk
:dec HLeft
 bne Chunk
Done:rts
.endproc

.proc BodyOrigin
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 sta R5
 lda Player_Y_Position
 clc
 adc FfRenderYOffset
 sta R6
 lda Player_Y_HighPos
 adc FfRenderYOffset+1
 sta R7
 rts
.endproc
.proc ShotOrigin
 ldx HSlot
 lda FfProjectile+4,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda FfProjectile+5,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda FfProjectile+7,x
 clc
 adc FfRenderYOffset
 sta R6
 lda #1
 adc FfRenderYOffset+1
 sta R7
 rts
.endproc

; Compact only records the real native renderer would keep. Shots also stay
; below the HUD. Never change any accepted relative coordinate or attribute.
.proc FfHostCompact
 lda FfRenderBuffer
 sta HTotal
 ldy #0
 ldx #0
Loop:
 cpy HTotal
 bcs Done
 lda FfRenderBuffer+4,y
 bpl XPositive
 clc
 adc R4
 lda R5
 adc #$ff
 bne Next
 beq CheckY
XPositive:
 clc
 adc R4
 lda R5
 adc #0
 bne Next
CheckY:
 lda FfRenderBuffer+3,y
 bpl YPositive
 clc
 adc R6
 sta FfTemp
 lda R7
 adc #$ff
 jmp High
YPositive:
 clc
 adc R6
 sta FfTemp
 lda R7
 adc #0
High:cmp #1
 bne Next
 lda FfTemp
 cmp #31
 bcc Next
 cmp #240
 bcs Next
 .repeat 4,I
 lda FfRenderBuffer+1+I,y
 sta FfRenderBuffer+1+I,x
 .endrepeat
 inx
 inx
 inx
 inx
Next:tya
 clc
 adc #4
 tay
 bne Loop
Done:stx FfRenderBuffer
 rts
.endproc

; Descriptor and R4..R7 are actual source/native inputs. Allocate at most156B
; before native's64B body reservation and at least32B of native world actors.
; 252 rather than256 is the native renderer's real non-wrapping end limit.
.proc FfHostRenderChunk
 jsr FfHostCompact
 lda FfRenderBuffer
 jeq Done
 sta HTotal
 lda #156
 sec
 sbc CurrentOAMOffset
 jcc Done
 jeq Done
 and #$fc
 sta HBytes
 lda #0
 sta HStart
 lda HTotal
 cmp HBytes
 bcc Complete
 beq Complete
 ldx HSlot
 cpx #$ff
 beq Subset
 lda FfProjectile+3,x
 asl
 asl
Modulo:cmp HTotal
 bcc Start
 sec
 sbc HTotal
 bcs Modulo
Start:sta HStart
 jmp Subset
Complete:sta HBytes
Subset:
 jsr FfPublishChunk
 lda #0
 sta R3
 lda HTotal
 sec
 sbc HStart
 cmp HBytes
 bcc First
 lda HBytes
First:sta HFirst
 jsr NativeSubset
 lda HBytes
 sec
 sbc HFirst
 beq Done
 sta HFirst
 lda #0
 sta HStart
 jsr NativeSubset
Done:rts
.endproc

.proc NativeSubset
 lda #<FfRenderBuffer
 clc
 adc HStart
 sta R0
 lda #>FfRenderBuffer
 adc #0
 sta R1
 ldy #0
 lda (R0),y
 pha
 lda HFirst
 sta (R0),y
 ; Genuine native farcall transport, not a cross-bank near call.
 sta SafecallA_SMC+1
 lda #<MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+1
 lda #>MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+2
 lda #<FfNativeRendererBank
 jsr FarCallCommon
 pla
 ldy #0
 sta (R0),y
 rts
.endproc
FfHostRenderEnd:
