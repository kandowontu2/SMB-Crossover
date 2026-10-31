"""Source3 ten-tick alignment/rapid pound; separate active state until land."""
from pathlib import Path
P=Path(__file__).with_name('prepare_bowser_source_core_v3.py')
s=P.read_text(encoding='utf-8').replace('bowser-source-core-v3','bowser-source-core-v4')
edits=r'''s=s.replace('BwStateEnd=$601f','BwPound=$601f\nBwTargetX=$6020\nBwTargetPage=$6021\nBwStateEnd=$6022')
s=s.replace('ldx #30','ldx #33')
s=s.replace('Air:\n lda BwVariant\n bne FireInput','Air:\n lda BwVariant\n bne FireInput\n lda BwPound\n bne FireInput')
s=s.replace('lda #10                    ; original AlignAndFall wait','''+repr('''lda #1
 sta BwPound
 lda BwPos
 clc
 adc #8
 and #$f0
 sta BwTargetX
 lda BwPage
 adc #0
 sta BwTargetPage
 lda #10                    ; original AlignAndFall wait''')+r''')
s=s.replace('Motion:\n ldx #0','''+repr('''Motion:
 lda BwPound
 beq Integrate
 lda #0
 sta BwBreath
 sta BwVel
 lda #6
 sta BwPose
 lda BwSlam
 beq Integrate
 dec BwSlam
 jsr BwAlign
 jmp Done
Integrate:
 ldx #0''')+r''')
s=s.replace('lda BwSlam\n beq Landed','lda BwPound\n beq Landed')
s=s.replace('sta BwSlam\nLanded:','sta BwSlam\n sta BwPound\nLanded:')
s=s.replace('lda BwSlam\n beq Gravity\n dec BwSlam\n lda #0\n sta BwVel\nGravity:','''+repr('''lda BwPound
 beq Gravity
 lda BwVel+1
 bmi PoundGravity
 cmp #$70
 bcs Pose
PoundGravity:
 clc
 adc #6
 sta BwVel+1
 jmp Pose
Gravity:''')+r''')
s=s.replace('Pose:\n lda BwVariant','Pose:\n lda BwPound\n beq :+\n lda #6\n sta BwPose\n jmp Done\n:lda BwVariant')
s=s.replace('HopFrames:.byte', '''+repr('''; Source boss arena never crossed pages; this world adapter extends the
; original one-pixel alignment without wrapping a world X byte.
BwAlign:
 lda BwPage
 cmp BwTargetPage
 beq AlignLow
 bcc AlignRight
 bcs AlignLeft
AlignLow:
 lda BwPos
 cmp BwTargetX
 beq AlignDone
 bcc AlignRight
AlignLeft:
 lda BwPos
 sec
 sbc #1
 sta BwPos
 lda BwPage
 sbc #0
 sta BwPage
 rts
AlignRight:
 inc BwPos
 bne AlignDone
 inc BwPage
AlignDone:rts
HopFrames:.byte''')+r''')
'''
s=s.replace("exec(compile(s,str(P),'exec'),",edits+"exec(compile(s,str(P),'exec'),")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
