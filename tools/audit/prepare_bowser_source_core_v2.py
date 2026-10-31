"""New successor: original native SMB1 Bowser gravity plus same source3 core."""
from pathlib import Path
P=Path(__file__).with_name('prepare_bowser_source_core_v1.py')
s=P.read_text(encoding='utf-8').replace('build/bowser-source-core-v1','build/bowser-source-core-v2')
s=s.replace('BwStateEnd=$601c','BwVariant=$601c\nBwForceY=$601d\nBwVerticalSign=$601e\nBwStateEnd=$601f')
s=s.replace('Bw3Step,Bw3AddVelFrac,BwCoreStart,BwCoreEnd,Bw3Fresh','Bw3Step,Bw1Step,Bw1Gravity,Bw3AddVelFrac,BwCoreStart,BwCoreEnd,Bw3Fresh')
s=s.replace('ldx #27','ldx #30')
s=s.replace('Bw3Step:\n sta BwInput','''Bw1Step:
 php
 pha
 lda #1
 sta BwVariant
 pla
 plp
 jmp BwStep
Bw3Step:
 php
 pha
 lda #0
 sta BwVariant
 pla
 plp
BwStep:
 sta BwInput''')
s=s.replace('lda #$e8                   ; authored left control: source velocity -$18','''lda #$e8                   ; source3 selected speed -$18
 ldx BwVariant
 beq :+
 lda #$f0                   ; source1 authored walking speed -1px
:''')
s=s.replace('lda #$18                   ; source Bowser_XVelByDist entry2, 1.5px/update','''lda #$18                   ; source3 Bowser_XVelByDist entry2, 1.5px/update
 ldx BwVariant
 beq :+
 lda #$10                   ; source1 authored walking speed +1px
:''')
s=s.replace('lda #$a0                   ; original Bowser jump velocity -$60 in4.4FP','''lda #$a0                   ; original source3 jump -$60 in4.4FP
 ldx BwVariant
 beq :+
 dec BwPos+1                ; exact native MakeBJump first Y decrement
 lda #$fe                   ; original source1 Bowser -2px jump
:''')
s=s.replace('sta BwVel+1\n lda #0\n sta BwGrounded','sta BwVel+1\n lda #0\n sta BwGrounded\n sta BwForceY\n sta BwFrac+1',1)
s=s.replace('Air:\n lda BwFresh','Air:\n lda BwVariant\n bne FireInput\n lda BwFresh')
s=s.replace('lda #$3f                   ; original Bowser_Counter1 timeline','''lda #$3f                   ; original source3 Counter1 timeline
 ldx BwVariant
 beq :+
 lda #$20                   ; original source1 mouth timer
:''')
s=s.replace('dec BwBreath\n lda BwBreath','''dec BwBreath
 lda BwVariant
 beq Breathe3
 lda BwBreath
 bne Motion
 inc BwEmit                 ; source1 emits on mouth-closing timer expiry
 jmp Motion
Breathe3:
 lda BwBreath''',1)
s=s.replace('ldx #1\n jsr Bw3AddVelFrac\n jsr BwWorldResolve','''lda BwVariant
 beq Motion3Y
 jsr Bw1Gravity             ; native1 integrates then imposes gravity
 jmp World
Motion3Y:
 ldx #1
 jsr Bw3AddVelFrac
World:
 jsr BwWorldResolve''')
s=s.replace('sta BwFrac+1\n jmp Pose','sta BwFrac+1\n sta BwForceY\n jmp Pose')
s=s.replace('Falling:\n lda BwSlam','Falling:\n lda BwVariant\n bne Pose\n lda BwSlam')
s=s.replace('Pose:\n lda BwBreath','''Pose:
 lda BwVariant
 beq Pose3
 lda BwFrame
 .repeat 5
 lsr
 .endrepeat
 and #1
 sta BwPose
 lda BwBreath
 beq Done
 lda BwPose
 ora #2
 sta BwPose
 jmp Done
Pose3:
 lda BwBreath''')
gravity='''; Literal native ImposeGravity down-only A0 specialization for
; MoveEnemySlowVert: R0=$0F, maximum integer speed2. Same five field writes,
; signed high byte, fractional carry and terminal-fraction threshold.
Bw1Gravity:
 lda BwFrac+1
 clc
 adc BwForceY
 sta BwFrac+1
 ldy #0
 lda BwVel+1
 bpl :+
 dey
:sty BwVerticalSign
 adc BwPos+1
 sta BwPos+1
 lda BwPage+1
 adc BwVerticalSign
 sta BwPage+1
 lda BwForceY
 clc
 adc #$0f
 sta BwForceY
 lda BwVel+1
 adc #0
 sta BwVel+1
 cmp #2
 bmi GravityDone1
 lda BwForceY
 cmp #$80
 bcc GravityDone1
 lda #2
 sta BwVel+1
 lda #0
 sta BwForceY
GravityDone1:rts
'''
s=s.replace("core+'\\n'+'\\n'.join(transformed)","core+'\\n'+"+repr(gravity)+"+'\\n'.join(transformed)")
s=s.replace('SOURCE_NATIVE_SMB3_INTEGRATOR_WITH_AUTHORED_PLAYER_CONTROL_ABSTRACT_CALLBACK_ONLY','BOTH_SOURCE_NATIVE_BOSS_MOTION_WITH_AUTHORED_CONTROLLER_ABSTRACT_CALLBACK_ONLY')
s=s.replace('SMB1 original art only, no SMB1 physics yet. SMB3 original velocity semantics/control kernel compiled;', 'SMB1 native down-only Bowser gravity and original3 velocity/controller kernels compiled;')
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
