"""Detached checked-C2 direct-leaf proposal; no new whole image or CPU."""
from pathlib import Path
from unittest.mock import patch
import json
import compose_contra_force_checked_resolver_1116 as Base

R,ROM,H=Base.R,Base.ROM,Base.H
BASE_SHA='a84044989c7965b7028fc2e5c3b0f1de4da22b5e6fc8a50fbf8bb057e70ccf6f'
PAYLOAD=2006032
TAIL_FILE=2022305
HELPER_FILE=573351


def private_resolver():
    a=Base.Plan.Code(0xbf91)
    a.mark('CheckedC2Resolver');a.emit('ada17dc902');a.branch(0xd0,'Bad')
    # X is the internal precomputed3*service, never the native callback X.
    a.emit('8aa200');a.mark('Divide');a.emit('c903');a.branch(0x90,'Index')
    a.emit('e903e8');a.branch(0xd0,'Divide')
    a.mark('Index');a.emit('e024');a.branch(0xb0,'Bad')
    a.emit('bd49bf8d6c018decc2bd6dbf8d6d018dedc2a9038deec23860')
    a.mark('Bad');a.emit('ad6a011860')
    new=a.done();assert len(new)==53 and a.pc==0xbfc6
    return new,dict(a.labels)


def descriptor(parent):
    assert H(Path(Base.__file__).read_bytes())==BASE_SHA
    assert isinstance(parent,bytes)and H(parent)==Base.PIN
    owning44b,_=Base.proposal(parent)
    old_payload=parent[PAYLOAD:PAYLOAD+24576]
    assert owning44b[PAYLOAD:PAYLOAD+24576]==old_payload
    new,labels=private_resolver();assert parent[TAIL_FILE:TAIL_FILE+53]==bytes([255])*53
    payload=bytearray(old_payload);relative=TAIL_FILE-PAYLOAD;payload[relative:relative+53]=new
    payload=bytes(payload);assert payload[:relative]==old_payload[:relative]and payload[relative+53:]==old_payload[relative+53:]
    assert payload[8192+0x1e00:8192+0x1f91]==old_payload[8192+0x1e00:8192+0x1f91]
    cookie=bytes.fromhex('a71f0005')+bytes.fromhex(H(payload))[:12]
    assert parent[573373:573389]==parent[642966:642982]==Base.C.OLD_COOKIE
    guard=bytes.fromhex('2047bf9063a9918d6c01984c5a01')
    assert len(guard)==14 and owning44b[573271+0xbfff-0xbf47]==0x60
    fragments=[]
    for name,at,old,after in(('ROM69 checked helper14',HELPER_FILE,owning44b[HELPER_FILE:HELPER_FILE+14],guard),
            ('RAM2 tail53',TAIL_FILE,old_payload[relative:relative+53],new),
            ('ROM69 expected cookie16',573373,owning44b[573373:573389],cookie),
            ('ROM78 expected cookie16',642966,owning44b[642966:642982],cookie)):
        fragments.append(dict(name=name,file_half_open=[at,at+len(old)],old_hex=old.hex(),new_hex=after.hex(),
            old_SHA256=H(old),new_SHA256=H(after),changed_bytes=sum(x!=y for x,y in zip(old,after,strict=True))))
    # Count the proposed owning union sparsely. Do not construct or mount a
    # new whole ROM; only the separately leased44b image already exists here.
    owned=set();updates={}
    for at,h in Base.PREIMAGES:
        for i in range(len(bytes.fromhex(h))):owned.add(at+i);updates[at+i]=owning44b[at+i]
    for row in fragments:
        at=row['file_half_open'][0]
        for i,value in enumerate(bytes.fromhex(row['new_hex'])):owned.add(at+i);updates[at+i]=value
    assert len(owned)==656
    old_A2=parent[PAYLOAD+8192+0x1e00:PAYLOAD+8192+0x1f91]
    result=dict(owning_parent_SHA256=Base.PIN,proposed_composition_reference44b_SHA256=Base.CANDIDATE,
        frozen_Base_composer_SHA256=BASE_SHA,additional_detached_fragments=fragments,
        proposed_total_owned_bytes=len(owned),proposed_total_changed_bytes=sum(parent[at]!=updates[at]for at in owned),
        new_CF_payload_SHA256=H(payload),old_CF_payload_SHA256=H(old_payload),new_expected_cookie_hex=cookie.hex(),
        old401_A2_API_and_inner_check_SHA256=H(old_A2),old401_A2_API_exact=True,
        RAM3_validation_and_every_real36_service_unchanged=True,private_helper_labels=labels,
        source_capacity_required=dict(CPU_half_open=[0xbf91,0xbfc6],physical_RAM=2,
            exact_new_code_bytes=53,source_declared_tail_bytes=79,remaining26_bytes_untouched=True),
        helper14_contract='Actual internal Y=2 supplies A2 for the nested SFC; BF high remains from the checked helper ingress. BCC goes only to existingBFFF RTS after the full checker has completely returned.',
        non_C2_contract='Before changing X, reject CurrentBankC!=2. Return C0 and original command from SafecallA016A; R87 retries the complete old Wf/Bw path. No service executes on this branch.',
        direct_C2_contract='After full16 and actual CurrentBankC=2, resolve existing Lo/Hi into a real RAM3 worker. R87 restores the original native AXYP before the genuine SFC invokes that worker.',
        portable_inverse_recipe='Restore these four exact44b preimages, assert whole44b, then frozenBase.inverse restores whole91dc. No mutable Downloads read and no permissive fallback.',
        unresolved_contracts=[
            'Finish source79 capacity/reader/typed indirect ingress classification before any allocation',
            'Prove exact current internal Y2/X3*slot/SafecallA command and highBF across full16 checker/SFC',
            'Prove every new private opcode follows all16 validated bytes and matching class',
            'Compare full native callback AXYP/CVID/SP/maps and all36/all4class/public faults/cold15-18-19/nonC2 aliases',
            'Direct leaves omit CfCallA ArgA/P temporary stores: prove all current direct/indirect readers overwrite-before-use, or retain those stores with a separately funded return design',
            'Existing587 rejected0162/016C and stack residues remain open, not silently accepted',
            'New reached IRQ/busyNMI and exact private/SMC publication contracts need a separate source lease',
            'Measure paired actual source Main costs before claiming the estimated structural gain or proposing native'],
        budget=dict(measured_current_idle_Main=56203.75,measured44b_idle_Main=53417.75,
            hypothetical_additional_direct_gain_not_measured=8000,
            hypothetical_direct_Main=45417.75,
            hypothetical_with_separate_old_marker_and_complete_unfunded_caller_front_removal=36051.75,
            typical_NMI_not_included=4300,
            zero_lag_or_60Hz_not_predicted=True),
        no_new_whole_ROM_CPU_mount_native_or_delivery=True,outputs=0)
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    parent=Base.load_current_image();assert H(parent)==Base.PIN
    def deny(*a,**kw):raise AssertionError('Detached direct plan attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=descriptor(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
