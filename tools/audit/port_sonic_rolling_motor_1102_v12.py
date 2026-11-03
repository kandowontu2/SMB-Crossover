"""Translate the original SMS rolling caller and execute both CPUs privately."""
import json, random, subprocess
from pathlib import Path
import port_sonic_horizontal_caller_1102_v11 as P
R=P.R; sha=P.sha; NesMPU=P.NesMPU
O=R/'build/sonic-sms-rolling-1102-v12'
ASM=P.ASM+'''
RollingBody:
 lda #0
 sta $49
 lda $42
 cmp #24
 beq RollHeightReady
 clc
 lda $43
 adc #8
 sta $43
 lda $44
 adc #0
 sta $44
RollHeightReady:
 lda #24
 sta $41
 sta $42
 lda OldV
 sta VL
 lda OldV+1
 sta VH
 lda OldV+2
 sta VB
 lda #0
 sta VC
 sta VE
 sta VD
 lda VL
 ora VH
 ora VB
 bne RollMoving
 jmp RollStationary
RollMoving:
 lda #9
 sta $31
 lda $40
 and #4
 bne RollCheckRight
 lda $40
 and #2
 beq RollCheckRight
 lda $30
 bpl RollGoLeft
 lda VB
 bmi RollFriction
 jmp RollBrake
RollGoLeft:
 lda #$f0
 sta VE
 lda #$ff
 sta VD
 sta VC
 jmp RollCommit
RollCheckRight:
 lda $40
 and #8
 bne RollFriction
 lda $40
 and #2
 beq RollFriction
 lda $30
 bpl RollGoRight
 lda VB
 bpl RollFriction
 jmp RollBrake
RollGoRight:
 lda #16
 sta VE
 lda #0
 sta VD
 sta VC
 jmp RollCommit
RollFriction:
 lda #4
 sta VE
 lda #0
 sta VD
 sta VC
 lda VB
 bpl RollFrictionPositive
 jmp RollCommit
RollFrictionPositive:
 lda #$fc
 sta VE
 lda #$ff
 sta VD
 sta VC
 jmp RollCommit
RollBrake:
 lda $30
 and #$fc
 sta $30
 lda #10
 sta $31
 jsr RollNegBrake
 lda #$ff
 sta VC
 lda VH
 bne RollCommit
 lda $30
 ora #2
 sta $30
 lda #1
 sta $31
 jmp RollCommit
RollStationary:
 lda $30
 bmi RollLookDown
 lda #9
 sta $31
 ; The original zero-speed airborne path still runs speed-cap selection.
 lda VL
 cmp $36
 lda VH
 sbc $37
 bcc RollCommit
 lda #0
 sta VC
 sta VE
 sta VD
 jmp RollCommit
RollLookDown:
 lda #7
 sta $31
 lda $30
 and #$fe
 sta $30
 lda $48
 sta VD
 lda $47
 sta VE
 lda VD
 bpl RollCameraDec
 ; Signed camera offsets stop decrementing at -80.
 sec
 lda #$b0
 sbc VE
 sta VL
 lda #$ff
 sbc VD
 sta VH
 bcs RollReturn
RollCameraDec:
 lda VE
 bne RollCameraLow
 dec VD
RollCameraLow:
 dec VE
 lda VE
 sta $47
 lda VD
 sta $48
RollReturn:
 rts
RollCommit:
 lda #1
 sta $49
 jmp SonicXVelocity
RollNegBrake:
 sec
 lda #0
 sbc $34
 sta VE
 lda #0
 sbc $35
 sta VD
 rts
'''

