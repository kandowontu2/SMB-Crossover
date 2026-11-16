"""Detached exact14B lifecycle HUD invalidation fit; no candidate image/CPU."""
from pathlib import Path
from hashlib import sha256
import json
import audit_rogue_stock_foundation_1327_1116 as Source
import current_rogue_missile_cb95_1116 as Current

R,W,N=Current.R,Current.W,Current.N
ROM=Current.ROM
PARENT=Current.PIN


def H(data):return sha256(data).hexdigest()


def descriptor(raw):
    assert isinstance(raw,bytes)and H(raw)==PARENT
    Current.C.inverse(raw)  # strict portable input authentication only
    b=W.Symbols.bundle()   # retained linker metadata; no UI.seed/bindings/cold
    records={}
    def actual(name,source):
        code=Source.source_bytes(b,name,source)
        if name in('RdBodyNewSession','RdBodyNewLife','RdBodyEnterScene'):
            old=b'\x4c'+W.address(b,'RdBodyLifecycleDirty').to_bytes(2,'little')
            new=b'\x4c'+W.address(b,'RdItSyncLifecycle').to_bytes(2,'little')
            assert code.endswith(old);code=code[:-3]+new
        at,pc=W.location(b,name),W.address(b,name)
        assert raw[at:at+len(code)]==code,('Current/source mismatch',name,at,code.hex(),raw[at:at+len(code)].hex())
        records[name]=dict(PC=pc,file=at,bytes=len(code),hex=code.hex(),SHA256=H(code),source=source,
            source_SHA256=H((R/'src'/source).read_bytes()),source_reassembled_byte_exact=True)
        return code
    for name,src in(
        ('RdHostEnabled','rogue_dawn_host.s'),
        ('RdHsImportPosition','rogue_dawn_host_services.s'),
        ('RdHsEnterScene','rogue_dawn_host_services.s'),
        ('RdHsNewSession','rogue_dawn_host_services.s'),
        ('RdHsNewLife','rogue_dawn_host_services.s'),
        ('RdTxMovementBegin','rogue_dawn_host_deferred.s'),
        ('RdBodyNewSession','rogue_dawn_host_body.s'),
        ('RdBodyNewLife','rogue_dawn_host_body.s'),
        ('RdBodyEnterScene','rogue_dawn_host_body.s'),
        ('RdItSyncLifecycle','rogue_dawn_host_items_gate.s'),
        ('RdItSyncStatus','rogue_dawn_host_items_gate.s'),
        ('RdBodyLifecycleDirty','rogue_dawn_host_body.s')):actual(name,src)
    old=bytes.fromhex(records['RdBodyLifecycleDirty']['hex'])
    new=(b'\x90\x0b\x20'+W.address(b,'RdTxMovementBegin').to_bytes(2,'little')+
         b'\xa9\x01\x8d'+W.address(b,'InvDirty').to_bytes(2,'little')+
         b'\x8d'+W.address(b,'RdColorRequest').to_bytes(2,'little')+b'\x60')
    assert len(old)==len(new)==14 and old[10:]==new[10:]
    at=records['RdBodyLifecycleDirty']['file'];pc=records['RdBodyLifecycleDirty']['PC']
    h=sha256();h.update(raw[:at]);h.update(new);h.update(raw[at+14:])
    # Literal leads are a finite census, NOT an instruction/consumer proof.
    # The source and current instruction-boundary classification accompany it.
    bank=(at-16)//8192;lo=16+bank*8192;window=pc&0xe000
    leads=[]
    for pos in range(lo,lo+8192-2):
        op=raw[pos]
        if op not in(0x20,0x4c,0x6c):continue
        target=int.from_bytes(raw[pos+1:pos+3],'little')
        if pc<=target<pc+14:
            leads.append(dict(file=pos,PC=window+pos-lo,opcode=op,target=target))
    symbols=[]
    for name,row in b['syms'].items():
        try:loc=W.location(b,name)
        except(KeyError,ValueError):continue
        if at<=loc<at+14:symbols.append(dict(name=name,PC=W.address(b,name),file=loc))
    words=[]
    for pos in range(lo,lo+8192-1):
        target=int.from_bytes(raw[pos:pos+2],'little')
        if pc<=target<pc+14:words.append(dict(file=pos,target=target))
    # Public old/private tail is not an emitted farcall/table target. Report
    # all typed raw95 target triples too, without labelling random data code.
    triples=[]
    for pos in range(16,16+128*8192-2):
        target=int.from_bytes(raw[pos:pos+2],'little')
        if pc<=target<pc+14 and raw[pos+2]in(95,223):
            triples.append(dict(file=pos,target=target,bank_byte=raw[pos+2]))
    producer=R/'tools/prepare_rogue_dawn_host_items_v3.py'
    producer_text=producer.read_text()
    assert "s.replace('jmp RdBodyLifecycleDirty','jmp RdItSyncLifecycle')"in producer_text
    assert "s.count('jmp RdBodyLifecycleDirty')==3"in producer_text
    expected_direct=[dict(file=W.location(b,'RdItSyncLifecycle'),PC=W.address(b,'RdItSyncLifecycle'),opcode=32,target=pc)]
    assert leads==expected_direct and words==[dict(file=expected_direct[0]['file']+1,target=pc)]
    assert not triples
    assert sorted((z['name'],z['file']-at)for z in symbols)==[('RdBodyLifecycleDirty',0),('RdBodyLifecycleDirty::Done',13)]
    lifecycle={}
    for name,target_names,size in(('RdLifeFresh',('RdBodyNewSession',),64),('RdLifeArea',('RdBodyNewLife','RdBodyEnterScene'),96)):
        pos=W.location(b,name);code=raw[pos:pos+size];refs=[]
        for target in target_names:
            needle=b'\x20'+W.address(b,target).to_bytes(2,'little')
            hits=[i for i in range(len(code)-2)if code[i:i+3]==needle]
            assert len(hits)==1,(name,target,hits)
            refs.append(dict(target=target,file=pos+hits[0],PC=W.address(b,name)+hits[0],preimage=needle.hex()))
        lifecycle[name]=dict(PC=W.address(b,name),file=pos,bytes=size,hex=code.hex(),typed_JSR_consumers=refs)
    ui={}
    for name in('RlUiDispatch','RlUi','LmUiGate','RdLifeUi','RdUiEarly','RdUiHud','X5BounceUiDispatch','X5OwnInventoryUi'):
        try:pos=W.location(b,name);address=W.address(b,name)
        except KeyError:continue
        ui[name]=dict(PC=address,file=pos,bank=(pos-16)//8192,first48=raw[pos:pos+48].hex())
    result=dict(passed=True,detached_only=True,parent_SHA256=PARENT,
        span=dict(file=at,PC=pc,bank=bank,bytes=14,old_hex=old.hex(),new_hex=new.hex(),
            old_SHA256=H(old),new_SHA256=H(new)),predicted_SHA256=h.hexdigest(),
        owned_bytes=14,changed_bytes=sum(a!=z for a,z in zip(old,new)),code_growth=0,new_RAM=0,
        original_last_ColorRequest_store_and_Done_RTS_exact=True,records=records,
        literal_bank_leads_requiring_classification=leads,interior_linker_symbols=symbols,
        current_private_bank_word_consumers=words,raw95_typed_farcall_or_table_triples=triples,
        current_lifecycle_consumers=lifecycle,
        retarget_producer=dict(path=producer.relative_to(R).as_posix(),SHA256=H(producer.read_bytes()),exact_three_target_replacement=True),
        admitted_tail_ingress='Sole current BCDE JSR B78F, reached through three retargeted public wrappers; B79C Done RTS unchanged.',
        estimated_cycles=dict(owned_old=114,owned_new=88,owned_delta=-26,
            foreign_character_reject_old=32,foreign_character_reject_new=9,
            foreign_variant_reject_old=40,foreign_variant_reject_new=9,
            scope='Static RP2A03 cycle count for private tail including real guard and MovementBegin; no proposed CPU execution.'),
        ui_readonly_pointer=ui,
        proposed_CPU=False,installed_game_CPU=False,metadata_UI_CPU=False,candidate_image_composed=False,
        scope='Only three explicit lifecycle helpers through current RdItSyncLifecycle; private arbitrary-C direct calls excluded pending consumer closure.',
        remaining_gates=['Independent exact carry/AXYP/ingress review; source lease before candidate CPU',
            'Reached IRQ/busyNMI and actual owning cold/lifecycle/hud transition after lease',
            'No constant packet emission; ordinary queue ownership and retraction unchanged'],outputs=0,native=False)
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    return result


if __name__=='__main__':print('RESULT '+json.dumps(descriptor(ROM.read_bytes()),separators=(',',':')),flush=True)
