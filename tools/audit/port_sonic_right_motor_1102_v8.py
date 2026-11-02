"""Compose original right-input acceleration/braking with horizontal commit."""
import json,random,subprocess,hashlib
from pathlib import Path
import port_sonic_x_velocity_1102_v3 as X
R=X.R;sha=X.sha;NesMPU=X.NesMPU
O=R/'build/sonic-sms-rightmotor-1102-v8'
ASM=X.ASM+'''
RightMotor:
 lda $30
 and #$fd
 sta $30
 lda VB
 bmi Brake
 lda $32
 sta VE
 lda $33
 sta VD
 lda #0
 sta VC
 lda #1
 sta $31
 lda VL
 cmp $36
 lda VH
 sbc $37
 bcc Commit
 lda #0
 sta VB
 sta VE
 sta VD
 sta VC
 lda $36
 sta VL
 lda $37
 sta VH
 lda $38
 sta $31
 jmp Commit
Brake:
 lda $30
 ora #2
 sta $30
 lda #10
 sta $31
 sec
 lda #0
 sbc VL
 lda #0
 sbc VH
 sta $39
 lda $34
 sta VE
 lda $35
 sta VD
 lda #0
 sta VC
 lda $39
 bne Commit
 lda $30
 and #$fd
 sta $30
 lda #1
 sta $31
Commit:
 jmp SonicXVelocity
'''

def right(rom,values,flags,anim,acc,brake,cap,capanim):
    l,h,c,b,e,d=values;r=dict(l=l,h=h,c=c,b=b,e=e,d=d);alt=dict.fromkeys(r,0);stack=[];a=0;carry=z=False;pc=0x4f01
    words={0xd20e:acc,0xd210:brake,0xd240:cap}
    for _ in range(80):
        if pc==0x4b1b:
            assert not stack
            return [r[k] for k in ['l','h','c','b','e','d']],flags,anim
        op=rom[pc];pc+=1
        if op==0xdd:
            sub=rom[pc];pc+=1
            if sub==0xcb:
                off,sub=rom[pc:pc+2];pc+=2;assert off==24
                if sub==0x8e:flags&=253
                elif sub==0xce:flags|=2
                else:raise AssertionError(sub)
            elif sub==0x36:assert rom[pc]==20;anim=rom[pc+1];pc+=2
            elif sub==0x77:assert rom[pc]==20;pc+=1;anim=a
            else:raise AssertionError(sub)
        elif op==0xcb:assert rom[pc]==0x78;pc+=1;z=not(r['b']&128)
        elif op==0x20:
            off=rom[pc];pc+=1
            if not z:pc+=off
        elif op==0xed:
            sub=rom[pc];pc+=1
            if sub==0x5b:
                at=rom[pc]|rom[pc+1]<<8;pc+=2;v=words[at];r['e']=v&255;r['d']=v>>8
            elif sub==0x52:
                n=(r['h']<<8|r['l'])-(r['d']<<8|r['e'])-int(carry);carry=n<0;r['l']=n&255;r['h']=n>>8&255
            else:raise AssertionError(sub)
        elif op==0x0e:r['c']=rom[pc];pc+=1
        elif op==0xe5:stack.append((r['l'],r['h']))
        elif op==0xe1:r['l'],r['h']=stack.pop()
        elif op==0xd9:r,alt=alt,r
        elif op in [0xaf,0xa7]:
            if op==0xaf:a=0
            carry=False;z=a==0
        elif op in [0xda,0xd2,0xc3]:
            dest=rom[pc]|rom[pc+1]<<8;pc+=2
            if op==0xc3 or (carry if op==0xda else not carry):pc=dest
        elif op in [0x47,0x5f,0x57,0x4f,0x6f,0x67]:r[{0x47:'b',0x5f:'e',0x57:'d',0x4f:'c',0x6f:'l',0x67:'h'}[op]]=a
        elif op==0x2a:
            at=rom[pc]|rom[pc+1]<<8;pc+=2;v=words[at];r['l']=v&255;r['h']=v>>8
        elif op==0x3a:assert rom[pc:pc+2]==bytes([0x16,0xd2]);pc+=2;a=capanim
        elif op in [0x7d,0x7c]:a=r['l' if op==0x7d else 'h']
        elif op==0x2f:a^=255
        elif op==0x23:n=((r['h']<<8|r['l'])+1)&65535;r['l']=n&255;r['h']=n>>8
        elif op==0x11:r['e'],r['d']=rom[pc:pc+2];pc+=2
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original bound')

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY { ROM: start=$8000,size=$1000,file=%O; } SEGMENTS { CODE: load=ROM,type=ro; }')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    code=(O/'component.bin').read_bytes();assert code[:65]==(R/'build/sonic-sms-xvelocity-1102-v3/component.bin').read_bytes()
    rng=random.Random(110208);fixtures=[];cycles=[]
    for velocity in [0,1,15,255,256,767,768,769,1536,32767,32768,65279,65280,65520,65535]:
        for flags in [0,2,128,255]:
            for acc,brake,cap in [(16,48,768),(4,12,256),(16,48,1536)]:
                fixtures.append(([velocity&255,velocity>>8,0,255 if velocity&32768 else 0,0,0],flags,0,acc,brake,cap,2))
    fixtures.extend(([rng.randrange(256) for _ in range(6)],rng.randrange(256),rng.randrange(256),rng.randrange(65536),rng.randrange(65536),rng.randrange(65536),rng.randrange(256)) for _ in range(2048))
    for values,flags,anim,acc,brake,cap,capanim in fixtures:
        selected,ef,ea=right(rom,values,flags,anim,acc,brake,cap,capanim)
        old=[values[0],values[1],values[3]];expected,stored,a=X.original(rom,selected,old)
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x10:0x16]=values;m[0x20:0x23]=old;m[0x30:0x39]=[flags,anim,acc&255,acc>>8,brake&255,brake>>8,cap&255,cap>>8,capanim]
        cpu=NesMPU(memory=m,pc=0x8041);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(130):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 bound')
        assert m[0x10:0x16]==expected and m[0x20:0x23]==stored and m[0x30:0x32]==[ef,ea] and cpu.a==a and cpu.sp==224,(values,flags,acc,brake,cap)
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(fixtures),bytes_6502=len(code),cycles=[min(cycles),max(cycles)],ROM_SHA256=sha(donor),scope='Actual original right-input opcode path composed with original horizontal commit vs assembled6502. Acceleration, cap, opposite-direction brake/animation/facing, signed clamp and live register/velocity outputs. No left input/terrain/full physics/host ABI or gameplay claim.',bindings={str(p):sha(p) for p in [Path(__file__),Path(X.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
