"""First private SMS-to-6502 primitive, checked against executed original bytes."""
import hashlib,json,random,subprocess,sys,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
sys.path.insert(0,str(R/'tools'))
from verify_native_relocation import NesMPU
O=R/'build/sonic-sms-xvelocity-1102-v3'

ASM='''; Original SMS bank1:4B1B..4B48 horizontal velocity commit.
; CPU-fixture addresses only. No host RAM allocation or ROM integration.
.setcpu "6502"
.export SonicXVelocity
VL=$10
VH=$11
VC=$12
VB=$13
VE=$14
VD=$15
OldV=$20
.segment "CODE"
SonicXVelocity:
 lda VB
 bmi Left
 jsr AddVelocity
 bpl Store
 lda OldV
 ora OldV+1
 ora OldV+2
 beq Store
 bne Zero
Left:
 jsr AddVelocity
 bmi Store
Zero:
 lda #0
 sta VC
 sta VL
 sta VH
Store:
 lda VL
 sta OldV
 lda VH
 sta OldV+1
 lda VC
 sta OldV+2
 rts
AddVelocity:
 clc
 lda VL
 adc VE
 sta VL
 lda VH
 adc VD
 sta VH
 lda VB
 adc VC
 sta VC
 rts
'''

def original(rom,values,old):
    l,h,c,b,e,d=values;pc=0x4b1b;a=0;s=z=carry=False
    output=list(old)
    def flags(v):return bool(v&128),v==0
    for steps in range(40):
        if pc==0x4b49:return [l,h,c,b,e,d],output,a
        op=rom[pc];pc+=1
        if op==0x78:a=b
        elif op==0xa7:s,z=flags(a);carry=False
        elif op in [0xfa,0xf2,0xc3]:
            dest=rom[pc]|rom[pc+1]<<8;pc+=2
            if op==0xc3 or (s if op==0xfa else not s):pc=dest
        elif op==0x19:
            total=(h<<8|l)+(d<<8|e);l=total&255;h=(total>>8)&255;carry=total>65535
        elif op==0x89:
            total=a+c+int(carry);a=total&255;carry=total>255;s,z=flags(a)
        elif op==0x4f:c=a
        elif op==0x3a:
            addr=rom[pc]|rom[pc+1]<<8;pc+=2;assert addr==0xd403;a=old[0]
        elif op==0xdd:
            sub,off=rom[pc:pc+2];pc+=2;assert sub==0xb6 and off in [8,9]
            a|=old[off-7];s,z=flags(a);carry=False
        elif op==0x28:
            delta=rom[pc];pc+=1
            if z:pc+=delta if delta<128 else delta-256
        elif op==0x0e:c=rom[pc];pc+=1
        elif op==0x69:l=c
        elif op==0x61:h=c
        elif op==0x79:a=c
        elif op in [0x22,0x32]:
            addr=rom[pc]|rom[pc+1]<<8;pc+=2
            if op==0x22:assert addr==0xd403;output[:2]=[l,h]
            else:assert addr==0xd405;output[2]=a
        else:raise AssertionError(('Unsupported original instruction',hex(pc-1),hex(op)))
    raise AssertionError('Original routine bound')

def main():
    O.mkdir(exist_ok=True)
    donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms'
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    rom=donor.read_bytes();(O/'component.s').write_text(ASM)
    (O/'component.cfg').write_text('MEMORY { ROM: start=$8000,size=$1000,file=%O; } SEGMENTS { CODE: load=ROM,type=ro; }')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        result=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert result.returncode==0,result.stderr
    binary=(O/'component.bin').read_bytes();rng=random.Random(110203);cases=0;cycles=[]
    edges=[0,1,7,15,16,127,128,254,255]
    fixtures=[]
    for high in [0,1,127,128,254,255]:
        for delta_high in [0,127,128,255]:
            for lo in edges:
                for delta in edges:
                    for previous in [[0,0,0],[1,0,0],[255,255,255]]:
                        fixtures.append(([lo,255,high,delta_high,delta,0],previous))
    fixtures.extend(([rng.randrange(256) for _ in range(6)],[rng.randrange(256) for _ in range(3)]) for _ in range(4096))
    for values,old in fixtures:
        expected,stored,a=original(rom,values,old)
        memory=[0]*65536;memory[0x8000:0x8000+len(binary)]=binary;memory[0x10:0x16]=values;memory[0x20:0x23]=old
        cpu=NesMPU(memory=memory,pc=0x8000);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(70):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 bound')
        assert memory[0x10:0x16]==expected and memory[0x20:0x23]==stored and cpu.a==a,(values,old,expected,stored,memory[0x10:0x16],memory[0x20:0x23])
        assert cpu.sp==224
        cycles.append(cpu.processorCycles);cases+=1
    q=dict(passed=True,private=True,installed=False,original_ROM_SHA256=sha(donor),original_range='bank1:4B1B..4B49 exclusive',original_bytes_SHA256=hashlib.sha256(rom[0x4b1b:0x4b49]).hexdigest(),
           bytes_6502=len(binary),cases=cases,cycles_min=min(cycles),cycles_max=max(cycles),
           scope='Exact original opcode interpreter vs assembled6502 horizontal velocity commit, sign-crossing clamp and zero-velocity exception. Live HL/C/B/DE and stored24-bit velocity plus finalA compared. No full player/caller ABI, host allocation, physics sequence, sprite or gameplay claim.',
           bindings={str(p):sha(p) for p in [Path(__file__),O/'component.s',O/'component.cfg',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
