"""Coalesce a separated one-byte universal palette packet as well."""
from pathlib import Path
from relink_menu_main_bounded_v1 import R,rebuild


def main():
    P=R/'build/ready76-menu-fixed-v3';O=R/'build/ready76-menu-fixed-v4'
    text=(P/'menu_vram_budget.s').read_text()
    start=text.index('.proc MenuDropShadowPalette');end=text.index('.endproc',start)+len('.endproc')
    replacement='''; Fold the final portrait colors with an earlier universal-color packet.
; Neither packet is visible until this entire foreground queue is published.
.proc MenuDropShadowPalette
 lda VRAM_Buffer1_Offset
 cmp #6
 jcc Done
 sec
 sbc #6
 sta R0
 tax
 lda VRAM_Buffer1,x
 cmp #$3f
 bne Done
 lda VRAM_Buffer1+1,x
 cmp #$11
 bne Done
 lda VRAM_Buffer1+2,x
 cmp #3
 bne Done
 ldx #0
Loop:
 cpx R0
 bcs Done
 lda VRAM_Buffer1,x
 cmp #$3f
 bne Next
 lda VRAM_Buffer1+1,x
 cmp #$10
 bne Next
 lda VRAM_Buffer1+2,x
 cmp #1
 beq Combine
 cmp #4
 bne Next
Combine:
 clc
 adc #3
 sta R1
 lda VRAM_Buffer1+3,x
 pha
 lda R0
 sec
 sbc R1
 sta R0
 jsr MenuDeleteBytes
 ldx R0
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 lda VRAM_Buffer1+5,x
 sta VRAM_Buffer1+6,x
 lda VRAM_Buffer1+4,x
 sta VRAM_Buffer1+5,x
 lda VRAM_Buffer1+3,x
 sta VRAM_Buffer1+4,x
 pla
 sta VRAM_Buffer1+3,x
 lda #0
 sta VRAM_Buffer1+7,x
 inc VRAM_Buffer1_Offset
 rts
Next:
 lda VRAM_Buffer1+2,x
 tay
 inx
 inx
 inx
Bytes:
 inx
 dey
 bne Bytes
 jmp Loop
Done:rts
.endproc'''
    text=text[:start]+replacement+text[end:]
    start=text.index('Gap:',text.index('.proc MenuMergePaletteRuns'));end=text.index('.endproc',start)
    part=text[start:end];assert part.count(' jne Next')==5
    text=text[:start]+part.replace(' jne Next',' bne Next')+text[end:]
    rebuild(P,O,text,expected='402df0276e01443a91920d5d75006f7d53295da6902947f1abcae57136598e02',creator=Path(__file__),
            defect='Alex supplies3F10/1 rather than3F10/4 and requires palette3 outlines, so the previous fold did not affect his packet. Combine either universal packet with final portrait colors, preserving his outlines and all original OAM. Fund the code with five range-checked short branches.')


if __name__=='__main__':main()
