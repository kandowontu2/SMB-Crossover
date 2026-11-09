.setcpu "6502"
.charmap $20,$24
.repeat 26,I
 .charmap $41+I,$0a+I
.endrepeat
.segment "CREDIT"
.byte "   BY KANDOWONTU  "
