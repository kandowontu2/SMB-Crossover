"""Exact6201 no-fallback-move WRAM1 layout/decode/ABI worksheet.

No candidate ROM, installed writes, artifacts or emulator. Runtime code is
fixture-loaded after actual cold entry; the fourth stream is decoded by the
current real decoder. Full cold source integration and three-header ownership
are explicitly not implemented or qualified here.
"""
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import probe_prince_wram1_funding_1123 as B
import probe_prince_oneup_lift_admission_1123 as Admission

F,H,W,N=B.F,B.H,B.W,B.N
ADMISSION_SOURCE='616bead6df75953b0c7b4122237a8af0028d92ea8c70f0f346f1f49d341d08b4'
IMPORT_OLD=bytes.fromhex('a5751869088d0fc6a55c69008d10c660')
ACTION_SHA='ca610fdf65eb77db44eac42693dc3447602a724f2c83161050132ae8e51c2c0c'


def assemble(text,fields,origin=0xa000):
    # Reuse the frozen instruction assembler, changing only its fixture's
    # artificial below8000 limit. The source module/file remains untouched.
    source=inspect.getsource(F.assemble)
    source=F.Q.P.G.First.once(source,'ORIGIN + len(out) < 0x8000','ORIGIN + len(out) < 0xc000')
    space=dict(F.assemble.__globals__,ORIGIN=origin)
    exec(compile(source,__file__+':relocation-only-assembler','exec'),space)
    return space['assemble'](text,fields)


def gateway(target,bundle):
    dest=W.address(bundle,'FarcallJmpTarget_SMC')+1
    far=W.address(bundle,'FarCallCommon')
    out=bytes((0xa9,target&255,0x8d,dest&255,dest>>8,
               0xa9,target>>8,0x8d,(dest+1)&255,(dest+1)>>8,
               0xa9,1,0x4c,far&255,far>>8))
    assert len(out)==15
    return out


def plan(raw, *, extend=None, build_allocator=None, rewrite_core=None):
    B.binding(raw)
    assert H(Path(Admission.__file__).read_bytes())==ADMISSION_SOURCE
    bundle=dict(W.Symbols.bundle(),raw=raw)
    head,parts,old_lengths=F.Q.P.Packet.extract(raw)
    core=bytearray(parts[0])
    assert core[0x13d1:0x13e1]==IMPORT_OLD
    action=bytes(core[0x6fc:0x71b]);assert len(action)==31 and H(action)==ACTION_SHA
    assert core[0x6f6:0x6f9]==bytes.fromhex('20d1d6')
    fallback=bytes(parts[1][0xed1:0xf56])
    text=F.ASM
    once=F.Q.P.G.First.once
    text=once(text,' jsr Support\n bcc ImportDone',
        ' lda $c0ab\n cmp #167\n bne SkipAdmission\n jsr Allocator\nSkipAdmission:\n jsr Support\n bcc ImportDone')
    text=once(text,' jmp $b3d1',''' lda Player_X_Position
 clc
 adc #8
 sta $c60f
 lda Player_PageLoc
 adc #0
 sta $c610
 rts''')
    target=W.address(bundle,'FarcallJmpTarget_SMC')+1
    far=W.address(bundle,'FarCallCommon')
    nested=f''' lda #209
 sta ${target:04x}
 lda #214
 sta ${target+1:04x}
 lda #3
 jsr ${far:04x}'''
    text=once(text,' jsr $bde2',nested)
    if extend is not None:
        text=extend(text)
    fields=dict(F.symbols(raw),Allocator=0xa000)
    if extend is not None:
        for name in ('R2', 'R3', 'R4', 'R6', 'Enemy_Y_Speed'):
            fields[name] = W.address(bundle, name)
    provisional,_=assemble(text,fields)
    allocator_at=0xa000+len(provisional)
    fields['Allocator']=allocator_at
    helper,labels=assemble(text,fields)
    assert len(helper)==len(provisional)
    if build_allocator is None:
        make=F.Q.P.clone(Admission.machine_code,dict(ORIGIN=allocator_at))
        allocator=make(SimpleNamespace(bundle=bundle))
        assert len(allocator)==183
    else:
        allocator=build_allocator(allocator_at, labels, bundle)
    action_at=allocator_at+len(allocator)
    blob=helper+allocator+action
    assert action_at+31==0xa000+len(blob)<0xbfe0
    for pc,old,new in (
        (0xb3d1,IMPORT_OLD,gateway(labels['Import'],bundle)+b'\xea'),
        (0xa6fc,action,gateway(action_at,bundle)+gateway(labels['Material'],bundle)+b'\xea'),
        (0xa6f6,bytes.fromhex('20d1d6'),bytes((0x20,0x0b,0xa7))),
    ):
        at=pc-0xa000;assert core[at:at+len(old)]==old and len(old)==len(new)
        core[at:at+len(new)]=new
    if rewrite_core is not None:
        rewrite_core(core, labels, bundle)
    parts2=(bytes(core),parts[1],parts[2])
    codec=F.Q.P.Packet
    packed=[codec.encode(x)for x in parts2+(blob,)]
    for a,b in zip(parts2+(blob,),packed):assert codec.decode(b,len(a))==a
    assert bytes(parts2[1][0xed1:0xf56])==fallback
    capacity=len(codec.PAGES)*1024
    budgets={size:capacity-(len(head)+(size-450))-sum(map(len,packed))for size in(450,480,512)}
    info=dict(ROM=H(raw),helper_bytes=len(helper),allocator_bytes=len(allocator),action_bytes=len(action),
              raw1_bytes=len(blob),raw1_SHA256=H(blob),raw1_packed_bytes=len(packed[3]),
              raw1_entries={n:hex(labels[n])for n in('Import','Material','Support')},
              allocator_entry=hex(allocator_at),original_action_entry=hex(action_at),
              runtime_gate_spans=[['0xb3d1',16],['0xa6fc',31]],
              runtime_gate_bytes=45,runtime_source_hook=['0xa6f6','20d1d6','200ba7'],
              old_encoded_lengths=list(old_lengths),new_encoded_lengths=list(map(len,packed)),
              remaining_by_cold_worker_bytes=budgets,
              unchanged_fallback_SHA256=H(fallback),unchanged_other_decoded_streams=True,
              requires_new_four_stream_cold_and_auth_protocol=True,outputs=0)
    return blob,labels,parts2,packed,info


