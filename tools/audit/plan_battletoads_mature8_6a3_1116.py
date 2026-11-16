"""Detached maturity admission in authenticated post-camera cache capacity."""
from pathlib import Path
from functools import lru_cache
import json
import current_battletoads_stock_6a3_1116 as Current
import compose_battletoads_camera_handoff_1114 as Camera

R,ROM,PIN,W,N=Current.R,Current.ROM,Current.PIN,Current.W,Current.N
ENTRY,STUB,ACTIVE,RETURN=0xa045,0xb603,0xae3e,0xb602
CODE=bytes.fromhex('b51f0a90fa4c3eae')
CFG=R/'tools/audit/prepare_battletoads_current64_host_v1.py'
CFG_SHA='923d60fcd0ef8bfa3b2dfc386cf607dc213dd777be8bef1177c1c1d25885d674'

def segment(b,name):
    rows=[v for v in b['segs'].values()if v.get('name','').strip('"')==name];assert len(rows)==1
    row=rows[0];return int(row['start'],0),int(row['size'],0),row['id']

@lru_cache(maxsize=1)
def funding(raw):
    Current.preservation(raw);b=Current.bundle(raw);cache=raw[Current.CACHE:Current.CACHE+8192]
    assert Current.digest(CFG.read_bytes())==CFG_SHA
    text=CFG.read_text()
    for literal in('BT_CACHE_MEM:start=$a000,size=$2000,bank=3,type=ro',
        'BT_CACHE_HOST:load=BT_CACHE_MEM,type=ro;',
        'BT_CACHE_STATE:load=BT_CACHE_MEM,type=ro,start=$bee0;',
        'BT_CACHE_HOST_STATE:load=BT_CACHE_MEM,type=ro,start=$bf60;',
        'BT_CACHE_INVALID_COOKIE:load=BT_CACHE_MEM,type=ro,start=$bfe0;'):
        assert text.count(literal)==1,literal
    host,size,host_id=segment(b,'BT_CACHE_HOST');assert(host,size)==(0xad9c,0x84a)and host+size==0xb5e6
    assert segment(b,'BT_ART_META')[:2]==(0xab9c,512)
    assert segment(b,'BT_CACHE_STATE')[:2]==(0xbee0,117)
    assert segment(b,'BT_CACHE_HOST_STATE')[:2]==(0xbf60,64)
    assert segment(b,'BT_CACHE_INVALID_COOKIE')[:2]==(0xbfe0,16)
    # Recover exactly the typed pre-camera packet by the three existing
    # leased private inverses. No whole ROM inverse/rebuild or archive read.
    lease=Camera.allocation();baseline=bytearray(cache);private=[]
    for at,old,new in Camera.spans():
        if Current.CACHE<=at<Current.CACHE+8192:
            offset=at-Current.CACHE;assert cache[offset:offset+len(new)]==new
            baseline[offset:offset+len(old)]=old
            private.append(dict(file=[at,at+len(old)],CPU=[0xa000+offset,0xa000+offset+len(old)],
                old_SHA256=Current.digest(old),current_SHA256=Current.digest(new)))
    baseline=bytes(baseline);assert Current.digest(baseline)==lease['old_payload_SHA256']
    assert len(private)==3 and private[-1]['CPU']==[0xb5e6,0xb603]
    assert cache[RETURN-0xa000]==0x60
    assert baseline[0x15e6:0x1ee0]==b'\xff'*(0x1ee0-0x15e6)
    assert cache[0x1603:0x1ee0]==b'\xff'*(0x1ee0-0x1603)
    assert all(not(Current.CACHE<=at<Current.CACHE+8192)for at,_ in Current.Frozen.C.Carry.PREIMAGES)
    aliases={}
    for target in range(STUB,STUB+8):
        hits=[i for i in range(8191)if cache[i:i+2]==target.to_bytes(2,'little')]
        assert not hits,('Existing private literal word points inside funding',hex(target),hits)
        aliases[hex(target)]=hits
    own_labels=[n for n,s in b['syms'].items()if s.get('seg')in(host_id,segment(b,'BT_CACHE_API')[2],segment(b,'BT_CORE')[2],segment(b,'BT_ART_META')[2])and STUB<=int(s.get('val','0'),0)<STUB+8]
    assert not own_labels
    # Real bounded descriptor pointers, not every accidental word in a bitmap.
    at=W.address(b,'BtPoseLo')&8191;hi=W.address(b,'BtPoseHi')&8191;poses=[]
    for i in range(12):
        ptr=cache[at+i]+256*cache[hi+i];length=cache[ptr&8191]
        assert 0xab9c<=ptr and ptr+length<0xad9c and length<=48
        poses.append(dict(pointer=ptr,length=length,half_open=[ptr,ptr+length+1]))
    return dict(actual_packet_SHA256=Current.digest(cache),typed_baseline_SHA256=Current.digest(baseline),
        recovery='Only three declared camera span preimages restored inside detached8192B array',
        original_typed_host_half_open=[host,host+size],existing_camera_appendage_half_open=[0xb5e6,0xb603],
        camera_private_spans=private,camera_grant_SHA256=Camera.GRANT_SHA,
        funding_CPU_half_open=[STUB,STUB+8],funding_file_half_open=[Current.CACHE+STUB-0xa000,Current.CACHE+STUB-0xa000+8],
        original_typed_fill_to_fixed_state=[0xb5e6,0xbee0],remaining_current_fill_to_fixed_state=[STUB,0xbee0],
        current_capacity_preimage_SHA256=Current.digest(cache[0x1603:0x1ee0]),
        fill_owner='Existing raw33 private cache8192; declared linker fill after host, fixed state remainsBEE0',
        configuration_source_SHA256=CFG_SHA,own_label_ingress=own_labels,literal_word_ingress=aliases,
        valid_twelve_pose_pointer_extents=poses,existing_RTS=dict(PC=RETURN,byte='60',owner='Last byte of qualified camera appendage'),
        generic_packet_copy_hash_readers_accounted_as_whole_packet_consumers=True,
        no_claim_exhaustive_foreign_undecoded_aliases=True,outputs=0)

