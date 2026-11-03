"""Original post-object 24-bit XY integration, connected to the motion kernel."""
import json,random,subprocess
from pathlib import Path
import compose_sonic_motion_1102_v14 as P
R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-position-1102-v15'
ASM=P.ASM+'''
.export PositionStep,MotionAndPosition
PositionStep:
 clc
 lda $70
 adc $20
 sta $70
 lda $71
 adc $21
 sta $71
 lda $72
 adc $22
 sta $72
 clc
 lda $73
 adc $60
 sta $73
 lda $74
 adc $61
 sta $74
 lda $75
 adc $62
 sta $75
 rts
MotionAndPosition:
 lda $74
 sta $43
 lda $75
 sta $44
 jsr MotionStep
 lda $43
 sta $74
 lda $44
 sta $75
 jmp PositionStep
'''

def original(rom,actor):
    m=list(actor);pc=0x32e2;r=dict(l=0,h=0,c=0,d=0,e=0);a=0;carry=False
    regs={0x5e:'e',0x56:'d',0x4e:'c',0x6e:'l',0x66:'h',0x7e:'a',0x75:'l',0x74:'h',0x77:'a'}
    for _ in range(40):
        if pc==0x331c:return m,a
        op=rom[pc];pc+=1
        if op==0xdd:
            sub,off=rom[pc:pc+2];pc+=2;assert sub in regs
            if sub in [0x75,0x74,0x77]:m[off]=a if sub==0x77 else r[regs[sub]]
            elif sub==0x7e:a=m[off]
            else:r[regs[sub]]=m[off]
        elif op==0x19:v=(r['h']<<8|r['l'])+(r['d']<<8|r['e']);carry=v>65535;r['l']=v&255;r['h']=v>>8&255
        elif op==0x89:v=a+r['c']+int(carry);a=v&255;carry=v>255
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original position bound')

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-Ln',O/'labels.txt','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    labels={line.split()[2].lstrip('.'):int(line.split()[1],16)for line in (O/'labels.txt').read_text().splitlines()}
    code=(O/'component.bin').read_bytes();prior=(R/'build/sonic-sms-motion-1102-v14/component.bin').read_bytes();assert code[:len(prior)]==prior
    rng=random.Random(110215);cases=[];cycles=[]
    edges=[0,1,255,256,65535,65536,0x7fffff,0x800000,0xffff00,0xffffff]
    for pos in edges:
        for vel in edges:
            cases.append([0]+list(pos.to_bytes(3,'little'))*2+list(vel.to_bytes(3,'little'))*2)
    cases.extend([rng.randrange(256)for _ in range(13)]for _ in range(8192))
    for state in cases:
        expected,a=original(rom,state);m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x70:0x76]=state[1:7];m[0x20:0x23]=state[7:10];m[0x60:0x63]=state[10:13]
        cpu=NesMPU(memory=m,pc=labels['PositionStep']);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(32):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('Position bound')
        assert m[0x70:0x76]==expected[1:7] and m[0x20:0x23]==state[7:10] and m[0x60:0x63]==state[10:13] and cpu.a==a and cpu.sp==224
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(cases),bytes_6502=len(code),added_bytes=len(code)-len(prior),position_cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Actual original32E2..331C 24-bit position integrator compared against6502 for XY fractional carries/signed wrapping. Unified entry restores source body-height Y change before post-object integration. Full terrain/animation/caps/native host admission remain incomplete; unified entry not full-Main-qualified.',bindings={str(p):sha(p)for p in [Path(__file__),Path(P.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
