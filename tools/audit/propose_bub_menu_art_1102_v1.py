"""Measure source-funded cold Bub/Bob UI and a same-span menu stream.

All candidate bytes are used only in memory. This is a lease proposal, not a
ROM producer or menu-admission recipe. Original source pixels are copied with
no scaling; private source/helper code in CHR441's tail is never read as art.
"""
from pathlib import Path
import sys,json,subprocess,hashlib,collections
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import audit_bub_menu_frontend_1102_v1 as F
M=F.M;address=F.address;location=F.location;O=F.O

def assemble(stem,source,start,size):
    (O/(stem+'.s')).write_text(source)
    (O/(stem+'.cfg')).write_text(f'MEMORY{{P:start=${start:04x},size=${size:x},file=%O;}}SEGMENTS{{CODE:load=P,type=ro;}}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/(stem+'.s'),'-o',O/(stem+'.o')],
                [cc/'ld65.exe','-C',O/(stem+'.cfg'),O/(stem+'.o'),'-o',O/(stem+'.bin'),'-Ln',O/(stem+'.lbl')]]:
        q=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert not q.returncode,q.stderr
    return (O/(stem+'.bin')).read_bytes()

def pack(data):
    # Exact shortest stream: 1..127 repeat, 129..255 literal, zero terminator.
    # No control128 is emitted. The native decoder never changes carry.
    n=len(data);cost=[0]*(n+1);choice=[None]*n
    for i in range(n-1,-1,-1):
        options=[]
        run=1
        while run<127 and i+run<n and data[i+run]==data[i]:run+=1
        for count in range(1,run+1):options.append((2+cost[i+count],-count,'repeat',count))
        for count in range(1,min(127,n-i)+1):options.append((1+count+cost[i+count],-count,'literal',count))
        cost[i],_,kind,count=min(options);choice[i]=(kind,count)
    out=bytearray();i=0;counts=collections.Counter()
    while i<n:
        kind,count=choice[i];counts[kind]+=1
        out.extend([count,data[i]]if kind=='repeat'else [128+count,*data[i:i+count]])
        i+=count
    out.append(0);assert len(out)==cost[0]+1
    return bytes(out),dict(counts)

def run_decoder(b,pc,*,p=0x31,watch=None):
    m=M.fresh(b);m[0x5115]=194;M.put(m,CurrentBank=194,NmiDisable=255,Mirror_PPUMASK=0,DisableScreenFlag=1,R0=0x1b,R1=0xae)
    m.ppu_addr=0x2000;m.toggle=0;m.ppu_log=[];m.writes=[]
    # The real public FarCallCommon entry has already traversed PHP/PLP;
    # py65's synthetic B/unused bits therefore have their native frame values.
    c=M.NesMPU(memory=m,pc=pc);c.a=0xae;c.x=71;c.y=0;c.p=p|0x30;c.sp=210
    count=0
    while c.pc!=0xa5b9:
        if watch:watch(c)
        assert m[c.pc]!=0,('decoder BRK',hex(c.pc));c.step();count+=1
        assert count<20000
    return m,dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,R0=m[3],R1=m[4],instructions=count,cycles=c.processorCycles)

def decode_tile(d):
    return [[((d[y]>>(7-x))&1)+2*((d[y+8]>>(7-x))&1)for x in range(8)]for y in range(8)]

