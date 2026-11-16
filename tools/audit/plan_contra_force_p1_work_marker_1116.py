"""Detached existing-byte CF work marker; contingent reader contract, no mount."""
from pathlib import Path
import argparse,json,re
from py65.disassembler import Disassembler
import audit_contra_force_p1_marker_producers_1116 as Audit

C,W,N=Audit.C,Audit.W,Audit.N
Code=C.Plan.Code
MARKER=0xc2df


def inputs(raw):
    # New explicit compact boundary. The full signed inverse was independently
    # exercised in producer79555. Here use its leased portable72 preimages and
    # both whole-image pins, without recursively rebuilding old symbol graphs.
    assert C.H(Path(Audit.Current.__file__).read_bytes())==Audit.CURRENT_SHA
    assert C.H(Path(Audit.__file__).read_bytes())=='5ce53c4cb84e957d75da1ff7c8fcca1504ee12283555b375d19756e44dc59e94'
    assert isinstance(raw,bytes)and C.H(raw)==Audit.Current.CANDIDATE
    reference=bytearray(raw)
    for at,old,new in Audit.Current.spans():
        assert raw[at:at+len(new)]==new;reference[at:at+len(old)]=old
    reference=bytes(reference);assert C.H(reference)==C.CANDIDATE
    rebound=bytearray(reference)
    for at,old,new in Audit.Current.spans():
        assert reference[at:at+len(old)]==old;rebound[at:at+len(new)]=new
    assert bytes(rebound)==raw
    for name in('runtime.lbl','runtime.dbg'):
        assert C.H((Audit.P.KERNEL/name).read_bytes())==Audit.P.PINS[name]
    carrier=raw[Audit.P.CHR+935*1024:Audit.P.CHR+959*1024]
    assert C.H(carrier)=='3a7d2d9a77d5accd30e7976645856118f8734fca5a84f7df7bff8946ec989f84'
    labels={name:int(pc,16)for pc,name in re.findall(r'^al ([0-9A-Fa-f]+) \.(\w+)',(Audit.P.KERNEL/'runtime.lbl').read_text(),re.M)}
    z=dict(raw=raw,reference=reference,q=dict(carrier=carrier),labels=labels)
    for name,pc in(('CfHostRenderAll',0xb3c4),('CfHostRenderBody',0xb400),('CfHostRenderShot',0xb47b),
                    ('CfSourceWindowHigh',0xb5c8),('CfP1EarlyTag',0xbdfe),('CfNativeP1MaskRead',0xbe14),
                    ('CfP1LateEntry',0xbe53),('CfP1Acquire',0xbf44),('CfP1PacketGate',0xbf55),('CfHostAreaReset',0xa898)):
        assert labels[name]==pc,(name,labels.get(name))
    return z,labels


def block(z,pc,count,tag=3):
    at=(tag-1)*8192+(pc&8191);return z['q']['carrier'][at:at+count]


