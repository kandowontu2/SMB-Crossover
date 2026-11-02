"""Add original left-input motor to the verified right/commit component."""
import inspect,json,random,subprocess
from pathlib import Path
import port_sonic_right_motor_1102_v8 as P
R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-leftmotor-1102-v9'
ASM=P.ASM+'''
LeftMotor:
 lda $30
 ora #2
 sta $30
 lda VL
 ora VH
 beq LAccel
 lda VB
 bpl LBrake
LAccel:
 lda $32
 sta VE
 lda $33
 sta VD
 jsr NegDE
 lda #255
 sta VC
 lda #1
 sta $31
 sec
 lda #0
 sbc VL
 sta $39
 lda #0
 sbc VH
 sta $3a
 lda $39
 cmp $36
 lda $3a
 sbc $37
 bcc LCommit
 lda #0
 sta VE
 sta VD
 sta VC
 sec
 lda #0
 sbc $36
 sta VL
 lda #0
 sbc $37
 sta VH
 lda #255
 sta VB
 lda $38
 sta $31
 jmp LCommit
LBrake:
 lda $30
 and #$fd
 sta $30
 lda #10
 sta $31
 lda $34
 sta VE
 lda $35
 sta VD
 jsr NegDE
 lda #255
 sta VC
 lda VH
 bne LCommit
 lda $30
 ora #2
 sta $30
 lda #1
 sta $31
LCommit:
 jmp SonicXVelocity
NegDE:
 sec
 lda #0
 sbc VE
 sta VE
 lda #0
 sbc VD
 sta VD
 rts
'''

def oracle():
    text=inspect.getsource(P.right)
    edits={
      'def right(':'def left(', 'pc=0x4f01':'pc=0x4f5c',
      'elif op==0x20:':'elif op in [0x20,0x28]:',
      'if not z:pc+=off':'if (not z if op==0x20 else z):pc+=off',
      'elif sub==0x52:':'elif sub in [0x52,0x42]:',
      "(r['d']<<8|r['e'])-int(carry)":"((r['d']<<8|r['e']) if sub==0x52 else (r['b']<<8|r['c']))-int(carry)",
      "elif op==0x0e:r['c']=rom[pc];pc+=1":"elif op in [0x0e,0x06]:r['c' if op==0x0e else 'b']=rom[pc];pc+=1",
      "elif op in [0x7d,0x7c]:a=r['l' if op==0x7d else 'h']":"elif op in [0x7d,0x7c,0x7b,0x7a]:a=r[{0x7d:'l',0x7c:'h',0x7b:'e',0x7a:'d'}[op]]\n        elif op==0xb4:a|=r['h'];z=a==0;carry=False\n        elif op==0x13:n=((r['d']<<8|r['e'])+1)&65535;r['e']=n&255;r['d']=n>>8\n        elif op==0x01:r['c'],r['b']=rom[pc:pc+2];pc+=2"
    }
    for old,new in edits.items():assert text.count(old)==1,old;text=text.replace(old,new)
    space={};exec(text,space);return space['left']

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY { ROM: start=$8000,size=$1000,file=%O; } SEGMENTS { CODE: load=ROM,type=ro; }')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    code=(O/'component.bin').read_bytes();prefix=(P.O/'component.bin').read_bytes();assert code[:len(prefix)]==prefix
    left=oracle();rng=random.Random(110209);fixtures=[];cycles=[]
    for velocity in [0,1,15,255,256,767,768,769,1536,32767,32768,65279,65280,65520,65535]:
        for flags in [0,2,128,255]:
            for acc,brake,cap in [(16,48,768),(4,12,256),(16,48,1536)]:fixtures.append(([velocity&255,velocity>>8,0,255 if velocity&32768 else 0,0,0],flags,0,acc,brake,cap,2))
    fixtures.extend(([rng.randrange(256) for _ in range(6)],rng.randrange(256),rng.randrange(256),rng.randrange(65536),rng.randrange(65536),rng.randrange(65536),rng.randrange(256)) for _ in range(2048))
    for values,flags,anim,acc,brake,cap,capanim in fixtures:
        selected,ef,ea=left(rom,values,flags,anim,acc,brake,cap,capanim)
        old=[values[0],values[1],values[3]];expected,stored,a=P.X.original(rom,selected,old)
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x10:0x16]=values;m[0x20:0x23]=old;m[0x30:0x39]=[flags,anim,acc&255,acc>>8,brake&255,brake>>8,cap&255,cap>>8,capanim]
        cpu=NesMPU(memory=m,pc=0x8000+len(prefix));cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(150):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 bound')
        assert m[0x10:0x16]==expected and m[0x20:0x23]==stored and m[0x30:0x32]==[ef,ea] and cpu.a==a and cpu.sp==224,(values,flags,acc,brake,cap)
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(fixtures),bytes_6502=len(code),cycles=[min(cycles),max(cycles)],ROM_SHA256=sha(donor),scope='Actual original left-input opcode path and original horizontal commit vs assembled6502. Right/commit176byte prefix unchanged. Left accel/cap/reversal/facing/animation/registers verified; no terrain/host/full-gameplay claim.',bindings={str(p):sha(p) for p in [Path(__file__),Path(P.__file__),Path(P.X.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
