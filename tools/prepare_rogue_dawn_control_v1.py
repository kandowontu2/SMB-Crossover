"""Generate/reproduce a separate literal Rogue action-control leaf, no emulator."""
from pathlib import Path
import argparse,json,re,subprocess
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import rogue_dawn_map_v1 as ref
R=Path(__file__).resolve().parents[1]
# Source actual control temporaries, not source room state or a generic hero.
EXTRA={0x55:0x5c17,0x53:0x5c18,0x65:0x5c19,0x64:0x5c1a,0x2a:0x5c1b,
       0x70:0x5c1c,0x72:0x5c1d,0x73:0x5c1e,0x77:0x5c1f,0x58:0x5c7e,0x0e:0x5c7f}
NAMES={0x55:'RdPlayerUpdating',0x53:'RdWalkDelay',0x65:'RdMoveCount',0x64:'RdSlow',0x2a:'RdMorphCooldown',
       0x70:'RdHurtClock',0x72:'RdHurtDirection',0x73:'RdContactFlags',0x77:'RdHurtBlink',0x58:'RdDoorMove',0x0e:'RdControlTemp'}
RANGES=[(0xcc36,0xcc7d),(0xcc8b,0xccbe),(0xccc2,0xcdf6),(0xcdfa,0xce92),(0xcf2e,0xcf6b),
        (0xcf77,0xcfbe),(0xd015,0xd055),(0xd09c,0xd0ea),(0xd0eb,0xd147),(0xd198,0xd1d4),
        (0xd41a,0xd423),(0xd9d4,0xda85)]
FUNCTIONS={0xd095:'RdControlReturn',0xc2c5:'RdTimes16',0xc2bf:'RdDivide16',0xc45c:'RdControlReturn',0xcb96:'RdWalkRequest',0xcbde:'RdControlHurtSound',
  0xcbe2:'RdControlDeathSound',0xcbef:'RdControlMorphSound',0xc7b2:'RdControlHurtLaunch',
  0xcf6b:'RdSetAnimation',0xcf6e:'RdControlSetIndex',0xcfb7:'RdC_CFB7',0xcfbe:'RdControlUpJump',
  0xcfc3:'RdStartJump',0xd002:'RdControlJump',0xd147:'RdStopVertical',0xd055:'RdAirControl',
  0xd150:'RdBombAllocate',0xdc61:'RdSetMaxSpeed',0xc3d4:'RdControlNegate',0xe1e1:'RdControlBitIndex',
  0xd1ee:'RdControlFire',0xd210:'RdControlFireHorizontal',0xd275:'RdControlFireUp',
  0xe7a2:'RdHostProbeUp',0xe7ad:'RdHostProbeDown',0xe880:'RdHostProbeRight',0xe88b:'RdHostProbeLeft',
  0xe8be:'RdHostStagePosition',0xfd8f:'RdHostOffsetPosition',0xd638:'RdHostCommitPosition',
  0xc799:'RdControlUnmorphNotify',0xb119:'RdHostLowHealthSound',0xb11c:'RdHostHealthSound',
  0xdbe6:'RdControlPhysics',0xde4a:'RdHostDrawPlayer',0xdb96:'RdControlAdvance',0xe1cb:'RdControlSpring'}
DATA={0xd097:'RdAirControl::Spin+1',0xd1eb:'RdControlActionFromDirection',0xcc87:'RdControlActionFromDirection',0xccbe:'RdControlRunAnimation',0xccc0:'RdSetGroundAcceleration::Acceleration',
      0xcdf6:'RdControlRunFireAnimation'}

