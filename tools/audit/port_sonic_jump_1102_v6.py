"""Original SMS non-rolling jump latch/countdown/gravity path, private 6502."""
import json,random,subprocess,hashlib
from pathlib import Path
from port_sonic_x_velocity_1102_v3 import R,sha,NesMPU
O=R/'build/sonic-sms-jump-1102-v6'
ASM='''.setcpu "6502"
.segment "CODE"
; Private fixture: HL10/11 B12 C13 E14 D15 flags16 input17 timer18
; jump19/1A gravity1B/1C terminal1D sound-event1E.
 lda $18
 bne Continue
 lda $16
 and #$80
 beq Suppress
 lda $16
 and #8
 bne Continue
 lda $17
 and #$20
 beq Suppress
Continue:
 lda $17
 and #$20
 bne Release
 lda $18
 bne Held
 lda #16
 sta $18
 lda #1
 sta $1e
Held:
 lda $19
 sta $10
 lda $1a
 sta $11
 lda #255
 sta $12
 lda #0
 sta $13
 sta $14
 sta $15
 dec $18
 lda $16
 ora #4
 sta $16
 rts
Suppress:
 lda $16
 and #$f7
 sta $16
 jmp Stop
Release:
 lda $16
 ora #8
 sta $16
Stop:
 lda #0
 sta $18
 lda $11
 bmi Gravity
 cmp $1d
 bcs Done
Gravity:
 lda $1b
 sta $14
 lda $1c
 sta $15
 lda #0
 sta $13
Done:
 rts
'''

def original(rom,state):
    m=list(state);pc=0x4b61;a=0;z=False;carry=False;stack=[]
    memory={0xd28e:8,0xd242:9,0xd243:10,0xd244:11,0xd245:12,0xd215:13}
    for _ in range(90):
        if pc==0x4bbe:
            assert not stack
            return m
        op=rom[pc];pc+=1
        if op==0x3a:
            addr=rom[pc]|rom[pc+1]<<8;pc+=2;a=m[memory[addr]]
        elif op==0xa7:z=a==0;carry=False
        elif op in [0x20,0x28,0x38]:
            off=rom[pc];pc+=1
            if (not z if op==0x20 else z if op==0x28 else carry):pc+=off if off<128 else off-256
        elif op in [0xdd,0xfd]:
            assert rom[pc]==0xcb;off,sub=rom[pc+1:pc+3];pc+=3
            idx=6 if op==0xdd else 7
            assert off==(24 if op==0xdd else 3)
            bit=(sub>>3)&7;group=sub>>6
            if group==1:z=not(m[idx]&(1<<bit))
            elif group==2:m[idx]&=255^(1<<bit)
            elif group==3:m[idx]|=1<<bit
            else:raise AssertionError(sub)
        elif op==0xcc:
            dest=rom[pc]|rom[pc+1]<<8;pc+=2
            if z:stack.append(pc);pc=dest
        elif op==0x3e:a=rom[pc];pc+=1
        elif op==0x32:
            addr=rom[pc]|rom[pc+1]<<8;pc+=2;m[memory[addr]]=a
        elif op==0xef:
            assert a==0;m[14]=1 # Original RST28 sound request, boundary only.
        elif op==0xc9:pc=stack.pop()
        elif op==0x2a:
            addr=rom[pc]|rom[pc+1]<<8;pc+=2;i=memory[addr];m[0:2]=m[i:i+2]
        elif op in [0x06,0x0e]:m[2 if op==0x06 else 3]=rom[pc];pc+=1
        elif op==0x59:m[4]=m[3]
        elif op==0x51:m[5]=m[3]
        elif op==0x3d:a=(a-1)&255;z=a==0
        elif op==0xc3:pc=rom[pc]|rom[pc+1]<<8
        elif op==0xaf:a=0;z=True;carry=False
        elif op==0xcb:
            assert rom[pc]==0x7c;pc+=1;z=not(m[1]&128)
        elif op==0xbc:z=a==m[1];carry=a<m[1]
        elif op==0xed:
            assert rom[pc]==0x5b;addr=rom[pc+1]|rom[pc+2]<<8;pc+=3;i=memory[addr];m[4:6]=m[i:i+2]
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original bound')

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY { ROM: start=$8000,size=$1000,file=%O; } SEGMENTS { CODE: load=ROM,type=ro; }')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    code=(O/'component.bin').read_bytes();cases=[];cycles=[];rng=random.Random(110206)
    for flags in range(256):
        for input_ in [0xdf,0xff]:
            for timer in [0,1,2,15,16,255]:
                for vy in [0,0x7ff,0x800,0xfc80,0xffff]:
                    cases.append([vy&255,vy>>8,255 if vy&32768 else 0,0,0,0,flags,input_,timer,0x80,0xfc,0x38,0,8,0])
    cases.extend([rng.randrange(256) for _ in range(14)]+[0] for _ in range(2048))
    def execute(state):
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x10:0x1f]=state
        cpu=NesMPU(memory=m,pc=0x8000);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(65):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 bound')
        assert cpu.sp==224;cycles.append(cpu.processorCycles);return m[0x10:0x1f]
    for state in cases:assert execute(state)==original(rom,state),state
    episodes=0
    for held in range(1,25):
        actual=[0,0,0,0,0,0,0x88,0xff,0,0x80,0xfc,0x38,0,8,0];expected=actual[:]
        for tick in range(40):
            for state in [actual,expected]:state[7]=0xdf if tick<held else 0xff;state[14]=0
            actual=execute(actual);expected=original(rom,expected);assert actual==expected
        episodes+=1
    q=dict(passed=True,private=True,installed=False,cases=len(cases),button_episodes=episodes,bytes_6502=len(code),cycles=[min(cycles),max(cycles)],ROM_SHA256=sha(donor),source_spans=['4B61..4BBE','509D..50A6'],source_SHA256=hashlib.sha256(rom[0x4b61:0x4bbe]+rom[0x509d:0x50a6]).hexdigest(),scope='Actual original opcode execution vs assembled non-rolling jump latch/countdown and gravity selection. Original jump sound request observed at boundary, not audio driver. Full state payload and held/released episodes compared. Landing/rolling/upside-down caller, native ABI, terrain and gameplay remain unqualified.',bindings={str(p):sha(p) for p in [Path(__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
