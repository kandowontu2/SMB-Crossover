"""Prepare a sparse RCR renderer successor without changing shared host sources."""
from pathlib import Path
import re

R = Path(__file__).resolve().parents[1]

SET_POSE = '''.proc RcSetPose
 BankPRGC #.bank(RcArtStart)
 cpx #18
 bcc Valid
 ldx #0
Valid:
 stx RcPose
 lda RcVariant
 beq Alex
 lda RcV1BodyPage,x
 sta SmChrBank
 lda RcV1InkPage,x
 sta RcInkChr
 lda PlayerFacingDir
 cmp #2
 beq RyanLeft
 lda RcV1PoseRLo,x
 sta SmPosePtr
 lda RcV1PoseRHi,x
 sta SmPosePtr+1
 lda RcV1InkRLo,x
 sta RcInkPtr
 lda RcV1InkRHi,x
 bne InkHi
RyanLeft:
 lda RcV1PoseLLo,x
 sta SmPosePtr
 lda RcV1PoseLHi,x
 sta SmPosePtr+1
 lda RcV1InkLLo,x
 sta RcInkPtr
 lda RcV1InkLHi,x
 bne InkHi
Alex:
 lda RcV0BodyPage,x
 sta SmChrBank
 lda RcV0InkPage,x
 sta RcInkChr
 lda PlayerFacingDir
 cmp #2
 beq AlexLeft
 lda RcV0PoseRLo,x
 sta SmPosePtr
 lda RcV0PoseRHi,x
 sta SmPosePtr+1
 lda RcV0InkRLo,x
 sta RcInkPtr
 lda RcV0InkRHi,x
 bne InkHi
AlexLeft:
 lda RcV0PoseLLo,x
 sta SmPosePtr
 lda RcV0PoseLHi,x
 sta SmPosePtr+1
 lda RcV0InkLLo,x
 sta RcInkPtr
 lda RcV0InkLHi,x
InkHi:
 sta RcInkPtr+1
 lda PlayerOutlinesOff
 bne Ready
 ; The shared buffer is129B; source maximum is14parts/57B.
 ; Invalidating all cache keys prevents a later legacy owner using stale ink.
 lda #0
 sta OutlineSourceHi
 ldx #3
Invalidate:
 sta OutlineTinyHi,x
 dex
 bpl Invalidate
 lda SmPosePtr
 sta R0
 lda SmPosePtr+1
 sta R1
 ldx #1
 jsr Copy
 lda RcInkPtr
 sta R0
 lda RcInkPtr+1
 sta R1
 jsr Copy
 dex
 stx OutlinePoseBuffer
 lda #<OutlinePoseBuffer
 sta SmPosePtr
 lda #>OutlinePoseBuffer
 sta SmPosePtr+1
Ready:
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
Copy:
 ldy #0
 lda (R0),y
 sta RcCopyLeft
Loop:
 iny
 lda (R0),y
 sta OutlinePoseBuffer,x
 inx
 dec RcCopyLeft
 bne Loop
 rts
.endproc
'''

PUBLISH = '''.proc RcPublish
 ; A single source pose owns two1KB windows; never remap world/effect2/3.
 lda SmChrBank
 ldy #0
 jsr Window
 lda PlayerOutlinesOff
 bne Done
 lda RcInkChr
 ldy #1
 jsr Window
Done:
 lda #1
 sta X5WideChrActive
 rts
Window:
 cmp CurrentCHRBank,y
 bne Changed
 pha
 lda X5ChrMode,y
 cmp #$82
 pla
 beq Return
Changed:
 sta CurrentCHRBank,y
 lda #$82
 sta X5ChrMode,y
 lda #1
 sta ReloadCHRBank
Return:
 rts
.endproc
'''

PALETTE = '''.proc RcQueuePalette
 ; Pal2 at3F19 remains entirely owned by native enemies/powerups.
 lda StarInvincibleTimer
 ora GuestPowerupActive
 beq Ordinary
 lda #0
 sta RcPalette
 rts
Ordinary:
 lda RcPalette
 bne Done
 ldx VRAM_Buffer1_Offset
 cpx #78                     ;6B command + terminator fits84B queue.
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$30                    ; native source white/skin/blue classes
 sta VRAM_Buffer1+3,x
 lda #$26
 sta VRAM_Buffer1+4,x
 lda #$11
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 inc RcPalette
Done:rts
.endproc
'''


def main():
    old = (R/'src/river_city_render.s').read_text()
    for name, body in [('RcSetPose', SET_POSE), ('RcPublish', PUBLISH), ('RcQueuePalette', PALETTE)]:
        old, n = re.subn(r'(?s)\.proc '+name+r'\n.*?\.endproc\n', lambda m: body, old)
        assert n == 1, name
    old = ('; Independent successor, shared host integration not yet admitted.\n'
           'RcInkPtr=$5c4c\nRcInkChr=$5c4e\nRcCopyLeft=$5c4f\n'+old)
    path = R/'src/river_city_shared_palette_render.inc'
    assert not path.exists()
    path.write_text(old, newline='\n')
    print(path)


if __name__ == '__main__':
    main()
