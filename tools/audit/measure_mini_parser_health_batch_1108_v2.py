"""Compare column-batched native health reset on exact installed ROM in memory."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import subprocess

import measure_mini_parser_health_1108_v1 as A

R, N, ROM, PIN, sha = A.R, A.N, A.ROM, A.PIN, A.sha
OUT = A.OUT
PC_TAIL = 0xa2ed
BEFORE = bytes.fromhex('a200a0008403bca104b936ef293fc90198b002a900a403910920769098186910a8e8e00d90de60')
SOURCE = '''.setcpu "6502"
.segment "PARSER"
ColumnTail:
 ldx #0
 ldy #0
NextTile:
 sty R0
 ldy MetatileBuffer,x
 lda MTileAttribute,y
 and #$3f
 beq StoreTile
 tya
StoreTile:
 ldy R0
 sta (R6),y
 tya
 clc
 adc #16
 tay
 inx
 cpx #13
 bcc NextTile
 ; Native A=D0/X=13 and V=0. Y becomes the owner only for the branch.
 ldy SelectedCharacter
 clc
 jmp ResetHealthColumn
 .res 39-(*-ColumnTail),$ea

.segment "FIXED"
ResetHealthColumn:
 bne Guest
 tay
 cpx #13
 rts
Guest:
 ldx #>(MmBrickHealth-Block_Buffer_1)
 lda #<(MmBrickHealth-Block_Buffer_1)
 jsr PrepareAndClearColumn
 ldx #>(MmCoinHits-Block_Buffer_1)
 lda #<(MmCoinHits-Block_Buffer_1)
 jsr PrepareAndClearColumn
 ldx #>(MmSolidTerrain-Block_Buffer_1)
 lda #<(MmSolidTerrain-Block_Buffer_1)
 jsr ColumnPointer
 ldx #0
 ldy #0
NextTerrain:
 cpx #11
 bcc ZeroTerrain
 lda GuestTerrainColumn,x
 beq StoreTerrain
 cmp MetatileBuffer,x
 beq TerrainValue
ZeroTerrain:
 clc
TerrainValue:
 lda #0
 rol a
StoreTerrain:
 sta (M0),y
 tya
 clc
 adc #16
 tay
 inx
 cpx #13
 bcc NextTerrain
 rts

PrepareAndClearColumn:
 jsr ColumnPointer
 ldy #$c0
 lda #0
 sec
ClearRow:
 sta (M0),y
 tya
 sbc #16
 tay
 lda #0
 bcs ClearRow
 ; Last subtract wrapped, so C=0 for the next base addition.
 rts

ColumnPointer:
 adc R6
 sta M0
 txa
 adc R7
 sta M1
 rts
 .res 92-(*-ResetHealthColumn),$ea
'''


def assemble(b):
    stem=OUT/'parser-batch'; src=stem.with_suffix('.s'); cfg=stem.with_suffix('.cfg')
    parser=OUT/'parser-batch-level.bin'; fixed=OUT/'parser-batch-fixed.bin'
    src.write_text(''.join(f'{n}=${A.address(b,n):04x}\n' for n in [*A.NAMES,'R0','MTileAttribute'])+SOURCE)
    cfg.write_text('MEMORY{P:start=$a2ed,size=39,file="'+parser.as_posix()+'";F:start=$9076,size=92,file="'+fixed.as_posix()+'";}\n'
                   'SEGMENTS{PARSER:load=P,type=ro;FIXED:load=F,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin'; obj=stem.with_suffix('.o')
    subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',stem.with_suffix('.bin')],check=True)
    obj.unlink()
    return parser.read_bytes(),fixed.read_bytes(),src


def state(m):
    return (bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x15a:0x17b]),bytes(m[0x5fe0:0x8000]),
            tuple(bytes(r) for r in m.ram),tuple(m.rawtags),tuple(m.ppu_log),tuple(m.chr_latches),m.upper)


def check_tails(old,new):
    samples=[]; hist=Counter(); CPU=N.NesMPU
    buses=[N.Bus(b) for b in [old,new]]
    for col,owner,pattern,flags in product(range(32),range(42),range(4),[0x21,0xf1]):
        results=[]
        for seed in buses:
            m=N.fork(seed); m.raw_page(1,130); N.put(m,SelectedCharacter=owner,CurrentBank=130)
            N.invoke(m,'GetBlockBufferAddr',a=col)
            for row in range(13):
                m[A.address(m.bundle,'MetatileBuffer')+row]=(0,0x54,0xc3,0x24)[(pattern+row)%4]
                m[A.address(m.bundle,'GuestTerrainColumn')+row]=(0,0x54,0x54,0x24)[pattern]
            for name in ['MmBrickHealth','MmCoinHits','MmSolidTerrain']:
                addr=A.address(m.bundle,name); m[addr:addr+416]=bytes((i*13+0x31)&255 for i in range(416))
            m[0xb:0xd]=[0xa5,0x67]
            c=CPU(memory=m,pc=PC_TAIL); c.a,c.x,c.y,c.p,c.sp=0x83,7,19,flags,239; c.stPushWord(0x5aff)
            low=c.sp
            for _ in range(4000):
                if c.pc==0x5b00:break
                low=min(low,c.sp); assert m[c.pc]; c.step()
            else:raise AssertionError(('column tail bound',col,owner,pattern,c.pc))
            results.append(((c.a,c.x,c.y,c.p,c.sp),state(m),low,c.processorCycles))
        a,b=results
        assert a[:2]==b[:2],(col,owner,pattern,flags,a[0],b[0])
        hist[a[-1]-b[-1]]+=1
        if col in [0,31] and owner in [0,41] and pattern==0 and flags==0x21:
            samples.append(dict(column=col,raw=owner,CPU=[a[-1],b[-1]],SP=[a[-2],b[-2]]))
    return dict(cases=sum(hist.values()),cycle_savings=dict(hist),examples=samples)


def check_mains(old,new):
    out={}
    for label,count,terrain,parser in [('empty',0,False,False),('four',4,False,False),
                                      ('six',6,False,False),('four_parser',4,False,True),('two_pipe',2,True,False)]:
        pair=[A.fixture(b,count,terrain,parser) for b in [old,new]]; hist=[]
        for frame in range(2,14):
            results=[]
            for m in pair:
                key=0 if frame<6 else 129
                N.put(m,FrameCounter=frame,SavedJoypadBits=key,SavedJoypad1Bits=key,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                results.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
            assert all(results[0][k]==results[1][k] for k in ['A','X','Y','P']), (label,frame,results)
            assert state(pair[0])==state(pair[1]),(label,frame)
            hist.append([results[0]['CPU'],results[1]['CPU']])
        out[label]=hist
    return out


def main():
    raw=ROM.read_bytes(); assert sha(raw)==PIN
    old=A.bundle(raw); parser,fixed,source=assemble(old)
    assert len(BEFORE)==len(parser)==39 and len(fixed)==92
    # This exact physical JSR is the only direct control ingress into the
    # former per-tile reset. Source references and data aliases are separate.
    at1=16+2*8192+PC_TAIL-0xa000; at2=A.location(old,'MegaManResetBlockHealth')
    assert raw[at1:at1+len(BEFORE)]==BEFORE
    assert raw[:1048592].count(bytes.fromhex('207690'))==1
    assert raw[:1048592].count(bytes.fromhex('4c7690'))==0
    assert raw[at2:at2+92]==A.EXPECTED
    changes=[(2,PC_TAIL,at1,BEFORE,parser),(126,A.START,at2,A.EXPECTED,fixed)]
    newraw=bytearray(raw)
    for _,_,at,prev,data in changes:newraw[at:at+len(prev)]=data
    new=A.bundle(newraw)
    # Check actual fully mapped gameplay before the wider exhaustive tail case.
    mains=check_mains(old,new); print('whole Main PASS',mains,flush=True)
    tails=check_tails(old,new)
    result=dict(passed=True,ROM_written=False,source_only=True,base_SHA256=PIN,expected_memory_only_SHA256=sha(newraw),
                whole_GameCore=mains,compiled_column_tail=tails,source_SHA256=sha(source.read_bytes()),
                scope='Final complete memory/AXYP/SP/SMC/maps/VRAM/PPU parity; dead stack and intermediate write order differ. Actual IRQ and FF cut qualification pending.',
                patches=[dict(physical_PRG=bank,CPU_half_open=[pc,pc+len(prev)],file_offset=at,old_hex=prev.hex(),new_hex=data.hex())
                         for bank,pc,at,prev,data in changes])
    (OUT/'health-batch-v2.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','expected_memory_only_SHA256','compiled_column_tail']}),flush=True)


if __name__=='__main__':main()
