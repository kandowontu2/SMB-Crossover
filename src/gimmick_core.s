; Original ce2f8461 hero/star kernel, host callbacks explicit. No shared hook.
.include "gimmick_state.inc"
.pushseg
.segment "GIMMICK_CORE"
GmCoreStart:
.proc GmQueueSound
 ; Exact31:F285..F295 four-slot producer semantics (fourth slot overwrites).
 sty GmQueueSaveY
 ldy GmCueCount
 sta GmCues,y
 iny
 cpy #4
 bcs :+
 sty GmCueCount
:ldy GmQueueSaveY
 rts
.endproc
.proc GmInventoryJump
 ; Exact31:F319 inline table dispatcher with genuine relocated pointers.
 asl
 tay
 iny
 pla
 sta R0
 pla
 sta R1
 lda (R0),y
 sta R2
 iny
 lda (R0),y
 sta R3
 jmp (R2)
.endproc
.proc GmKernelStar
 lda GmRam0091
 beq Done
 lda GmRam0351
 beq Normal
 cmp #1
 beq Type1
 cmp #2
 bne Done
 jmp GmN29_82AB
Normal:jmp GmN29_8023
Type1:jmp GmN29_8171
Done:rts
.endproc
.proc GmIntegrateCall
 ; Actual caller saves complete previous fractional coordinates, not pixels.
 lda GmRam009A,x
 sta GmOldY
 lda GmRam00A4,x
 sta GmOldY+1
 lda GmRam00AE,x
 sta GmOldX
 lda GmRam00B8,x
 sta GmOldX+1
 GmFar GmIntegrate,122
 rts
.endproc
.proc GmScriptedCall
 GmFar GmScriptedBody,75
 lda GmCalleeFlags
 pha
 lda GmCalleeA
 plp
 rts
.endproc
.proc GmTransportCall
 GmFar GmTransportBody,75
 lda GmCalleeFlags
 pha
 lda GmCalleeA
 plp
 rts
.endproc
.proc GmSpawnEffect
 GmFar GmSpawnEffectBody,122
 rts
.endproc
.proc GmEnsureCall
 GmFar GmEnsure,75
 rts
.endproc
.segment "GIMMICK_COLD"
.proc GmScriptedBody
 jsr GmN31_FD6D
 jmp GmCaptureCallee
.endproc
.proc GmTransportBody
 jsr GmN31_FCFD
 jmp GmCaptureCallee
.endproc
.proc GmCaptureCallee
 sta GmCalleeA
 php
 pla
 sta GmCalleeFlags
 lda GmCalleeA
 rts
.endproc
.proc GmColdQueue
 GmFar GmQueueSound,24
 rts
.endproc
.proc GmNewGame
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Done
 lda #0
 sta GmReady                   ; Revoke before any constructor bulk write.
 ldx #127
Clear:sta $5c00,x
 dex
 bpl Clear
 lda #2                       ; Original31:E135/E137 initial max health.
 sta GmRam002B
 sta GmRam0346
 lda #1
 sta GmNextSpecial
 lda SavedJoypadBits
 sta GmPrevious
 jsr GmScene
 lda #$47
 sta GmReady                   ; Publish only after complete constructor.
Done:rts
.endproc
.proc GmScene
 ; Exact owner first. Preserve own12 persistent bytes, NMI clock and pending
 ; original cue producer queue through a same-life room/pipe transition.
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Done
 lda #0
 ldx #127
Clear:
 cpx #<(GmClock-$5c00)
 bcc TestCue
 cpx #<(GmPrevious+1-$5c00)
 bcc Skip                     ; NMI-owned clock/input cannot be lost by Main.
TestCue:
 cpx #<(GmCueCount-$5c00)
 bcc Store
 cpx #<(GmCues+4-$5c00)
 bcc Skip
Store:sta $5c00,x
Skip:
 dex
 cpx #11
 bne Clear
 lda NumberofLives
 sta GmLife
 lda AreaPointer
 sta GmArea
 lda WorldNumber
 sta GmWorld
 lda #$ff
 sta GmPaletteAck
 lda #1
 sta GmRam0090
 lda #0
 sta GmRam030A