def renderer(z,s):
    base,end,table=0xb34c,0xb5e8,0xb5c8;old=block(z,base,end-base)
    a=Code(base);m=[0]*65536;m[base:end]=old;dis=Disassembler(N.NesMPU(memory=m))
    op_branches={0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0}
    references=[]
    def label(pc):return f'Old_{pc:04X}'
    def copy(lo,hi):
        pc=lo
        while pc<hi:
            a.label(label(pc));n,_=dis.instruction_at(pc);op=m[pc];data=bytes(m[pc:pc+n])
            if op in op_branches:
                target=pc+2+(m[pc+1]if m[pc+1]<128 else m[pc+1]-256)
                assert base<=target<table;a.branch(op,label(target));references.append((pc,target))
            elif n==3 and base<=(target:=m[pc+1]+256*m[pc+2])<table:
                if op in(0x20,0x4c):
                    a.absolute(op,label(target));references.append((pc,target))
                else:
                    assert op==0xbd and target==s['CfStandingFrames']<s['CfHostRenderAll'],'Unexpected renderer interior data read'
                    a.data.extend(data) # Four standing-frame bytes remain anchored.
            else:
                if pc==s['CfShotNoLoan']:assert data==bytes.fromhex('a900');data=bytes.fromhex('a940')
                if pc==s['CfShotNoLoan']-4:assert data==bytes.fromhex('a908');data=bytes.fromhex('a948')
                a.data.extend(data)
            pc+=n
        assert pc==hi
    copy(base,s['CfHostRenderAll']);a.label(label(s['CfHostRenderAll']))
    a.absolute(0x20,label(s['CfHostVisible']));a.branch(0x90,'ModuloStart');a.absolute(0x20,label(s['CfHostRenderBody']))
    a.label('ModuloStart');a.emit('ad23c0');a.label('Modulo');a.emit('c90c');a.branch(0x90,'StartShot')
    a.emit('e90c');a.branch(0xb0,'Modulo');a.label('StartShot');a.emit('690a8dfbc2aa')
    a.label('NextShot');a.absolute(0x20,label(s['CfHostRenderShot']));a.emit('aef1c2e8e016');a.branch(0x90,'NoWrap')
    a.emit('a20a');a.label('NoWrap');a.emit('ecfbc2');a.branch(0xd0,'NextShot');a.emit('a200')
    cursor=s['CurrentOAMOffset'];a.emit('ad'+cursor.to_bytes(2,'little').hex()+'3860')
    assert len(a.data)-(s['CfHostRenderAll']-base)==50
    a.label(label(s['CfHostRenderBody']));assert block(z,s['CfHostRenderBody'],8)==bytes.fromhex('a9008ddfc28df1c2')
    a.emit('addfc229408ddfc2a9008df1c2')
    attr=0xb58e
    # The retained carrier binds the genuine borrowed pointer operand.
    attr_old=block(z,attr,5);assert attr_old[0]==0xb1 and attr_old[2:]==bytes.fromhex('0ddfc2')
    copy(s['CfHostRenderBody']+8,attr);a.label(label(attr));a.emit('addfc22908');a.data.extend(bytes((0x11,attr_old[1])))
    copy(attr+5,table);assert len(a.data)==table-base-3
    a.emit('eaeaea');assert len(a.data)==table-base;a.data.extend(old[table-base:])
    new=a.done();assert len(new)==len(old)==668 and new[-32:]==old[-32:]
    return old,new,dict(a.labels),dict(internal_references=references,retained_source_window_table_PC=table,
        new_Body_PC=a.labels[label(s['CfHostRenderBody'])],new_Shot_PC=a.labels[label(s['CfHostRenderShot'])],
        loop_12_slots_same_order_and_final_Turn_requires_detached_proof=True,
        internal_shot_A_C_and_intermediate_Turn_changes_require_liveness_proof=True,owned_alignment_NOPS=3)


def early(z,s):
    base=0xbdfe;old=block(z,base,85);a=Code(base)
    attr=s['SprObject_SprAttrib'];meta=s['ObjectMetasprite']
    saved=s['CfP1SavedAttributes'];temp=0xc2f7
    a.emit('a217');a.label('Actor');a.emit('bd'+attr.to_bytes(2,'little').hex()+'9d'+saved.to_bytes(2,'little').hex()+'e000')
    a.branch(0xf0,'NextActor');a.emit('bd'+meta.to_bytes(2,'little').hex());a.branch(0xf0,'NextActor')
    a.emit('c991');a.branch(0xb0,'MarkWork');a.emit('a8');assert a.base+len(a.data)==s['CfNativeP1MaskRead']
    a.label('NativeMaskRead');a.emit('08c040');a.branch(0xb0,'MaskTail');a.emit('98');a.branch(0xf0,'MaskReady')
    a.emit('a902');a.branch(0xd0,'MaskReady');a.label('MaskTail');a.emit('b9'+(s['CfNativeP1MaskTail']-64).to_bytes(2,'little').hex())
    a.label('MaskReady');a.emit('8d'+temp.to_bytes(2,'little').hex()+'280900');a.label('NativeMaskReadEnd')
    a.emit('bd'+attr.to_bytes(2,'little').hex()+'2903a8')
    bits,at=0x8c7b,1035403
    assert z['raw'][at:at+8]==bytes.fromhex('0102040810204080')and bits==0x8c7b
    a.emit('b9'+bits.to_bytes(2,'little').hex()+'2d'+temp.to_bytes(2,'little').hex());a.branch(0xf0,'MarkWork')
    a.emit('bd'+attr.to_bytes(2,'little').hex()+'09109d'+attr.to_bytes(2,'little').hex())
    a.label('MarkWork');a.emit('addfc209408ddfc2');a.label('NextActor');a.emit('ca');a.branch(0x10,'Actor')
    a.emit('addfc209808ddfc260');new=a.done();assert len(new)==len(old)==85
    return old,new,dict(a.labels),dict(native_mask_entry_BE14_preserved=True,constant_masks_file=at,
        marks_every_nonzero_native_pose_slots1_to23_including_high_pose=True,source_local_Bits4_removed=True)


