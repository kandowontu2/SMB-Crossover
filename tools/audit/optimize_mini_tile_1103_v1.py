"""Exact-output Mini tile query speedup; no shared code, ROM, or Mesen."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import build_storage_guard_v1 as G
O=R/'build/mini-tile-fast-1103-v1'
BASE=R/'build/mini-zero-visible-direct/mini-zero.s'
BIN=BASE.with_suffix('.bin')
LABELS=BASE.with_suffix('.lbl')
sha=lambda b:hashlib.sha256(b).hexdigest()

FAST='''Tile_Invalid:
 lda #0
 sta MiniQueryTile
 sta MiniQueryFlags
 sta MiniQueryKind
 sta MiniQueryAddress
 sta MiniQueryAddress+1
 cmp #15
 clc
 rts
MiniNativeTile:
 lda MiniQueryY+1
 bne Tile_Invalid
 lda MiniQueryY
 cmp #32
 bcc Tile_Invalid
 cmp #240
 bcs Tile_Invalid
 txa
 pha
 tya
 pha
 lda #0
 sta MiniQueryKind
 lda MiniQueryX
 lsr
 lsr
 lsr
 lsr
 sta MiniQueryColumn
 lda MiniQueryY
 and #$f0
 sec
 sbc #32
 ora MiniQueryColumn
 tay
 lda MiniQueryX+1
 and #1
 bne Tile_Buffer2
 tya
 sta MiniQueryAddress
 lda #>Block_Buffer_1
 sta MiniQueryAddress+1
 lda Block_Buffer_1,y
 jmp Tile_Classify
Tile_Buffer2:
 tya
 clc
 adc #<Block_Buffer_2
 sta MiniQueryAddress
 lda #>Block_Buffer_2
 adc #0
 sta MiniQueryAddress+1
 lda Block_Buffer_2,y
Tile_Classify:
 sta MiniQueryTile
 tax
__CLASSIFY__
Tile_Restore:
 pla
 tay
 pla
 tax
 lda MiniQueryFlags
 cmp #15
 beq Tile_Return
 clc
Tile_Return:
 rts
MiniNativeTileEnd:
'''
ENCODED=''' ; Packed table retains native low2 attributes for the other reader.
 lda MiniTileAttributes,x
 lsr
 lsr
 sta MiniQueryFlags
 cmp #16
 bne Tile_Restore
 lda #151
 sta MiniQueryKind
 jmp Tile_Restore'''
PLAIN=''' and #$fe
 cmp #$c2
 beq Tile_Zero
 lda MiniTileAttributes,x
 and #3
 cmp #1
 bne Tile_Vine
 lda #15
 bne Tile_Store
Tile_Vine:
 cpx #$26
 bne Tile_Zero
 lda #151
 sta MiniQueryKind
 lda #16
 bne Tile_Store
Tile_Zero:lda #0
Tile_Store:sta MiniQueryFlags
 jmp Tile_Restore'''

def labels(path):
    return {n:int(v,16) for v,n in re.findall(r'^al ([0-9a-fA-F]+) \.(\w+)$',path.read_text(),re.M)}

def encoded_attributes(old):
    assert len(old)==256
    flags=lambda n:0 if n in (0xc2,0xc3) else 15 if old[n]&3==1 else 16 if n==0x26 else 0
    return bytes((a&3)|(flags(i)<<2) for i,a in enumerate(old))

def successor(source,encoded=True):
    a=source.index('MiniNativeTile:\n');z=source.index('MiniNativeTileEnd:\n',a)+len('MiniNativeTileEnd:\n')
    assert source.count('lda MiniTileAttributes,x')==2
    other=source[source.index('MiniHostFilterSolid:'):]
    assert 'lda MiniTileAttributes,x\n and #3\n cmp #1' in other
    return source[:a]+FAST.replace('__CLASSIFY__',ENCODED if encoded else PLAIN)+source[z:]

def assemble(stem,source=None,path=None):
    if source is not None:
        path=O/(stem+'.s');path.write_text(source)
    cfg=O/'tile.cfg'
    if not cfg.exists():cfg.write_text('MEMORY{M:start=$a000,size=$2000,file=%O;}SEGMENTS{CODE:load=M,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',path,'-o',O/(stem+'.o')],
        [cc/'ld65.exe','-C',cfg,O/(stem+'.o'),'-o',O/(stem+'.bin'),'-Ln',O/(stem+'.lbl')]]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    (O/(stem+'.o')).unlink()
    return (O/(stem+'.bin')).read_bytes(),labels(O/(stem+'.lbl'))

class CPU(MPU):
    # NES2A03 arithmetic ignores D; retain the architectural D bit.
    def opADC(self,x):
        d=self.p&8;self.p&=~8;super().opADC(x);self.p|=d
    def opSBC(self,x):
        d=self.p&8;self.p&=~8;super().opSBC(x);self.p|=d

def qualify(old,oldlab,new,newlab,attrs,table):
    memories=[];cpus=[]
    for data,lab,at in [(old,oldlab,attrs),(new,newlab,table)]:
        m=bytearray(65536);m[0xa000:0xa000+len(data)]=data;m[0xd300:0xd400]=at
        m[0x300:0x4a0]=bytes((i*73+19)&255 for i in range(416))
        memories.append(m);cpus.append(CPU(memory=m))
    before=bytes(memories[0][0x300:0x4a0]);count=0;oldsum=newsum=0;stats={};case_min=10**9
    def call(x,y,tag=0):
        nonlocal count,oldsum,newsum,case_min
        outputs=[];cycles=[]
        for m,c,lab in zip(memories,cpus,[oldlab,newlab]):
            m[0xc2e0:0xc2ea]=bytes([x&255,x>>8,y&255,y>>8,0x93,0x7b,0x26,0xe1,0x62,0xaf])
            c.pc=lab['MiniNativeTile'];c.a=tag&255;c.x=(tag*37+71)&255;c.y=(tag*23+109)&255
            c.p=(0x20|(tag&0xcf));c.sp=224;c.stPushWord(0x5aff);start=c.processorCycles
            for _ in range(120):
                if c.pc==0x5b00:break
                c.step()
            else:raise AssertionError(('Query bound',x,y,hex(c.pc)))
            outputs.append((c.a,c.x,c.y,c.p,c.sp,bytes(m[0xc2e0:0xc2ea])))
            cycles.append(c.processorCycles-start)
        assert outputs[0]==outputs[1],(x,y,tag,outputs)
        assert bytes(memories[1][0x300:0x4a0])==before or tag>=0x10000
        a,b=cycles;oldsum+=a;newsum+=b;count+=1;case_min=min(case_min,a-b)
        valid=32<=y<240
        tile=outputs[0][5][4]
        kind='invalid' if not valid else 'solid' if outputs[0][0]==15 else 'vine' if outputs[0][0]==16 else 'empty'
        key=kind+('/buffer2' if valid and x&256 else '')
        r=stats.setdefault(key,dict(cases=0,old_min=999,old_max=0,new_min=999,new_max=0,saved_min=999,saved_max=-999))
        r['cases']+=1
        for k,v in [('old_min',a),('new_min',b),('saved_min',a-b)]:r[k]=min(r[k],v)
        for k,v in [('old_max',a),('new_max',b),('saved_max',a-b)]:r[k]=max(r[k],v)
    # Every supported low-X value and page parity; all256 low Y values.
    for x in range(512):
        for y in range(256):call(x,y,(x+y)&255)
    # Every unsigned16 Y, all high-X bytes and parity wrap/near-page values.
    for y in range(256,65536):call(0xa5ff,y,y&255)
    for hi in range(256):
        for low in [0,7,15,127,128,239,240,255]:
            for y in [32,47,48,127,128,223,224,239]:call((hi<<8)|low,y,hi)
    for tile in range(256):
        for m in memories:m[0x300]=m[0x3d0]=tile
        for x in [0,7,15,256,263,271]:
            for p in [0,1,0x40,0x41,0x8,0xc9]:call(x,32,0x10000|p)
    for m in memories:m[0x300:0x4a0]=before
    # All existing source consumers keep the complete low2 attribute ABI.
    assert all((a&3)==(b&3) for a,b in zip(attrs,table))
    return dict(passed=True,cases=count,cycles=dict(old_total=oldsum,new_total=newsum,saved=oldsum-newsum,
        saved_percent=round(100*(oldsum-newsum)/oldsum,3),minimum_saved_per_case=case_min),groups=stats,
        full_registers_flags_query_packet_column_and_native_buffer_parity=True,
        X16_all_hi_and_lo_classes=True,Y16_exhaustive=True,all256tiles=True,D_ignored_as_NES2A03=True,
        native_low2_attribute_consumer_parity=True)

def main():
    G.preflight(private_root=O,reserved_bytes=120000,reserved_files=15,fresh=True);O.mkdir(exist_ok=True)
    ref,lab=assemble('reference',path=BASE)
    assert ref==BIN.read_bytes() and lab==labels(LABELS),'Recompiled baseline differs'
    source=BASE.read_text();attrs=(R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin').read_bytes()
    outputs=[]
    for name,encoded in [('plain',False),('encoded',True)]:
        data,l=assemble('tile-'+name,successor(source,encoded))
        table=encoded_attributes(attrs) if encoded else attrs
        q=qualify(ref,lab,data,l,attrs,table)
        q.update(kernel_bytes=len(data),kernel_SHA256=sha(data),query_bytes=l['MiniNativeTileEnd']-l['MiniNativeTile'],
            reference_kernel_bytes=len(ref),code_bytes_recovered=len(ref)-len(data),encoded_table=encoded)
        if encoded:(O/'encoded-attributes.bin').write_bytes(table)
        outputs.append(q);print(name,json.dumps(q),flush=True)
    # Keep exact baseline read-only; generated linker outputs are disposable.
    for suffix in ['bin','lbl']:(O/('reference.'+suffix)).unlink()
    out=dict(passed=True,CPU_only=True,ROM_written=False,Mesen_run=False,results=outputs,
        input_kernel_SHA256=sha(ref),source_consumers='Exactly2 MiniTileAttributes readers; querydecode and unchanged MiniHostFilterSolid AND3.',
        recipe='successor(source, encoded=True), encoded_attributes(original256); relink full currentsource; no shared source edit.',
        bindings={p.relative_to(R).as_posix():sha(p.read_bytes()) for p in [Path(__file__),BASE,BIN,LABELS]})
    (O/'tile-proof.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()