def main():
    assert F.sha(F.BASE)==F.PIN;b=F.scoped_load(F.BASE);raw=b['raw'];patches=[]
    def proposal(at,new,role):
        old=raw[at:at+len(new)];patches.append(dict(offset=at,old=old.hex(),new=new.hex(),role=role,preimage_SHA256=hashlib.sha256(old).hexdigest()))
    artpath=R/'build/bubble-bobble-source-1101-v1/component-native.chr';art=artpath.read_bytes()
    assert len(art)==1024 and F.sha(artpath)=='781827ea26f9c0c2896bc275da44aefc298f9e52c529cd2d9ef60b352e08a14d'
    # Native odd tiles1/11 select source pairs0/5. No read reaches byte800.
    left,right=art[:32],art[160:192];assert len(left)==len(right)==32
    portrait=bytes(32)+left+right
    proposal(1048592+700*1024,portrait,'Unused static portrait pairs0..2; exact source body, blank top row')
    bg=bytearray(raw[1048592+4096:1048592+8192]);icon_tiles=[245,246,247,248]
    source_tiles=[left[:16],right[:16],left[16:],right[16:]]
    for tile,data in zip(icon_tiles,source_tiles):
        assert not any(bg[tile*16:(tile+1)*16]);proposal(1048592+4096+tile*16,data,'Blank and unreferenced BG tile; exact source silhouette pixels')
    at=location(b,'SelectNameTable');assert at==16+66*8192+0xe1b
    oldstream=raw[at:at+677];nam=bytearray();i=0
    while oldstream[i]:
        count,value=oldstream[i:i+2];nam.extend([value]*count);i+=2
    assert i==676 and len(nam)==1024 and not set(icon_tiles)&set(nam[:960])
    oldnam=bytes(nam)
    changed=[]
    for dy in range(2):
        for dx in range(2):
            pos=(21+dy)*32+4+dx;assert nam[pos]==36
            nam[pos]=icon_tiles[dy*2+dx];changed.append(pos)
    assert nam[960+5*8+1]==0,'New icon must retain native gray palette0'
    stream,kinds=pack(nam);decoder_at=0xae1b+len(stream)
    decoder=assemble('menu-stream',f'''.setcpu "6502"
.segment "CODE"
.export BubMenuStreamDecoder
BubMenuStreamDecoder:
 ; A pending split IRQ writes PPUADDR. Mask before the first address write;
 ; a pre-SEI IRQ is harmless because this initializer replaces its address.
 php
 sei
 lda $2002
 lda #$20
 sta $2006
 lda #0
 sta $2006
 lda #$1b
 sta $03
 lda #$ae
 sta $04
 ldy #0
Next:
 lda ($03),y
 beq Done
 bmi Literal
 tax
 iny
 bne :+
 inc $04
:
 lda ($03),y
 iny
 bne Repeat
 inc $04
Repeat:
 sta $2007
 dex
 bne Repeat
 jmp Next
Literal:
 and #$7f
 tax
LiteralLoop:
 iny
 bne :+
 inc $04
:
 lda ($03),y
 sta $2007
 dex
 bne LiteralLoop
 iny
 bne Next
 inc $04
 jmp Next
Done:
 ; Preserve exact old decoder continuation, including C/D/I/V and R0/R1.
 lda #$b0
 sta $04
 ldy #$a4
 ldx #0
 plp
 lda #0
 jmp $a5b9
''',decoder_at,677-len(stream))
    assert len(stream)+len(decoder)<=677
    proposal(at,stream+decoder+bytes([0xea])*(677-len(stream)-len(decoder)),'Same677B stream plus carry-preserving literal/repeat decoder')
    olddecoder=16+66*8192+0x588;assert raw[olddecoder:olddecoder+3]==bytes.fromhex('ad0220')
    proposal(olddecoder,bytes([0x4c,decoder_at&255,decoder_at>>8])+bytes([0xea])*46,'Original49B PPU initialization/decoder replaced by same-bank transaction; A5B9 continuation fixed')
    # Cold slot32 intentionally uses real pending UI, not private owner rows.
    pending=assemble('pending-static','''.setcpu "6502"
.segment "CODE"
.export BubColdPending
BubColdPending:
 ldx $7309
 cpx #32
 bne Foreign
 lda $5fe8
 bmi Bob
 lda #9
 bne Return
Bob:lda #14
Return:sec
 rts
Foreign:jmp $b97c
''',0xbced,32)
    assert len(pending)==23
    proposal(location(b,'FmPending'),bytes.fromhex('4cedbc'),'Cold slot32 pending UI wrapper; all old slots resume original CPX0')
    proposal(location(b,'FmNames'),pending+bytes([0xea])*(32-len(pending)),'Unused names0/1 fund static pending wrapper')
    for row,label,color in [(9,'BUB',[0x2a,0x26,0x30]),(14,'BOB',[0x2c,0x23,0x30])]:
        name=[36]*16;name[6:9]=[ord(c)-ord('A')+10 for c in label]
        proposal(location(b,'FmNames')+16*row,bytes(name),'Unused pending name row'+str(row))
        proposal(location(b,'FmPreviewTiles')+4*row,bytes([0,0,2,4]),'Unused pending portrait row'+str(row))
        proposal(location(b,'FmPreviewColors')+3*row,bytes(color),'Original source RGB portrait palette row'+str(row))
    nr=bytearray(raw)
    for z in patches:nr[z['offset']:z['offset']+len(bytes.fromhex(z['new']))]=bytes.fromhex(z['new'])
    nb=dict(b);nb['raw']=bytes(nr)
    decoder_cases=0
    for flags in range(256):
        old,zold=run_decoder(b,0xa588,p=flags);new,znew=run_decoder(nb,0xa588,p=flags)
        assert {k:v for k,v in zold.items()if k not in['instructions','cycles']}=={k:v for k,v in znew.items()if k not in['instructions','cycles']}
        assert bytes(old.vram[0x2000:0x2400])==oldnam and bytes(new.vram[0x2000:0x2400])==nam
        assert sum(a==0x2007 for a,v in old.ppu_log)==sum(a==0x2007 for a,v in new.ppu_log)==1024
        assert new.ppu_addr==old.ppu_addr==0x2400
        assert old.rawtags==new.rawtags and old.chr_latches==new.chr_latches
        decoder_cases+=1
    oldseed=M.fresh(b);newseed=M.fresh(nb);pending_cases=0;domains=collections.defaultdict(set)
    # Every byte value of the single family-dependent input is tested. The
    # actual original pending code reads at most one of these fields per slot.
    fields={0:'MarioVariant',2:'RdVariant',7:'FmAlts',9:'FmAlts',10:'FmAlts',11:'FmAlts',21:'FfMode',24:'Sm2Variant',26:'FmAlts',28:'FmGroups',29:'FmAlts',30:'FmGroups',31:'FmAlts'}
    aliases={0:0x730a,2:0x5fee,7:0x5fe5,9:0x5fe5,10:0x5fe5,11:0x5fe5,21:0x5fef,24:0x5fe3,26:0x5fe5,28:0x5fe8,29:0x5fe5,30:0x5fe8,31:0x5fe5}
    for slot in range(32):
        for value in range(256)if slot in aliases else [0]:
            pair=[]
            for seed in [oldseed,newseed]:
                m=M.fork(seed);M.put(m,CrossoverMenuIndex=slot)
                if slot in aliases:m[aliases[slot]]=value
                z=F.invoke(m,'FmPending');pair.append(z)
            assert all(pair[0][k]==pair[1][k]for k in ['A','X','Y','P']),('pending foreign',slot,value,pair)
            domains[slot].add((pair[0]['A'],pair[0]['P']&1));pending_cases+=1
    own=[]
    for groups in range(256):
        m=M.fork(newseed);M.put(m,CrossoverMenuIndex=32,FmGroups=groups)
        z=F.invoke(m,'FmPending');assert z['A']==(14 if groups&128 else 9)and z['P']&1
        own.append(z['A'])
    q=dict(passed=True,proposal_only=True,ROM_written=False,menu_admitted=False,native=False,base_ROM_SHA256=F.PIN,
        requested_patches=patches,old_stream_bytes=677,new_stream_bytes=len(stream),decoder_bytes=len(decoder),stream_and_decoder_bytes=len(stream)+len(decoder),spare_bytes=677-len(stream)-len(decoder),stream_packet_kinds=kinds,
        new_icon=dict(leftX=32,topY=160,source_body_topY=168,width=16,height=24,nametable_changed_positions=changed,tiles=icon_tiles,exact_source_pixel_count=256),
        decoder_full_input_P_cases=decoder_cases,old_decoder_continuation=zold,new_decoder_continuation=znew,
        foreign_pending_byte_cases=pending_cases,own_pending_byte_cases=len(own),pending_wrapper_bytes=len(pending),
        pending_domains={str(k):sorted(v)for k,v in domains.items()},dependent_field_per_slot=fields,
        lease_closure_remaining=['Formal root grants for requested static data, CHR and same677B decoder rewrite.','Confirm actual global CHR700/menuBG reader ownership against finite publisher closure.','Actual disabled-NMI/IRQ cuts and native menu inspection before admission.'],
        bindings={p.relative_to(R).as_posix():F.sha(p)for p in [Path(__file__),Path(F.__file__),F.BASE,artpath,O/'menu-stream.s',O/'menu-stream.bin',O/'pending-static.s',O/'pending-static.bin',O/'frontend-closure.json']})
    (O/'art-proposal.json').write_text(json.dumps(q,indent=2)+'\n')
    files=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in files)<16000000 and len(files)<=128
    print(json.dumps({k:v for k,v in q.items()if k not in['requested_patches','bindings','pending_domains','dependent_field_per_slot']}))
if __name__=='__main__':main()
