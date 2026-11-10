"""Link Jay's cold entry into current source-backed cartridge banks."""
from collections import Counter, defaultdict
import json

import check_jay_silius_funded_hot_1110 as Hot

S,C,H,W,N = Hot.S,Hot.C,Hot.H,Hot.W,Hot.N
SOURCE = H.ROOT/'tools/reference/jay_silius_cold_resident_1110.s'
PIN = S.PIN
BOOT = 0xd25e
PROTO = ('ProtoPoseLeftLo','ProtoPoseLeftHi','ProtoPoseRightLo','ProtoPoseRightHi','ProtoPoseChrLo')
SUNNY = ('SunnyRLo','SunnyRHi','SunnyLLo','SunnyLHi','SunnyChrLow','SunnySemanticSmall','SunnySemanticBig')


def u16(value):
    return value.to_bytes(2,'little')


def pack(data):
    # The existing format charges a flag byte per eight tokens. Include the
    # flag slot when choosing the least expensive exact parse.
    positions=defaultdict(list)
    options=[]
    for offset in range(len(data)):
        stem=data[offset:offset+3]
        lengths={}
        if len(stem)==3:
            for earlier in reversed(positions[stem]):
                distance=offset-earlier
                if distance>4095:break
                length=3
                while length<18 and offset+length<len(data) and data[earlier+length]==data[offset+length]:
                    length+=1
                for size in range(3,length+1):
                    lengths.setdefault(size,distance)
            positions[stem].append(offset)
        options.append([(1,0),*lengths.items()])
    cost=[[0]*8 for _ in range(len(data)+1)]
    choice=[[None]*8 for _ in range(len(data))]
    for offset in range(len(data)-1,-1,-1):
        for bit in range(8):
            def expense(token):
                size,_=token
                return (1 if size==1 else 2)+cost[offset+size][(bit+1)&7]
            token=min(options[offset],key=expense)
            choice[offset][bit]=token
            cost[offset][bit]=(bit==0)+expense(token)
    packed=bytearray()
    offset=0
    while offset<len(data):
        flags=len(packed)
        packed.append(0)
        for bit in range(8):
            if offset==len(data):break
            size,distance=choice[offset][bit]
            if size==1:
                packed.append(data[offset])
            else:
                packed[flags]|=1<<bit
                packed.extend((distance&255,((distance>>8)<<4)|(size-3)))
            offset+=size
    assert len(packed)==cost[0][0]
    return bytes(packed)


def boot_stage(runtime):
    encoded=pack(runtime)
    assert C.digest(S.SOURCE.read_bytes())=='b269f8a94faa2a88b4a0dae756fece6603eb75c850820e500403ed3d6a68cf43'
    source=S.SOURCE.read_text()
    start=source.index('Complete:\n')
    stop=source.index('ReadByte:\n',start)
    complete=source[start:stop].replace(' bne Failed\n sec\n bcs Return',' beq Return')
    assert ' beq Return\nFailed:' in complete
    source=source[:start]+source[stop:]
    source=source.replace('Match:\n',complete+'Match:\n',1)
    source=source.replace(' bne More\n jmp Complete\nEarlyFailed:\n jmp Failed',' beq Complete')
    source=source.replace('EarlyFailed','Failed')
    source=source.replace(' cmp #$c0\n bcs Failed\n','')
    source=source.replace('ReadByte:\n','''ReadByte:
 lda Src+1
 cmp #$d2
 bne CheckPackedEnd
 lda Src
 cmp #$5e
 bne CheckPackedEnd
 lda #$61
 sta Src
CheckPackedEnd:
''')
    end=f'DecodedEnd=${0xa000+len(runtime):04x}\n'
    decoder=H.assemble(end+'PackedEnd=$d800\n'+source,{'DECODE':(0xd000,512)})
    size=decoder['used']['DECODE']+len(encoded)+3
    assert size<=2048,(size,len(encoded),decoder['used'])
    decoder=H.assemble(end+f'PackedEnd=${0xd000+size:04x}\n'+source,{'DECODE':(0xd000,512)})
    data=decoder['images']['DECODE']+encoded
    split=BOOT-0xd000
    staged=data[:split]+b'\x4c\x00\xd0'+data[split:]
    return staged.ljust(2048,b'\xea'),decoder,dict(packed=len(encoded),decoder=decoder['used']['DECODE'],
        trampoline=3,used=size,spare=2048-size)


