"""Original neutral-input friction composed with the verified Sonic X motor."""
import inspect,json,random,subprocess
from pathlib import Path
import port_sonic_left_motor_1102_v9 as P
R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-coasting-1102-v10'
ASM=P.ASM+'''
CoastMotor:
 lda VL
 ora VH
 ora VB
 beq CoastCommit
 lda #1
 sta $31
 lda $34
 sta VE
 lda $35
 sta VD
 lda VB
 bmi CoastLeft
 jsr NegDE
 lda #255
 sta VC
 lda VL
 cmp $36
 lda VH
 sbc $37
 bcc CoastCommit
 lda $32
 sta VE
 lda $33
 sta VD
 jsr NegDE
 jmp CoastFast
CoastLeft:
 lda #0
 sta VC
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
 bcc CoastCommit
 lda $32
 sta VE
 lda $33
 sta VD
CoastFast:
 lda $38
 sta $31
CoastCommit:
 jmp SonicXVelocity
'''

def oracle():
    text=inspect.getsource(P.P.right)
    changes={
      'def right(':'def coast(', 'pc=0x4f01':'pc=0x4aba',
      'words={':'words={0xd212:brake,',
      'elif op==0x20:':'elif op in [0x20,0x28,0x38]:',
      'if not z:pc+=off':'if (carry if op==0x38 else z if op==0x28 else not z):pc+=off',
      "elif op in [0x7d,0x7c]:a=r['l' if op==0x7d else 'h']":"elif op in [0x7d,0x7c,0x7b,0x7a]:a=r[{0x7d:'l',0x7c:'h',0x7b:'e',0x7a:'d'}[op]]\n        elif op in [0xb5,0xb0]:a|=r['l' if op==0xb5 else 'b'];z=a==0;carry=False\n        elif op==0xd5:stack.append((r['e'],r['d']))\n        elif op==0xd1:r['e'],r['d']=stack.pop()\n        elif op==0x13:n=((r['d']<<8|r['e'])+1)&65535;r['e']=n&255;r['d']=n>>8"
    }
    for old,new in changes.items():assert text.count(old)==1,old;text=text.replace(old,new)
    scope={};exec(text,scope);return scope['coast']

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        z=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    code=(O/'component.bin').read_bytes();prefix=(R/'build/sonic-sms-leftmotor-1102-v9/component.bin').read_bytes();assert code[:len(prefix)]==prefix
    rng=random.Random(110210);fixtures=[];cycles=[];original=oracle()
    for v in [0,1,7,8,15,255,256,767,768,769,1536,32767,32768,65279,65280,65528,65535]:
        for flags in [0,2,128,255]:
            for acc,friction,cap in [(16,8,768),(4,2,256),(16,8,1536)]:
                fixtures.append(([v&255,v>>8,0,255 if v&32768 else 0,0,0],flags,5,acc,friction,cap,2))
    fixtures.extend(([rng.randrange(256)for _ in range(6)],rng.randrange(256),rng.randrange(256),rng.randrange(65536),rng.randrange(65536),rng.randrange(65536),rng.randrange(256))for _ in range(4096))
    for values,flags,anim,acc,friction,cap,capanim in fixtures:
        selected,ef,ea=original(rom,values,flags,anim,acc,friction,cap,capanim)
        old=[values[0],values[1],values[3]];expected,stored,a=P.P.X.original(rom,selected,old)
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x10:0x16]=values;m[0x20:0x23]=old
        m[0x30:0x39]=[flags,anim,acc&255,acc>>8,friction&255,friction>>8,cap&255,cap>>8,capanim]
        cpu=NesMPU(memory=m,pc=0x8000+len(prefix));cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(140):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 instruction bound')
        assert m[0x10:0x16]==expected and m[0x20:0x23]==stored and m[0x30:0x32]==[ef,ea] and cpu.a==a and cpu.sp==224,(values,acc,friction,cap)
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(fixtures),bytes_6502=len(code),unchanged_prior_component_bytes=len(prefix),cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),original_range='4ABA..4B1B then original horizontal commit',scope='Actual original neutral-input opcode path versus compiled6502: signed friction, overspeed deceleration, animation, zero crossing and velocity/register outputs. No terrain/caller/host allocation/native gameplay claim.',bindings={str(p):sha(p)for p in [Path(__file__),Path(P.__file__),Path(P.P.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
