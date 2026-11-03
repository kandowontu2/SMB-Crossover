"""Lossless original Sonic SMS shape tables and source probe selection.

Private component only: the caller still supplies the original zone tile flag.
This does not invent an SMB world-to-shape adapter or admit a playable Sonic.
"""
import json, random, subprocess
from pathlib import Path
import port_sonic_contact_1102_v16 as P

R=P.R; sha=P.sha; NesMPU=P.NesMPU
O=R/'build/sonic-sms-shapes-1102-v17'
TABLES=[0x4020,0x411e,0x41ec,0x448a]
EXTRA='''
.export ShapeHorizontal,ShapeVertical,HorizontalTerrain,VerticalTerrain
; Input:82 original zone flag. Fixture positions/body/velocity are v16's.
; Output:80 signed source offset,81 axis edge probe,82 masked flag.
; 8A..8E are private scratch, not an admitted host RAM allocation.
HorizontalTerrain:
 jsr ShapeHorizontal
 jmp HorizontalContact
VerticalTerrain:
 jsr ShapeVertical
 jmp VerticalContact
ShapeHorizontal:
 lda $30
 and #$bf
 sta $30
 lda $42
 lsr
 clc
 adc $74
 and #31
 sta $8a
 lda #0
 sta $8b
 sta $81
 lda $21
 bmi ShapeFetch
 lda $41
 sta $81
 lda #47
 sta $8b
 jmp ShapeFetch
ShapeVertical:
 lda $30
 and #$7f
 sta $30
 lda $41
 lsr
 clc
 adc $71
 and #31
 sta $8a
 lda #0
 sta $81
 lda #94
 sta $8b
 lda $61
 bmi ShapeFetch
 lda $42
 sta $81
 lda #141
 sta $8b
ShapeFetch:
 lda #$80
 sta $80
 lda $82
 and #63
 sta $82
 beq ShapeReturn
 cmp #47
 bcs ShapeReturn
 clc
 adc $8b
 tax
 lda ShapeLo,x
 sta $8c
 lda ShapeHi,x
 sta $8d
 ldy $8a
 lda ($8c),y
 sta $80
ShapeReturn:
 rts
'''

def original_shape(rom,axis,actor,tile):
    """Actual donor pointer indirection, before the v16 contact cores."""
    negative=bool(actor[8 if axis==0 else 11]&128)
    direction=axis*2+(0 if negative else 1)
    probe=0 if negative else actor[13 if axis==0 else 14]
    row=(actor[5 if axis==0 else 2]+(actor[14 if axis==0 else 13]>>1))&31
    flag=tile&63
    if flag==0:return 128,probe,flag
    assert flag<47
    at=TABLES[direction]+2*flag
    ptr=int.from_bytes(rom[at:at+2],'little')
    return rom[ptr+row],probe,flag

def main():
    O.mkdir(exist_ok=True)
    donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    # Every zone's original flag domain, without assuming unused table indices.
    zones=sorted((R/'build/sonic-sms-original-1102-v2/src/data').glob('*.tileflags'))
    flags={v&63 for p in zones for v in p.read_bytes()}
    assert len(zones)==8 and flags==set(range(47))
    pool=[];indices=[]
    for table in TABLES:
        for tile in range(47):
            at=table+tile*2;ptr=int.from_bytes(rom[at:at+2],'little')
            block=rom[ptr:ptr+32];assert len(block)==32
            if block not in pool:pool.append(block)
            indices.append(pool.index(block))
    prior=R/'build/sonic-sms-contact-1102-v16'
    asm=(prior/'component.s').read_text()+EXTRA
    for name,operator in [('ShapeLo','<'),('ShapeHi','>')]:
        asm+='\n'+name+':\n.byte '+','.join(operator+'Shape'+str(i) for i in indices)+'\n'
    for i,block in enumerate(pool):asm+='\nShape'+str(i)+':\n.byte '+','.join(str(v)for v in block)+'\n'
    (O/'component.s').write_text(asm)
    (O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-Ln',O/'labels.txt','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    labels={line.split()[2].lstrip('.'):int(line.split()[1],16)for line in (O/'labels.txt').read_text().splitlines()}
    code=(O/'component.bin').read_bytes();old=(prior/'component.bin').read_bytes();assert code[:len(old)]==old
    rng=random.Random(110217);cases=[]
    for axis in [0,1]:
        for tile in range(47):
            for row in range(32):
                for negative in [False,True]:
                    a=[rng.randrange(256)for _ in range(26)]
                    a[8 if axis==0 else 11]=128 if negative else 127
                    a[5 if axis==0 else 2]=(row-(a[14 if axis==0 else 13]>>1))&255
                    cases.append((axis,a,tile))
    cases.extend((rng.randrange(2),[rng.randrange(256)for _ in range(26)],rng.randrange(47)|rng.choice([0,64,128,192]))for _ in range(4096))
    cycles=[]
    for axis,actor,tile in cases:
        expected=original_shape(rom,axis,actor,tile)
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x70:0x76]=actor[1:7]
        m[0x20:0x23]=actor[7:10];m[0x60:0x63]=actor[10:13]
        m[0x41:0x43]=actor[13:15];m[0x30]=actor[24];m[0x82]=tile
        cpu=NesMPU(memory=m,pc=labels['ShapeHorizontal'if axis==0 else'ShapeVertical']);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(100):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('Shape lookup bound')
        assert tuple(m[0x80:0x83])==expected,(axis,actor,tile,expected,m[0x80:0x83])
        assert m[0x30]==actor[24]&(~(64 if axis==0 else 128)&255)
        assert m[0x70:0x76]==actor[1:7]and m[0x20:0x23]==actor[7:10]and m[0x60:0x63]==actor[10:13]and cpu.sp==224
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(cases),bytes_6502=len(code),added_bytes=len(code)-len(old),unique_shapes=len(pool),shape_bytes=sum(map(len,pool)),cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Lossless original four-direction shape tables, exhaustive legal47flags/all32rows/bothsigns plus4096 carry/mask fixtures. Source pixel-velocity table selection, half-body sample, edge probe, flag clearing and sentinel preserved. Comparison uses actual donor pointer indirection; not execution of full donor collision dispatcher. Caller-supplied original zone flag; native SMB geometry query, full Main/render/audio/host admission incomplete.',bindings={str(p):sha(p)for p in [Path(__file__),Path(P.__file__),prior/'component.s',O/'component.s',O/'component.bin',*zones]})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))

if __name__=='__main__':main()
