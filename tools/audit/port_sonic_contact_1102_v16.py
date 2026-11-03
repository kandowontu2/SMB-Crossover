"""Original resolved terrain-contact cores, before host query integration."""
import json,random,subprocess
from pathlib import Path
import port_sonic_position_1102_v15 as P
R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-contact-1102-v16'
ASM=P.ASM+'''
.export HorizontalContact,VerticalContact
; Fixture80: original signed shape offset (80 means absent),81: edge probe,
; 82: original tileflag index. Coordinates/velocities retain v15 precision.
HorizontalContact:
 lda #0
 sta $83
 tay
 jmp ContactBegin
VerticalContact:
 lda #1
 sta $83
 ldy #3
ContactBegin:
 lda $80
 cmp #$80
 bne ContactPresent
 rts
ContactPresent:
 clc
 lda $71,y
 adc $81
 sta $85
 lda $72,y
 adc #0
 sta $86
 lda $80
 bpl ContactPositive
 jmp ContactClip
ContactPositive:
 lda $83
 bne ContactVerticalTest
 lda $85
 and #31
 sta $87
 lda $22
 bmi ContactReverse
 lda $87
 cmp $80
 bcs ContactClip
 rts
ContactReverse:
 lda $87
 cmp $80
 bcc ContactClip
 rts
ContactVerticalTest:
 ldx $82
 lda $85
 and #31
 clc
 adc ContactMagnet,x
 sta $87
 lda $62
 bmi ContactReverse
 lda $87
 cmp $80
 bcs ContactGround
 rts
ContactGround:
 lda $30
 ora #$80
 sta $30
ContactClip:
 lda #0
 bit $80
 bpl ContactSignReady
 lda #$ff
ContactSignReady:
 sta $87
 lda $85
 and #$e0
 clc
 adc $80
 sta $85
 lda $86
 adc $87
 sta $86
 sec
 lda $85
 sbc $81
 sta $71,y
 lda $86
 sbc #0
 sta $72,y
 ldx $82
 lda $83
 bne ContactYVelocity
 lda $30
 ora #$40
 sta $30
 lda #0
 sta $20
 sta $21
 sta $22
 lda ContactYSlide,x
 ldx #$40
 jmp ContactSlide
ContactYVelocity:
 lda #0
 sta $60
 sta $61
 sta $62
 lda ContactXSlide,x
 ldx #0
ContactSlide:
 sta $88
 lda #0
 bit $88
 bpl ContactSlideSign
 lda #$ff
ContactSlideSign:
 sta $89
 clc
 lda $20,x
 adc $88
 sta $20,x
 lda $21,x
 adc $89
 sta $21,x
 lda $22,x
 adc $89
 sta $22,x
 rts
'''

