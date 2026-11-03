"""Original normal/water/shoes/special physics selection and roll ingress."""
import itertools,json,random,subprocess
from pathlib import Path
import port_sonic_shapes_1102_v17 as P
import port_sonic_roll_1102_v7 as B

R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-physics-selection-1102-v19'
FIELDS=[0x32,0x33,0x34,0x35,0x45,0x46,0x99,0x5d,0x38,0x36,0x37,0x59,0x5a,0x5b,0x5c]
EXTRA='''
.export SelectPhysics,SelectAndRoll
; Private fixture90 shoes timer,91 source level flags,92 global tick,
; 93/94 saved music tempo,95/96 live tempo;99 is original tmp06 low.
; All are unallocated host resources. Existing component fields are v17's.
SelectPhysics:
 ldx #32
 lda $30
 and #16
 bne PhysicsSelected
 ldx #48
 lda $90
 bne PhysicsSelected
 ldx #0
 lda $91
 and #1
 beq PhysicsSelected
 lda $30
 bmi PhysicsSelected
 ldx #16
PhysicsSelected:
'''+''.join(' lda PhysicsData+'+str(i)+',x\n sta $'+format(at,'02x')+'\n'for i,at in enumerate(FIELDS))+'''
 cpx #32
 beq PhysicsDone
 lda $93
 sta $95
 lda $94
 sta $96
 cpx #48
 bne PhysicsDone
 inc $95
 bne PhysicsTimer
 inc $96
PhysicsTimer:
 lda $92
 and #3
 bne PhysicsDone
 dec $90
PhysicsDone:
 rts
SelectAndRoll:
 jsr SelectPhysics
 lda $40
 and #2
 beq OriginalTryRoll
 lda $91
 and #$fb
 sta $91
 rts
OriginalTryRoll:
 lda $30
 and #5
 bne OriginalTryRollDone
 lda $30
 bpl OriginalTryRollDone
 ora #1
 sta $30
 lda $20
 ora $21
 beq OriginalRollQuiet
 lda #6
 sta $5e
OriginalRollQuiet:
 lda $91
 ora #4
 sta $91
OriginalTryRollDone:
 rts
'''

def original(rom,flags,boots,level,tick,saved,live):
    """Execute the actual original4928..49D9 selection instructions."""
    mem={0xd223:tick,0xdc0c:saved&255,0xdc0d:saved>>8,0xdc0a:live&255,0xdc0b:live>>8}
    actor={24:flags,21:boots};pc=0x4928;a=0;hl=de=bc=0;zero=False;stack=[]
    def read(at):return rom[at]if at<0x8000 else mem.get(at,0)
    for _ in range(80):
        if pc==0x49d9:return [mem[0xd20e+i]for i in range(9)]+[mem[0xd240+i]for i in range(6)],actor[21],mem[0xdc0a]|mem[0xdc0b]<<8
        op=rom[pc];pc+=1
        if op in [0xdd,0xfd]:
            sub=rom[pc];pc+=1
            if sub==0xcb:
                off,sub=rom[pc:pc+2];pc+=2;assert sub>>6==1
                zero=not((actor[off]if op==0xdd else level)&(1<<((sub>>3)&7)))
            elif sub==0x7e:
                assert op==0xdd;a=actor[rom[pc]];pc+=1
            elif sub==0x35:
                assert op==0xdd and rom[pc]==21;pc+=1;actor[21]=(actor[21]-1)&255;zero=actor[21]==0
            else:raise AssertionError(hex(sub))
        elif op in [0x21,0x11,0x01]:
            value=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if op==0x21:hl=value
            elif op==0x11:de=value
            else:bc=value
        elif op==0xed:
            assert rom[pc]==0xb0;pc+=1
            for _ in range(bc):mem[de]=read(hl);de+=1;hl+=1
            bc=0
        elif op in [0x22,0x2a]:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if op==0x22:mem[at]=hl&255;mem[at+1]=hl>>8
            else:hl=read(at)|read(at+1)<<8
        elif op==0x3a:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2;a=read(at)
        elif op==0x23:hl=(hl+1)&65535
        elif op==0xa7:zero=a==0
        elif op==0xe6:a&=rom[pc];pc+=1;zero=a==0
        elif op in [0xc3,0xca]:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if op==0xc3 or zero:pc=at
        elif op==0x20:
            off=rom[pc];pc+=1
            if not zero:pc+=off if off<128 else off-256
        elif op==0xcc:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if zero:stack.append(pc);pc=at
        elif op==0xc9:pc=stack.pop()
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original physics selector bound')

def main():
    O.mkdir(exist_ok=True)
    donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    prior=R/'build/sonic-sms-shapes-1102-v17'
    asm=(prior/'component.s').read_text()+EXTRA+'\nPhysicsData:\n'
    for entry in [0x495b,0x4987,0x492f,0x49ad]:
        assert rom[entry]==rom[entry+11]==rom[entry+17]==rom[entry+23]==0x21
        at=int.from_bytes(rom[entry+1:entry+3],'little')
        row=rom[at:at+9]+b''.join(rom[entry+off+1:entry+off+3]for off in [11,17,23])+bytes(1)
        assert len(row)==16
        asm+='.byte '+','.join(map(str,row))+'\n'
    (O/'component.s').write_text(asm);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-Ln',O/'labels.txt','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    labels={line.split()[2].lstrip('.'):int(line.split()[1],16)for line in (O/'labels.txt').read_text().splitlines()}
    code=(O/'component.bin').read_bytes();old=(prior/'component.bin').read_bytes();assert code[:len(old)]==old
    rng=random.Random(110219);cycles=[];count=0
    for flags,boots,level,tick in itertools.product(range(256),[0,1,2,255],[0,1,5,255],[0,1,3,4]):
        saved=rng.choice([0,1,255,256,65535,rng.randrange(65536)]);live=rng.randrange(65536)
        expected,newboots,newtempo=original(rom,flags,boots,level,tick,saved,live)
        inp=rng.randrange(256);velocity=rng.randrange(65536);sound=rng.randrange(256)
        if inp&2:ef,el,es=flags,level&251,sound
        else:
            result=B.original(rom,[flags,velocity&255,velocity>>8,level,sound]);ef,el,es=result[0],result[3],result[4]
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code
        m[0x30]=flags;m[0x40]=inp;m[0x20:0x22]=[velocity&255,velocity>>8];m[0x5e]=sound
        m[0x90:0x97]=[boots,level,tick,saved&255,saved>>8,live&255,live>>8]
        cpu=NesMPU(memory=m,pc=labels['SelectAndRoll']);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(130):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 physics selector bound')
        assert[m[at]for at in FIELDS]==expected,(flags,boots,level,tick)
        assert m[0x90]==newboots and(m[0x95]|m[0x96]<<8)==newtempo
        assert(m[0x30],m[0x91],m[0x5e])==(ef,el,es)and cpu.sp==224
        assert m[0x20:0x22]==[velocity&255,velocity>>8]
        cycles.append(cpu.processorCycles);count+=1
    result=dict(passed=True,private=True,installed=False,cases=count,bytes_6502=len(code),added_bytes=len(code)-len(old),cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Original4928..49D9 opcode execution versus6502 physics selection, original four coefficient rows/cap/jump/gravity, water/shoes/special-ground precedence, tempo restoration/wrap and shoes timer phase. Composed actual down-input roll admission/extra flag clear against original50C1..50E8. Full Main, runtime world queries, animation, audio rendering, host allocation/admission remain incomplete.',bindings={str(p):sha(p)for p in [Path(__file__),Path(B.__file__),prior/'component.s',O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
