; OWN C2 transport viewed as rawA2. Genuine SFC-only entry and successful
; forced-blank CF load BEFORE any entry opcode are mandatory preconditions.
; No shared ingress/readiness is installed by this source-only component.
.setcpu "6502"
.macpack longbranch
.import CfTarget,CfTargetBank,CfCallA,CfLoaderExpectedCookie
.import CurrentBankC,FmGroups,FarcallJmpTarget_SMC
.import CfHostGraphics,CfHostPortrait,CfHostVisible
.import CfHostMovement,CfHostDraw,CfHostShots,CfHostInjury,CfHostHead
.import CfHostBody,CfHostAdder,CfHostBoxProfile,CfHostSide,CfHostConstruct
.import CfHostBox,CfHostSceneEnsure,CfHostReset,CfHostCollect,CfHostFullPower,CfHostHeadWithin
.export CfServiceVeneers,CfServiceUnavailable,CfA2Router,CfA2RouterEnd
.export CfHostUnimplemented
.segment "CF_A2_ROUTER"
CfServiceVeneers:
 .repeat 36
  jmp CfA2Router
 .endrepeat
CfServiceUnavailable:clc
 rts
.assert .lobyte(CfServiceVeneers)=0,lderror,"True page-aligned arithmetic ABI"

CfA2Router:
 php
 pha
 lda CurrentBankC
 pha
 txa
 pha
 tya
 pha
 ; ROM expected fingerprint is outside the hashed carrier. This avoids
 ; inventing a cyclic payload hash embedded in the payload it authenticates.
 lda #$ce
 sta CurrentBankC
 sta $5116
 ldx #15
CfCookieByte:
 cpx #2
 beq CfCookieNext
 lda $bfe0,x
 cmp CfLoaderExpectedCookie,x
 bne CfBadCookie
CfCookieNext:
 dex
 bpl CfCookieByte
 lda FmGroups
 lsr
 lsr
 lsr
 and #3
 cmp $bfe2
 bne CfBadCookie
 lda #2
 sta CurrentBankC
 sta $5116
 ; The actual public common arithmetic target encodes3*service in the
 ; real SFC operand. No leased global or another family's scratch is used.
 lda FarcallJmpTarget_SMC+1
 ldx #0
CfDivide3:
 cmp #3
 bcc CfHaveIndex
 sbc #3
 inx
 bne CfDivide3
CfHaveIndex:
 cpx #36
 bcs CfBadCookie
 lda CfOwnLo,x
 sta CfTarget-$2000
 lda CfOwnHi,x
 sta CfTarget+1-$2000
 lda #3
 sta CfTargetBank-$2000
 ; Put oldC BELOW saved Y/X/A/P without leaving it in a nested-call-unsafe
 ; global. A2 is still mapped; all table/state references use its true alias.
 tsx
 lda $0103,x
 tay
 lda $0104,x
 sta $0103,x
 lda $0105,x
 sta $0104,x
 tya
 sta $0105,x
 pla
 tay
 pla
 tax
 pla
 plp
 jsr CfCallA
 jmp CfA2Return
CfBadCookie:
 tsx
 lda $0103,x
 tay
 lda $0104,x
 sta $0103,x
 lda $0105,x
 sta $0104,x
 tya
 sta $0105,x
 pla
 tay
 pla
 tax
 pla
 plp
 clc
CfA2Return:
 php
 pha
 txa
 pha
 tya
 pha
 tsx
 lda $0105,x
 sta CurrentBankC
 sta $5116                       ; executable A2 never self-unmaps here
 ; Remove only the oldC stack byte, retaining ALL worker AXYP outputs and
 ; the original SFC worker return. This also works with live upper page1.
 lda $0104,x
 sta $0105,x
 lda $0103,x
 sta $0104,x
 lda $0102,x
 sta $0103,x
 lda $0101,x
 sta $0102,x
 inx
 txs
 pla
 tay
 pla
 tax
 pla
 plp
 rts

CfOwnLo:
 .lobytes CfHostMovement,CfHostGraphics,CfHostDraw,CfHostGraphics,CfHostShots,CfHostInjury,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostVisible,CfHostHead,CfHostBody,CfHostAdder,CfHostBoxProfile,CfHostSide,CfHostSceneEnsure,CfHostBox,CfHostPortrait,CfHostUnimplemented,CfHostReset,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostCollect,CfHostFullPower,CfHostUnimplemented,CfHostUnimplemented,CfHostHeadWithin,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostShots,CfHostUnimplemented
CfOwnHi:
 .hibytes CfHostMovement,CfHostGraphics,CfHostDraw,CfHostGraphics,CfHostShots,CfHostInjury,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostVisible,CfHostHead,CfHostBody,CfHostAdder,CfHostBoxProfile,CfHostSide,CfHostSceneEnsure,CfHostBox,CfHostPortrait,CfHostUnimplemented,CfHostReset,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostCollect,CfHostFullPower,CfHostUnimplemented,CfHostUnimplemented,CfHostHeadWithin,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostUnimplemented,CfHostShots,CfHostUnimplemented
CfA2RouterEnd:
.assert CfA2RouterEnd<=$bfe0,lderror,"C2 own alias/cookie boundary"
.segment "CF_HOST_BOUNDARIES"
CfHostUnimplemented:clc
 rts
