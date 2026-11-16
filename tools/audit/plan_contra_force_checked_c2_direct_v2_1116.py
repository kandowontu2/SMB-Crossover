"""Detached58B successor; the53B draft fails exact non-C2 fallback."""
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_checked_c2_direct_1116 as Rejected

Base,H,ROM=Rejected.Base,Rejected.H,Rejected.ROM
REJECTED_SHA='7bfcb282a5f99e5dc5579aabb46585ff5a0c63b8e81417ff4a644a8289909a4b'
REJECTED_RECEIPT='1b73d5a53d4d5cdb5a37280c7adb296210597b21c67d333b66683303467858a2'


def private_resolver():
    old,labels=Rejected.private_resolver();assert old[-5:]==bytes.fromhex('ad6a011860')
    # R87 Legacy publishes only the high byte B7. A rejected private
    # resolver must first recover the exact Wf entry low97, not leave91.
    new=old[:-5]+bytes.fromhex('a9978d6c01ad6a011860')
    assert len(new)==58 and labels['Bad']==0xbfc1
    return new,dict(labels,LegacyLowRestored=0xbfc6)


def descriptor(parent):
    assert H(Path(Rejected.__file__).read_bytes())==REJECTED_SHA
    q=Rejected.descriptor(parent);assert q['receipt_SHA256']==REJECTED_RECEIPT
    q.pop('receipt_SHA256');image,_=Base.proposal(parent)
    assert image[716848:717072].count(bytes.fromhex('a9b78d6d01a9e0205a01'))==1
    new,labels=private_resolver();payload=bytearray(parent[Rejected.PAYLOAD:Rejected.PAYLOAD+24576])
    relative=Rejected.TAIL_FILE-Rejected.PAYLOAD
    assert payload[relative:relative+58]==bytes([255])*58
    payload[relative:relative+58]=new;payload=bytes(payload)
    cookie=bytes.fromhex('a71f0005')+bytes.fromhex(H(payload))[:12]
    for row in q['additional_detached_fragments']:
        at=row['file_half_open'][0]
        if at==Rejected.TAIL_FILE:
            row['name']='RAM2 tail58';row['file_half_open'][1]=at+58;row['old_hex']=bytes([255]*58).hex();row['new_hex']=new.hex()
        elif at in(573373,642966):row['new_hex']=cookie.hex()
        old,after=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert image[at:at+len(old)]==old
        row.update(old_SHA256=H(old),new_SHA256=H(after),changed_bytes=sum(a!=b for a,b in zip(old,after,strict=True)))
    owned=set();updates={}
    for at,h in Base.PREIMAGES:
        for i in range(len(bytes.fromhex(h))):owned.add(at+i);updates[at+i]=image[at+i]
    for row in q['additional_detached_fragments']:
        for i,value in enumerate(bytes.fromhex(row['new_hex'])):
            at=row['file_half_open'][0]+i;owned.add(at);updates[at]=value
    assert len(owned)==661
    q.update(rejected53B_draft_SHA256=REJECTED_SHA,rejected53B_receipt=REJECTED_RECEIPT,
        rejected53B_reason='Non-C2 rejection left low91; unchanged R87 Legacy would call B791 instead of B797. Caught analytically before CPU.',
        proposed_total_owned_bytes=661,proposed_total_changed_bytes=sum(parent[at]!=updates[at]for at in owned),
        new_CF_payload_SHA256=H(payload),new_expected_cookie_hex=cookie.hex(),private_helper_labels=labels,
        source_capacity_required=dict(CPU_half_open=[0xbf91,0xbfcb],physical_RAM=2,exact_new_code_bytes=58,
            source_declared_tail_bytes=79,remaining21_bytes_untouched=True),
        non_C2_contract='Before changing X reject CurrentBankC!=2. Restore target low97, return original command from SafecallA016A/C0, then exact old R87 Legacy highB7 reaches B797 and retries Wf/Bw. No worker executes.',
        corrected_fallback_entry=0xb797,
        successful_public_SMC_publication_obligation=dict(addresses=[0x162,0x16c,0x16d],
            old='bank2 and BE+3*service veneer',new='bank3 and actual RAM3 leaf',
            consumer_and_interrupt_proof_pending=True,not_a_blanket_SMC_exclusion=True))
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    parent=Base.load_current_image();assert H(parent)==Base.PIN
    def deny(*a,**kw):raise AssertionError('Detached58B plan attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=descriptor(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
