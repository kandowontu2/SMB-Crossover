"""Private vertical commit/bounce primitive; actual SMS instruction oracle."""
import hashlib,json,random,subprocess
from pathlib import Path
from port_sonic_x_velocity_1102_v3 import R,sha,NesMPU
O=R/'build/sonic-sms-yvelocity-1102-v4'
ASM='''.setcpu "6502"
.segment "CODE"
; Fixture-only addresses; no native RAM allocation.
 clc
 lda $10
 adc $14
 sta $10
 sta $23
 lda $11
 adc $15
 sta $11
 sta $24
 lda $13
 adc $12
 sta $25
 sec
 lda #0
 sbc $14
 sta $26
 lda #0
 sbc $15
 sta $27
 lda #0
 sbc $12
 sta $28
 ldx #1
 stx $14
 dex
 stx $15
 rts
'''

def original(rom,values):
    l,h,c,b,e,d=values; a=0;carry=False;pc=0x4bd6;stack=[];out={}
    for _ in range(32):
        if pc==0x4bf5:
            assert not stack
            return [l,h,c,b,e,d],[out[x] for x in [0xd406,0xd407,0xd408,0xd2e6,0xd2e7,0xd2e8]],a
        op=rom[pc];pc+=1
        if op==0x19:
            n=(h<<8|l)+(d<<8|e);l=n&255;h=n>>8&255;carry=n>65535
        elif op==0x78:a=b
        elif op==0x89:
            n=a+c+int(carry);a=n&255;carry=n>255
        elif op in [0x22,0x32]:
            addr=rom[pc]|rom[pc+1]<<8;pc+=2
            if op==0x22:out[addr]=l;out[addr+1]=h
            else:out[addr]=a
        elif op==0xe5:stack.append((l,h))
        elif op==0xe1:l,h=stack.pop()
        elif op==0x7b:a=e
        elif op==0x7a:a=d
        elif op==0x79:a=c
        elif op==0x2f:a^=255
        elif op==0x6f:l=a
        elif op==0x67:h=a
        elif op==0x11:e,d=rom[pc:pc+2];pc+=2
        elif op==0xce:
            n=a+rom[pc]+int(carry);pc+=1;a=n&255;carry=n>255
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original bound')

def main():
    O.mkdir(exist_ok=True)
    donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms'
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    rom=donor.read_bytes();(O/'component.s').write_text(ASM)
    (O/'component.cfg').write_text('MEMORY { ROM: start=$8000,size=$1000,file=%O; } SEGMENTS { CODE: load=ROM,type=ro; }')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    binary=(O/'component.bin').read_bytes();rng=random.Random(110204);cycles=[]
    edges=[0,1,127,128,254,255]
    cases=[[l,255,c,b,e,d] for l in edges for c in edges for b in edges for e in edges for d in [0,255]]
    cases.extend([rng.randrange(256) for _ in range(6)] for _ in range(4096))
    for values in cases:
        expected,stored,a=original(rom,values)
        m=[0]*65536;m[0x8000:0x8000+len(binary)]=binary;m[0x10:0x16]=values
        cpu=NesMPU(memory=m,pc=0x8000);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(60):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 bound')
        assert m[0x10:0x16]==expected and m[0x23:0x29]==stored and cpu.a==a,(values,expected,stored)
        assert cpu.sp==224
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(cases),bytes_6502=len(binary),cycles_min=min(cycles),cycles_max=max(cycles),original_ROM_SHA256=sha(donor),original_range='bank1:4BD6..4BF5 exclusive',original_bytes_SHA256=hashlib.sha256(rom[0x4bd6:0x4bf5]).hexdigest(),scope='Actual original opcode execution versus 6502: live HL/C/B/DE, vertical velocity, negated acceleration bounce value, final A and stack balance. No full caller flags, host allocation or gameplay claim.',bindings={str(p):sha(p) for p in [Path(__file__),O/'component.s',O/'component.cfg',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
