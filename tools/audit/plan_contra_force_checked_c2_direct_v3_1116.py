"""Detached73B successor preserves the original query6 native-C capture."""
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_checked_c2_direct_v2_1116 as Previous

Base,H=Previous.Base,Previous.H
PREVIOUS_SHA='0c2c3f37b326c6899ce261e4afca6fccab752eee8632422d74fa94080dfc5bce'
PREVIOUS_RECEIPT='e93be9a4fb97384ff41e4158051f1f481726e2ecd701a3a297a04a3410de9232'


def private_resolver():
    a=Base.Plan.Code(0xbf91)
    a.mark('CheckedC2Resolver');a.emit('ada17dc902');a.branch(0xd0,'Bad')
    a.emit('8ac912');a.branch(0xd0,'DivideInit')
    a.emit('addfc2');a.branch(0x10,'RestoreCommand')
    # The fast path proved original nativeC exactly2. Reproduce the old
    # A2 late prefix's write before borrowing any other C bank.
    a.emit('a9028dd1dd');a.mark('RestoreCommand');a.emit('8a')
    a.mark('DivideInit');a.emit('a200');a.mark('Divide');a.emit('c903');a.branch(0x90,'Index')
    a.emit('e903e8');a.branch(0xd0,'Divide');a.mark('Index');a.emit('e024');a.branch(0xb0,'Bad')
    a.emit('bd49bf8d6c018decc2bd6dbf8d6d018dedc2a9038deec23860')
    a.mark('Bad');a.emit('a9978d6c01ad6a011860')
    new=a.done();assert len(new)==73 and a.pc==0xbfda
    return new,dict(a.labels)


def descriptor(parent):
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    q=Previous.descriptor(parent);assert q['receipt_SHA256']==PREVIOUS_RECEIPT;q.pop('receipt_SHA256')
    image,_=Base.proposal(parent)
    payload_at=Previous.Rejected.PAYLOAD;tail_at=Previous.Rejected.TAIL_FILE
    old=parent[payload_at:payload_at+24576];relative=tail_at-payload_at
    # Exact current old-prefix source/bytes, not a new palette policy.
    old_prefix=bytes.fromhex('ad6c01c912d00baddfa21006ada17d8dd1bd')
    assert old[8192+0x1e78:8192+0x1e8a]==old_prefix
    labels=Base.Plan.Rejected.Source.C.Plan.inputs(Base.reference(parent))[1]
    assert(labels['CfShotPaletteOwned'],labels['CfP1NativeC'])==(0xc2df,0xddd1)
    new,pcs=private_resolver();payload=bytearray(old)
    assert payload[relative:relative+73]==bytes([255])*73
    payload[relative:relative+73]=new;payload=bytes(payload)
    cookie=bytes.fromhex('a71f0005')+bytes.fromhex(H(payload))[:12]
    for row in q['additional_detached_fragments']:
        at=row['file_half_open'][0]
        if at==tail_at:row.update(name='RAM2 tail73',file_half_open=[at,at+73],old_hex=bytes([255]*73).hex(),new_hex=new.hex())
        elif at in(573373,642966):row['new_hex']=cookie.hex()
        before,after=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert image[at:at+len(before)]==before
        row.update(old_SHA256=H(before),new_SHA256=H(after),changed_bytes=sum(a!=b for a,b in zip(before,after,strict=True)))
    owned=set();updates={}
    for at,h in Base.PREIMAGES:
        for i in range(len(bytes.fromhex(h))):owned.add(at+i);updates[at+i]=image[at+i]
    for row in q['additional_detached_fragments']:
        for i,value in enumerate(bytes.fromhex(row['new_hex'])):
            at=row['file_half_open'][0]+i;owned.add(at);updates[at]=value
    assert len(owned)==676
    q.update(previous58B_plan_SHA256=PREVIOUS_SHA,previous58B_plan_receipt=PREVIOUS_RECEIPT,
        previous58B_candidate_SHA256='b8bd4affddb231dbc7d3b67fe5bcad51be110b120665773db80c4dab5f2d73fd',
        previous58B_negative='Actual component11105/query6/C2: omitted old A2 late prefix left physical RAM2 offset1DD1 staleFF instead of2 when Owned was negative.',
        preserved_original_query6_prefix=old_prefix.hex(),old_capture_PC_half_open=[0xbe78,0xbe8a],
        new_capture_contract='Only command18 and negative physicalRAM2 C2DF write exactly2 to DDD1; C2 eligibility proves this equals the old pre-borrow CurrentBankC. Non-C2 still takes whole old path.',
        proposed_total_owned_bytes=676,proposed_total_changed_bytes=sum(parent[at]!=updates[at]for at in owned),
        new_CF_payload_SHA256=H(payload),new_expected_cookie_hex=cookie.hex(),private_helper_labels=pcs,
        source_capacity_required=dict(CPU_half_open=[0xbf91,0xbfda],physical_RAM=2,exact_new_code_bytes=73,
            source_declared_tail_bytes=79,remaining6_bytes_untouched=True),
        new_CPU_or_mount_authorized=False,source_lease_for58B_does_not_authorize_this_successor=True)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    parent=Base.load_current_image();assert H(parent)==Base.PIN
    def deny(*a,**kw):raise AssertionError('Detached73B plan attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=descriptor(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
