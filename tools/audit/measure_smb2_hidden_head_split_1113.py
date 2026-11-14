"""Unallocated publisher-sharing fit; code bytes only, never a ROM composer."""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from py65.devices.mpu6502 import MPU

import measure_smb2_hidden_head_1113 as Prior
from compose_metal_head_bridge_1112 import assemble_segments

Route=Prior.Route
ORIGINS=dict(S2_FLAG_PROBE=0xb128,HIDDEN_PREDICATE=0xa637,
             HIDDEN_VY=0xb86b,HIDDEN_RETURN=0xbc96)
PAD_SOURCES=(
    ('HIDDEN_PREDICATE',9,'src/smb2_roster.s',
     'e800627aa1297c7f9503a18c700383bda2fc16b516f30e79c3b379cfba60e057',5,
     '.res 9,$ff',255),
    ('HIDDEN_VY',4,'src/smb2_roster_palette_v2.s',
     '54b432ff7332181fd092e19a7f5d6a02043bc4ec1c8edece786ff3ef2f1cbe7f',27,
     '.res 45-(*-OwnStart),$ea',234),
    ('HIDDEN_RETURN',14,'src/smb2_roster_main_v2.s',
     '605c9db58cea4b18a860b961ad5b34db16dddf4bf09af18cfe3b3c40fcb2f92c',567,
     '.res 14,$ea',234))


def recipe(raw):
    assert sha256(raw).hexdigest()==Route.PIN
    _,b,_=Route.inputs(raw);W=Route.W;Owner=Route.Current.Flag
    _,current,_=Owner.source_recipe(raw)
    source=Owner.Check.SOURCE.read_text().split('.segment "S2_FLAG_WORLD"')[0]
    names=('R0','R2','R4','R5','R6','R7','S2X','S2Y','S2Page','S2YPage',
           'S2ProbeDirection','S2HeadX','S2HeadPage','S2HeadY','S2Math0',
           'S2DF011','S2DF055','GetBlockBufferAddr','MTileAttribute','S2VY')
    constants={n:W.address(b,n)for n in names}
    old,labels=assemble_segments(source,{'S2_FLAG_PROBE':0xb128},constants)
    assert old['S2_FLAG_PROBE']==current['probe']==raw[Owner.PROBE_AT:Owner.PROBE_AT+174]
    source=Prior.once(source,' lda R6\n sta R2\n lda R6\n sec',' sta R2\n sec')
    source=Prior.once(source,''' lda R5
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda R4
 lsr
 lsr
 lsr
 lsr
 ora R0''',''' lda R5
 lsr
 lda R4
 ror
 lsr
 lsr
 lsr
 pha
 and #$10
 sta R0
 pla''')
    source=Prior.once(source,' cmp #$60\n beq ProbeEmpty\n tay',''' cmp #$60
 bne HiddenNormalTile
 jsr S2HiddenPredicate
 bmi HiddenCacheGate
 bcs ProbeEmpty
HiddenNormalTile:
 tay''')
    source=Prior.once(source,' lda S2ProbeDirection\n cmp #2\n bcs ProbeSolid',''' tax
HiddenCacheGate:
 lda S2ProbeDirection
 cmp #2
 bcs ProbeSolid''')
    source=Prior.once(source,'ProbeSolid:\n lda #$ff\n bne ProbeResult','''ProbeSolid:
 jmp S2HiddenReturn''')
    source+='''
.segment "HIDDEN_PREDICATE"
S2HiddenPredicate:
 txa
 beq HiddenPlayer
 and #$7f
 rts
HiddenPlayer:
 jmp S2HiddenLoadVY
.segment "HIDDEN_VY"
S2HiddenLoadVY:
 lda S2VY
 rts
.segment "HIDDEN_RETURN"
S2HiddenReturn:
 txa
 beq HiddenZero
 lda #$ff
 bne HiddenStore
HiddenZero:
 sec
HiddenStore:
 sta S2Math0
 pla
 tax
 rts
'''
    code,newlabels=assemble_segments(source,ORIGINS,constants)
    assert {k:len(v)for k,v in code.items()}==dict(S2_FLAG_PROBE=174,HIDDEN_PREDICATE=9,HIDDEN_VY=4,HIDDEN_RETURN=14)
    assert newlabels['S2FlagProbe']==0xb128 and newlabels['S2FlagSharedReturn']==0xb1d5
    return b,source,old['S2_FLAG_PROBE'],code,labels,newlabels


