"""Same-span Arthur cache transport repair; memory-only source qualification.

No ROM, private candidate, captures, or persistent generated outputs. The
original normalized canonical input, decoded cache, runtime and cookie remain
identical. Only their cold storage transport changes. DK pages stay exact.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import tempfile
from unittest.mock import patch
import zipfile

import probe_arthur_cache_conflict_1123 as P

R,W,N,H=P.R,P.W,P.N,P.H
OUT=R/'build/arthur-tail-cache-source-1123'
SOURCE=R/'tools/audit/arthur_cache_loader.s'


def once(s,a,b):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)


def inputs():
    with zipfile.ZipFile(P.ARCHIVE)as z:
        objects={name:z.read('objects/'+pin)for name,(pin,size)in P.OBJECTS.items()}
    for name,data in objects.items():assert (H(data),len(data))==P.OBJECTS[name]
    return objects


def pack(raw,objects):
    canonical,code=objects['canonical'],objects['emitter']
    assert raw[1048592+868*1024:1048592+881*1024]==objects['atlas']
    tails=json.loads(objects['tail_census'])['candidate_unreferenced_art_tails']
    free=[]
    for row in tails:
        p,a,z=row['physical_page'],row['offset_start'],row['end']
        if p==868:free.extend([(p,a,768),(p,1014,z)])
        elif p==878:free.append((p,128+len(code),z))
        else:free.append((p,a,z))
    image=bytearray(raw);header=bytearray(canonical[:246]);rows=[]
    records={int.from_bytes(canonical[i:i+2],'little')for i in range(0,172,2)}
    assert min(records)==246
    def length(at):
        n=canonical[at];assert 1<=n<=11
        return 2+4*n
    sorted_old=sorted(records)
    assert all(a+length(a)==z for a,z in zip(sorted_old,sorted_old[1:]+[2326]))
    pointers={}
    for old in sorted(records,key=lambda a:(-length(a),a)):
        size=length(old)
        j=next(i for i,(p,a,z)in enumerate(free)if z-a>=size)
        page,a,z=free[j];free[j]=(page,a+size,z)
        at=1048592+page*1024+a
        assert image[at:at+size]==bytes(size)
        image[at:at+size]=canonical[old:old+size]
        pointers[old]=(page-868)*1024+a
        rows.append(dict(canonical=[old,old+size],physical_page=page,byte_half_open=[a,a+size]))
    for i in range(0,172,2):header[i:i+2]=pointers[int.from_bytes(canonical[i:i+2],'little')].to_bytes(2,'little')
    def store(page,start,data):
        at=1048592+page*1024+start;assert image[at:at+len(data)]==bytes(len(data));image[at:at+len(data)]=data
    store(868,768,header);store(878,128,code)
    # Logical serialization is unchanged once physical addresses are decoded.
    normalized=bytearray(header)
    for i in range(0,172,2):
        ptr=int.from_bytes(header[i:i+2],'little');old=next(k for k,v in pointers.items()if v==ptr)
        normalized[i:i+2]=old.to_bytes(2,'little')
    assert normalized==canonical[:246]
    return bytes(image),rows


def source(raw,changed=False,pad=0):
    b=dict(W.Symbols.bundle(),raw=raw);s=SOURCE.read_text()
    if changed:
        old=''' lda #113                    ; source-granted physical881
 sta $5120
 sta $5128
 lda #114
 sta $5121
 sta $5129
 lda #115
 sta $5122
 sta $512a
'''
        s=once(s,old,' ; Physical source page is selected by each genuine seek.\n')
        s=once(s,' adc #172\n ldx #0\n jsr SeekInput',' adc #172\n ldx #3\n jsr SeekInput')
        s=once(s,'MasterReady:\n asl\n ldx #0\n jsr SeekInput','MasterReady:\n asl\n ldx #3\n jsr SeekInput')
        s=once(s,' lda #.lobyte(__ARTHUR_CACHE_EXEC_LOAD__-$dc400)\n ldx #.hibyte(__ARTHUR_CACHE_EXEC_LOAD__-$dc400)',
                   ' lda #$80\n ldx #$28 ; page878 tail: (878-868)*1024+128')
        s=once(s,'''SeekInput:
 bit $2002
 stx $2006
 sta $2006
 lda $2007                  ; genuine buffered-read dummy
 rts
''','''SeekInput:
 ; A/X is the compact physical stream offset, not a live actor coordinate.
 ; X/Y and stack return exactly; C is dead at the four proven local callers.
 pha
 txa
 pha
 lsr
 lsr
 clc
 adc #100
 sta $5120
 sta $5128
 txa
 and #3
 bit $2002
 sta $2006
 pla
 tax
 pla
 sta $2006
 lda $2007
 rts
''')
        s=once(s,'Signature:',f'.res {pad},$ea ; measured reclaimed source bytes, no external span\nSignature:')
    s=re.sub(r'^\.import[^\n]*\n','',s,flags=re.M)
    defined=set(re.findall(r'(?:\.proc\s+|::)(\w+)',s))
    tokens=set(re.findall(r'\b[A-Za-z_]\w*\b',s))
    constants={n:W.address(b,n)for n in tokens if n in b['syms']and n not in defined}
    constants.update(__ARTHUR_CACHE_EXEC_LOAD__=0xdcd16,__ARTHUR_CACHE_EXEC_SIZE__=550)
    at=W.location(b,'ArCacheSignature');sig=raw[at:at+16]
    constants.update({f'AR_CACHE_SIG{i}':v for i,v in enumerate(sig)})
    pre='.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${v:x}\n'for n,v in sorted(constants.items()))
    return pre+s+'\n.export ArCachePublishCheckpoint\n.export ArCacheSignature=ArCacheLoad::Signature\n.export ArTailSeek=ArCacheLoad::SeekInput\n'


def link(raw,changed=False,pad=0):
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=OUT)as name:
        work=Path(name);asm,config,obj,output,labels=[work/n for n in ('loader.s','loader.cfg','loader.o','loader.bin','loader.lbl')]
        asm.write_text(source(raw,changed,pad))
        config.write_text('MEMORY{CODE:start=$d9b8,size=$2dd,file=%O;}SEGMENTS{ARTHUR_ART_TAIL:load=CODE,type=ro;}')
        tools=R/'tools/Windows/cc65/bin'
        for command in ([str(tools/'ca65.exe'),str(asm),'-o',str(obj)],
                        [str(tools/'ld65.exe'),str(obj),'-C',str(config),'-o',str(output),'-Ln',str(labels)]):
            q=subprocess.run(command,capture_output=True,text=True)
            assert q.returncode==0,(q.stdout,q.stderr)
        blob=output.read_bytes();lab={n:int(a,16)for a,n in re.findall(r'^al ([\da-fA-F]+) \.(\S+)$',labels.read_text(),re.M)}
    return blob,lab


def build(raw):
    assert H(raw)==P.PIN
    objects=inputs();original,ol=link(raw)
    at=16+70*8192+(0xd9b8&8191)
    assert len(original)==733
    actual=raw[at:at+733]
    assert original==actual,('Original exact preimage',next((i for i,(x,y)in enumerate(zip(original,actual))if x!=y),None))
    blob,lab=link(raw,True)
    assert len(blob)<=733,('Measured source-funded fit',len(blob))
    reclaimed=733-len(blob)
    if reclaimed:blob,lab=link(raw,True,reclaimed)
    assert len(blob)==733
    # Keep the existing signature and public checkpoint positions unchanged.
    assert lab['ArCacheLoad']==0xd9b8
    assert lab['ArCachePublishCheckpoint']==ol['ArCachePublishCheckpoint'],(lab,ol)
    assert blob[-39:]==original[-39:]
    image,rows=pack(raw,objects)
    image=image[:at]+blob+image[at+len(blob):]
    assert image[1048592+881*1024:1048592+884*1024]==raw[1048592+881*1024:1048592+884*1024]
    for p in range(868,881):
        count=next((x['offset_start']for x in json.loads(objects['tail_census'])['candidate_unreferenced_art_tails']if x['physical_page']==p),1024)
        off=1048592+p*1024;assert image[off:off+count]==raw[off:off+count]
    return image,dict(loader_bytes=len(blob),reclaimed_padding_bytes=reclaimed,labels=lab,record_extents=rows,loader_SHA256=H(blob))


def cold(raw):
    with patch.object(P.A,'controller',lambda data:b''):
        return P.A.cold(raw)


def native_memory(m):
    # A bus slice would read $2002/$2007/controllers and mutate the fixture.
    # Native RAM/register backing is compared without performing MMIO reads.
    return bytes(list.__getitem__(m,slice(0,0x8000)))


def qualify(raw,image):
    objects=inputs();at=1048592+881*1024
    cache=(objects['canonical']+objects['emitter']).ljust(3072,b'\0')
    reference=raw[:at]+cache+raw[at+3072:]
    before,after=cold(reference),cold(image)
    assert N.get(after,'ArHostReady')==167
    assert all(bytes(a)==bytes(b)for a,b in zip(before.ram,after.ram)),'All loaded WRAM bytes, state, code, header'
    assert native_memory(before)==native_memory(after),'All native/application RAM and final mapper registers'
    assert before.rawtags==after.rawtags and before.chr_latches==after.chr_latches
    assert (before.upper,before.lastset)==(after.upper,after.lastset)
    assert before.vram==after.vram,'All cold native nametable/palette writes produce identical VRAM'
    expanded=bytes(after.ram[2][:6130]);runtime=bytes(after.ram[2][0x1800:0x1800+550])
    assert runtime==objects['emitter']
    cookie=bytes([167,32,0,1])+bytes.fromhex(H(objects['canonical']+runtime+expanded))[:12]
    assert cookie==bytes(after.ram[2][0x1fe0:0x1ff0])
    # Reclose every actual art reader against the final decoded cache, rather
    # than relying on zero fill as a resource grant.
    used={p:set()for p in range(868,881)};views=parts=0
    for mode in range(3):
        for key in range(74):
            p=int.from_bytes(expanded[(mode*74+key)*2:(mode*74+key)*2+2],'little')
            if not p:continue
            at=p-0xc000;n,page=expanded[at:at+2];assert 1<=n<=11;views+=1
            for i in range(n):
                dy,tile,attr,dx=expanded[at+2+i*4:at+6+i*4]
                address=(tile&1)*4096+(tile&254)*16;slot=address//1024;pair=(address%1024)//32
                if slot==0:physical=768+page
                else:
                    assert slot in(6,7)and page==255
                    physical=([877,878]if mode==0 else[879,880])[slot-6]
                assert physical in used;used[physical].add(pair);parts+=1
                a=1048592+physical*1024+pair*32;assert raw[a:a+32]==image[a:a+32]
    b=dict(W.Symbols.bundle(),raw=raw);off=W.location(b,'ArPalWhiteLookup')
    lookup=raw[off:off+128];used[880].update(v&31 for v in lookup if v<128)
    for p,pairs in used.items():
        count=max(pairs)+1;assert pairs==set(range(count))
        a=1048592+p*1024;assert raw[a:a+count*32]==image[a:a+count*32]
    assert views==201
    # Every ordinary source update follows the same original phase/physics.
    advances=0
    for pad in (0,1,1,1,129,129,1,1,1,0,2,2):
        for m in (before,after):m.controller_pad=pad;P.A.Engine.Frames.frame(m,whole_pass=True)
        assert all(bytes(a)==bytes(b)for a,b in zip(before.ram,after.ram))
        assert native_memory(before)==native_memory(after)
        assert before.rawtags==after.rawtags and before.chr_latches==after.chr_latches
        advances+=1
    return dict(genuine_cold_exact=True,all_four_WRAM_banks_exact=True,all_native_RAM_exact=True,
        full_header_exact=cookie.hex(),normalized_payload_fingerprint_exact=True,
        all_native_VRAM_exact=True,mapper_and_CHR_restore_exact=True,
        finite_pose_mode_views=views,finite_pose_parts=parts,white_table_entries=128,
        all_active_tile_bytes_exact=True,controller_update_continuations=advances,
        limits=['CPU model only; no native run or repair admission.',
                'Cold source PPU seek traffic intentionally differs. Final native VRAM/CHR and application state are exact.',
                'New seek Carry is overwritten before every actual caller reads Carry; public loader restores entry P then sets result Carry.',
                'Actual FF-NMI/IRQ qualification is reported separately in vectors.'])


def patches(raw,image):
    rows=[]
    a=16+70*8192+(0xd9b8&8191)
    rows.append(dict(file_offset=a,old_hex=raw[a:a+733].hex(),new_hex=image[a:a+733].hex()))
    tails=json.loads(inputs()['tail_census'])['candidate_unreferenced_art_tails']
    for row in tails:
        a=1048592+row['physical_page']*1024+row['offset_start'];z=1048592+(row['physical_page']+1)*1024
        if raw[a:z]!=image[a:z]:rows.append(dict(file_offset=a,old_hex=raw[a:z].hex(),new_hex=image[a:z].hex()))
    check=bytearray(raw)
    for row in rows:
        a=row['file_offset'];old,new=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert bytes(check[a:a+len(old)])==old;check[a:a+len(old)]=new
    assert bytes(check)==image
    return rows


def clone(c):
    m=list.__new__(type(c.memory));list.extend(m,list.__iter__(c.memory))
    for k,v in vars(c.memory).items():
        setattr(m,k,[]if k in('writes','ram_writes','ppu_log')else v if k=='bundle'else deepcopy(v))
    z=N.NesMPU(memory=m,pc=c.pc)
    z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
    return z


def vectors(raw,image,lab):
    # Every instruction of the first real new seek, plus every actual I0
    # constructor edge. This is forced blank/Ready0, never a fabricated I0
    # inside the PHP/SEI-protected stream.
    old=N.NesMPU;cuts=[];seen=set();in_seek=False;seek_done=False
    seek=lab['ArTailSeek'];end=lab['ArCacheSignature']
    start=16+70*8192+(seek&8191);seek_bytes=image[start:start+end-seek]
    pending_ppu={seek+i for i in range(len(seek_bytes)-2)if seek_bytes[i:i+3]==bytes.fromhex('ad0720')}
    pending_ppu.update(seek+i+3 for i in range(len(seek_bytes)-2)if seek_bytes[i:i+3]==bytes.fromhex('ad0720'))
    class Capture(old):
        def step(self):
            nonlocal in_seek,seek_done
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            if tag==198 and 0xd9b8<=self.pc<end:
                if self.pc==seek and not seek_done:in_seek=True
                hit=in_seek or not self.p&4
                key=self.pc,self.sp,bool(self.p&4)
                if hit and key not in seen:seen.add(key);cuts.append(clone(self))
                if in_seek and m[self.pc]==0x60:in_seek=False;seek_done=True
            return super().step()
    with patch.object(N,'NesMPU',Capture):cold(image)
    assert seek_done and len(cuts)>=20
    def live(c):
        m=c.memory
        return ((c.a,c.x,c.y,c.p,c.sp,c.pc),bytes(m[0x101+c.sp:0x200]),
                bytes(m[0x15a:0x17b]),bytes(m[3:11]),tuple(m.rawtags),tuple(m.chr_latches),
                m.upper,m.lastset,m.ppu_addr,m.toggle,m.buffer,
                tuple(bytes(a)for a in m.ram),bytes(m[0x5c00:0x5cb0]))
    counts={'FF_NMI':0,'hardware_IRQ':0,'nested_IRQ':0};minimum=255
    def run(c,stop,visit=None):
        nonlocal minimum
        for _ in range(200000):
            if stop(c):return
            minimum=min(minimum,c.sp)
            if visit:visit(c)
            assert c.memory[c.pc],('Actual cold vector BRK',hex(c.pc));c.step()
        raise AssertionError(('Actual cold vector bound',hex(c.pc),c.sp))
    for sample in cuts:
        for kind in ('FF_NMI',)+(('hardware_IRQ',)if not sample.p&4 else()):
            c=clone(sample);m=c.memory;before=live(c);stop=c.pc,c.sp
            # Keep this exact physical input data in the ISR comparator. The
            # only excluded immutable bytes are the changed loader itself,
            # which the ISR is required never to execute.
            baseline=bytearray(image);code_at=16+70*8192+(0xd9b8&8191)
            baseline[code_at:code_at+733]=raw[code_at:code_at+733]
            legacy=clone(sample);legacy.memory.bundle=dict(legacy.memory.bundle,raw=bytes(baseline))
            for win,tag in enumerate(tuple(legacy.memory.rawtags)):
                if tag&128:legacy.memory.raw_page(win,tag)
            skipped=N.get(m,'NmiSkipped');assert N.get(m,'NmiDisable')==255
            native=bytes(m[0xe000:0x10000])
            hits=[i for i in range(len(native)-8)if native[i:i+4]==bytes.fromhex('ad390110')and native[i+5:i+8]==bytes.fromhex('ee3a01')]
            start,=hits;lag=0xe000+start+5;relative=native[start+4];regular=lag+(relative-256 if relative>=128 else relative)
            branch=[0];deepest=[None];ppu_reads=[]
            if kind=='FF_NMI':c.nmi();legacy.nmi()
            else:c.irq();legacy.irq()
            def watch(z):
                if bytes(z.memory[z.pc:z.pc+3])==bytes.fromhex('ad0720'):
                    ppu_reads.append(dict(pc=z.pc,bank=z.memory.rawtags[(z.pc-0x8000)//8192],address=z.memory.ppu_addr))
                if kind=='FF_NMI':
                    assert z.pc!=regular
                    branch[0]+=int(z.pc==lag)
                    if not z.p&4 and(deepest[0]is None or z.sp<deepest[0].sp):deepest[0]=clone(z)
            run(c,lambda z:(z.pc,z.sp)==stop,watch)
            def no_loader(z):
                assert not(0xd9b8<=z.pc<end and z.memory.rawtags[2]==198),'ISR must not reenter constructor'
            run(legacy,lambda z:(z.pc,z.sp)==stop,no_loader)
            assert native_memory(m)==native_memory(legacy.memory),'All actual ISR native/application writes exact'
            assert live(c)==live(legacy),'All actual ISR CPU/SMC/mapper/WRAM/PPU results exact'
            assert m.writes==legacy.memory.writes,'Ordered actual ISR bus writes exact'
            assert m.ram_writes==legacy.memory.ram_writes and m.ppu_log==legacy.memory.ppu_log
            if kind=='FF_NMI':
                assert live(c)[:8]==before[:8]and live(c)[-2:]==before[-2:],(kind,hex(sample.pc),'Exact foreground restore')
                if sample.pc in pending_ppu:
                    assert live(c)==before,(kind,hex(sample.pc),'Live source stream PPU counter/buffer',
                        [(i,str(a)[:180],str(b)[:180])for i,(a,b)in enumerate(zip(before,live(c)))if a!=b],ppu_reads)
            else:
                # Native IRQ may change its native scroll/PPU state, identically
                # in the actual unchanged handler. The interrupted ABI is exact.
                assert live(c)[:4]==before[:4]and live(c)[-2:]==before[-2:],('Hardware IRQ foreground ABI',hex(sample.pc))
            assert branch[0]==int(kind=='FF_NMI')
            assert N.get(m,'NmiSkipped')==(skipped+int(kind=='FF_NMI'))&255
            counts[kind]+=1
            if deepest[0]is not None:
                z=deepest[0];entry=z.pc,z.sp;previous=live(z);z.irq()
                run(z,lambda z:(z.pc,z.sp)==entry)
                assert live(z)==previous,'Actual deepest legal nested IRQ restoration'
                counts['nested_IRQ']+=1
    return dict(passed=True,actual_cold_instruction_cuts=len(cuts),**counts,minimum_SP=minimum,
        actual_FF_branch_reached=True,all_foreground_P_values_retained=True,
        SMC_015A_017A_exact=True,full_WRAM_exact=True,FF_CHR_PPU_buffer_latch_exact=True,
        all_ISR_application_RAM_and_ordered_bus_writes_exact=True,
        live_stack_and_AXYP_PC_SP_exact=True,synthetic_I0_inside_masked_stream=False,
        scope='First genuine new seek and all genuine unmasked constructor edges; no normal NMI permitted in forced-blank constructor')


def proposal(raw,*,checks=True,interrupts=True):
    image,q=build(raw)
    if checks:q['qualification']=qualify(raw,image)
    if interrupts:q['vectors']=vectors(raw,image,q['labels'])
    files=[Path(__file__),SOURCE,Path(P.__file__),Path(P.A.__file__),P.A.BODY,
           Path(W.__file__),Path(N.__file__),Path(P.A.Engine.Frames.__file__)]
    return dict(passed=True,parent_SHA256=H(raw),expected_memory_only_SHA256=H(image),
                patches=patches(raw,image),bindings={p.relative_to(R).as_posix():H(p.read_bytes())for p in files},
                archived_input_objects={k:v[0]for k,v in P.OBJECTS.items()},**q)


def compose(raw,q):
    assert q['passed']and H(raw)==q['parent_SHA256']==P.PIN
    data=bytearray(raw)
    for row in q['patches']:
        a=row['file_offset'];old,new=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert len(old)==len(new)and bytes(data[a:a+len(old)])==old;data[a:a+len(old)]=new
    assert H(data)==q['expected_memory_only_SHA256'];return bytes(data)


def inverse(image,q):
    assert H(image)==q['expected_memory_only_SHA256']
    data=bytearray(image)
    for row in reversed(q['patches']):
        a=row['file_offset'];old,new=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert bytes(data[a:a+len(new)])==new;data[a:a+len(new)]=old
    assert H(data)==q['parent_SHA256']==P.PIN;return bytes(data)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--qualify',action='store_true');p.add_argument('--vectors',action='store_true');args=p.parse_args()
    raw=P.A.ROM.read_bytes();image,q=build(raw)
    if args.qualify:q['qualification']=qualify(raw,image)
    if args.vectors:q['vectors']=vectors(raw,image,q['labels'])
    q['patches']=patches(raw,image)
    receipt=dict(passed=True,parent_SHA256=H(raw),expected_memory_only_SHA256=H(image),**q)
    assert compose(raw,receipt)==image and inverse(image,receipt)==raw
    print('ARTHUR_TAIL_LINK '+json.dumps({k:v for k,v in receipt.items()if k not in('patches','record_extents')},separators=(',',':')),flush=True)


if __name__=='__main__':main()