PREFIX='''; Rogue Dawn1.21 actual action/control instruction projection. Source9271411a.
; Include AFTER frozen kernel/weapons/art/render. No default Samus delegation.
; ROOT owns all RdHost* boundaries; no source Metroid room RAM is constructed.
; Native source radius/center and all canonical input bits remain source units.
.include "rogue_dawn_state.inc"
.macpack longbranch
'''
CUSTOM='''
.export RdControlStep,RdControlDispatch,RdControlJump,RdControlSpring
.export RdControlScrew,RdControlPhysics,RdControlDamageComplete
.proc RdControlStep
 lda RdSourceAltPalette
 bne Unsupported
 ldx #0
 stx RdSlot
 inx
 stx RdPlayerUpdating
 jsr RdControlDispatch
 dec RdPlayerUpdating
 rts
Unsupported:clc
 rts
.endproc
.pushseg
.segment "ROGUE_DAWN_CONTROL_AUX"
.proc RdControlDispatch
 lda RdAction
 bmi Stand
 cmp #0
 beq Stand0
 cmp #1
 beq Run
 cmp #2
 beq Jump
 cmp #3
 beq Ball
 cmp #4
 beq Aim
 cmp #5
 beq Door
 cmp #6
 beq JumpAim
 cmp #7
 beq Dead
 cmp #8
 beq Dead2
 cmp #9
 beq Elevator
 clc
 rts
Stand0:clc
 lda #$cc
Stand:jmp RdC_CC36
Run:clc
 lda #$da
 jmp RdC_DA25
Jump:clc
 lda #$da
 jmp RdC_DA0A
Ball:clc
 lda #$d0
 jmp RdC_D0E1
Aim:clc
 lda #$d1
 jmp RdC_D198
Door:clc
 lda #$d3
 jmp RdHostDoor
JumpAim:clc
 lda #$da
 jmp RdC_DA72
Dead:clc
 lda #$d4
 jmp RdC_D41A
Dead2:clc
 lda #$d4
 jmp RdC_D41F
Elevator:clc
 lda #$d4
 jmp RdHostElevator
.endproc
.proc RdControlStandFollow
 cmp #1
 beq Run
 cmp #2
 beq Jump
 cmp #3
 beq Morph
 cmp #4
 beq Aim
 clc
 lda #$c4
 rts
Run:clc
 lda #$cc
 jmp RdC_CC98
Jump:clc
 lda #$cf
 jmp RdStartJump
Morph:clc
 lda #$d0
 jmp RdC_D0B5
Aim:clc
 lda #$cf
 jmp RdC_CF77
.endproc
.proc RdControlAimFollow
 cmp #0
 beq Stand
 cmp #1
 beq Run
 cmp #3
 beq Morph
 cmp #6
 beq Jump
 clc
 lda #$c4
 rts
Stand:clc
 lda #$cf
 jmp RdC_CF55
Run:clc
 lda #$cc
 jmp RdC_CC98
Morph:clc
 lda #$d0
 jmp RdC_D0B5
Jump:clc
 lda #$cf
 jmp RdControlUpJump
.endproc
.popseg
RdControlJump:
 jsr RdCutOrdinaryJump
 jmp RdC_D015
.pushseg
.segment "ROGUE_DAWN_CONTROL_AUX"
RdControlSetIndex:
 sta RdAnimIndex
 lda #0
 sta RdAnimDelay
 rts
RdControlReturn:rts
RdControlUnmorphNotify:
 bit RdVY
 bpl RdControlReturn
 jmp RdStopVertical
RdControlNegate:
 eor #$ff
 clc
 adc #1
 rts
RdControlBitIndex:
 stx RdControlTemp
 ldx #0
Loop:lsr
 bcs Found
 inx
 cpx #8
 bne Loop
Found:txa
 ldx RdControlTemp
 rts
RdControlAdvance:
 pha
 lda #0
 sta RdWeaponColor
 pla
 ldx #0
 ldy RdAnimDelay
 beq Advance
 dec RdAnimDelay
 bne AdvanceDone
Advance:sta RdAnimDelay
 ldy RdAnimIndex
AdvanceRead:cpy #$99
 bcc AdvanceOriginal
 lda RdControlRunExtension-$99,y
 jmp AdvanceCompare
AdvanceOriginal:lda RdArtAnimation,y
AdvanceCompare:cmp #$ff
 beq AdvanceLoop
 sta RdAnimFrame
 iny
 tya
 sta RdAnimIndex
AdvanceDone:rts
AdvanceLoop:ldy RdAnimReset
 jmp AdvanceRead
RdControlRunExtension:.byte 4,3,5,3,$ff ; actual02:860B..860F
RdControlSpring:
 bit RdFresh
 bpl Release
 lda RdFrozenSupport
 bne Admit
 jsr RdHostProbeDown
 bcs Release
Admit:jsr RdSpringAdmitted
 jmp RdC_D11E
Release:jsr RdSpringRelease
 jmp RdC_D11E
RdControlHurtSound:
 lda #4
 ldx #4
 jmp RdControlSound
RdControlDeathSound:
 lda #$80
 ldx #3
 jmp RdControlSound
RdControlMorphSound:
 lda #2
 ldx #3
RdControlSound:
 ora RdSfx,x
 sta RdSfx,x
 rts
RdControlUpJump:
 ldy #$35
 sty RdAnimReset
 dey
 sty RdAnimIndex
 lda #4
 sta RdAnimDelay
 lda #0
 sta RdJumpDistance
 lda #$fc
 sta RdVY
 jsr RdJumpRequest
 ldy #$18
 lda RdGear
 and #2
 beq Gravity
 ldy #$12
Gravity:jsr RdSetJumpGravity
 rts
RdControlHurtLaunch:
 lda RdEnvironment
 bmi Dry
 jsr RdHostProbeDown
 bcs Done
Dry:lda RdVY
 beq Launch
 bpl Done
Launch:lda #$fd
 sta RdVY
 lda #$38
 jsr RdSetGravity
 bit RdEnvironment
 bmi Done
 lda #$fe
 sta RdVY
Done:rts
; Host must apply real native-style BCD damage before this continuation;
; ordinary Samus HP is never read. This is actual post-damage CEDA..CEF9.
RdControlDamageComplete:
 lda RdHealthLo
 and #$f0
 ora RdHealthHi
 beq Death
 bcs RdControlDamageDone
Death:lda #0
 sta RdHealthLo
 sta RdHealthHi
 lda #7
 sta RdAction
 jsr RdControlDeathSound
 jmp RdC_CC8B
RdControlDamageDone:lda #0
 rts
; Public aliases refer to the actual source handlers below.
RdControlScrew=RdC_CD9C
RdControlActionFromDirection:.byte 1,1,3,4
RdControlRunAnimation:.byte $99,$37
RdControlRunFireAnimation:.byte $3f,$3b,$3d,$3f
RdControlFire:
 lda RdHeld
 and #8
 beq RdControlFireHorizontal
 jmp RdControlFireUp
RdControlFireHorizontal:
 jsr RdPrepareHorizontalShot
 bpl FireDenied
 jsr RdHostSpawnProjectile
 jmp RdFireHorizontalFinish
FireDenied:rts
RdControlFireUp:
 jsr RdPrepareUpShot
 bpl FireDenied
 jsr RdHostSpawnProjectile
 jmp RdFireUpFinish
.popseg
; Real source DBE6 environment boundary precedes E2A9 movement. Host geometry
; callbacks have source carryclear=blocked, carryset=one pixel committed.
.proc RdControlPhysics
 jsr RdHostEnvironment
 jsr RdControlVerticalAdmission
 jsr RdHostRelativeY
 lda RdDelta
 bpl Down
 jsr RdControlNegate
 ldy RdSlow
 beq UpCount
 lsr
 beq Horizontal
UpCount:sta RdMoveCount
Up:jsr RdHostMoveUp
 bcs NextUp
 sec
 ror RdVY
 ror RdVerticalFraction
 jmp Horizontal
NextUp:dec RdMoveCount
 bne Up
 beq Horizontal
Down:beq Horizontal
 ldy RdSlow
 beq DownCount
 lsr
 lsr
 beq Horizontal
DownCount:sta RdMoveCount
DownLoop:jsr RdHostMoveDown
 bcs NextDown
 jsr RdGroundCollisionResponse
 jmp Horizontal
NextDown:dec RdMoveCount
 bne DownLoop
Horizontal:jsr RdHorizontalAccelerate
 jsr RdHostRelativeX
 lda RdDelta
 bpl Right
 jsr RdControlNegate
 ldy RdSlow
 beq LeftCount
 lsr
 beq End
LeftCount:sta RdMoveCount
Left:jsr RdHostMoveLeft
 jsr RdControlSideResponse
 dec RdMoveCount
 bne Left
 lda RdDoorMove
 beq End
 lda #1
 jmp RdHostDoorDirection
Right:beq End
 ldy RdSlow
 beq RightCount
 lsr
 beq End
RightCount:sta RdMoveCount
RightLoop:jsr RdHostMoveRight
 jsr RdControlSideResponse
 dec RdMoveCount
 bne RightLoop
 lda RdDoorMove
 beq End
 lda #0
 jmp RdHostDoorDirection
End:rts
.endproc
.proc RdControlSideResponse
 bcs End
 lda #1
 sta RdMoveCount
 lda RdGravity
 bne End
 lda RdAction
 cmp #3
 beq End
 jmp RdC_CF55
End:rts
.endproc
.proc RdControlVerticalAdmission
 lda RdGravity
 bne Accelerate
 lda #$18
 jsr RdSetMaxSpeed
 lda RdY
 clc
 adc RdRadiusY
 and #7
 bne Support
 jsr RdHostProbeDown
 bcc Accelerate
Support:jsr RdHostFindSupport
 lda RdElevator
 bne Accelerate
 lda RdFrozenSupport
 bne Accelerate
 lda #$1a
 jsr RdSetGravity
Accelerate:jmp RdVerticalAccelerate
.endproc
'''