def proposal(raw):
    proof=funding(raw);old=raw[Current.CACHE:Current.CACHE+8192]
    assert old[0x45:0x48]==bytes.fromhex('4c46b5')and old[0x1603:0x160b]==b'\xff'*8
    assert W.address(Current.bundle(raw),'Enemy_State')==0x1f
    new=old[:0x45]+b'\x4c'+STUB.to_bytes(2,'little')+old[0x48:0x1603]+CODE+old[0x160b:]
    cookie=raw[Current.COOKIE:Current.COOKIE+16];assert cookie[4:]==bytes.fromhex(Current.digest(old))[:12]
    after=cookie[:4]+bytes.fromhex(Current.digest(new))[:12]
    header=raw[Current.HEADER:Current.HEADER+487];delta=Current.COOKIE-Current.HEADER
    new_header=header[:delta]+after+header[delta+16:]
    rows=[(Current.CACHE+0x45,old[0x45:0x48],new[0x45:0x48]),(Current.CACHE+0x1603,b'\xff'*8,CODE),(Current.COOKIE,cookie,after)]
    q=dict(owning_parent_SHA256=PIN,detached_only=True,ROM_composed=False,mounted=False,source_lease_pending=True,outputs=0,
        owned_bytes=27,changed_bytes=sum(a!=b for _,x,y in rows for a,b in zip(x,y,strict=True)),
        spans=[dict(file=[at,at+len(x)],old=x.hex(),new=y.hex(),old_SHA256=Current.digest(x),new_SHA256=Current.digest(y))for at,x,y in rows],
        old_packet_SHA256=Current.digest(old),proposed_packet_SHA256=Current.digest(new),
        proposed_header487_SHA256=Current.digest(new_header),funding=proof,
        contract='LDAstate/ASLA exportsMSB toC; BCC existingRTS rejectsrising withC0; mature JMP existingActive',
        no_new_RAM_CHR_carrier_art_physics_helper_capacity=True)
    return old,new,q

if __name__=='__main__':
    _,_,q=proposal(ROM.read_bytes());q['receipt_SHA256']=Current.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
