"""Original Sonic animation streams, frame reset and speed-dependent clock."""
import json,random,subprocess
from pathlib import Path
import port_sonic_physics_selection_1102_v19 as P
import port_sonic_animation_clock_1102_v5 as C
R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-animation-player-1102-v20'
EXTRA='''
.export AnimationRead,AnimationAdvance
; Private A0 previous animation, A1 frame, A2 subframe, A3 sprite result.
; Current animation is31; caller supplies source post-cap velocity20/21.
AnimationRead:
 lda $31
 cmp #26
 bcs AnimationReject
 cmp #3
 beq AnimationReject
 tax
 lda AnimationLo,x
 sta $8c
 lda AnimationHi,x
 sta $8d
 lda $31
 cmp $a0
 beq AnimationSame
 lda #0
 sta $a1
AnimationSame:
 lda $a1
 cmp AnimationLast,x
 bcc AnimationFetchReady
 beq AnimationFetchReady
AnimationReject:
 clc
 rts
AnimationFetchReady:
 tay
AnimationFetch:
 lda ($8c),y
 bpl AnimationFound
 iny
 lda ($8c),y
 sta $a1
 tay
 jmp AnimationFetch
AnimationFound:
 sta $a3
 sec
 rts
AnimationAdvance:
 lda $31
 sta $a0
 ldx #1
 ldy #48
 cmp #1
 beq AnimationSpeed
 ldx #6
 ldy #80
 cmp #9
 beq AnimationSpeed
 inc $a1
 rts
AnimationSpeed:
 stx $a6
 sty $a7
 lda $20
 sta $a4
 lda $21
 sta $a5
 bpl AnimationPositive
 sec
 lda #0
 sbc $a4
 sta $a4
 lda #0
 sbc $a5
 sta $a5
AnimationPositive:
 lsr $a5
 ror $a4
 clc
 lda $a4
 adc $a2
 sta $a2
 lda $a5
 adc $a6
 adc $a1
 cmp $a7
 bcc AnimationClockStore
 sbc $a7
AnimationClockStore:
 sta $a1
 rts
'''

def original_read(rom,anim,prev,frame):
    """Execute original4C56..4C83, including reset helper521F..5223."""
    assert anim!=3 and 0<=anim<26
    pc=0x4c56;a=0;hl=de=0;c=0;positive=zero=False;stack=[]
    for _ in range(80):
        if pc==0x4c83:return a,frame
        op=rom[pc];pc+=1
        if op==0xdd:
            sub,off=rom[pc:pc+2];pc+=2
            if sub==0x6e:assert off==20;hl=(hl&0xff00)|anim
            elif sub==0x36:assert off==19 and rom[pc]==0;pc+=1;frame=0
            else:raise AssertionError((hex(sub),off))
        elif op==0x4d:c=hl&255
        elif op==0x26:hl=(hl&255)|(rom[pc]<<8);pc+=1
        elif op==0x6f:hl=(hl&0xff00)|a
        elif op==0x3a:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2;a=prev if at==0xd2df else frame if at==0xd40f else None;assert a is not None
        elif op==0x11:de=int.from_bytes(rom[pc:pc+2],'little');pc+=2
        elif op==0x29:hl=hl*2&65535
        elif op==0x19:hl=(hl+de)&65535
        elif op==0x5e:de=(de&0xff00)|rom[hl]
        elif op==0x56:de=(de&255)|(rom[hl]<<8)
        elif op==0x23:hl=(hl+1)&65535
        elif op==0xed:
            assert rom[pc]==0x53 and int.from_bytes(rom[pc+1:pc+3],'little')==0xd40d;pc+=3
        elif op==0x91:a=(a-c)&255;zero=a==0
        elif op==0xc4:
            target=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if not zero:stack.append(pc);pc=target
        elif op==0xc9:pc=stack.pop()
        elif op==0x7e:a=rom[hl]
        elif op==0xa7:positive=not bool(a&128)
        elif op==0xf2:
            target=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if positive:pc=target
        elif op==0xc3:pc=int.from_bytes(rom[pc:pc+2],'little')
        elif op==0x32:
            assert int.from_bytes(rom[pc:pc+2],'little')==0xd40f;pc+=2;frame=a
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original animation read bound')

