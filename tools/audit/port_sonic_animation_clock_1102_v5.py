"""Source-bound SMS Sonic walking/rolling animation clock, private fixture."""
import json,random,subprocess,hashlib
from pathlib import Path
from port_sonic_x_velocity_1102_v3 import R,sha,NesMPU
O=R/'build/sonic-sms-animation-1102-v5'
ASM='''.setcpu "6502"
.segment "CODE"
; 10/11 velocity,12 subframe,13 frame,14 base,15 period.
 lda $11
 bpl Positive
 sec
 lda #0
 sbc $10
 sta $10
 lda #0
 sbc $11
 sta $11
Positive:
 lsr $11
 ror $10
 clc
 lda $10
 adc $12
 sta $12
 lda $11
 adc $14
 adc $13
 cmp $15
 bcc Store
 sbc $15
Store:
 sta $13
 rts
'''

def original(rom,v,sub,frame,base,period):
    l=v&255;h=v>>8;b=sub;d=base;c=period;a=0;carry=False;z=False;pc=0x4da8
    for _ in range(40):
        op=rom[pc];pc+=1
        if op==0xcb:
            op=rom[pc];pc+=1
            if op==0x7c:z=not(h&128)
            elif op==0x3c:carry=bool(h&1);h>>=1
            elif op==0x1d:n=l;l=(l>>1)|(int(carry)<<7);carry=bool(n&1)
            else:raise AssertionError(op)
        elif op==0x28:
            offset=rom[pc];pc+=1
            if z:pc+=offset
        elif op==0x7d:a=l
        elif op==0x7c:a=h
        elif op==0x2f:a^=255
        elif op==0x6f:l=a
        elif op==0x67:h=a
        elif op==0x23:n=((h<<8|l)+1)&65535;l=n&255;h=n>>8
        elif op in [0x80,0x8a]:
            n=a+(b if op==0x80 else d)+(int(carry) if op==0x8a else 0);a=n&255;carry=n>255
        elif op==0xdd:
            assert rom[pc:pc+2]==bytes([0x8e,0x13]);pc+=2;n=a+frame+int(carry);a=n&255;carry=n>255
        elif op==0x32:
            at=rom[pc]|rom[pc+1]<<8;pc+=2
            if at==0xd2e0:sub=a
            elif at==0xd40f:frame=a
            else:raise AssertionError(at)
        elif op==0xb9:carry=a<c
        elif op==0xd8:
            if carry:return sub,frame
        elif op==0x91:a=(a-c)&255
        elif op==0xc9:return sub,frame
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original bound')

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY { ROM: start=$8000,size=$1000,file=%O; } SEGMENTS { CODE: load=ROM,type=ro; }')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    code=(O/'component.bin').read_bytes();rng=random.Random(110205);cases=[];cycles=[]
    for v in [0,1,255,256,257,768,32767,32768,65280,65535]:
        for sub in [0,1,127,254,255]:
            for base,period in [(1,48),(6,80)]:
                for frame in range(period):cases.append((v,sub,frame,base,period))
    cases.extend((rng.randrange(65536),rng.randrange(256),rng.randrange(256),*rng.choice([(1,48),(6,80)])) for _ in range(4096))
    for v,sub,frame,base,period in cases:
        expected=original(rom,v,sub,frame,base,period)
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x10:0x16]=[v&255,v>>8,sub,frame,base,period]
        cpu=NesMPU(memory=m,pc=0x8000);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(50):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 bound')
        assert tuple(m[0x12:0x14])==expected,(v,sub,frame,base,period,expected,m[0x12:0x14])
        assert cpu.sp==224;cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(cases),bytes_6502=len(code),cycles=[min(cycles),max(cycles)],source_ROM_SHA256=sha(donor),original_span='bank1:4DA8..4DCB',original_span_SHA256=hashlib.sha256(rom[0x4da8:0x4dcb]).hexdigest(),scope='Original opcode execution versus assembled walking/rolling speed-driven frame/subframe update. Includes original chained ADC carry and single period subtraction; caller registers/flags, renderer, host allocation and gameplay remain unqualified.',bindings={str(p):sha(p) for p in [Path(__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
