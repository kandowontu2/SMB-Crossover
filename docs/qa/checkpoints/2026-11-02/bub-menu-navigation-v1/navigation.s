.setcpu "6502"
.segment "BUB_MENU_NAV"
.export BubMenuLeft
BubMenuLeft:
 .byte 7,0,1,2,3,4,5,6,15,8,9,10,11,12,13,14,23,16,17,18,19,20,21,22,31,24,25,26,27,28,29,30,32
.export BubMenuRight
BubMenuRight:
 .byte 1,2,3,4,5,6,7,0,9,10,11,12,13,14,15,8,17,18,19,20,21,22,23,16,25,26,27,28,29,30,31,24,32
.export BubMenuUp
BubMenuUp:
 .byte 32,32,32,32,32,32,32,32,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24
.export BubMenuDown
BubMenuDown:
 .byte 8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,32,32,32,32,32,32,32,0
.export BubMenuCharacters
BubMenuCharacters:
 .byte 0,1,2,3,4,5,6,7,12,9,10,11,13,14,15,16,17,18,19,20,21,22,23,33,25,26,27,28,29,30,31,32,39
.export BubMenuCursorLo
BubMenuCursorLo:
 .byte 163,166,169,172,175,178,181,184,35,38,41,44,47,50,53,56,163,166,169,172,175,178,181,184,35,38,41,44,47,50,53,56,163
.export BubMenuCursorHi,BubMenuUsedEnd
BubMenuCursorHi:
 php
 tya
 lsr
 lsr
 lsr
 clc
 adc #1
 lsr
 clc
 adc #$20
 plp
 ora #0
 rts
BubMenuUsedEnd:
 .res $e0-(*-BubMenuLeft),$ff
