; Mac-only fast endpoints keep their genuine entry/whole original spans.
; Bank93 owns the new art-aligned terrain geometry; foreign gates unchanged.
.proc TnMacHeadProbe
 farcall MacRosterTerrainHead,jmp
 .res 160,$ea
 .assert *-TnMacHeadProbe=178,error,"Mac head endpoint span"
.endproc
.export TnMacHeadProbe
.proc TnMacSideProbe
 farcall MacRosterTerrainSide,jmp
 .res 178,$ea
 .assert *-TnMacSideProbe=196,error,"Mac side endpoint span"
.endproc
.export TnMacSideProbe
; Private side probe: the source body can extend into the HUD. Never
; wrap those samples into unrelated block-buffer rows below the playfield.
.proc TnMacVisibleSideProbe
 php
 pha
 lda Player_Y_Position
 clc
 adc BlockBuffer_Y_Adder,y
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 pla
 plp
 jmp BlockBufferColli_Side
Empty:
 pla
 plp
 lda #0
 sta R3
 rts
.endproc
.export TnMacVisibleSideProbe
