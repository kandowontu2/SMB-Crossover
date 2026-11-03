"""Translate original post-velocity pose and hard caps; no native admission."""
import itertools,json,random,subprocess
from pathlib import Path
import port_sonic_animation_player_1102_v20 as P
R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-post-velocity-1102-v22'
EXTRA='''
.export PoseAfterVelocity,HardCapsAndTop
; Private fixture fields: flags30, animation31, Y velocity60..62.
PoseAfterVelocity:
 lda $30
 and #4
 beq PoseAbsolute
 lda #9
 sta $31
PoseAbsolute:
 lda $60
 sta $a4
 lda $61
 sta $a5
 bpl PoseCompare
 sec
 lda #0
 sbc $a4
 sta $a4
 lda #0
 sbc $a5
 sta $a5
PoseCompare:
 ; Original 0100-abs(value): only abs strictly above0100 continues.
 lda $a5
 beq PoseDone
 cmp #1
 bne PoseMaySelect
 lda $a4
 beq PoseDone
PoseMaySelect:
 lda $30
 and #$85
 bne PoseDone
 lda #1
 ldx $62
 bpl PoseStore
 lda #19
PoseStore:
 sta $31
PoseDone:
 rts
HardCapsAndTop:
 ldx #$10
 lda $21
 bpl CapXAbsolute
 eor #$ff
 clc
 adc #1
 ldx #$f0
CapXAbsolute:
 cmp #$10
 bcc CapY
 stx $21
CapY:
 ldx #$10
 lda $61
 bpl CapYAbsolute
 eor #$ff
 clc
 adc #1
 ldx #$f0
CapYAbsolute:
 cmp #$10
 bcc CapTop
 stx $61
CapTop:
 ; Unsigned word <=16 clamps to16; fractional coordinate73 survives.
 lda $75
 bne CapDone
 lda $74
 cmp #17
 bcs CapDone
 lda #16
 sta $74
CapDone:
 rts
'''


def original(rom,entry,flags,anim,xvel,yvel,ypos):
    """Execute actual donor opcodes, including 5280 roll-animation leaf."""
    mem={0xd414:flags,0xd410:anim}
    for at,value in [(0xd403,xvel),(0xd406,yvel),(0xd400,ypos)]:
        for n in range(3):mem[at+n]=(value>>(8*n))&255
    pc=entry;a=c=0;hl=yvel&65535;de=0;zero=positive=False;carry=False;stack=[]
    for _ in range(90):
        if pc in [0x4c28,0x4d05]:
            return mem[0xd410],sum(mem[0xd403+n]<<(8*n)for n in range(3)),sum(mem[0xd406+n]<<(8*n)for n in range(3)),sum(mem[0xd400+n]<<(8*n)for n in range(3))
        op=rom[pc];pc+=1
        if op==0xdd:
            sub=rom[pc];pc+=1
            if sub==0xcb:
                off,sub=rom[pc:pc+2];pc+=2;assert sub in [0x56,0x7e]
                value=flags if off==24 else(yvel>>16)&255 if off==12 else None
                assert value is not None;zero=not(value&(1<<((sub>>3)&7)))
            elif sub==0x36:
                off,val=rom[pc:pc+2];pc+=2;assert off==20;mem[0xd410]=val
            else:raise AssertionError(hex(sub))
        elif op==0xc4:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if not zero:stack.append(pc);pc=at
        elif op==0xc9:pc=stack.pop()
        elif op==0x7c:a=hl>>8
        elif op==0x7d:a=hl&255
        elif op==0xa7:zero=a==0;positive=not(a&128);carry=False
        elif op==0x2f:a^=255
        elif op==0x67:hl=(hl&255)|(a<<8)
        elif op==0x6f:hl=(hl&0xff00)|a
        elif op==0x23:hl=(hl+1)&65535
        elif op in [0x11,0x21]:
            val=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if op==0x11:de=val
            else:hl=val
        elif op==0xeb:de,hl=hl,de
        elif op==0xed:
            sub=rom[pc];pc+=1
            if sub==0x52:
                val=hl-de-int(carry);carry=val<0;hl=val&65535
            elif sub==0x44:a=(-a)&255
            elif sub==0x5b:
                at=int.from_bytes(rom[pc:pc+2],'little');pc+=2;de=mem[at]|mem[at+1]<<8
            else:raise AssertionError(hex(sub))
        elif op==0x3a:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2;a=mem[at]
        elif op==0xe6:a&=rom[pc];pc+=1;zero=a==0;positive=not(a&128);carry=False
        elif op==0xf2:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2
            if positive:pc=at
        elif op in [0x30,0x38,0x20,0x28,0x18]:
            off=rom[pc];pc+=1
            take={0x30:not carry,0x38:carry,0x20:not zero,0x28:zero,0x18:True}[op]
            if take:pc+=off if off<128 else off-256
        elif op==0x0e:c=rom[pc];pc+=1
        elif op==0xfe:carry=a<rom[pc];zero=a==rom[pc];pc+=1
        elif op==0x79:a=c
        elif op==0x32:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2;mem[at]=a
        elif op==0x19:
            val=hl+de;carry=val>65535;hl=val&65535
        elif op==0x22:
            at=int.from_bytes(rom[pc:pc+2],'little');pc+=2;mem[at]=hl&255;mem[at+1]=hl>>8
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Actual post-velocity donor bound')