def measure(raw):
    b,source,old,code,labels,newlabels=recipe(raw);W=Route.W
    packet=W.R/'docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1/source.zip'
    prefix='build/doki-current-component-1101-v1/'
    pads=[]
    with ZipFile(packet)as z:
        for name,size,member,digest,line,declaration,fill in PAD_SOURCES:
            data=z.read(prefix+member);assert sha256(data).hexdigest()==digest
            assert declaration in data.decode().splitlines()[line-1]
            pc=ORIGINS[name];at=16+118*8192+(pc&8191)
            pre=raw[at:at+size];assert pre==bytes([fill])*size
            pads.append(dict(segment=name,CPU_begin=pc,CPU_end_exclusive=pc+size,
                file=at,bytes=size,preimage_hex=pre.hex(),preimage_SHA256=sha256(pre).hexdigest(),
                proposed_hex=code[name].hex(),source_member=prefix+member,
                source_member_SHA256=digest,source_line=line,declaration=declaration))
    changes=[]
    for i,(a,c)in enumerate(zip(old,code['S2_FLAG_PROBE'],strict=True)):
        if a!=c:
            at=Route.Current.Flag.PROBE_AT+i
            if changes and sum(changes[-1])==at:changes[-1][1]+=1
            else:changes.append([at,1])
    return dict(passed=True,ROM_SHA256=Route.PIN,
        source_packet=str(packet.relative_to(W.R)),main_bytes=174,
        current_probe_file=Route.Current.Flag.PROBE_AT,
        current_probe_SHA256=sha256(old).hexdigest(),current_probe_hex=old.hex(),
        measured_probe_hex=code['S2_FLAG_PROBE'].hex(),main_changed_ranges=changes,
        relocated_internal_labels={n:[labels[n],newlabels[n]]for n in labels if n in newlabels and labels[n]!=newlabels[n]},
        protected_public_anchors=dict(probe=0xb128,shared_return=0xb1d5,ground=0xb1d6,
            component=0xa640,main=0xb86f,spawn=0xbca4),
        requested_code_bytes=27,requested_resources=pads,
        generated_source_SHA256=sha256(source.encode()).hexdigest(),
        shared_publisher='Existing R4/R5/R2 to HeadX/Page/Y stores; no duplicated publisher',
        return_stack='Predicate JSR returns first; solid JMP tail consumes original saved X and original caller return',
        all_non60_oracle_and_interrupt_gates_PENDING=True,
        reader_closure_PENDING=True,formal_grant=False,composer_created=False,
        source_candidate_ROM=False,ROM_mutations=0,new_RAM_bytes=0,outputs=0,Mesen_run=False)


def _procedure(data,name,padding):
    body=data.decode().split('.proc '+name,1)[1].split('.endproc',1)[0]
    rows=[]
    for line in body.splitlines():
        line=line.split(';',1)[0].strip()
        if not line or line.startswith('.assert'):continue
        if line.startswith('.res'):
            line='.byte '+','.join(['$ea']*padding)
        match=re.match(r'^(\w+):(.*)$',line)
        if match:rows.append(match[1]+':');line=match[2].strip()
        if line:rows.append(line)
    return '.segment "OWNER"\n'+'\n'.join(rows)