def original(rom, old, height, y, inp, flags, anim, brake, cap, camera):
    """Interpret the pinned donor instructions, not a duplicate motion formula."""
    r=dict(l=0,h=0,c=0,b=0,e=0,d=0); alt=r.copy(); stack=[]
    pc=0x532e; a=0; z=carry=sign=False; width=99
    words={0xd401:y,0xd403:old[0]|old[1]<<8,0xd210:brake,0xd240:cap,0xd2b7:camera}
    for _ in range(160):
        if pc in [0x4b1b,0x4b49]:
            assert not stack
            values=[r[k]for k in ['l','h','c','b','e','d']]
            return values,flags,anim,width,height,words[0xd401],words[0xd2b7],pc==0x4b1b
        op=rom[pc]; pc+=1
        if op in [0xdd,0xfd]:
            sub=rom[pc];pc+=1
            if sub==0xcb:
                off,sub=rom[pc:pc+2];pc+=2
                assert off==(24 if op==0xdd else 3)
                v=flags if op==0xdd else inp;bit=(sub>>3)&7;group=sub>>6
                if group==1:z=not(v&(1<<bit));sign=bit==7 and not z
                elif group==2:assert op==0xdd;flags&=255^(1<<bit)
                elif group==3:assert op==0xdd;flags|=1<<bit
                else:raise AssertionError(sub)
            else:
                off=rom[pc];pc+=1;assert op==0xdd
                if sub==0x7e:assert off==14;a=height
                elif sub==0x46:assert off==9;r['b']=old[2]
                elif sub==0x36:
                    v=rom[pc];pc+=1
                    if off==13:width=v
                    elif off==14:height=v
                    elif off==20:anim=v
                    else:raise AssertionError(off)
                else:raise AssertionError(sub)
        elif op==0xfe:z=a==rom[pc];carry=a<rom[pc];sign=bool((a-rom[pc])&128);pc+=1
        elif op in [0x20,0x28]:
            off=rom[pc];pc+=1
            if (not z if op==0x20 else z):pc+=off if off<128 else off-256
        elif op in [0xc3,0xca,0xda,0xd2,0xfa]:
            at=rom[pc]|rom[pc+1]<<8;pc+=2
            if op==0xc3 or {0xca:z,0xda:carry,0xd2:not carry,0xfa:sign}.get(op,False):pc=at
        elif op==0x2a:
            at=rom[pc]|rom[pc+1]<<8;pc+=2;v=words[at];r['l']=v&255;r['h']=v>>8
        elif op==0x22:
            at=rom[pc]|rom[pc+1]<<8;pc+=2;words[at]=r['h']<<8|r['l']
        elif op==0x21:r['l'],r['h']=rom[pc:pc+2];pc+=2
        elif op==0x11:r['e'],r['d']=rom[pc:pc+2];pc+=2
        elif op==0x01:r['c'],r['b']=rom[pc:pc+2];pc+=2
        elif op==0x0e:r['c']=rom[pc];pc+=1
        elif op in [0x59,0x51]:r['e' if op==0x59 else 'd']=r['c']
        elif op in [0x7c,0x7d,0x78,0x7b,0x7a]:a=r[{0x7c:'h',0x7d:'l',0x78:'b',0x7b:'e',0x7a:'d'}[op]]
        elif op in [0xb5,0xb0]:a|=r['l' if op==0xb5 else 'b'];z=a==0;carry=False;sign=bool(a&128)
        elif op in [0xa7,0xaf]:
            if op==0xaf:a=0
            z=a==0;carry=False;sign=bool(a&128)
        elif op==0x2f:a^=255
        elif op in [0x6f,0x67,0x5f,0x57,0x4f]:r[{0x6f:'l',0x67:'h',0x5f:'e',0x57:'d',0x4f:'c'}[op]]=a
        elif op in [0x23,0x13,0x1b]:
            lo,hi=('l','h')if op==0x23 else ('e','d');v=((r[hi]<<8|r[lo])+(-1 if op==0x1b else 1))&65535;r[lo]=v&255;r[hi]=v>>8
        elif op==0x19:
            v=(r['h']<<8|r['l'])+(r['d']<<8|r['e']);carry=v>65535;r['l']=v&255;r['h']=v>>8&255
        elif op==0xcb:
            sub=rom[pc];pc+=1;assert sub in [0x78,0x7a]
            z=not(r['b' if sub==0x78 else 'd']&128);sign=not z
        elif op==0xed:
            sub=rom[pc];pc+=1
            if sub in [0x5b,0x53]:
                at=rom[pc]|rom[pc+1]<<8;pc+=2
                if sub==0x5b:v=words[at];r['e']=v&255;r['d']=v>>8
                else:words[at]=r['d']<<8|r['e']
            elif sub in [0x52,0x42]:
                v=(r['h']<<8|r['l'])-(r['d']<<8|r['e'] if sub==0x52 else r['b']<<8|r['c'])-int(carry)
                carry=v<0;r['l']=v&255;r['h']=v>>8&255;z=(v&65535)==0;sign=bool(v&32768)
            else:raise AssertionError(sub)
        elif op in [0xd5,0xe5]:stack.append((r['e'],r['d'])if op==0xd5 else (r['l'],r['h']))
        elif op in [0xd1,0xe1]:
            lo,hi=('e','d')if op==0xd1 else ('l','h');r[lo],r[hi]=stack.pop()
        elif op==0xd9:r,alt=alt,r
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original rolling bound')

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        z=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    code=(O/'component.bin').read_bytes();prior=(R/'build/sonic-sms-horizontal-1102-v11/component.bin').read_bytes();assert code[:len(prior)]==prior
    rng=random.Random(110212);fixtures=[];cycles=[];camera_paths=0
    for inp in range(256):
        for flags in [0,1,128,129,130,255]:
            for vel in [0,255,256,768,65535]:fixtures.append(([vel&255,vel>>8,255 if vel&32768 else 0],32,65532,inp,flags,5,48,768,65535))
    for camera in [0,1,32767,32768,65454,65455,65456,65457,65535]:
        for height in [0,24,32,255]:fixtures.append(([0,0,0],height,65532,255,129,5,48,768,camera))
    fixtures.extend(([rng.randrange(256)for _ in range(3)],rng.randrange(256),rng.randrange(65536),rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(65536),rng.randrange(65536),rng.randrange(65536))for _ in range(2048))
    for f in fixtures:
        old,height,y,inp,flags,anim,brake,cap,camera=f
        values,ef,ea,width,eh,ey,ec,commit=original(rom,*f)
        if commit:expected,stored,_=P.P.P.P.X.original(rom,values,old)
        else:expected,stored=values,old;camera_paths+=1
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x20:0x23]=old;m[0x30:0x39]=[flags,anim,16,0,brake&255,brake>>8,cap&255,cap>>8,2]
        m[0x40:0x4a]=[inp,99,height,y&255,y>>8,8,0,camera&255,camera>>8,99]
        cpu=NesMPU(memory=m,pc=0x8000+len(prior));cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(240):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 rolling bound')
        assert m[0x10:0x16]==expected and m[0x20:0x23]==stored and m[0x30:0x32]==[ef,ea],(f,expected,m[0x10:0x16],ef,ea,m[0x30:0x32])
        assert m[0x41:0x45]==[width,eh,ey&255,ey>>8] and m[0x47:0x4a]==[ec&255,ec>>8,int(commit)] and cpu.sp==224,f
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(fixtures),camera_paths=camera_paths,bytes_6502=len(code),added_bytes=len(code)-len(prior),cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Executed original532E..5407 rolling body/input/friction/ground braking/look-down and horizontal commit against assembled6502. All256 active-low inputs, signed velocities, body dimensions, camera stop boundary. Full rolling jump/terrain/Main/native integration remain incomplete.',bindings={str(p):sha(p)for p in [Path(__file__),Path(P.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