def main():
    O.mkdir(exist_ok=True)
    donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    prior=R/'build/sonic-sms-physics-selection-1102-v19'
    asm=(prior/'component.s').read_text()+EXTRA;offsets=[];last=[]
    for i in range(26):
        at=int.from_bytes(rom[0x5965+i*2:0x5967+i*2],'little');offsets.append(at-0x5999)
        end=next(j for j in range(256)if rom[at+j]&128);last.append(end)
        target=rom[at+end+1]
        assert target<=end and(i==3 or not rom[at+target]&128)
    assert offsets[0]==offsets[1]==0 and last[3]==0
    for label,operator in [('AnimationLo','<'),('AnimationHi','>')]:asm+='\n'+label+':\n.byte '+','.join(operator+'(AnimationData+'+str(at)+')'for at in offsets)+'\n'
    asm+='\nAnimationLast:\n.byte '+','.join(map(str,last))+'\nAnimationData:\n.byte '+','.join(map(str,rom[0x5999:0x5b09]))+'\n'
    (O/'component.s').write_text(asm);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$2000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-Ln',O/'labels.txt','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    labels={line.split()[2].lstrip('.'):int(line.split()[1],16)for line in (O/'labels.txt').read_text().splitlines()}
    code=(O/'component.bin').read_bytes();old=(prior/'component.bin').read_bytes();assert code[:len(old)]==old
    rng=random.Random(110220);cases=[];cycles=[]
    for anim in range(26):
        if anim==3:continue
        for frame in range(last[anim]+1):
            for prev in [anim,255]:cases.append((anim,prev,frame,rng.randrange(256),rng.randrange(65536)))
    cases.extend((anim,rng.randrange(26),rng.randrange(last[anim]+1),rng.randrange(256),rng.randrange(65536))for anim in [a for a in range(26)if a!=3]for _ in range(64))
    def run(m,entry):
        cpu=NesMPU(memory=m,pc=labels[entry]);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(100):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 animation bound')
        assert cpu.sp==224;return cpu
    for anim,prev,frame,sub,velocity in cases:
        sprite,selected=original_read(rom,anim,prev,frame)
        expected=C.original(rom,velocity,sub,selected,1 if anim==1 else 6,48 if anim==1 else 80)if anim in [1,9]else(sub,(selected+1)&255)
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x31]=anim;m[0x20:0x22]=[velocity&255,velocity>>8];m[0xa0:0xa4]=[prev,frame,sub,255]
        read=run(m,'AnimationRead');assert read.p&1 and m[0xa3]==sprite and m[0xa1]==selected
        advance=run(m,'AnimationAdvance');assert m[0xa0]==anim and(m[0xa2],m[0xa1])==expected
        assert m[0x20:0x22]==[velocity&255,velocity>>8]
        cycles.append(read.processorCycles+advance.processorCycles)
    rejected=0
    for anim in [3,*range(26,256)]:
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x31]=anim;m[0xa0:0xa4]=[7,8,9,10]
        cpu=run(m,'AnimationRead');assert not cpu.p&1 and m[0xa0:0xa4]==[7,8,9,10];rejected+=1
    result=dict(passed=True,private=True,installed=False,cases=len(cases),invalid_animation_rejections=rejected,bytes_6502=len(code),added_bytes=len(code)-len(old),cycles_read_and_advance=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Actual4C56..4C83 opcode execution plus original speed-clock4DA8..4DCB versus6502, all25valid source animation streams/every frame including loopmarker, transition frame reset without resetting subframe, ordinary increment and walking/rolling clocks. Original empty03 hangs; invalid index03/outside26 rejected as non-source gameplay state. Private frame/sprite selector only; full Main pose choice, source post-cap placement, CHR conversion/OAM/audio/native admission incomplete.',bindings={str(p):sha(p)for p in [Path(__file__),Path(C.__file__),prior/'component.s',O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