def generate(raw):
    import rogue_dawn_weapons_controls_v1 as w
    projection={s:t for s,t in w.P.items()if not 0x317<=s<=0x31f};projection.update(EXTRA)
    assert raw[16+2*8192+0x60b:16+2*8192+0x610]==bytes([4,3,5,3,255]),'Native run-extension source changed'
    memory=ref.cpu_image(raw,lower_bank=2);d=Disassembler(MPU(memory=memory))
    pcs={};
    for start,end in RANGES:
        pc=start
        while pc<end:
            size,op=d.instruction_at(pc);assert pc+size<=end,(hex(pc),op)
            pcs[pc]=(size,op);pc+=size
    resolve=lambda at:FUNCTIONS.get(at,DATA.get(at,f'RdC_{at:04X}'if at in pcs else None))
    out=PREFIX+''.join(f'{NAMES[s]}=${t:04x} ; source{s:04X}\n'for s,t in EXTRA.items())
    out+='.pushseg\n.segment "ROGUE_DAWN_CORE"\n'+CUSTOM
    for pc,(size,op)in pcs.items():
        if pc==0xcc7a:op='JMP RdControlStandFollow'
        elif pc==0xcd6d:op='JSR RdControlAdvance'
        elif pc==0xd1ce:op='JSR RdC_CD6D'
        elif pc==0xd1d1:pass
        # native branches/calls and absolute RAM/table operands retain the
        # literal opcode and addressing mode after declared address projection.
        match=re.search(r'\$([0-9a-fA-F]{2,4})',op)
        if match and pc not in [0xcc7a,0xcd6d,0xd1ce]:
            at=int(match[1],16)
            if op.startswith(('JMP','JSR','BNE','BEQ','BCC','BCS','BPL','BMI','BVC','BVS')):
                label=resolve(at);assert label,(hex(pc),op,'unbound continuation')
                op=op.replace(match[0],label)
            elif not op.split(' ',1)[1].startswith('#'):
                if at in projection:op=op.replace(match[0],f'${projection[at]:04x}')
                elif at in DATA:op=op.replace(match[0],DATA[at])
                else:raise AssertionError((hex(pc),op,'unprojected RAM/data'))
        if pc==0xd0a1:op='jpl RdControlReturn'
        if pc==0xd0cd:op='LDA RdControlMorphByteWindow,X'
        out+=f'RdC_{pc:04X}: {op.lower() if not re.search("Rd",op) else op} ; source62:{pc:04X}\n'
        if pc+size==0xcf6b:out+=' jmp RdSetAnimation\n'
        if pc+size==0xd1d4:out+=' jmp RdControlAimFollow\n'
    # D1D4 inline table is outside the copied span, so its real tail dispatcher
    # is explicit instead of treating inline words as opcodes.
    out+='RdControlMorphByteWindow:\n'+''.join(' .byte '+','.join(f'${v:02x}'for v in raw[16+62*8192+0xcc0+i:16+62*8192+0xcc0+i+16])+'\n'for i in range(0,256,16))
    out+='.export RdControlEnd\nRdControlEnd:\n.popseg\n'
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--generate',action='store_true');a=p.parse_args()
    raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
    source=R/'src/rogue_dawn_control.s';text=generate(raw)
    if a.generate:source.write_text(text,newline='\n')
    else:assert source.read_text()==text,'Owned source differs from authenticated recipe'
    print(json.dumps(dict(passed=True,source=str(source),bytes=source.stat().st_size,sha256=ref.digest(source.read_bytes()))))
if __name__=='__main__':main()
