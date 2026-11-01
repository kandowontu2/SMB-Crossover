; Existing Start wrapper discards its incoming A in FmStartRetireFlags.
; Removing the redundant incoming-A save funds this13-byte private helper.
; Keep FmPending itself intact for cold atlas portraits and pending names.
.export Ms14PlayablePending
Ms14PlayablePending:
 jsr FmPending
 bcc Ms14Done
 eor #4
 bne Ms14RestoreA
 clc
Ms14RestoreA:
 eor #4
Ms14Done:
 rts
.assert *-Ms14PlayablePending=13,error,"Exact funded menu helper"
