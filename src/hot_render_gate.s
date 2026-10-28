; Select the first existing owner without visiting unrelated family banks.
; Preserve Roll's original alternate override and A/P at its and Mac's leaves.
.pushseg
.segment "HOT_RENDER_GATE"
.macro HotRender Name,Roll,Kirby,Chip,Mac,Mike,Mario3,Vic,Turtle,Original
.proc Name
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_BASS
 bne NotRoll
 lda RlVariant
 beq NotRoll
 pla
 plp
 farcall Roll,jmp
NotRoll:
 lda SelectedCharacter
 cmp #20
 jcs Fallback
 cmp #14
 bcc ToKirby
 beq ToChip
 cmp #15
 beq ToMac
 cmp #16
 beq ToMike
 cmp #17
 beq ToMario3
 cmp #18
 beq ToVic
 pla
 plp
 farcall Turtle,jmp
ToKirby:
 pla
 plp
 farcall Kirby,jmp
ToChip:
 pla
 plp
 farcall Chip,jmp
ToMac:
 pla
 plp
 farcall Mac,jmp
ToMike:
 pla
 plp
 farcall Mike,jmp
ToMario3:
 pla
 plp
 farcall Mario3,jmp
ToVic:
 pla
 plp
 farcall Vic,jmp
Fallback:
 pla
 plp
 farcall Original,jmp
.endproc
.endmacro
HotRender HotPlayerGraphics,RlGraphics,KbGraphicsDispatch,CdGraphicsDispatch,LmGraphicsGate,JnGraphicsDispatch,M3GraphicsDispatch,VvGraphicsDispatch,TnGraphics,NrGraphics
HotRender HotNewCharacterDraw,RlDraw,CdNewDrawDispatch,CdNewDrawDispatch,LmDrawGate,JnDrawDispatch,M3NewDrawDispatch,VvDrawDispatch,TnDraw,NrDraw
.popseg
