"""Qualify CHR739 retirement through an exact blank alias, in memory only."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile
from unittest.mock import patch

import audit_current_roster_powerups_1110 as Host
import check_metal_head_bridge_1112 as ISR
from compose_metal_head_bridge_1112 import assemble_segments

R=Path(__file__).resolve().parents[2]
CHR=1048592
START=CHR+728*1024
PACKET=R/'docs/qa/checkpoints/2026-11-02/excitebike-source-v1/inputs.zip'
PACKET_SHA='19deba8a9c45e1e23cc38cc5bedd46903fb4e14fa9bf27705a7336d4414c6e2d'
SOURCE=R/'tools/reference/steve_wave_blank_alias_1113.s'
ORIGIN=0xaf8c
M=Host.N


def current_writers(raw):
    import steve_armor_art_1112 as Art
    import audit_mega_giant_chr_candidates_1110_v1 as Census
    import check_sonic_eighth_cold_owner_1110 as FF
    from check_steve_shatterhand_roll_blank_1111 import C as RollCPU
    ledger_bytes=Art.LEDGER.read_bytes()
    assert sha256(ledger_bytes).hexdigest()==Art.LEDGER_PIN
    ledger=json.loads(ledger_bytes);b=Host.W.Symbols.bundle();historic=b['raw'];b['raw']=raw
    assert [n for n,v in ledger['exact_finite_domains'].items()if 739 in v]==['Excitebike body']
    rows=ledger['current_table_bindings']
    exact=[row['name'] for row in rows if sha256(raw[row['offset']:row['offset']+row['bytes']]).hexdigest()==row['SHA256']]
    changed={row['name'] for row in rows}-set(exact)
    assert len(rows)==54 and len(exact)==44
    assert changed=={'ProtoPoseChrLo','ProtoPoseChrHi','SunnyChrLow','Z2PoseChrLo',
        'RlPoolChrLo','RlPoolChrHi','M3Form2ChrLo','M3Form3ChrLo','M3Form4ChrLo','M3Form6ChrLo'}
    rebound={}
    store=b'\x8d'+M.address(b,'SmChrBank').to_bytes(2,'little')
    for name,setter,size,span,upper in (('ProtoPoseChrLo','ProtoSetPose',27,53,256),('SunnyChrLow','SunnySetPose',35,150,512)):
        at=Host.W.location(b,setter);code=raw[at:at+span]
        sites=[i for i in range(len(code)-5)if code[i]==0xbd and code[i+3:i+6]==store]
        i,=sites;pointer=int.from_bytes(code[i+1:i+3],'little')
        assert 0xce00<=pointer and pointer+size<=0xd27f
        table_at=16+94*8192+(pointer&8191);data=raw[table_at:table_at+size]
        old=Host.W.location(b,name);assert data==historic[old:old+size]
        pages=sorted({upper+v for v in data});assert 739 not in pages
        publish='ProtoPublishBody' if name=='ProtoPoseChrLo' else 'SunnyDraw'
        model=RollCPU.Common.blank(b);setter_pc=M.address(b,'X5SetPhysicalChr')
        published=[]
        for value in data:
            M.put(model,SmChrBank=value);requests=[]
            def observe(m,c):
                if c.pc==setter_pc and m.rawtags[1]==0xbe:requests.append(c.a+256*c.x)
            RollCPU.Vector.call(model,publish,p=0x31,observe=observe)
            assert requests==[upper+value],(publish,value,requests)
            published+=requests
        rebound[name]=dict(current_reader=setter,reader_PC=M.address(b,setter)+i,
            physical_table_PRG=94,table_PC=pointer,pages=pages,actual_publisher=publish,
            actual_native_publications=len(published))
    high=M.address(b,'ProtoPoseChrHi')
    assert bytes((0xbd,high&255,high>>8))not in raw[16+66*8192:16+67*8192]
    rebound['ProtoPoseChrHi']=dict(retired_as_high_table=True,current_upper=1,pages=rebound['ProtoPoseChrLo']['pages'])
    lo=Host.W.location(b,'Z2PoseChrLo');hi=Host.W.location(b,'Z2PoseChrHi')
    assert lo==574138 and raw[hi:hi+27]==bytes([1])*27
    expected=bytes(52+i if i<13 else 63+((i+1)&1) for i in range(27))
    assert raw[lo:lo+27]==expected
    signature=bytes.fromhex('e01b9002a203a9c68da17da9c68d1651bdaac28d086b')
    assert raw[16+69*8192+0x4cf:16+69*8192+0x4cf+len(signature)]==signature
    assert raw[:CHR].count(bytes.fromhex('bdaac2'))==1
    rebound['Z2PoseChrLo']=dict(current_reader_PC=0xa4cf,physical_reader_PRG=69,
        table_PC=0xc2aa,pages=sorted({256+v for v in expected}),bounded_poses=27)
    constraint=json.loads((R/'build/prince-actor-1101-v1/smb3-pages.json').read_text())['current_source_constraint']
    for key in ('exact_live_caller_bytes','exact_live_helper_bytes'):
        assert raw.count(bytes.fromhex(constraint[key]))==1
    lows=Host.W.location(b,'M3ChrLoTableLo');highs=Host.W.location(b,'M3ChrLoTableHi')
    assert [raw[lows+i]+256*raw[highs+i]for i in range(7)]==[M.address(b,'M3Form0ChrLo')]*7
    at=Host.W.location(b,'M3Form0ChrLo');base=raw[at:at+81]
    at=Host.W.location(b,'MbChrOffsets');offsets=raw[at:at+7]
    assert set(base)=={24,25,26,27}and list(offsets)==constraint['form_offsets']
    pages=sorted({512+((v+off)&255)for v in base for off in offsets})
    assert pages==list(range(524,544))
    for n in ('M3Form2ChrLo','M3Form3ChrLo','M3Form4ChrLo','M3Form6ChrLo'):
        rebound[n]=dict(retired_array=True,current_reader='M3Form0ChrLo + MbChrOffsets[clamped0..6]',pages=pages)
    # The former Roll high table is now low-byte data for window7; actual
    # compiled publishers supply constant upper1 or canonical blank21.
    low=Host.W.location(b,'RlPoolChrLo');high=Host.W.location(b,'RlPoolChrHi')
    assert raw[low:low+6]==bytes((108,112,116,120,48,48))
    assert raw[high:high+6]==bytes((111,111,111,111,48,48))
    model=RollCPU.Common.blank(b);setter=M.address(b,'X5SetPhysicalChr');requests=[]
    for pool in range(6):
        M.put(model,RlPool=pool);current=[]
        def observe(m,c):
            if c.pc==setter and m.rawtags[1]==0xbe:current.append((c.y,c.a+256*c.x))
        RollCPU.Vector.call(model,'RlPublish',p=0x31,observe=observe)
        body=(364,368,372,376,21,21)[pool]
        assert current==[(0,body),(6,body+2 if pool<4 else 21),(7,367 if pool<4 else 21)],(pool,current)
        requests+=current
    roll_pages=sorted({p for _,p in requests});assert 739 not in roll_pages
    for n in ('RlPoolChrLo','RlPoolChrHi'):
        rebound[n]=dict(current_reader='RlPublish B03D / six finite pools; constant upper1 / blank21',
            physical_reader_PRG=79,pages=roll_pages,actual_native_publications=len(requests))
    assert set(rebound)==changed
    old_ff=FF.C.ROM.read_bytes();assert sha256(old_ff).hexdigest()==FF.C.PIN
    ff=FF.FF.proposal(old_ff)[0]
    assert raw[CHR+893*1024:CHR+901*1024]==ff[CHR+893*1024:CHR+901*1024]
    assert raw[16+93*8192:16+94*8192]==ff[16+93*8192:16+94*8192]
    assert FF.FF.Funding.gateways(raw,b)==FF.FF.Funding.gateways(ff,b)
    # Our ten-table rebinding above replaces that function's historical
    # table census. Preserve its complete actual37-root FF writer closure.
    with patch.object(FF.Alias.Authority,'chr_authority',lambda _:dict(private_writer_chunks_exact=15)):
        ff_scope=FF.current_authority(old_ff,ff)
    assert ff_scope['current_private_writer_scopes_rebound']==15
    ff_scope['current_FF8k_and_record_bank_source_reproduced']=ff_scope.pop('current_complete_ROM_source_reproduced')
    for row in ff_scope['changed_coarse_pages_rebound']:row.pop('changed_offsets')
    private_exact=0
    for row in ledger['inherited_private_writer_chunks_exact']:
        if row['pages'] in ([898],[900]):continue
        assert any(sha256(raw[CHR+p*1024:CHR+(p+1)*1024]).hexdigest()==row['SHA256'] for p in row['pages'])
        private_exact+=1
    assert private_exact==13
    native_at,native=Census.table(b,'ChrPhysicalMap',256)
    assert 739 not in list(native) and all(raw[Census.prg_at(bank,0xe36):Census.prg_at(bank,0xe36)+256]==native for bank in Census.MAP_BANKS)
    special=Census.compiled_readers(b)
    assert all(739 not in row['actual_mmc5_outputs']for row in special.values())
    assert all(739 not in row['pages']for row in ledger['inherited_private_writer_chunks_exact'])
    claims=[]
    def allocations(value,file):
        if isinstance(value,dict):
            for key,item in value.items():
                if any(part in key.lower()for part in ('pages','physical_chr','chr_page')):
                    if item==739 or isinstance(item,list) and 739 in item:claims.append((file.name,key))
                allocations(item,file)
        elif isinstance(value,list):
            for item in value:allocations(item,file)
    for file in (R/'docs/qa/allocations').glob('*.json'):allocations(json.loads(file.read_text()),file)
    assert all(file.startswith('steve-')for file,_ in claims),claims
    return dict(prior_finite_domains=88,whole_tables_exact=len(exact),changed_tables_rebound=rebound,
        private_scopes_rebound=ff_scope,legacy_map_mirrors=4,special_readers_exclude739=True,
        current_allocation_claims739=claims,no_other_finite_or_private_owner_claims739=True)


def proof(raw):
    assert sha256(PACKET.read_bytes()).hexdigest()==PACKET_SHA
    with zipfile.ZipFile(PACKET)as z:
        body=z.read('build/excitebike-pose-1101-v3/body-native.chr')
        meta=json.loads(z.read('build/excitebike-pose-1101-v3/body-native.json'))
        ownership=json.loads(z.read('build/excitebike-pose-1101-v3/consumer-closure.json'))
    assert len(body)==3072 and raw[CHR+736*1024:CHR+739*1024]==body
    assert len(meta['poses'])==23
    highest=max(cell['tile']for pose in meta['poses']for cell in pose['cells'])
    assert highest==90 and ownership['unused_page']==739
    assert ownership['reclaimed_pages']==list(range(728,739))
    assert raw[CHR+739*1024:CHR+740*1024]==raw[CHR+21*1024:CHR+22*1024]==bytes(1024)
    cfg=(R/'build/excitebike-pose-1101-v3/host.cfg').read_text()
    assert 'EX_HOST:load=K,type=ro,start=$a950;'in cfg and 'CODE:load=K,type=ro,start=$b000;'in cfg
    labels=(R/'build/excitebike-pose-1101-v3/heat-host.lbl').read_text()
    assert 'al 00AF7A .ExHostEnd'in labels and 'al 00B000 .ExPose'in labels
    assert raw[START+0xf7a:START+0xf8c]==bytes.fromhex('8d6a01a9998d6c01a9b28d6d01a98a4c5a01')
    assert raw[START+0xf8c:START+0x1000]==bytes(116)
    return dict(original_poses=23,maximum_pair=highest,exact_body_bytes=3072,
        declared_unused_page=739,source_owned_gap=[ORIGIN,0xb000],available_bytes=116,
        current_page_SHA256=sha256(bytes(1024)).hexdigest())


def proposal(raw):
    evidence=proof(raw)
    parts,_=assemble_segments(SOURCE.read_text(),{'BLANK_ALIAS':ORIGIN},
        dict(ExBodyLow=0xad62,CurrentCHRBank4=0x14b,X5ChrMode4=0x73e4,ExGraphicsAfterLoop=0xad28))
    program=parts['BLANK_ALIAS'];assert len(program)==24
    assert raw[START+0xd18:START+0xd2a]==bytes.fromhex('a203bd62ad9d4b01a9829de473ca10f2a900')
    assert raw[START+0xd62:START+0xd66]==bytes.fromhex('e0e1e2e3')
    old_cookie=bytes((167,37,2))+sha256(raw[START:START+11264]).digest()[:13]
    assert raw.count(old_cookie)==1
    cookie_at=raw.index(old_cookie);assert 16+65*8192<=cookie_at<16+66*8192
    changed=bytearray(raw)
    changed[START+0xd18:START+0xd1d]=bytes.fromhex('4c8cafeaea')
    changed[START+0xd65]=21
    changed[START+0xf8c:START+0xf8c+len(program)]=program
    cookie=bytes((167,37,3))+sha256(changed[START:START+11264]).digest()[:13]
    changed[cookie_at:cookie_at+16]=cookie
    edits=[dict(offset=at,before=raw[at:at+size].hex(),after=changed[at:at+size].hex())
        for at,size in ((START+0xd18,5),(START+0xd65,1),(START+0xf8c,len(program)),(cookie_at,16))]
    return bytes(changed),dict(**evidence,old_cookie=old_cookie.hex(),cookie=cookie.hex(),
        cookie_at=cookie_at,program=program.hex(),program_bytes=len(program),
        edits=edits,
        parent_SHA256=sha256(raw).hexdigest(),blank_alias_SHA256=sha256(changed).hexdigest())


def reverse(image):
    """Undo the Ex alias after the caller restores retired739 to its old zeros."""
    restored=bytearray(image)
    assert image[START+0xd18:START+0xd1d]==bytes.fromhex('4c8cafeaea')
    assert image[START+0xd65]==21
    restored[START+0xd18:START+0xd1d]=bytes.fromhex('a203bd62ad')
    restored[START+0xd65]=0xe3
    restored[START+0xf8c:START+0xf8c+24]=bytes(24)
    old_cookie=bytes((167,37,2))+sha256(restored[START:START+11264]).digest()[:13]
    cookie=bytes((167,37,3))+sha256(image[START:START+11264]).digest()[:13]
    assert image.count(cookie)==1
    at=image.index(cookie);restored[at:at+16]=old_cookie
    restored=bytes(restored)
    assert proposal(restored)[0]==image
    return restored


def qualify(raw):
    writers=current_writers(raw)
    image,layout=proposal(raw)
    assert reverse(image)==raw
    # Arbitrary new carrier contents cannot leak through the retired blank
    # window. No file/ROM is written and no allocation is granted here.
    marked=bytearray(image);at=CHR+739*1024
    marked[at:at+1024]=bytes((i*37+113)&255 for i in range(1024));marked=bytes(marked)
    seeds=[];cold=[];cold_points=set();cold_cuts=Counter();cold_minimum=255
    cold_native=M.NesMPU
    class ColdProbe(cold_native):
        def step(self):
            nonlocal cold_minimum
            mem=self.memory;opcode=mem[self.pc]
            if mem.rawtags[2]==3 and opcode in (0x91,0xb1,0xd1) and M.get(mem,'NmiDisable')==255:
                pointer=mem[self.pc+1]
                target=(mem[pointer]+256*mem[(pointer+1)&255]+self.y)&65535
                if target in (ORIGIN+0x2000,ORIGIN+23+0x2000):
                    key=(self.pc,self.sp,self.p&4,target)
                    if key not in cold_points:
                        cold_points.add(key)
                        for kind in ('IRQ','lagNMI'):
                            if kind=='IRQ'and self.p&4:cold_cuts['masked_IRQ_points']+=1;continue
                            model=M.fork(mem);cpu=cold_native(memory=model,pc=self.pc)
                            for f in ('a','x','y','p','sp'):setattr(cpu,f,getattr(self,f))
                            cold_minimum=min(cold_minimum,ISR.inject(cpu,cold_native,kind));cold_cuts[kind]+=1
            return cold_native.step(self)
    for cart in (raw,marked):
        b=Host.W.Symbols.bundle();b['raw']=cart
        if cart is marked:M.NesMPU=ColdProbe
        try:opened,m=Host.cold(b,dict(name='EXCITEBIKE',slot=29,cycle=0,raw=37))
        finally:M.NesMPU=cold_native
        cold.append(opened);seeds.append(m)
    assert cold_cuts['lagNMI'] and cold_minimum>=128
    for m in seeds:
        M.put(m,CurrentOAMOffset=4,GuestOamRotationActive=0,RgOamRotation=0)
        M.invoke(m,'HuGraphics',a=85,x=7,y=91,p=0x21)
        M.invoke(m,'X5PublishChr')
    a,b=seeds
    assert a.chr_latches[4:8]==[736,737,738,739] and b.chr_latches[4:8]==[736,737,738,21]
    for old,new in zip(a.chr_latches,b.chr_latches):
        assert raw[CHR+old*1024:CHR+(old+1)*1024]==marked[CHR+new*1024:CHR+(new+1)*1024]
    returns=[]
    for m in seeds:returns.append(M.invoke(m,'HuDraw',a=85,x=7,y=91,p=0x21))
    assert [tuple(row[k]for k in ('A','X','Y','P'))for row in returns][0]==tuple(returns[1][k]for k in ('A','X','Y','P'))
    assert bytes(a[0x200:0x300])==bytes(b[0x200:0x300])
    native=M.NesMPU;points=set();counts=Counter();minimum=255
    class Probe(native):
        def step(self):
            nonlocal minimum
            if self.memory.rawtags[1]==3 and ORIGIN<=self.pc<ORIGIN+20:
                key=(self.pc,self.sp,self.p&4)
                if key not in points:
                    points.add(key)
                    for kind in ('IRQ','lagNMI'):
                        if kind=='IRQ'and self.p&4:continue
                        m=M.fork(self.memory);cpu=native(memory=m,pc=self.pc)
                        for f in ('a','x','y','p','sp'):setattr(cpu,f,getattr(self,f))
                        minimum=min(minimum,ISR.inject(cpu,native,kind));counts[kind]+=1
            return native.step(self)
    M.NesMPU=Probe
    try:
        m=M.fork(b);M.put(m,NmiDisable=255)
        M.invoke(m,'HuGraphics',a=85,x=7,y=91,p=0x21)
    finally:M.NesMPU=native
    assert counts['IRQ'] and counts['lagNMI'] and minimum>=128
    return dict(layout=layout,current_writer_scope=writers,actual_cold_openings=cold,all12_published_windows_byte_identical=True,
        actual_public_draw_OAM_and_AXYP_identical=True,retired_row_poison_bytes=1024,
        IRQ=dict(counts),minimum_SP=minimum,cold_copy_verify_cuts=dict(cold_cuts),cold_minimum_SP=cold_minimum,
        resource_granted=False,ROM_written=False,output_files=0,
        scope='Full-row proposal conditional on root grant and exact current private-writer exclusion. New aliases cold-load and publish through actual native menu/Start/parser/Main. Unchanged current graphics are compared across all12 mapped windows, including arbitrary replacement bytes in retired739.')


if __name__=='__main__':print(json.dumps(qualify(Host.ROM.read_bytes()),separators=(',',':')),flush=True)
