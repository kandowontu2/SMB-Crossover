"""Pack exact Mega Giant pose art for the current native metasprite renderer."""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path

from check_mega_giant_geometry_1110_v1 import M, ROM, HOST_PIN, DONOR, DONOR_PIN
from check_mega_giant_geometry_1110_v1 import bundle, sha


DESCRIPTOR=0x5b80


def donor_oam(donor,x,y,left,odd,attr):
    donor[0x3ad]=x
    donor[0xce]=y
    donor[0xb5]=1
    donor[0x33]=2 if left else 1
    donor[0x56]=attr
    donor[0x09]=odd
    cpu=M.NesMPU(memory=donor,pc=0xef2f)
    cpu.a,cpu.p,cpu.sp=8,0x21,230
    cpu.stPushWord(0x5aff)
    for _ in range(2400):
        if cpu.pc==0x5b00:
            break
        assert donor[cpu.pc],hex(cpu.pc)
        cpu.step()
    else:
        raise AssertionError('Donor body draw did not return')
    assert cpu.sp==230
    start=odd*128
    return [bytes(donor[0x200+(start+i)%256:0x204+(start+i)%256]) for i in range(0,256,4)]


def draw(m,packets,x,y,attr,offset,rotation):
    M.put(m,CurrentOAMOffset=offset,GuestOamRotationActive=int(bool(rotation)),RgOamRotation=rotation)
    m[0x200:0x300]=bytes([0xf8])*256
    end=offset
    for packet in packets:
        m[DESCRIPTOR:DESCRIPTOR+len(packet)]=packet
        M.put(m,R0=DESCRIPTOR&255,R1=DESCRIPTOR>>8,R3=attr,R4=x,R5=0,R6=y,R7=1)
        result=M.invoke(m,'MetaspriteRenderLoop')
        assert result['P']&1
        end+=packet[0]
        assert M.get(m,'CurrentOAMOffset')==end
    start=(offset+rotation)&255
    return [bytes(m[0x200+(start+i)%256:0x204+(start+i)%256]) for i in range(0,end-offset,4)]


def prepare(raw,source):
    donor=bytearray(65536)
    donor[0x8000:]=source[16:32784]
    art=source[32784:]
    banks=tuple(zip(donor[0xee07:0xee14],donor[0xee14:0xee21],strict=True))
    pages=sorted({p for pair in banks for p in pair})
    assert pages==list(range(8,30))
    retained=bytes(art[p*1024+i] for p in pages for i in range(1024))
    base=M.fresh(bundle(raw))
    data=bytearray()
    descriptors=[]
    cases=0

    for pose,(top,bottom) in enumerate(banks):
        for left in (False,True):
            original=donor_oam(donor,128,176,left,0,0)
            assert original==donor_oam(donor,128,176,left,1,0)
            selected=[]
            record=[]
            for index,(py,tile,attr,px) in enumerate(original):
                second=index>=32
                page=(top,bottom)[second]
                start=(tile>>1)*32
                part=art[page*1024+start:page*1024+start+32]
                if not any(part):
                    continue
                relocated=tile|(0x40 if second else 0)
                mapped=pages.index(page)*1024+((relocated&0x3f)>>1)*32
                assert retained[mapped:mapped+32]==part
                selected.append(index)
                record.append(bytes((relocated,attr,(py-176)&255,(px-128)&255)))
            packets=[]
            offsets=[]
            # The compiled native entry uses BPL to enter its first sprite.
            # One packet with a negative length would silently skip it.
            for group in (record[:31],record[31:]):
                packet=bytes((4*len(group),))+b''.join(reversed(group))
                assert 0<packet[0]<128
                offsets.append(len(data))
                packets.append(packet)
                data+=packet
            descriptors.append(dict(pose=pose,left=left,packet_offsets=offsets,parts=len(record),
                                    relative_CHR_windows=[pages.index(top),pages.index(bottom)]))
            for x,y,attr,offset,rotation in product((40,128,200),(144,176),(0,3,0x20),(0,4),(0,128)):
                actual=donor_oam(donor,x,y,left,0,attr)
                expected=[bytes((actual[i][0],actual[i][1]|(0x40 if i>=32 else 0),actual[i][2],actual[i][3]))
                          for i in selected]
                got=draw(M.fork(base),packets,x,y,attr,offset,rotation)
                assert got==expected,(pose,left,x,y,attr,offset,rotation,
                                      [(i,a.hex(),b.hex()) for i,(a,b) in enumerate(zip(got,expected,strict=True)) if a!=b][:8])
                cases+=1
    return bytes(data),retained,descriptors,cases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    assert sha(ROM)==HOST_PIN and sha(DONOR)==DONOR_PIN
    poses,chr_data,descriptors,cases=prepare(ROM.read_bytes(),DONOR.read_bytes())
    (out/'giant-render-packets.bin').write_bytes(poses)
    (out/'giant-render-source-pages.chr').write_bytes(chr_data)
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,host_SHA256=HOST_PIN,donor_SHA256=DONOR_PIN,
           source_pose_count=13,cases=cases,descriptor_bytes=len(poses),physical_CHR_bytes=len(chr_data),
           parts_range=[min(q['parts'] for q in descriptors),max(q['parts'] for q in descriptors)],
           descriptors=descriptors,bindings={str(path):sha(path) for path in
               (Path(__file__),ROM,DONOR,out/'giant-render-packets.bin',out/'giant-render-source-pages.chr')},
           scope='Exact original interior body OAM and all nonempty source tile pairs, executed by current MetaspriteRenderLoop with two ≤31-part packets. Empty pairs elided. Two simultaneous native CHR windows replace the original mid-screen register swap. No ownership lease, budget scheduler, palette admission, or native playability.')
    (out/'render-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ('descriptors','bindings')}))


if __name__=='__main__':
    main()