def original(rom,actor,axis,offset,probe,tile):
    m=list(actor);pc=0x3381 if axis==0 else 0x3459;end=0x33f6 if axis==0 else 0x34e6
    r=dict(l=0,h=0,b=0,c=0,d=0,e=0);alt=r.copy();a=offset;carry=z=sign=False
    words={0xd210:probe,0xd214:tile}
    def read(at):return rom[at]if at<0x8000 else words[at]
    for _ in range(140):
        if pc==end:return m
        op=rom[pc];pc+=1
        if op==0xdd:
            sub=rom[pc];pc+=1
            if sub==0xcb:
                off,sub=rom[pc:pc+2];pc+=2;bit=(sub>>3)&7;group=sub>>6
                if group==1:z=not(m[off]&(1<<bit));sign=bit==7 and not z
                elif group==3:m[off]|=1<<bit
                else:raise AssertionError(sub)
            else:
                off=rom[pc];pc+=1
                if sub in [0x6e,0x66,0x7e]:
                    if sub==0x7e:a=m[off]
                    else:r['l'if sub==0x6e else'h']=m[off]
                elif sub in [0x75,0x74,0x77,0x72]:m[off]=a if sub==0x77 else r[{0x75:'l',0x74:'h',0x72:'d'}[sub]]
                elif sub==0x8e:v=a+m[off]+int(carry);a=v&255;carry=v>255;z=a==0;sign=bool(a&128)
                else:raise AssertionError(sub)
        elif op==0xfe:z=a==rom[pc];carry=a<rom[pc];sign=bool((a-rom[pc])&128);pc+=1
        elif op in [0xc3,0xca,0xfa,0xf2]:
            dest=rom[pc]|rom[pc+1]<<8;pc+=2
            if op==0xc3 or {0xca:z,0xfa:sign,0xf2:not sign}.get(op,False):pc=dest
        elif op in [0x20,0x28,0x30,0x38]:
            off=rom[pc];pc+=1
            if {0x20:not z,0x28:z,0x30:not carry,0x38:carry}[op]:pc+=off if off<128 else off-256
        elif op in [0x5f,0x4f,0x6f,0x7d,0x7a,0x42]:
            if op in [0x7d,0x7a]:a=r['l'if op==0x7d else'd']
            elif op==0x42:r['b']=r['d']
            else:r[{0x5f:'e',0x4f:'c',0x6f:'l'}[op]]=a
        elif op in [0x16,0x06,0x26]:r[{0x16:'d',0x06:'b',0x26:'h'}[op]]=rom[pc];pc+=1
        elif op==0xe6:a&=rom[pc];pc+=1;z=a==0;sign=bool(a&128);carry=False
        elif op==0xa7:z=a==0;sign=bool(a&128);carry=False
        elif op in [0xbb,0xb9]:v=r['e'if op==0xbb else'c'];z=a==v;carry=a<v;sign=bool((a-v)&128)
        elif op in [0x19,0x09]:
            lo,hi=('e','d')if op==0x19 else('c','b');v=(r['h']<<8|r['l'])+(r[hi]<<8|r[lo]);carry=v>65535;r['l']=v&255;r['h']=v>>8&255
        elif op==0xed:
            sub=rom[pc];pc+=1
            if sub in [0x4b,0x5b]:
                at=rom[pc]|rom[pc+1]<<8;pc+=2;v=words[at];lo,hi=('c','b')if sub==0x4b else('e','d');r[lo]=v&255;r[hi]=v>>8
            elif sub in [0x42,0x52]:
                lo,hi=('c','b')if sub==0x42 else('e','d');v=(r['h']<<8|r['l'])-(r[hi]<<8|r[lo])-int(carry);carry=v<0;r['l']=v&255;r['h']=v>>8&255
            else:raise AssertionError(sub)
        elif op==0x3a:at=rom[pc]|rom[pc+1]<<8;pc+=2;a=read(at)
        elif op==0x2a:at=rom[pc]|rom[pc+1]<<8;pc+=2;v=words[at];r['l']=v&255;r['h']=v>>8
        elif op==0x21:r['l'],r['h']=rom[pc:pc+2];pc+=2
        elif op==0x11:r['e'],r['d']=rom[pc:pc+2];pc+=2
        elif op==0x4e:r['c']=read(r['h']<<8|r['l'])
        elif op==0x86:v=a+read(r['h']<<8|r['l']);carry=v>255;a=v&255;z=a==0;sign=bool(a&128)
        elif op==0xd9:r,alt=alt,r
        elif op==0xcb:assert rom[pc]==0x79;pc+=1;z=not(r['c']&128);sign=not z
        elif op in [0x3d,0x05]:
            if op==0x3d:a=(a-1)&255;v=a
            else:r['b']=(r['b']-1)&255;v=r['b']
            z=v==0;sign=bool(v&128)
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original contact bound')

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    source=ASM
    for name,at in [('ContactYSlide',0x3fbf),('ContactXSlide',0x3f90),('ContactMagnet',0x3ff0)]:source+='\n'+name+':\n.byte '+','.join(str(v)for v in rom[at:at+64])+'\n'
    (O/'component.s').write_text(source);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-Ln',O/'labels.txt','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    labels={line.split()[2].lstrip('.'):int(line.split()[1],16)for line in (O/'labels.txt').read_text().splitlines()};code=(O/'component.bin').read_bytes();prior=(R/'build/sonic-sms-position-1102-v15/component.bin').read_bytes();assert code[:len(prior)]==prior
    rng=random.Random(110216);fixtures=[];cycles=[]
    for axis in [0,1]:
        for offset in range(256):
            for neg in [0,255]:
                actor=[rng.randrange(256)for _ in range(26)];actor[9 if axis==0 else 12]=neg
                fixtures.append((actor,axis,offset,24 if axis==0 else 32,rng.randrange(64)))
    fixtures.extend(([rng.randrange(256)for _ in range(26)],rng.randrange(2),rng.randrange(256),rng.randrange(256),rng.randrange(64))for _ in range(4096))
    for actor,axis,offset,probe,tile in fixtures:
        expected=original(rom,actor,axis,offset,probe,tile)
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x70:0x76]=actor[1:7];m[0x20:0x23]=actor[7:10];m[0x60:0x63]=actor[10:13];m[0x30]=actor[24];m[0x80:0x83]=[offset,probe,tile]
        cpu=NesMPU(memory=m,pc=labels['HorizontalContact'if axis==0 else'VerticalContact']);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(150):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 contact bound')
        assert m[0x70:0x76]==expected[1:7] and m[0x20:0x23]==expected[7:10] and m[0x60:0x63]==expected[10:13] and m[0x30]==expected[24],(axis,offset,probe,tile,actor,expected,m[0x70:0x76],m[0x20:0x23],m[0x60:0x63],m[0x30])
        assert cpu.sp==224;cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(fixtures),bytes_6502=len(code),added_bytes=len(code)-len(prior),cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Actual donor3381..33F6 /3459..34E6 resolved-contact cores versus6502. All256 shape offsets, sentinel80, signed/probe carries, original table slide/magnet effects, position fractions, velocity resets and support flags. Source shape lookup/world probes and full Main/host/native integration remain incomplete.',bindings={str(p):sha(p)for p in [Path(__file__),Path(P.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