def late(z,s):
    base=0xbe53;old=block(z,base,172);a=Code(base)
    attr=s['SprObject_SprAttrib'];saved=s['CfP1SavedAttributes'];oam=s['Sprite_Data']
    a.emit('0848addfc2');a.branch(0x30,'Late');a.emit('68281860')
    a.label('Late');a.emit('c9c0a9008ddfc28dfac28dfbc28a489848a217')
    a.label('RestoreAttributes');a.emit('bd'+saved.to_bytes(2,'little').hex()+'9d'+attr.to_bytes(2,'little').hex()+'ca');a.branch(0x10,'RestoreAttributes')
    a.absolute(0x20,'Leaf');a.emit('68a868aa682860');assert a.base+len(a.data)==base+49
    a.label('Leaf');a.branch(0xb0,'FullScan');a.emit('ad'+(oam+254).to_bytes(2,'little').hex()+'a200');a.branch(0xf0,'Gate')
    a.label('FullScan');a.emit('a200');a.label('Scan');a.emit('bd'+oam.to_bytes(2,'little').hex()+'c9f0');a.branch(0xb0,'Next')
    a.emit('bd'+(oam+2).to_bytes(2,'little').hex()+'29184a4a4ac901');a.branch(0xf0,'AddVisible');a.emit('c902');a.branch(0xd0,'Next')
    a.label('AddVisible');a.emit('0dfac28dfac2');a.label('Next');a.emit('e8e8e8e8');a.branch(0xd0,'Scan')
    a.emit('adfac2c903');a.branch(0xf0,'Both');a.emit('2901');a.branch(0xf0,'PaintStart');a.emit('a901');a.branch(0xd0,'SetChoice')
    a.label('Both');a.emit('adf87f490129018df87f');a.label('SetChoice');a.emit('8dfbc2');a.label('PaintStart');a.emit('a200')
    assert a.base+len(a.data)==0xbed0
    a.data.extend(old[0xbed0-base:-3]);a.label('Gate');assert a.base+len(a.data)==0xbefc;a.emit('4c55bf')
    new=a.done();assert len(new)==len(old)==172
    return old,new,dict(a.labels),dict(fast_path_requires_work_false_implies_all64_attributes_18_zero=True,
        full_paint44_and_packet_gate_BF55_unchanged=True,native24_attributes_always_restored=True,
        fast_palette_packet_still_published_and_Turn_preserved=True)


def acquire(z,s):
    base=0xbf44;old=block(z,base,17)
    pend=s['SmFreezePalettePending'];turn=s['SmFreezeTurn']
    new=bytes.fromhex('a9008d'+pend.to_bytes(2,'little').hex()+'8d'+turn.to_bytes(2,'little').hex()+'a9408ddfc24c55bfea')
    assert len(new)==len(old)==17
    return old,new,{},dict(contingent_on_root_complete_pending_LastBlue_reader_contract=True,
        actual_ingress='Only full-cookie-guarded constructor after five-page clear and HostImport; arbitrary private Acquire call is not the admitted boundary',
        first_Pending0_retained=True,LastBlue_and_Choice_redundant_early_stores_removed=True,owned_trailing_NOP=1)