Done:rts
.endproc
.proc GmEnsure
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Foreign
 lda GmReady
 cmp #$47
 bne Fresh
 lda NumberofLives
 sec
 sbc GmLife
 bmi LostLife
 lda NumberofLives
 sta GmLife                    ; Multiple real gains/wrap preserve inventory.
 lda AreaPointer
 cmp GmArea
 bne Scene
 lda WorldNumber
 cmp GmWorld
 beq Ready
Scene:jsr GmScene
Ready:sec
 rts
LostLife:
 lda GmRam002B                 ; Original death->E152/E1F9 refills to capacity.
 sta GmRam0346                 ; Original inventory is not reset by E152.
 jmp Scene
Fresh:jsr GmNewGame
 sec
 rts
Foreign:clc
 rts
.endproc
.proc GmPickup
 ; A0=Mushroom capacity/refill,A1=Flower alternating original star kinds1/2
 ; through the genuine inventory codes2/3 (code1 is native healing).
 ; This callback is invoked only by a real physical native actor collector.
 pha
 jsr GmEnsure
 bcc Foreign
 pla
 cmp #2
 bcs No
 cmp #1
 beq Flower
 lda GmRam002B
 cmp #4
 bcs Refill
 inc GmRam002B
Refill:lda GmRam002B
 sta GmRam0346
 lda #$45
 jsr GmColdQueue
 sec
 rts
Flower:
 ldx GmRam0039
 cpx #3
 bcs No                       ; Authentic three-slot capacity refusal.
 lda GmNextSpecial
 pha
 clc
 adc #1                       ; Native inventory2/3 selects star kinds1/2.
 sta GmRam0036,x
 pla
 eor #3                       ; Authored earned reward alternates1/2 only.
 sta GmNextSpecial
 inc GmRam0039
 lda #$1c
 jsr GmColdQueue
 sec
 rts
Foreign:pla
No:clc
 rts
.endproc
.proc GmNmiClock
 ; Root must call once per REAL outerNMI, including lag/pause. No Main tick.
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Done
 lda GmReady
 cmp #$47
 bne Done
 lda SavedJoypadBits
 eor GmPrevious
 and SavedJoypadBits
 sta GmFresh
 lda SavedJoypadBits
 sta GmPrevious
 inc GmClock
Done:pla
 plp
 rts
.endproc
.proc GmInjury
 ; A=actual accepted overlap SIDE0/1, not old facing. Original source returns
 ; A0/Y1 or A1 on opposite sides; Z is not a Boolean test of that A value.
 ; Root's native contact adapter must pass the real side after overlap.
 pha
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne NoPop
 lda GmRam038C
 bne NoPop
 lda GmRam0090
 cmp #$d0
 bcs NoPop
 pla
 and #1
 sta GmRam030A
 dec GmRam0346
 lda #$17
 jsr GmColdQueue
 lda #$7f
 sta GmRam038C
 lda #$12
 sta GmRam00CC
 lda #$e8
 sta GmRam00C2
 lda GmRam030A
 beq Hit
 lda GmRam00CC
 eor #$ff
 clc
 adc #1
 sta GmRam00CC
Hit:sec
 rts
NoPop:pla
No:clc
 rts
.endproc
.proc GmStompPolicy
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne No
 lda CrossoverBehaviorVersion ; Explicit authored Easy policy, not original.
 bne No
 sec
 rts
No:clc
 rts
.endproc
.proc GmBounce
 lda SelectedCharacter
 cmp #CHARACTER_GIMMICK
 bne Done
 lda #$ac                     ; Synchronize real Easy native stomp to source.
 sta GmRam00C2
 sta GmRam004B
 lda #0
 sta GmRam036E
Done:rts
.endproc
.include "gimmick_native.inc"
.segment "GIMMICK_CORE"
GmCoreEnd:
.export GmNewGame,GmScene,GmEnsure,GmPickup,GmNmiClock,GmInjury,GmStompPolicy,GmBounce
.export GmKernelStar,GmQueueSound,GmCoreStart,GmCoreEnd
.popseg
