"""Coalesce the final portrait colors into their earlier full palette packet."""
from pathlib import Path
from relink_menu_main_bounded_v1 import R,rebuild


def main():
    P=R/'build/ready76-menu-fixed-v2';O=R/'build/ready76-menu-fixed-v3'
    text=(P/'menu_vram_budget.s').read_text()
    # Assembler range checks verify that these formerly long branches fit.
    start=text.index('.proc MenuQueueValidate');end=text.index('.endproc',start)
    section=text[start:end];assert section.count(' jne Invalid')==9
    text=text[:start]+section.replace(' jne Invalid',' bne Invalid')+text[end:]
    old=''' lda #1
 sta VRAM_Buffer1+2,x
 inx
 inx
 inx
 inx
 lda #3
 sta R1
 jmp MenuDeleteBytes'''
    new=''' ; Keep the earlier universal color and replace its three shadowed
 ; payload bytes with the final portrait colors. Delete the final command,
 ; saving its address/length overhead even across name/cursor commands.
 ldy R0
 lda VRAM_Buffer1+3,y
 sta VRAM_Buffer1+4,x
 lda VRAM_Buffer1+4,y
 sta VRAM_Buffer1+5,x
 lda VRAM_Buffer1+5,y
 sta VRAM_Buffer1+6,x
 ldx R0
 lda #6
 sta R1
 jmp MenuDeleteBytes'''
    assert text.count(old)==1;text=text.replace(old,new,1)
    rebuild(P,O,text,expected='08c0fd9f693788aad279970a56a9278e3801aba2e6cf2ad222e0362be7a26cea',creator=Path(__file__),
            defect='Alex still had one heading corruption frame after the initial fix. Fold the final3F11/3 payload into the earlier3F10/4 command without changing palette values, saving another PPU packet setup. Fund it with assembler-checked short branches.')


if __name__=='__main__':main()