def area(z,s):
    base=0xa898;old=block(z,base,68);a=Code(base);a.emit('a900aa');a.label('ClearActors');a.emit('9d00c39d00c4e8');a.branch(0xd0,'ClearActors')
    a.emit('8d40c08d42c0a203');a.label('ClearFour');a.emit('9de5c2ca');a.branch(0x10,'ClearFour');a.emit('e88dffc2')
    a.emit('a92e8d82c4a90a8d82c3a9018dd2c48de2c2ad23c038e9018ddec2a9408ddfc2')
    a.emit('20'+s['CfHostImport'].to_bytes(2,'little').hex()+'3860ea');new=a.done();assert len(new)==len(old)==68
    return old,new,dict(a.labels),dict(contingent_on_no_foreground_reentrancy_or_ISR_marker_reader_during_reset=True,
        final_X0_and_marker40_before_HostImport=True,public_import_A8DC_anchored=True,owned_trailing_NOP=1)


def descriptor(raw):
    z,s=inputs(raw);payload=bytearray(z['q']['carrier']);fragments=[]
    for name,pc,make in(('renderer',0xb34c,renderer),('native_early_tag',0xbdfe,early),('late',0xbe53,late),('acquire',0xbf44,acquire),('area_reset',0xa898,area)):
        old,new,labels,contract=make(z,s);at=16384+(pc&8191);assert payload[at:at+len(old)]==old
        payload[at:at+len(old)]=new
        fragments.append(dict(name=name,physical_RAM=3,CPU_half_open=[pc,pc+len(old)],carrier_offset=at,
            file=Audit.P.CHR+935*1024+at,bytes=len(old),changed_bytes=sum(x!=y for x,y in zip(old,new,strict=True)),
            old_SHA256=C.H(old),new_SHA256=C.H(new),old_hex=old.hex(),new_hex=new.hex(),labels=labels,contract=contract))
    cookie_sites=[573373,642966]
    old_cookie=raw[cookie_sites[0]:cookie_sites[0]+16];assert old_cookie[:4]==bytes.fromhex('a71f0005')
    assert all(raw[at:at+16]==old_cookie for at in cookie_sites)
    new_cookie=old_cookie[:4]+bytes.fromhex(C.H(payload))[:12]
    return dict(owning_current_ROM_SHA256=C.H(raw),reference_bc5_SHA256=C.CANDIDATE,
        old_payload_SHA256=C.H(z['q']['carrier']),detached_new_payload_SHA256=C.H(payload),fragments=fragments,
        cookie_views=[dict(file=at,bytes=16,old_hex=old_cookie.hex(),new_hex=new_cookie.hex(),only_digest12_changes=True)for at in cookie_sites],
        owned_bytes=sum(f['bytes']for f in fragments)+32,changed_bytes=sum(f['changed_bytes']for f in fragments)+sum(x!=y for x,y in zip(old_cookie,new_cookie))*2,
        existing_router_and_all_full_cookie_checks_unchanged=True,existing_packet124_and_native_C_save_gate_unchanged=True,
        current_Bowser72_and_all_unowned_bytes_not_composed=True,new_RAM_CHR_art_fields=0,
        contingent_reader_and_actor_domain_contracts=True,detached_CPU_proof_pending=True,
        no_new_whole_ROM_source_mount_native_or_delivery=True,outputs=0)


if __name__=='__main__':
    from unittest.mock import patch
    ap=argparse.ArgumentParser();ap.add_argument('--compact',action='store_true');args=ap.parse_args()
    raw=C.ROM.read_bytes()
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No second mutable Nightly read'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Detached descriptor attempted files/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=descriptor(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    if args.compact:
        q=dict(q,fragments=[{k:v for k,v in f.items()if k not in('old_hex','new_hex','labels')}for f in q['fragments']])
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
