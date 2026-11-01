"""Remove shadowed palette packets after coalescing the final portrait colors."""
from pathlib import Path
from relink_menu_main_bounded_v1 import R,rebuild


def main():
    P=R/'build/ready76-menu-fixed-v4';O=R/'build/ready76-menu-fixed-v5'
    text=(P/'menu_vram_budget.s').read_text()
    a=text.index('.proc MenuDropShadowPalette');z=text.index('.endproc',a)
    block=text[a:z]
    old=' cmp #$3f\n bne Done';assert block.count(old)==1
    block=block.replace(old,' cmp #$3f\n beq HavePalette\n rts\nHavePalette:',1)
    old=''' cmp #$10
 bne Next
 lda VRAM_Buffer1+2,x'''
    new=''' cmp #$10
 beq Universal
 jmp MenuHandlePalette11
Universal:
 lda VRAM_Buffer1+2,x'''
    assert block.count(old)==1;block=block.replace(old,new,1)
    old=' inc VRAM_Buffer1_Offset\n rts';assert block.count(old)==1
    block=block.replace(old,' inc VRAM_Buffer1_Offset\n ldx #0\n jmp Loop',1)
    text=text[:a]+block+text[z:]
    a=text.index('.proc MenuRemoveHint');z=text.index('.endproc',a);block=text[a:z]
    old=''' lda VRAM_Buffer1+2,x
 cmp #20
 bne Next
 lda #23'''
    assert block.count(old)==1;block=block.replace(old,' lda #23 ; validated2346 packets are exactly20 cells',1)
    text=text[:a]+block+text[z:]
    a=text.index('.proc MenuPruneUnusedPalette2');z=text.index('.endproc',a);block=text[a:z]
    old=''' txa
 clc
 adc #4
 tax
 bne Oam
 ldx #0'''
    new=''' inx
 inx
 inx
 inx
 bne Oam                    ; X already wrapped to zero'''
    assert block.count(old)==1;block=block.replace(old,new,1)
    old=''' lda VRAM_Buffer1+2,x
 tay
 inx
 inx
 inx
Bytes:
 inx
 dey
 bne Bytes
 jmp Packet'''
    new=''' txa
 clc
 adc VRAM_Buffer1+2,x
 adc #3                     ; validated queue ends below84: no carry here
 tax
 jmp Packet'''
    assert block.count(old)==1;block=block.replace(old,new,1)
    text=text[:a]+block+text[z:]
    helper='''
.proc MenuHandlePalette11
 cmp #$11
 bne Other
 lda VRAM_Buffer1+2,x
 cmp #3
 bne Other
 lda R0
 sec
 sbc #6
 sta R0
 lda #6
 sta R1
 jsr MenuDeleteBytes
 jmp MenuDropShadowPalette::Loop
Other:
 jmp MenuDropShadowPalette::Next
.endproc
'''
    anchor='.assert *<=$bb50,lderror,"Keep the fixed menu entry"'
    assert text.count(anchor)==1;text=text.replace(anchor,helper+anchor,1)
    rebuild(P,O,text,expected='abbaee336338c1a143df83c5ebe95ec5ce11a14466781f071b52f80746cfdce4',creator=Path(__file__),
            defect='Alex had an earlier3F11/3 packet as well as the final colors. Continue scanning after coalescing and delete all fully shadowed3F11/3 packets. Preserve every3F11/7 packet. Fund the helper inside the existing103-byte gap using equivalent validated-queue traversal and the redundant hint-length check.')


if __name__=='__main__':main()