def source_art(base):
    raw=base['raw']
    assert W.address(base,'SunnyArtBegin')==0xce00 and W.address(base,'SunnyArtEnd')==0xd25f
    assert W.address(base,'ProtoPoseLeftLo')==0xc696 and W.address(base,'ProtoArtEnd')==0xc738
    assert W.address(base,'RdArtStart')==0xd300
    packed=bytearray()
    emitted={}
    lows=[]
    highs=[]
    for face in ('R','L'):
        low=bytearray()
        high=[]
        for pose in range(35):
            at=W.location(base,f'SunnyFrame{pose}{face}')
            art=raw[at:at+1+raw[at]]
            if art not in emitted:
                emitted[art]=0xce00+len(packed)
                packed.extend(art)
            low.append(emitted[art]&255)
            high.append(emitted[art]>>8)
        lows.append(bytes(low))
        highs.append(high)
    assert len(packed)==838
    assert highs[0]==[0xcf if n>=25 and n!=26 else 0xce for n in range(35)]
    assert highs[1]==[0xd1 if n>=32 else 0xcf if n<=10 or 12<=n<=14 or n==26 else 0xd0 for n in range(35)]
    new={}
    for name,data in zip(('SunnyRLo','SunnyLLo'),lows):
        new[name]=0xce00+len(packed)
        packed.extend(data)
    for name,size in zip(SUNNY[4:],(35,17,17)):
        at=W.location(base,name)
        new[name]=0xce00+len(packed)
        packed.extend(raw[at:at+size])
    high_start=0xce00+len(packed)
    return bytes(packed),new,high_start