def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    prior=R/'build/sonic-sms-animation-player-1102-v20';asm=(prior/'component.s').read_text()+EXTRA
    (O/'component.s').write_text(asm);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$2000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-Ln',O/'labels.txt','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    labels={s.split()[2].lstrip('.'):int(s.split()[1],16)for s in(O/'labels.txt').read_text().splitlines()}
    code=(O/'component.bin').read_bytes();old=(prior/'component.bin').read_bytes();assert code[:len(old)]==old
    rng=random.Random(110222);counts={};cycles={}
    template=[0]*65536;template[0x8000:0x8000+len(code)]=code
    def run(entry,state,original_entry):
        flags,anim,xvel,yvel,ypos=state;expected=original(rom,original_entry,*state)
        m=template.copy();m[0x30]=flags;m[0x31]=anim
        for at,val in[(0x20,xvel),(0x60,yvel),(0x73,ypos)]:m[at:at+3]=val.to_bytes(3,'little')
        cpu=NesMPU(memory=m,pc=labels[entry]);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(80):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 post-velocity bound')
        got=(m[0x31],int.from_bytes(bytes(m[0x20:0x23]),'little'),int.from_bytes(bytes(m[0x60:0x63]),'little'),int.from_bytes(bytes(m[0x73:0x76]),'little'))
        assert got==expected,(entry,state,got,expected)
        assert m[0x30]==flags and cpu.sp==224
        counts[entry]=counts.get(entry,0)+1;cycles.setdefault(entry,[]).append(cpu.processorCycles)
    edges=[0,1,255,256,257,32767,32768,65279,65280,65281,65535]
    for flags,low,high in itertools.product(range(256),edges,[0,255]):
        run('PoseAfterVelocity',(flags,rng.randrange(26),rng.randrange(1<<24),low|(high<<16),rng.randrange(1<<24)),0x4bf5)
    for byte in range(256):
        for _ in range(4):
            x=(rng.randrange(256)<<16)|(byte<<8)|rng.randrange(256);y=(rng.randrange(256)<<16)|((255-byte)<<8)|rng.randrange(256)
            run('HardCapsAndTop',(rng.randrange(256),rng.randrange(26),x,y,rng.randrange(1<<24)),0x4ccb)
    # Exhaust every unsigned Y word while cycling both signed velocity bytes.
    for word in range(65536):
        x=rng.randrange(1<<24);y=rng.randrange(1<<24)
        run('HardCapsAndTop',(word&255,word%26,x,y,(word<<8)|(word&255)),0x4ccb)
    result=dict(passed=True,private=True,installed=False,cases=counts,cycles={k:[min(v),max(v)]for k,v in cycles.items()},bytes_6502=len(code),added_bytes=len(code)-len(old),original_ROM_SHA256=sha(donor),scope='Actual original4BF5..4C28 including5280 roll leaf, and4CCB..4D05 hard caps/top clamp, compared with6502. Pose override uses abs(frac,pixel) strictly above0100, original85 exclusion and Y high sign. Hard cap changes only pixel bytes; high/fractions retained. All256 flags, near0100/signed edges, all256 velocity pixel values and all65536 unsigned Y words. Two private leaves, not a complete Main/call-order/native-world/render/audio/lifecycle admission.',bindings={str(p):sha(p)for p in[Path(__file__),donor,prior/'component.s',O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
