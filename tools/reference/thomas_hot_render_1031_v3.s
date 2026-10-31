; Source-funded exact226B bodies. Tables contain the original nine targets.
.pushseg
.segment "HOT_RENDER_GATE"
.macro HotRender Name,Roll,Kirby,Chip,Mac,Mike,Mario3,Vic,Turtle,Original
.proc Name
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_BASS
 bne NotRoll
 lda RlVariant
 beq NotRoll
 ldx #0
 beq Pick
NotRoll:
 lda SelectedCharacter
 cmp #20
 bcs Default
 cmp #10
 bne Range
 lda FmAlts
 and #$44
 cmp #$40
 beq Default
 lda SelectedCharacter
Range:
 cmp #14
 bcc KirbyIndex
 sec
 sbc #12
 tax
 bne Pick
KirbyIndex:ldx #1
 bne Pick
Default:ldx #8
Pick:
 lda Lo,x
 sta FarcallJmpTarget_SMC+1
 lda Hi,x
 sta FarcallJmpTarget_SMC+2
 lda Bank,x
 sta NextBank_SMC+1
 pla
 tay
 pla
 tax
 pla
 sta SafecallA_SMC+1
 plp
 jmp FarCallCommon+3
Lo:.byte <Roll,<Kirby,<Chip,<Mac,<Mike,<Mario3,<Vic,<Turtle,<Original
Hi:.byte >Roll,>Kirby,>Chip,>Mac,>Mike,>Mario3,>Vic,>Turtle,>Original
Bank:.byte .lobyte(.bank(Roll)|$80),.lobyte(.bank(Kirby)|$80),.lobyte(.bank(Chip)|$80),.lobyte(.bank(Mac)|$80),.lobyte(.bank(Mike)|$80),.lobyte(.bank(Mario3)|$80),.lobyte(.bank(Vic)|$80),.lobyte(.bank(Turtle)|$80),.lobyte(.bank(Original)|$80)
 .if .xmatch({Name},{HotPlayerGraphics})
::ThPostNativeHot:
 php
 pha
 lda SelectedCharacter
 cmp #10
 bne Foreign
 lda FmAlts
 and #$44
 cmp #$40
 bne Foreign
 pla
 plp
 farcall ThServiceVeneers+81,jmp
Foreign:
 pla
 plp
 farcall HuAfterTerrainGate,jmp
 .else
::ThSharedDrawHot:
 php
 pha
 lda SelectedCharacter
 cmp #10
 bne Foreign
 lda FmAlts
 and #$44
 cmp #$40
 bne Foreign
 pla
 plp
 farcall ThServiceVeneers+6,jmp
Foreign:
 pla
 plp
 ; Exact original KbDrawDispatch classification. The retained bank4 native
 ; fragment owns its original Simon/Z2 branches and callback results.
 lda SelectedCharacter
 cmp #CHARACTER_KIRBY
 bcc Native
 jmp HotNewCharacterDraw
Native:farcall ThKbNativeFallback,jmp
 .endif
 .assert *-::Name<=226,lderror,"Thomas named HotRender body226B"
 .res 226-(*-::Name),$ff
.endproc
.endmacro
HotRender HotPlayerGraphics,RlGraphics,KbGraphicsDispatch,CdGraphicsDispatch,LmGraphicsGate,JnGraphicsDispatch,M3GraphicsDispatch,VvGraphicsDispatch,TnGraphics,NrGraphics
HotRender HotNewCharacterDraw,RlDraw,CdNewDrawDispatch,CdNewDrawDispatch,LmDrawGate,JnDrawDispatch,M3NewDrawDispatch,VvDrawDispatch,TnDraw,NrDraw
.popseg