def proposal(raw,donor):
    assert C.digest(raw)==PIN
    base,_,_,linked,runtime,_,_,_,extra,_=S.proposal(raw,donor)
    stage,decoder,sizes=boot_stage(runtime)
    desc=bytes.fromhex('0200014b014c01')
    cookie=bytes((0xa7,16,32,3))+C.sha256(stage+runtime+desc).digest()[:12]
    packed,sunny,high_start=source_art(base)
    proto={}
    proto_bytes=bytearray()
    text=SOURCE.read_text().replace('CookieBytes',','.join(map(str,cookie)))
    high_only=text[text.index('.segment "SUNNY94"'):]
    high=H.assemble(high_only,{'SUNNY94':(high_start,64)})
    start=high_start+len(high['images']['SUNNY94'])
    for name in PROTO:
        at=W.location(base,name)
        proto[name.replace('Pose','')]=start+len(proto_bytes)
        proto_bytes.extend(raw[at:at+27])
    hot_start=start+len(proto_bytes)-0x2000
    gate=H.assemble('PrivateUpdate=$a785\n'+Hot.HOT_SOURCE.read_text().replace('CookieBytes',','.join(map(str,cookie))),
                    {'HOT94':(hot_start,124)})
    layout={'COLD65':(0xa696,162),'PROTO66':(0xa12e,53),'SUNNY94':(high_start,64)}
    constants=''.join(f'{name}=${value:04x}\n' for name,value in proto.items())
    program=H.assemble(constants+text,layout)
    image=bytearray(raw)
    asset=packed+high['images']['SUNNY94']+bytes(proto_bytes)+gate['images']['HOT94']
    assert len(asset)<=0x500 and len(proto_bytes)==135
    assert raw[C.offset(94,0xd25f):C.offset(94,0xd300)]==b'\xff'*161
    image[C.offset(94,0xce00):C.offset(94,0xd300)]=asset.ljust(0x500,b'\xff')
    start=C.offset(65,0xa696)
    assert raw[start+135:start+162]==b'\x01'*27
    image[start:start+162]=program['images']['COLD65'].ljust(162,b'\xea')
    start=C.offset(66,0xa12e)
    assert W.location(base,'ProtoSetPose')==start and W.location(base,'ProtoPortrait')==start+53
    assert len(program['images']['PROTO66'])==53
    image[start:start+53]=program['images']['PROTO66']
    # Close each old table reader and replace only the corresponding operand.
    readers={}
    for name in (*PROTO,'ProtoPoseChrHi',*SUNNY):
        old=W.address(base,name)
        bank=66 if name.startswith('Proto') else 81
        at=16+8192*bank
        prefix=bytes((0xbd,))+u16(old)
        hits=[pc for pc in range(at,at+8190) if raw[pc:pc+3]==prefix]
        readers[name]=[hex(0xa000+pc-at) for pc in hits]
        if name=='ProtoPoseChrHi':
            assert not hits
            continue
        assert len(hits)==1,(name,hits)
        if bank==66:
            assert C.offset(66,0xa12e)<=hits[0]<C.offset(66,0xa163)
            continue
        assert C.offset(81,W.address(base,'SunnySetPose'))<=hits[0]<C.offset(81,W.address(base,'SunnySetPose'))+150
        if name in ('SunnyRHi','SunnyLHi'):
            target=high['symbols']['SunnyRightHigh' if name=='SunnyRHi' else 'SunnyLeftHigh']
            image[hits[0]:hits[0]+3]=b'\x20'+u16(target)
        else:
            image[hits[0]+1:hits[0]+3]=u16(sunny[name])
    for bank,pc,old,label in ((65,0xac2c,'2026b0','JaySceneOrRetire'),(65,0xaf00,'ad0260','JaySelect')):
        at=C.offset(bank,pc)
        assert raw[at:at+3]==bytes.fromhex(old)
        image[at:at+3]=bytes((0x20 if old.startswith('20')else 0x4c,))+u16(program['symbols'][label])
    assert image[C.offset(65,0xae85):C.offset(65,0xae88)]==bytes.fromhex('2072ab')
    pose=S.Funding.SOURCE.read_text().split('JayMovementRoute:',1)[0]+f'''JayMovementRoute:
 lda #${hot_start&255:02x}
 sta $016c
 lda #${hot_start>>8:02x}
 sta $016d
 lda #$de
 jmp $015a
'''
    route=H.assemble(pose,{'MIKE_POSE':(0xa276,85)})
    start=C.offset(96,0xa276)
    image[start:start+85]=route['images']['MIKE_POSE']
    start=C.offset(96,0xa53d)
    assert raw[start:start+3]==bytes.fromhex('4ccba2')
    image[start:start+3]=bytes.fromhex('4cbca2')
    for i,page in enumerate(C.PAGES):
        start=C.CHR+1024*page
        image[start:start+1024]=stage[1024*i:1024*(i+1)]
    changed_prg={i for i in range(128) if raw[16+8192*i:16+8192*(i+1)]!=image[16+8192*i:16+8192*(i+1)]}
    assert changed_prg=={65,66,81,94,96}
    changed_chr={i for i in range(1024) if raw[C.CHR+1024*i:C.CHR+1024*(i+1)]!=image[C.CHR+1024*i:C.CHR+1024*(i+1)]}
    assert changed_chr=={331,332}
    # This harness still imports the donor weapon. All scene and movement
    # entry instructions and descriptor data are now native cartridge bytes.
    receipt=dict(cold_bytes=program['used']['COLD65'],bank94_used=len(asset),bank94_spare=0x500-len(asset),
        hot_entry=hex(hot_start),proto_table_start=hex(min(proto.values())),readers=readers,stage=sizes,
        changed_prg_banks=sorted(changed_prg),changed_chr_pages=sorted(changed_chr))
    return base,dict(base,raw=bytes(image)),program,linked,runtime,stage,cookie,gate,extra,decoder,receipt


