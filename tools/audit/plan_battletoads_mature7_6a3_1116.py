"""Detached seven-byte maturity stub; no ROM composition, mount or grant."""
from pathlib import Path
from itertools import product
import argparse,json
import plan_battletoads_food_gate_6a3_1116 as Rejected

Current,R,ROM,PIN,W,N=Rejected.Current,Rejected.R,Rejected.ROM,Rejected.PIN,Rejected.W,Rejected.N
ENTRY,STUB,ACTIVE=0xa045,0xb548,0xae3e
REJECTED_SHA='ad2cf7660ac7aefb341f1097732874f83c9dfda7c246fa1396cbf3df1fe1b64a'
CODE=bytes.fromhex('b51f10fa4c3eae')
CFG_SOURCE=R/'tools/audit/prepare_battletoads_current64_host_v1.py'
API_SOURCE=R/'tools/audit/battletoads_native_adapter_v7.s'

def proposal(raw):
    assert Current.digest(Path(Rejected.__file__).read_bytes())==REJECTED_SHA
    Current.preservation(raw);b=Current.bundle(raw);old=raw[Current.CACHE:Current.CACHE+8192]
    assert W.address(b,'BtUnavailable')==STUB-2 and W.address(b,'BtActive')==ACTIVE
    assert old[STUB-0xa000-2:STUB-0xa000]==b'\x18\x60'
    assert old[STUB-0xa000:STUB-0xa000+7]==b'\xff'*7
    assert old[0x45:0x48]==bytes.fromhex('4c46b5') and W.address(b,'Enemy_State')==0x1f
    new=old[:0x45]+b'\x4c'+STUB.to_bytes(2,'little')+old[0x48:STUB-0xa000]+CODE+old[STUB-0xa000+7:]
    assert len(new)==8192 and sum(a!=b for a,b in zip(old,new,strict=True))==8
    cookie=raw[Current.COOKIE:Current.COOKIE+16];assert cookie[4:]==bytes.fromhex(Current.digest(old))[:12]
    after=cookie[:4]+bytes.fromhex(Current.digest(new))[:12]
    header=raw[Current.HEADER:Current.HEADER+487];delta=Current.COOKIE-Current.HEADER
    new_header=header[:delta]+after+header[delta+16:]
    spans=[(Current.CACHE+0x45,old[0x45:0x48],new[0x45:0x48]),(Current.CACHE+STUB-0xa000,b'\xff'*7,CODE),(Current.COOKIE,cookie,after)]
    rows=[dict(file=[at,at+len(left)],old=left.hex(),new=right.hex(),old_SHA256=Current.digest(left),new_SHA256=Current.digest(right))for at,left,right in spans]
    return old,new,dict(owning_parent_SHA256=PIN,detached_only=True,ROM_composed=False,mounted=False,outputs=0,
        source_lease_pending=True,owned_bytes=26,changed_bytes=8+sum(a!=b for a,b in zip(cookie,after,strict=True)),spans=rows,
        old_packet_SHA256=Current.digest(old),proposed_packet_SHA256=Current.digest(new),
        old_header487_SHA256=Current.digest(header),proposed_header487_SHA256=Current.digest(new_header),
        rejected_Active_only_plan_SHA256=REJECTED_SHA,
        reason='Reject all rising states before Active; growing M/F cannot enter native physical collision fallback',
        no_new_RAM_capacity_art_physics_helper=True)

def layout(raw):
    Current.preservation(raw);b=Current.bundle(raw);old=raw[Current.CACHE:Current.CACHE+8192];segments=[]
    q=dict(owning_parent_SHA256=PIN,detached_layout_only=True,proposal_rejected=True,
        reason='Actual B548 preimage is occupied; no FF-capacity assumption',
        observed_B548_96bytes=old[0x1548:0x15a8].hex(),ROM_composed=False,mounted=False,outputs=0)
    for k,v in b['segs'].items():
        if v.get('name','').strip('"')in('BT_CACHE_API','BT_CORE','BT_ART_META','BT_CACHE_HOST','BT_CACHE_STATE','BT_CACHE_HOST_STATE','BT_CACHE_INVALID_COOKIE'):
            segments.append(dict(v))
    q['typed_segments']=segments
    q['source_files']={str(p.relative_to(R)):Current.digest(p.read_bytes())for p in(CFG_SOURCE,API_SOURCE)}
    q['existing_gap_preimage_SHA256']=Current.digest(old[0x1548:0x1ee0])
    q['gap_bytes']=0x1ee0-0x1548
    q['stub_physical_file']=Current.CACHE+0x1548
    q['nearby_symbols']={n:dict(v)for n,v in b['syms'].items()if n.startswith('Bt')and 0xb500<=int(v.get('val','0'),0)<0xc000}
    q['hole_word_aliases']={hex(at):[i for i in range(8191)if old[i:i+2]==at.to_bytes(2,'little')]for at in range(STUB,STUB+7)}
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inspect',action='store_true');a=p.parse_args()
    q=layout(ROM.read_bytes());q['receipt_SHA256']=Current.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
