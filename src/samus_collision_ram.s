; Kept after the pre-existing SRAM modules so their addresses remain stable.
.pushseg
.segment "SRAM"
SmCeilingHit: .res 1
SmSourceJumped: .res 1

; Tail allocation preserves every existing guest/audio SRAM address.
; The dedicated cold entry leaves standalone inventory resets unchanged.
; Ryu source normal-air/climb wall receipt; cleared with every roster reset.
RyWallEdge: .res 1
RyWallPage: .res 1
RyWallSide: .res 1
RyWallResolved: .res 1
RyWallBlocked: .res 1
RyWallSupported: .res 1
RyWallWasGround: .res 1
RyWallOldHeight: .res 1
RyWallOldX: .res 1
RyWallOldPage: .res 1
RyWallOldXFine: .res 1
RyWallOldXFrac: .res 1
RyWallOldY: .res 1
RyWallOldYFine: .res 1
RyWallOldYFrac: .res 1
RyWallScanY: .res 1
RyWallScanLast: .res 1
.assert *-RyWallEdge=17, error, "Ryu wall state must remain17 bytes"

.segment "SPECIAL_MM"
; RosterClearState supplies A=0. Append this cold entry so all pre-existing
; SPECIAL_MM code keeps its original CPU addresses and branch placement.
.proc SpecialRosterClear
  sta RyuSourceBodyProfile     ; Roster lifecycle only; inventory clear retains it.
  ldx #18
Loop:
  sta RyWallEdge,x
  dex
  bpl Loop
  jmp SpecialClear
.endproc

.segment "SAMUS"
; Entered by JMP only for Ryu. A/X and the caller's stack stay intact.
; An unresolved/different side resumes the original native guest dispatch.
.proc SamusRyuWallHandled
  ; Sole predecessor supplies Y=R0 and consumes C only. No incoming A is
  ; required by the predicate or NativeGuest. Avoid the unused SafecallA save.
  lda #.lobyte(RyuSourceSideDispatch)
  SMC_StoreLowByte FarcallJmpTarget, a
  lda #.hibyte(RyuSourceSideDispatch)
  SMC_StoreHighByte FarcallJmpTarget, a
.if ::MAPPER_MMC5
  lda #.bank(RyuSourceSideDispatch) | MMC5_PRG_ROM
.else
  lda #.bank(RyuSourceSideDispatch)
.endif
  jmp FarCallCommon
  .assert *-SamusRyuWallHandled=15,error,"Keep the original SAMUS gate span"
.endproc
.popseg