def pose_checks(base,trial):
    seeds=[N.fresh(q) for q in (base,trial)]
    proto=0
    for face in (1,2):
        for pose in range(27):
            pair=[]
            for seed in seeds:
                m=N.fork(seed)
                N.put(m,SelectedCharacter=1,ProtoVariant=1,PlayerFacingDir=face)
                result=N.invoke(m,'ProtoSetPose',x=pose)
                pair.append((tuple(result[k]for k in ('A','X','Y','P')),bytes(m[:0x1c0]),
                             bytes(m[0x200:0x8000]),m.ram,m.rawtags,m.chr_latches))
            assert pair[0]==pair[1], (face,pose)
            proto+=1
    sunny=0
    for form in (0,1):
        for face in (1,2):
            for pose in range(256):
                pair=[]
                for seed in seeds:
                    m=N.fork(seed)
                    N.put(m,SelectedCharacter=23,PlayerFacingDir=face,PlayerStatus=form)
                    result=N.invoke(m,'SunnySetPose',x=pose)
                    ptr=N.get(m,'SmPosePtr')+256*N.get(m,'SmPosePtr',1)
                    art=bytes(m[ptr:ptr+1+m[ptr]])
                    N.put(m,SmPosePtr=0)
                    m[W.address(base,'SmPosePtr')+1]=0
                    pair.append((tuple(result[k]for k in ('A','X','Y','P')),art,bytes(m[:0x1c0]),
                                 bytes(m[0x200:0x8000]),m.ram,m.rawtags,m.chr_latches))
                assert pair[0]==pair[1], (form,face,pose)
                sunny+=1
    first=H.Roster.Starts.C.inventory(base['raw'])
    assert H.Roster.Starts.C.inventory(trial['raw'])==first
    names=[]
    for row in first['rows']:
        if row['name'] not in ('SUNNY','PROTO MAN','ROGUE DAWN','LITTLE MAC','DOC LOUIS','MIKE TYSON'):
            continue
        a,old=H.Roster.cold(base,row)
        b,new=H.Roster.cold(trial,row)
        assert a==b and (old.vram,old.chr_latches,bytes(old[0x200:0x300]))==(
            new.vram,new.chr_latches,bytes(new[0x200:0x300])),row['name']
        names.append(row['name'])
    assert len(names)==6
    return dict(Proto_pose_pairs=proto,Sunny_pose_pairs=sunny,matched_menu_entries=100,real_neighbor_openings=names)


def scene(m,program,decoder,*,vectors=False):
    cpu=C.ColdVector.entry(m)
    address=program['symbols']['JaySceneOrRetire']
    m[0x16c],m[0x16d]=address&255,address>>8
    report=Counter()
    seen=set()
    reader=None
    resident={i['pc'] for i in program['instructions']if i['segment']=='COLD65'}
    decode={i['pc'] for i in decoder['instructions']}
    for _ in range(2_000_000):
        if (cpu.pc,cpu.sp)==(C.STOP,224):break
        bank=m.rawtags[1]
        if bank==251 and cpu.pc==0xaf40:
            ptr=m[6]+256*m[7]
            assert 0x101+cpu.sp<=ptr and ptr+7<=0x200
            reader=ptr,bytes(m[ptr:ptr+7])
            assert reader[1]==bytes.fromhex('0200014b014c01')
        own=bank==193 and cpu.pc in resident
        copy=bank==251 and (0xaf40<=cpu.pc<0xafd2 or 0xb9d6<=cpu.pc<0xb9fe)
        unpack=m.rawtags[2]==2 and cpu.pc in decode
        if unpack:
            assert not m.ram[2][0x1fe0] and not m.ram[3][0x1fe0] and cpu.p&4
        key=bank,cpu.pc,cpu.sp,cpu.p&4
        if vectors and (own or copy or unpack) and key not in seen:
            seen.add(key)
            for kind in ('FF',) if cpu.p&4 else ('FF','IRQ'):
                q,d=C.Vector.clone(m,cpu)
                C.ColdVector.interrupt(d,kind)
                report[kind]+=1
        C.ColdVector.step(cpu)
    else:raise AssertionError(('resident scene bound',hex(cpu.pc)))
    assert (cpu.a,cpu.x,cpu.y,cpu.p&0xef)==(83,71,109,0x21)
    return reader,dict(report)


