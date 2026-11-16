"""Separate detached shared resolver tail proposal; old CF06a4 plan frozen."""
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_idle_dispatch_1115 as Prior

C,N,W=Prior.C,Prior.N,Prior.W
Code=Prior.Code
PRIOR_SHA='06a4efc814a0b81957f03026fe892b0e13a90fd4c9f9ca04264c08eae6c9f9b4'
BASE,FILE,SIZE=0xb799,792489,175
OLD_SHA='1db29ae7f1b6ecc475f5282287b4e0aba1865fe4892bf8e54cd2a63abfbb8119'


def new_code(raw,base=BASE):
    assert C.H(Path(Prior.__file__).read_bytes())==PRIOR_SHA
    Prior.bindings(raw);old=raw[FILE:FILE+SIZE];assert C.H(old)==OLD_SHA
    a=Code(base);a.label('Entry');a.branch(0xb0,'Fast');a.emit('88');a.branch(0xf0,'Own')
    a.label('Foreign');a.emit('a2b2a92b');a.branch(0xd0,'Setup')
    a.label('Own');a.emit('a82039b6');a.branch(0x90,'Return')
    a.absolute(0xb9,'Targets');a.emit('8d6c01');a.absolute(0xb9,'Targets',1);a.emit('8d6d01');a.absolute(0xb9,'Targets',2)
    a.label('Return');a.emit('60');a.label('Fast');a.emit('a9c0')
    a.label('Setup');a.emit('8d6c018e6d01');a.branch(0x90,'ForeignTail')
    a.emit('a9dd205a01');a.branch(0x90,'Foreign');a.emit('8d6c01a9a08d6d019860')
    a.label('ForeignTail');a.emit('6868a9c34c6301')
    assert len(a.data)==67
    a.label('Targets');a.data.extend(old[67:]);new=a.done()
    assert len(new)==175 and new[67:]==old[67:]and a.labels['Targets']==base+67
    return new,dict(a.labels)


def old_code(raw,base=BASE):
    Prior.bindings(raw);old=bytearray(raw[FILE:FILE+SIZE]);assert C.H(old)==OLD_SHA
    if base!=BASE:
        readers=[]
        for i in range(67):
            if old[i]==0xb9 and int.from_bytes(old[i+1:i+3],'little')in(BASE+67,BASE+68,BASE+69):
                old[i+1:i+3]=(int.from_bytes(old[i+1:i+3],'little')+base-BASE).to_bytes(2,'little');readers.append(i)
        assert len(readers)==3
    return bytes(old)


def descriptor(raw):
    q,_=Prior.bindings(raw);new,labels=new_code(raw);old=old_code(raw);b=q['bundle']
    at=W.location(b,'FarCallCommon');smc=raw[at:at+33]
    assert W.address(b,'FarCallCommon')==0x15a and smc[9:12]==bytes.fromhex('8d4501')and smc[12:15]==bytes.fromhex('8d1551')
    return dict(owning_ROM_SHA256=C.CANDIDATE,file_half_open=[FILE,FILE+SIZE],physical_PRG=96,CPU_half_open=[BASE,BASE+SIZE],
        old_SHA256=C.H(old),new_SHA256=C.H(new),old_hex=old.hex(),new_hex=new.hex(),changed_bytes=sum(a!=b for a,b in zip(old,new,strict=True)),
        labels=labels,code_bytes=67,all108_target_table_bytes_and_address_B7DC_exact=True,
        current_Router87_224_bytes_unchanged=True,all_other_source_bytes_not_composed=True,
        actual_33byte_FarCall_source=dict(file=at,PC=0x15a,hex=smc.hex(),SHA256=C.H(smc)),
        tail_continuation=dict(PC=0x163,first_op='STA CurrentBank',drops_only_existing_helper_SFC_return_word=True,
            helper_frame_return_word=0x16d,outer_old_bank_byte_retained=True),
        mandatory_ingress='Only actual FarCallCommon SFC entry; arbitrary direct JSR is not an admitted new boundary',
        required_internal_contract_reviews=['Foreign X becomes B2; Bw overwrites it on valid paths; caller must discard it on faults',
            'NextBank_SMC0162 can differ until header/caller overwrites it; prove all reads and ISR snapshot behavior',
            'Two discarded helper-return stack bytes require actual SFC entry/frame and all ingress closure'],
        expected_no_header_skip_or_private_cache_code_bypass=True,
        actual_public_caller_ABI_and_frequency_proof_pending=True,
        no_ROM_image_mount_native_or_delivery=True,proposal_only=True,outputs=0)


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    def deny(*a,**kw):raise AssertionError('Detached shared plan attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=descriptor(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
