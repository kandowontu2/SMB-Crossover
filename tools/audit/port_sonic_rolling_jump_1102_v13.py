"""Original rolling jump input, including its distinct timer retention rules."""
import inspect,json,random,subprocess
from pathlib import Path
import port_sonic_jump_1102_v6 as P
R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-rolling-jump-1102-v13'
ASM=P.ASM+'''
RollingJump:
 lda $16
 and #$80
 beq RollingSuppress
 lda $16
 and #8
 bne RollingContinue
 lda $17
 and #$20
 beq RollingSuppress
RollingContinue:
 lda $17
 and #$20
 bne RollingRelease
 lda $16
 and #$fe
 sta $16
 lda $1f
 and #$f8
 sta $1f
 lda $18
 bne RollingHeld
 lda #16
 sta $18
 lda #1
 sta $1e
RollingHeld:
 jmp Held
RollingSuppress:
 lda $16
 and #$f7
 sta $16
 jmp RollingGravity
RollingRelease:
 lda $16
 ora #8
 sta $16
RollingGravity:
 jmp GravityEntry
'''.replace(' jmp GravityEntry',' jmp RollGravityTarget')
# Reuse the original nonrolling gravity decision, but not its timer reset.
ASM=ASM.replace(' lda $11\n bmi Gravity','RollGravityTarget:\n lda $11\n bmi Gravity')

def oracle():
    source=inspect.getsource(P.original)
    changes={
        'pc=0x4b61':'pc=0x5407',
        '0xd215:13':'0xd215:13,0xd403:15',
        'elif op==0xa7:':'elif op==0xe6:a&=rom[pc];pc+=1;z=a==0;carry=False\n        elif op==0xa7:',
    }
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    scope={};exec(source,scope);return scope['original']

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    code=(O/'component.bin').read_bytes();prior=(R/'build/sonic-sms-jump-1102-v6/component.bin').read_bytes();assert code[:len(prior)]==prior
    rng=random.Random(110213);cases=[];cycles=[];original=oracle()
    for flags in range(256):
        for inp in [0xdf,0xff]:
            for timer in [0,1,15,16,255]:
                for vy in [0,0x7ff,0x800,0xfc80,0xffff]:
                    cases.append([vy&255,vy>>8,255 if vy&32768 else 0,0,0,0,flags,inp,timer,0x80,0xfc,0x38,0,8,0,255])
    cases.extend([rng.randrange(256)for _ in range(14)]+[0,rng.randrange(256)]for _ in range(2048))
    def execute(state):
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x10:0x20]=state
        cpu=NesMPU(memory=m,pc=0x8000+len(prior));cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(100):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 bound')
        assert cpu.sp==224;cycles.append(cpu.processorCycles);return m[0x10:0x20]
    for state in cases:assert execute(state)==original(rom,state),state
    for held in range(1,25):
        actual=[0,0,0,0,0,0,0x89,0xff,0,0x80,0xfc,0x38,0,8,0,255];expected=actual[:]
        for tick in range(40):
            for state in [actual,expected]:state[7]=0xdf if tick<held else 0xff;state[14]=0
            actual=execute(actual);expected=original(rom,expected);assert actual==expected
    q=dict(passed=True,private=True,installed=False,cases=len(cases),episodes=24,bytes_6502=len(code),added_bytes=len(code)-len(prior),cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Executed original5407..543C and shared4B7F..4BBE/509D jump event versus compiled6502. Rolling timer retention, grounded input latch, Xfractionmask, jump sound event and Ygravity selection. Full Main/terrain/host ABI/audio driver remain incomplete.',bindings={str(p):sha(p)for p in [Path(__file__),Path(P.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