def load_fixture(seed,blob,parts):
    m=N.fork(seed)
    m.ram[1][:len(blob)]=blob
    # Preserve the reached live SMC and post-finalizer overlays. Only the
    # three authenticated proposed code intervals differ in this fixture.
    for start,size in((0x13d1,16),(0x6fc,31),(0x6f6,3)):
        m.ram[3][start:start+size]=parts[0][start:start+size]
    return m


def compare_fields(a,b,*,skip=()):
    for bank in(2,3):
        omitted=set(skip)if bank==3 else set()
        assert all(x==y or i in omitted for i,(x,y)in enumerate(zip(a.ram[bank],b.ram[bank]))),[
            (bank,hex(i),x,y)for i,(x,y)in enumerate(zip(a.ram[bank],b.ram[bank]))if x!=y and i not in omitted][:10]


def gateway_units(seed,blob,labels,parts):
    skip=set(range(0x13d1,0x13e1))|set(range(0x6fc,0x71b))|set(range(0x6f6,0x6f9))
    imports=0
    for p in(0x31,0x71,0xf1,0x30):
        old=N.fork(seed);new=load_fixture(seed,blob,parts)
        a=F.private(old,0xb3d1,p=p);b=F.private(new,0xb3d1,p=p)
        assert a['regs']==b['regs'];compare_fields(old,new,skip=skip);imports+=1
    parsed=F.authored(seed);count=0
    for x in(929,943):
        for action in(0,1,17,42):
            for mode in(0,1,5):
                old=F.scene(parsed,x=x)
                for i in range(6):F.slot(old,'Enemy_Flag',0,i)
                N.put(old,Player_Y_Position=112,Player_State=0,Player_Y_Speed=0)
                old.ram[2][0x611]=old.ram[2][0x8b]=64
                old.ram[2][0x84:0x88]=bytes((144,0,144,0))
                old.ram[2][0x616]=action;old.ram[2][0x618]=mode
                new=load_fixture(old,blob,parts)
                a=F.private(old,0xd6d1);b=F.private(new,0xa70b)
                assert a['regs']==b['regs'],(x,action,mode,a,b)
                compare_fields(old,new,skip=skip);count+=1
    m=F.scene(seed);land=F.native_platform(m);assert land['flag']==5
    new=load_fixture(m,blob,parts)
    F.private(new,0xb3d1)
    assert int.from_bytes(new.ram[2][0x84:0x86],'little')==land['top']
    q=F.private(new,0xa70b)
    assert q['regs'][0]==1 and int.from_bytes(new.ram[2][0x7f:0x81],'little')==land['top']
    return dict(original_import_return_pairs=imports,complete_original_fallback_pairs=count,
                positive_native_support=True,nested_maps_restored=new.rawtags[1:3]==[3,2],
                standalone_SupportAction_N_flag_not_claimed=True)


