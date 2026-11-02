; Exact no-op service result: preserve A/X/Y/P except handled carry clear.
; No cache read or execution, so no authentication is necessary on this path.
.setcpu "6502"
.segment "PATCH"
clc
rts
nop
