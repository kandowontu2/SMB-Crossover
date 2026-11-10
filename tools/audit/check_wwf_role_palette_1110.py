"""Source-funded secondary palette repair; reconstruct all six owner cookies."""
from hashlib import sha256
import json
import sys

import stage_wwf_powerups_1110 as Stage
import check_wwf_native_powerups_1110 as P

W,N,L=P.W,P.N,P.L
R=W.R
sys.path.insert(0,str(R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm
SOURCE=R/'tools/reference/wwf_role_palette_1110.s'


def private_images(raw,b):
    def page(i):return raw[1048592+1024*i:1048592+1024*(i+1)]
    a1=b''.join(page(i) for i in range(637,645))
    a3=b''.join(page(i) for i in range(650,658))
    c2=bytearray(8192)
    for i,p in zip([2,4,5,6,7],range(645,650)):
        c2[1024*i:1024*(i+1)]=page(p)
    at=W.location(b,'WfMetadataOffsets')
    offsets=[int.from_bytes(raw[at+2*i:at+2*i+2],'little') for i in range(6)]
    metadata=b''.join(page(i) for i in range(658,666))
    bodies=b''.join(page(i) for i in [*range(546,604),*range(442,460),*range(629,637)])
    return a1,c2,a3,offsets,metadata,bodies


def cookies(raw,b,c2=None):
    a1,original,a3,offsets,metadata,bodies=private_images(raw,b)
    if c2 is None:c2=original
    result=[]
    for role,o in enumerate(offsets):
        selected=bytearray(c2)
        selected[0xa42:0xa42+1687]=metadata[o:o+1687]
        assert len(selected)==8192
        result.append(bytes([167,29,role,2])+sha256(a1+selected+a3+bodies).digest()[:12])
    return b''.join(result)


def proposal(raw):
    assert sha256(raw).hexdigest()==Stage.PIN
    b=W.Symbols.bundle()
    at=W.location(b,'WfNativeP1Mask')
    mask=raw[at:at+145]
    assert W.address(b,'WfNativeP1Mask')==0xbc28
    assert W.address(b,'WfAudioProbe')==0xbcb9
    assert b['syms']['WfNativeP1Mask']['ref'].count('+')==0
    values=[0,2,3,15]
    packed=bytes(sum(values.index(mask[i+j])<<(2*j) for j in range(min(4,len(mask)-i)))
                 for i in range(0,len(mask),4))
    assert len(packed)==37
    assert bytes(values[(packed[i//4]>>(2*(i%4)))&3] for i in range(145))==mask
    role_at=W.location(b,'WfRolePackets')
    packets=[raw[role_at+13*i:role_at+13*(i+1)] for i in range(6)]
    assert all(p[:3]==bytes.fromhex('3f1103') and p[6:9]==bytes.fromhex('3f1503')
               and p[11:]==bytes((15,0)) for p in packets)
    first=[p[9] for p in packets];second=[p[10] for p in packets]
    source=SOURCE.read_text().replace('NATIVE_PACKED',','.join(str(i) for i in packed))
    source=source.replace('ROLE_FIRST',','.join(str(i) for i in first))
    source=source.replace('ROLE_SECOND',','.join(str(i) for i in second))
    defs={n:W.address(b,n) for n in ['WfP1Temp','WfP1Packet','WfOwnerCookie','VRAM_Buffer1','CancelNext']}
    oldc2=private_images(raw,b)[1]
    needle=bytes.fromhex('a8b928bc')
    assert oldc2.count(needle)==1
    early=oldc2.index(needle)
    cancel=W.location(b,'CancelNext')
    # Bind the actual command matcher, not a coincidental data occurrence.
    scan=raw[W.location(b,'CancelScan'):W.location(b,'CancelDone')]
    # Derive exact native operands/branch destinations instead of fixed offsets.
    start=scan.index(bytes((0xbd, (defs['VRAM_Buffer1']+3)&255,(defs['VRAM_Buffer1']+3)>>8,0xc9,0x16)))
    cancel_at=W.location(b,'CancelScan')+start
    before=raw[cancel_at:cancel_at+14]
    assert before[0]==before[7]==0xbd and before[3:5]==bytes.fromhex('c916') and before[10:12]==bytes.fromhex('c905')
    assert before[5]==before[12]==0xd0
    assert cancel_at+7+int.from_bytes(before[6:7],'little',signed=True)==cancel
    assert cancel_at+14+int.from_bytes(before[13:14],'little',signed=True)==cancel
    code=Asm.assemble('\n'.join(f'{n}=${v:04x}' for n,v in defs.items())+'\n'+source,
        {'MASK':(0xbc28,145),'EARLY':(0xc000+early,4),'OWN':(0xbbf6,16),
         'CANCEL':(0xa000+(cancel_at-16)%8192,14)})
    assert code['used']['MASK']<=145,code['used']
    own=W.location(b,'OwnColors')
    assert raw[own:own+16]==bytes.fromhex('a9168dbbdea9058dbcdea90f8dbdde60')
    cookie_at=W.location(b,'WfCookieC')
    old_cookies=raw[cookie_at:cookie_at+96]
    assert cookies(raw,b)==old_cookies
    image=bytearray(raw)
    patches=[]
    for name,target,size in [('MASK',at,145),('OWN',own,16),('CANCEL',cancel_at,14)]:
        new=code['images'][name].ljust(size,b'\xea')
        patches.append(dict(role=name,offset=target,old=raw[target:target+size].hex(),new=new.hex()))
        image[target:target+size]=new
    c2=bytearray(oldc2);c2[early:early+4]=code['images']['EARLY']
    page_index=early//1024
    physical=dict(zip([2,4,5,6,7],range(645,650)))[page_index]
    target=1048592+physical*1024+early%1024
    assert raw[target:target+4]==needle
    image[target:target+4]=code['images']['EARLY']
    patches.append(dict(role='EARLY',offset=target,old=needle.hex(),new=code['images']['EARLY'].hex()))
    new_cookies=cookies(raw,b,c2)
    image[cookie_at:cookie_at+96]=new_cookies
    patches.append(dict(role='full image + selected metadata + audio + all art cookies',
        offset=cookie_at,old=old_cookies.hex(),new=new_cookies.hex()))
    assert cookies(image,b)==new_cookies
    return bytes(image),dict(parent_SHA256=Stage.PIN,ROM_SHA256=sha256(image).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),used=code['used'],symbols=code['symbols'],
        patches=patches,packed_mask_bytes=len(packed),original_mask_bytes=145,
        palettes=[p[9:12].hex() for p in packets],new_RAM_bytes=0,new_allocations=0)


def main():
    raw,_=Stage.reconstruct()
    image,record=proposal(raw)
    print(json.dumps(dict(passed=True,source_construction_only=True,native_Mesen=False,
        ROM_written=False,output_files=0,record=record),sort_keys=True),flush=True)


if __name__=='__main__':main()