def decoder_unit(seed,raw,blob,packed):
    head=F.Q.P.Packet.extract(raw)[0]
    decoder=head[31072:F.Q.P.Packet.LOADER]
    assert len(decoder)==254 and decoder[:2]==bytes.fromhex('a200')
    assert len(packed)<0x500
    m=N.fork(seed)
    m.ram[2][:254]=decoder
    m.ram[2][0x300:0x300+len(packed)]=packed
    m.ram[2][0x60e]=0
    for bank in(1,2,3):m.ram[bank][0x1fe0]=0
    m.ram[2][0xaa:0xac]=(0xc300).to_bytes(2,'little')
    m.ram[2][0xec:0xee]=len(blob).to_bytes(2,'little')
    N.put(m,R0=0,R1=0xa0,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,
          CurrentBank=3,CurrentBankC=2)
    m.raw_page(1,3);m.raw_page(2,2)
    target=W.address(m.bundle,'FarcallJmpTarget_SMC')+1
    m[target:target+2]=(0xc000).to_bytes(2,'little')
    m[W.address(m.bundle,'SafecallA_SMC')+1]=0
    before3=bytes(m.ram[3]);writes=0;entry=None
    cpu=N.NesMPU(memory=m,pc=W.address(m.bundle,'FarCallCommon'))
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=1,0,0,0x35,224;cpu.stPushWord(0x5aff)
    for _ in range(600000):
        if cpu.pc==0x5b00:break
        if cpu.pc==0xc000:entry=[list(m.rawtags),N.get(m,'CurrentBank'),cpu.sp]
        if cpu.pc==0xc0c8:writes+=1
        assert m[cpu.pc],('Fourth decode BRK',hex(cpu.pc),m.rawtags)
        cpu.step()
    else:raise AssertionError('Fourth decode bound')
    assert cpu.sp==224 and bytes(m.ram[1][:len(blob)])==blob and writes==len(blob)
    assert m.rawtags[1:3]==[3,2]and N.get(m,'CurrentBank')==3
    assert bytes(m.ram[3])==before3 and all(m.ram[b][0x1fe0]==0 for b in(1,2,3))
    assert bytes(m.ram[2][0x300:0x300+len(packed)])==packed
    return dict(actual_decoder_bytes=254,decoded_bytes=writes,staged_input=['0xc300',hex(0xc300+len(packed))],
                destination=['raw1','0xa000',hex(0xa000+len(blob))],entry=entry,
                CPU=cpu.processorCycles,raw3_and_unpublished_headers_exact=True,
                real_FarCall_restored_raw3=True,complete_cold_scheduler_not_claimed=True)


def main():
    raw=F.Q.P.G.ROM.read_bytes();proof=B.binding(raw)
    blob,labels,parts,packed,info=plan(raw)
    print('PRINCE_WRAM1_ROUTE_PLAN '+json.dumps(info,separators=(',',':')),flush=True)
    def auth(image):assert image==raw;return proof
    def deny(*a,**k):raise AssertionError('Cold worksheet attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        seed=F.Q.P.clone(F.Q.P.cold,dict(authenticate=auth))(raw)
        for _ in range(12):seed.controller_pad=0;F.Q.Engine.Frames.frame(seed,cold=True)
        gates=gateway_units(seed,blob,labels,parts)
        decode=decoder_unit(seed,raw,blob,packed[3])
    report=dict(passed=True,ROM=H(raw),plan=info,gates=gates,fourth_decode=decode,
                full_cold_or_header_ownership_or_native_claim=False,outputs=0)
    digest=H(json.dumps(report,sort_keys=True,separators=(',',':')).encode())
    print('PRINCE_WRAM1_ROUTE_RESULT '+json.dumps(dict(report,SHA256=digest),separators=(',',':')),flush=True)


if __name__=='__main__':main()