def readers(raw):
    """Declared source padding and its actual bounded consumers; no placement."""
    b,_,_,_,_,_=recipe(raw);W=Route.W
    packet=W.R/'docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1/source.zip'
    prefix='build/doki-current-component-1101-v1/'
    with ZipFile(packet)as z:
        palette=z.read(prefix+'src/smb2_roster_palette_v2.s')
        main=z.read(prefix+'src/smb2_roster_main_v2.s')
    constants={n:W.address(b,n)for n in ('VRAM_Buffer1','BackgroundColorCtrl','AreaType',
        'StarInvincibleTimer','VRAM_Buffer_AddrCtrl','S2NativeCharacter','S2PaletteAck',
        'S2PalettePointer','VRAM_Buffer1_Offset','S2NativePaletteHeader','R0')}
    originals=[]
    for name,data,origin,size,padding in (
        ('S2NativePaletteHeader',palette,0xb842,45,4),
        ('S2MainPalette',main,0xbc5a,74,14)):
        source=_procedure(data,name,padding)
        source=re.sub(r'\b(\w+)\+([0-9]+)',
            lambda m:'$%04x'%(constants[m[1]]+int(m[2])),source)
        code,labels=assemble_segments(source,{'OWNER':origin},constants)
        at=16+118*8192+(origin&8191)
        assert len(code['OWNER'])==size and raw[at:at+size]==code['OWNER'],name
        originals.append(dict(name=name,CPU=origin,bytes=size,
            SHA256=sha256(code['OWNER']).hexdigest(),labels=labels))
    hdr=originals[0]['labels'];pal=originals[1]['labels']
    assert hdr['S2NativeBGBytes']==0xb863 and pal['Done']==0xbc95
    parodius=W.location(b,'PnBombWorldDamage')
    assert parodius+18==16+118*8192+0x637,(parodius,raw[parodius:parodius+40].hex(),
        raw[16+118*8192+0x617:16+118*8192+0x640].hex())
    assert raw[parodius:parodius+3]==bytes.fromhex('8d6a01')
    assert raw[parodius+15:parodius+18]==bytes.fromhex('4c5a01')
    image=raw[16+118*8192:16+119*8192]
    # Literal call/jump census includes every byte offset, even data, and is
    # deliberately only a conservative inbound check, not a decoder proof.
    pads=[(ORIGINS[n],ORIGINS[n]+s)for n,s,*_ in PAD_SOURCES]
    targets=[]
    for i in range(8190):
        if image[i]in(0x20,0x4c):
            dest=int.from_bytes(image[i+1:i+3],'little')
            if any(lo<=dest<hi for lo,hi in pads):targets.append((0xa000+i,dest))
    assert not targets
    header_calls=[0xa000+i for i in range(8190)if image[i:i+3]==b'\x20\x42\xb8']
    assert len(header_calls)==1 and 0xbc5a<=header_calls[0]<0xbc96
    # The sole indexed ROM read in the Header is its original eight colors.
    table_read=b'\xb9\x63\xb8'
    table_readers=[0xa000+i for i in range(8190)if image[i:i+3]==table_read]
    assert len(table_readers)==1 and 0xb842<=table_readers[0]<0xb863
    assert image[0x1863:0x186b]==bytes.fromhex('22220f0f0f220f0f')
    # Bind the native producers, not just a comment about their range. Both
    # level parser writers mask to three bits. Title/menu write0/2; the lives
    # screen saves/restores that value and temporarily writes2.
    bg=constants['BackgroundColorCtrl'];store=b'\x8d'+bg.to_bytes(2,'little')
    prg=raw[16:16+128*8192]
    parser_prefix=b'\x29\x07\xc9\x04\x90'
    parser_writers=[]
    for i in range(len(prg)-12):
        if prg[i:i+5]==parser_prefix and prg[i+6:i+9]==store:
            parser_writers.append(dict(bank=i//8192,offset=i%8192,window=prg[i:i+11].hex()))
    assert len(parser_writers)==2,parser_writers
    for member in ('level_tiles.s','character_select.s','screen_render.s'):
        text=(W.R/'src'/member).read_text()
        if member=='level_tiles.s':
            assert text.count('sta BackgroundColorCtrl')==2
            assert text.count('and #%00000111')>=2
        elif member=='character_select.s':
            assert text.count('sta BackgroundColorCtrl')==3
        else:
            assert text.count('sta BackgroundColorCtrl')==2
    rogue=[]
    for mode,count,banks,highs in (
        ('lower',192,'RdaLowerBankTable','RdaLowerHighTable'),
        ('upper',32,'RdaUpperRawBankTable','RdaUpperRawHighTable')):
        bank_at,high_at=W.location(b,banks),W.location(b,highs)
        for i in range(count):
            bank=raw[bank_at+i]&127;start=(raw[high_at+i]-0xa0)*256
            assert 0<=start<=8192-256 and bank!=118
            rogue.append((mode,i,bank,start))
    banks=W.location(b,'S2AudioSampleBank');starts=W.location(b,'S2AudioSampleStart')
    lengths=W.location(b,'S2AR8349');samples=[]
    for i in range(8):
        bank=raw[banks+i];begin=0xc000+64*raw[starts+i];size=16*raw[lengths+i+1]+1
        assert bank in(119,120)and begin>=0xf140 and begin+size<=0x10000
        samples.append(dict(bank=bank,CPU_begin=begin,bytes=size))
    assert (W.location(b,'S2AudioCodeEnd')-16)//8192==74
    assert (W.location(b,'S2AudioMusicData')-16)//8192==117
    return dict(passed=True,ROM_SHA256=Route.PIN,
        full_source_reproduced_envelopes=[{k:v for k,v in q.items()if k!='labels'}for q in originals],
        local_literal_JSR_JMP_into_requested_padding=targets,
        sole_header_caller=header_calls[0],sole_header_color_read=table_readers[0],
        header_ROM_table_half_open=[0xb863,0xb86b],
        header_index_domain='BackgroundColorCtrl0..7; if0, AreaType0..3',
        actual_masked_parser_writers=parser_writers,
        current_Rogue_page_readers_excluding_bank118=len(rogue),
        S2_DMC_samples=samples,audio_driver_physical_bank=74,music_data_physical_bank=117,
        original_padding_fallthrough=False,
        protected_header_return=0xb862,protected_palette_return=0xbc95,
        preceding_Parodius_tail=dict(file=parodius,bytes=18,
            hex=raw[parodius:parodius+18].hex(),terminates_with='JMP resident015A'),
        excluded_fill='BFFC..BFFF and module-end gaps are not requested',
        formal_grant=False,composer_created=False,ROM_mutations=0,outputs=0,Mesen_run=False)


def units(raw):
    """Synthetic code/stack measurements, not gameplay or whole-probe proof."""
    b,_,old,code,labels,newlabels=recipe(raw);W=Route.W
    def memory(proposed):
        m=bytearray(65536)
        at=W.location(b,'MTileAttribute');pc=W.address(b,'MTileAttribute')
        m[pc:pc+256]=raw[at:at+256]
        m[0xb128:0xb1d6]=code['S2_FLAG_PROBE']if proposed else old
        if proposed:
            for name in ('HIDDEN_PREDICATE','HIDDEN_VY','HIDDEN_RETURN'):
                m[ORIGINS[name]:ORIGINS[name]+len(code[name])]=code[name]
        return m
    oldm,newm=memory(False),memory(True)
    addr={n:W.address(b,n)for n in ('S2VY','S2ProbeDirection','S2Math0','S2HeadX','S2HeadPage','S2HeadY')}
    def call(m,proposed,tile,owner,p,direction,vy):
        m[7],m[8],m[5]=0,4,128
        m[addr['S2VY']],m[addr['S2ProbeDirection']]=vy,direction
        for name,val in (('S2Math0',77),('S2HeadX',11),('S2HeadPage',22),('S2HeadY',33)):
            m[addr[name]]=val
        m[0x1fb:0x1fe]=bytes([owner,0xee,0xbe])
        cpu=MPU(memory=m,pc=(newlabels if proposed else labels)['ProbeOtherTile'])
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=tile,owner,96,p,250
        for _ in range(80):
            if cpu.pc==0xbeef:
                return ((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc),
                    tuple(m[addr[n]]for n in ('S2Math0','S2HeadX','S2HeadPage','S2HeadY')),
                    cpu.processorCycles)
            cpu.step()
        raise AssertionError('bounded code unit')
    normal=hidden=0;cycles={}
    for tile in range(256):
        for owner in (0,1,128,255):
            for p in (0,65,255):
                for direction in (0,1,2,3,6,7):
                    for vy in (0,128):
                        a=call(oldm,False,tile,owner,p,direction,vy)
                        c=call(newm,True,tile,owner,p,direction,vy)
                        assert a[0]==c[0],(tile,owner,p,direction,vy,a,c)
                        if tile!=96:
                            assert a[1]==c[1],(tile,owner,p,direction,vy,a,c)
                            normal+=1
                        else:
                            assert c[1]==(0,*((0,4,128)if owner==0 and vy>=128 and direction<2 else(11,22,33)))
                            hidden+=1
                        if owner==0 and p==0 and direction in(0,3)and vy==128 and tile in(0x54,0x60,0xc2,0xc4):
                            cycles['%02x/dir%d'%(tile,direction)]=dict(old_leaf=a[2],new_leaf=c[2],delta=c[2]-a[2])
    # Independent execution of the index algebra over every source page and
    # aligned world X. Only V/C/P subsets matter; the remaining bits survive.
    factor_old=bytes.fromhex('a50829010a0a0a0a8503a5074a4a4a4a0503')
    factor_new=bytes.fromhex('a5084aa5076a4a4a4a482910850368')
    index_pairs=0
    fm=[bytearray(65536),bytearray(65536)]
    for m,q in zip(fm,(factor_old,factor_new),strict=True):m[0x8000:0x8000+len(q)]=q
    for page in range(256):
        for x in range(0,256,16):
            for p in(0,1,64,255):
                results=[]
                for m,q in zip(fm,(factor_old,factor_new),strict=True):
                    m[3],m[7],m[8]=173,x,page
                    cpu=MPU(memory=m,pc=0x8000);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=37,99,25,p,200
                    for _ in range(30):
                        if cpu.pc==0x8000+len(q):break
                        cpu.step()
                    else:raise AssertionError('bounded index unit')
                    results.append(((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,m[3]),cpu.processorCycles))
                assert results[0][0]==results[1][0],(page,x,p,results)
                assert results[1][1]-results[0][1]==-2
                index_pairs+=1
    return dict(passed=True,ROM_SHA256=Route.PIN,
        synthetic_unit_only=True,non60_leaf_pairs=normal,hidden_leaf_pairs=hidden,
        independent_index_pairs=index_pairs,
        leaf_AXYP_SP_return_and_Math_cache_exact_except_intended_hidden_cache=True,
        leaf_cycles=cycles,prefix_cycle_saving=8,
        cycle_scope='Leaf starts OtherTile; subtract8 for full-prefix factoring; no native interrupt/performance claim',
        full_probe_caller_IRQ_busyNMI_and_natural_lifecycle_PENDING=True,
        formal_grant=False,composer_created=False,ROM_mutations=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--readers',action='store_true');p.add_argument('--units',action='store_true');args=p.parse_args()
    raw=Route.Post.Owner.NIGHTLY.read_bytes()
    print(json.dumps(units(raw)if args.units else readers(raw)if args.readers else measure(raw),separators=(',',':')),flush=True)
