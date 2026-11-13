"""Qualify CHR739 retirement through an exact blank alias, in memory only."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile

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
    image,layout=proposal(raw)
    assert reverse(image)==raw
    # Arbitrary new carrier contents cannot leak through the retired blank
    # window. No file/ROM is written and no allocation is granted here.
    marked=bytearray(image);at=CHR+739*1024
    marked[at:at+1024]=bytes((i*37+113)&255 for i in range(1024));marked=bytes(marked)
    seeds=[];cold=[]
    for cart in (raw,marked):
        b=Host.W.Symbols.bundle();b['raw']=cart
        opened,m=Host.cold(b,dict(name='EXCITEBIKE',slot=29,cycle=0,raw=37))
        cold.append(opened);seeds.append(m)
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
    return dict(layout=layout,actual_cold_openings=cold,all12_published_windows_byte_identical=True,
        actual_public_draw_OAM_and_AXYP_identical=True,retired_row_poison_bytes=1024,
        IRQ=dict(counts),minimum_SP=minimum,resource_granted=False,ROM_written=False,output_files=0,
        scope='Full-row proposal conditional on root grant and exact current private-writer exclusion. New aliases cold-load and publish through actual native menu/Start/parser/Main. Unchanged current graphics are compared across all12 mapped windows, including arbitrary replacement bytes in retired739.')


if __name__=='__main__':print(json.dumps(qualify(Host.ROM.read_bytes()),separators=(',',':')),flush=True)
