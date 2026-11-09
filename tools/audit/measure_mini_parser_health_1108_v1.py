"""Exact fixed-span native block-health constant folding, CPU proof only."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import subprocess

from profile_mini_busy_1108_v1 import ROM, PIN, R, N, address, bundle, location, sha, fixture

OUT = R/'build/mini-parser-health-1108-v1'
START = 0x9076
EXPECTED = bytes.fromhex('48ad0260d0026860a50938e900850ba50ae903850ca50b186951850ba50c6960850ca900910b18a50b69a0850ba50c6901850ca900910b18a50969d1850ba50a6963850ce00b900ebd7168f009dda104d004a901d002a900910b6860')
NAMES = ['R6','R7','M0','M1','Block_Buffer_1','MmBrickHealth','MmCoinHits','MmSolidTerrain',
         'SelectedCharacter','GuestTerrainColumn','MetatileBuffer']
SOURCE = '''.setcpu "6502"
.segment "CODE"
.export MegaManResetBlockHealth
MegaManResetBlockHealth:
 pha
 lda SelectedCharacter
 bne Guest
 pla
 rts
Guest:
 ; Exactly the native 16-bit address (R7:R6)-Block_Buffer_1+MmBrickHealth.
 ; The first intermediate M0/M1 value had no reader before replacement.
 lda R6
 clc
 adc #<(MmBrickHealth-Block_Buffer_1)
 sta M0
 lda R7
 adc #>(MmBrickHealth-Block_Buffer_1)
 sta M1
 lda #0
 sta (M0),y
 clc
 lda M0
 adc #<(MmCoinHits-MmBrickHealth)
 sta M0
 lda M1
 adc #>(MmCoinHits-MmBrickHealth)
 sta M1
 lda #0
 sta (M0),y
 ; Preserve the exact final flags, scratch pointers and terrain provenance.
 clc
 lda R6
 adc #<(MmSolidTerrain-Block_Buffer_1)
 sta M0
 lda R7
 adc #>(MmSolidTerrain-Block_Buffer_1)
 sta M1
 cpx #11
 bcc NotTerrain
 lda GuestTerrainColumn,x
 beq NotTerrain
 cmp MetatileBuffer,x
 bne NotTerrain
 lda #1
 bne StoreTerrain
NotTerrain:
 lda #0
StoreTerrain:
 sta (M0),y
 pla
 rts
 .res 92-(*-MegaManResetBlockHealth),$ea
'''


def assemble(b):
    OUT.mkdir(exist_ok=True)
    stem=OUT/'parser-health'; src=stem.with_suffix('.s'); cfg=stem.with_suffix('.cfg')
    defs=''.join(f'{n}=${address(b,n):04x}\n' for n in NAMES)
    src.write_text(defs+SOURCE)
    cfg.write_text('MEMORY {F:start=$9076,size=92,file=%O;} SEGMENTS {CODE:load=F,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin'; obj=stem.with_suffix('.o'); out=stem.with_suffix('.bin')
    subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',out],check=True)
    obj.unlink()
    return out.read_bytes(),src


def compare_primitive(b, old, new):
    count=0; gains=Counter()
    # Exercise all actual 32 column bases and all 13 rows. Test both natural
    # provenance choices and full CPU A/P classes. This address domain is from
    # the compiled GetBlockBufferAddr routine, not arbitrary unowned pointers.
    ram=N.fresh(b)
    bases=[]
    for col in range(32):
        N.invoke(ram,'GetBlockBufferAddr',a=col)
        bases.append(ram[9]+256*ram[10])
    assert bases==list(range(0x300,0x310))+list(range(0x3d0,0x3e0)),bases
    seed=N.Bus(b)
    def call(code,base,row,owner,kind,a,p):
        m=N.fork(seed)
        # Fixed executable mapping. Overlay code differs only at the bounded
        # 92-byte routine, and the compare checks the entire native bus state.
        m.bundle=dict(b,raw=code)
        m.raw_page(0,254)
        m[9]=base&255;m[10]=base>>8
        m[address(b,'SelectedCharacter')]=owner
        m[address(b,'MetatileBuffer')+row]=0x54
        m[address(b,'GuestTerrainColumn')+row]=kind
        for name in ['MmBrickHealth','MmCoinHits','MmSolidTerrain']:
            m[address(b,name)+base-0x300+row*16]=0xa5
        c=N.NesMPU(memory=m,pc=START);c.a,c.x,c.y,c.p,c.sp=a,row,row*16,p,239
        c.stPushWord(0x5aff)
        for _ in range(100):
            if c.pc==0x5b00:break
            assert m[c.pc];c.step()
        else:raise AssertionError(('leaf bound',base,row,owner,kind,a,p,c.pc))
        assert c.sp==239
        return ((c.a,c.x,c.y,c.p,c.sp),bytes(list.__getitem__(m,slice(0x800))),bytes(list.__getitem__(m,slice(0x5fe0,0x8000))),
                tuple(m.rawtags),tuple(bytes(x) for x in m.ram),tuple(m.ppu_log),c.processorCycles)
    for base,row,owner,kind,(a,p) in product(bases,range(13),[0,1,41], [0,0x54,0xc3],[(0,0x30),(0x57,0x71),(0xa5,0xf4),(255,0xf1)]):
        first=call(old,base,row,owner,kind,a,p);second=call(new,base,row,owner,kind,a,p)
        assert first[:-1]==second[:-1],(base,row,owner,kind,a,p,first[0],second[0])
        gain=first[-1]-second[-1]
        assert gain==(18 if owner else 0),gain
        gains[gain]+=1;count+=1
    return count,dict(gains)


def compare_whole(old,new):
    output={}
    for name,actors,terrain,parser in [('empty',0,False,False),('four',4,False,False),
                                    ('four_parser',4,False,True),('two_pipe',2,True,False)]:
        a,b=[fixture(x,actors,terrain,parser) for x in [old,new]]; rows=[]
        for frame in range(2,18):
            results=[]
            for m in [a,b]:
                key=0 if frame<6 else 129
                N.put(m,FrameCounter=frame,SavedJoypadBits=key,SavedJoypad1Bits=key,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                results.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
            assert {k:v for k,v in results[0].items() if k!='CPU'}=={k:v for k,v in results[1].items() if k!='CPU'}
            assert (bytes(a[:0x800]),bytes(a[0x5fe0:0x8000]),a.rawtags,a.ram,a.ppu_log)==(bytes(b[:0x800]),bytes(b[0x5fe0:0x8000]),b.rawtags,b.ram,b.ppu_log),(name,frame)
            gain=results[0]['CPU']-results[1]['CPU']
            assert gain in (0,18*13), (name,frame,gain)
            rows.append(gain)
        output[name]=rows
    return output


def main():
    raw=ROM.read_bytes();assert sha(raw)==PIN
    b=bundle(raw);at=location(b,'MegaManResetBlockHealth')
    assert address(b,'MegaManResetBlockHealth')==START and (at-16)//8192==126
    assert len(EXPECTED)==92 and raw[at:at+92]==EXPECTED
    data,source=assemble(b)
    assert len(data)==92
    revised=raw[:at]+data+raw[at+92:]
    count,gains=compare_primitive(b,raw,revised)
    comparisons=compare_whole(b,bundle(revised))
    assert any(234 in row for row in comparisons.values())
    manifest=dict(passed=True,source_only=True,ROM_written=False,Mesen_run=False,base_SHA256=PIN,
                  expected_memory_only_SHA256=sha(revised),leaf_cases=count,leaf_cycles_saved=gains,
                  whole_GameCore_cases=sum(map(len,comparisons.values())),whole_GameCore_cycles_saved=comparisons,
                  source_preimage='src/megaman_weapons.s::MegaManResetBlockHealth, source-owned 92-byte existing live body. No lease growth.',
                  scope='CPU comparison includes full native RAM, AXYP/SP/SMC/mapper, cartridge private RAM and PPU log. Real lag-NMI/IRQ cut testing remains before native composition.',
                  patches=[dict(physical_PRG=126,CPU_half_open=[START,START+92],file_offset=at,old_hex=EXPECTED.hex(),new_hex=data.hex())],
                  bindings={str(p):sha(p.read_bytes()) for p in [Path(__file__),source,R/'src/megaman_weapons.s',R/'src/level_tiles.s',ROM]})
    (OUT/'health-fold.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['passed','expected_memory_only_SHA256','leaf_cases','leaf_cycles_saved','whole_GameCore_cycles_saved']}),flush=True)


if __name__=='__main__':main()
