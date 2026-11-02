"""Original grounded roll admission and sound request, private 6502 primitive."""
import json,subprocess,hashlib
from pathlib import Path
from port_sonic_x_velocity_1102_v3 import R,sha,NesMPU
O=R/'build/sonic-sms-roll-1102-v7'
ASM='''.setcpu "6502"
.segment "CODE"
; 10 flags,11/12 horizontal velocity,13 level flags,14 sound event.
 lda $10
 and #5
 bne Done
 lda $10
 bpl Done
 ora #1
 sta $10
 lda $11
 ora $12
 beq Quiet
 lda #6
 sta $14
Quiet:
 lda $13
 ora #4
 sta $13
Done:
 rts
'''

def original(rom,state):
    flags,l,h,level,sound=state;pc=0x50c1;a=0;z=False
    for _ in range(24):
        op=rom[pc];pc+=1
        if op in [0xdd,0xfd]:
            assert rom[pc]==0xcb;offset,sub=rom[pc+1:pc+3];pc+=3
            assert offset==(24 if op==0xdd else 7)
            value=flags if op==0xdd else level;bit=(sub>>3)&7
            if sub>>6==1:z=not(value&(1<<bit))
            elif sub>>6==3:
                value|=1<<bit
                if op==0xdd:flags=value
                else:level=value
            else:raise AssertionError(sub)
        elif op in [0xc0,0xc8,0xc9]:
            if op==0xc9 or (z if op==0xc8 else not z):return [flags,state[1],state[2],level,sound]
        elif op==0x2a:
            assert rom[pc:pc+2]==bytes([3,0xd4]);pc+=2;l,h=state[1:3]
        elif op==0x7d:a=l
        elif op==0xb4:a|=h;z=a==0
        elif op==0x28:
            off=rom[pc];pc+=1
            if z:pc+=off
        elif op==0x3e:a=rom[pc];pc+=1
        elif op==0xef:assert a==6;sound=a
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original bound')

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY { ROM: start=$8000,size=$1000,file=%O; } SEGMENTS { CODE: load=ROM,type=ro; }')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    code=(O/'component.bin').read_bytes();cases=0;cycles=[]
    for flags in range(256):
        for velocity in [0,1,255,256,32767,32768,65280,65535]:
            for level in [0,4,251,255]:
                state=[flags,velocity&255,velocity>>8,level,0];expected=original(rom,state)
                m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x10:0x15]=state
                cpu=NesMPU(memory=m,pc=0x8000);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
                for _ in range(30):
                    if cpu.pc==0x5b00:break
                    cpu.step()
                else:raise AssertionError('6502 bound')
                assert m[0x10:0x15]==expected and cpu.sp==224,state;cases+=1;cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=cases,bytes_6502=len(code),cycles=[min(cycles),max(cycles)],ROM_SHA256=sha(donor),source_span='50C1..50E3',source_SHA256=hashlib.sha256(rom[0x50c1:0x50e3]).hexdigest(),scope='Original opcode execution vs native6502 grounded roll admission; all256playerflags, zero/signed velocity boundaries and unrelated level flags. Sound6 request checked at original RST28 boundary; audio, caller registers, rolling motion and host integration unqualified.',bindings={str(p):sha(p) for p in [Path(__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