def cold_checks(trial,program,runtime,stage,cookie,decoder):
    m=C.Common.blank(trial)
    C.Common.scene(m,16)
    m[0x730b]=32
    original=tuple(map(bytes,m.ram))
    c,_=C.native_cold(m,program)
    assert not c.p&1 and m.ppu_reads==0 and tuple(map(bytes,m.ram))==original
    (pointer,descriptor),vectors=scene(m,program,decoder,vectors=True)
    assert m.ppu_reads==4100 and bytes(m.ram[3][:len(runtime)])==runtime
    assert bytes(m.ram[2][0x1000:0x1800])==stage and C.Common.headers(m)==(cookie,)*2
    q=C.Vector.clone(m)
    q.ram[2][0x33]=1
    assert scene(q,program,decoder)[0] is None and q.ppu_reads==4100 and not q.ram[2][0x33]
    for bank in (2,3):
        for index in range(16):
            q=C.Vector.clone(m)
            q.ram[bank][0x1fe0+index]^=1
            assert scene(q,program,decoder)[0][1]==descriptor
            assert q.ppu_reads==8200 and C.Common.headers(q)==(cookie,)*2
    for fault in ((2,0x1000),(3,0),(3,len(runtime)-1)):
        q=C.Vector.clone(m)
        q.ram[2][0x1fe0]=0
        q.corrupt_at=fault
        scene(q,program,decoder)
        assert not any(head[0] for head in C.Common.headers(q)),fault
    owners=[]
    for owner in range(37,44):
        q=C.Common.blank(trial)
        C.Common.scene(q,owner)
        assert C.native_cold(q,program)[0].p&1
        old=C.Common.headers(q)
        C.Common.scene(q,16)
        q[0x730b]=32
        assert scene(q,program,decoder)[0][1]==descriptor and C.Common.headers(q)==(cookie,)*2
        C.Common.scene(q,owner)
        assert C.native_cold(q,program)[0].p&1 and C.Common.headers(q)==old
        owners.append(owner)
    return dict(stack_descriptor=descriptor.hex(),example_stack_pointer=hex(pointer),cold_PPU_reads=4100,
        warm_PPU_reads=0,invalid_header_reload_cases=32,copy_or_decode_fault_cases=3,
        unframed_public_cold_reject=True,old_owner_roundtrips=owners,vectors=vectors)


def pinned_parent():
    current=H.ROM.read_bytes()
    if C.digest(current)==PIN:
        return current
    from deliver_dkjr_second_pipe_1110 import Recipe
    parent=Recipe.proposal(Recipe.V1.BASE.read_bytes())[0]
    assert C.digest(parent)==PIN
    return parent


def main():
    donor=C.actual_donor()
    base,trial,program,linked,runtime,stage,cookie,gate,extra,decoder,layout=proposal(pinned_parent(),donor)
    print('Resident cold layout',layout,flush=True)
    cold=cold_checks(trial,program,runtime,stage,cookie,decoder)
    print('Resident native cold checks',cold,flush=True)
    harness={'images':{},'symbols':{'JayHot':0x4a00,'JaySceneOrRetire':0,'PublishPosition':0},'instructions':[]}
    legacy=C.family_parity(base,trial,harness,linked,donor)
    main_result=Hot.opening(trial,harness,linked,runtime,cookie,gate,extra,donor)
    print('Resident Jay Main',main_result,flush=True)
    art=pose_checks(base,trial)
    print(json.dumps(dict(passed=True,ROM_SHA256=PIN,ROM_written=False,Mesen=False,build_files=0,
        image_SHA256=C.digest(trial['raw']),source_SHA256=C.digest(SOURCE.read_bytes()),
        layout=layout,cold=cold,actual_Main=main_result,legacy=legacy,art=art,
        runtime_SHA256=C.digest(runtime),stage_SHA256=C.digest(stage),cookie=cookie.hex()),sort_keys=True),flush=True)


if __name__=='__main__':
    main()
