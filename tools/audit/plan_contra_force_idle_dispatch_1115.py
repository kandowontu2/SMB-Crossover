"""Detached CF router/P1 alternatives; no ROM composition or mounted image."""
from functools import lru_cache
from pathlib import Path
import json,re
import profile_contra_force_current_costs_1115 as P

C,W,N=P.C,P.W,P.N
Code=C.Plan.Code
PROFILE_SHA='721d91c5220c20f71d31cb61683b05cfb3612244b4f86aff1d3c6c692d8f1a94'
ROUTER_BASE,ROUTER_END=0xbe6e,0xbf91
LATE_BASE,LATE_END=0xbe53,0xbeff
PAINT_BASE,PAINT_END=0xbed0,0xbefc
CHR=1048592


@lru_cache(maxsize=1)
def bindings(raw):
    assert C.H(Path(P.__file__).read_bytes())==PROFILE_SHA
    assert C.H(raw)==C.CANDIDATE,'Exact owning bc5 only'
    q=P.bindings(raw);text=(P.KERNEL/'runtime.lbl').read_text()
    labels={name:int(pc,16)for pc,name in re.findall(r'^al ([0-9A-Fa-f]+) \.(\w+)',text,re.M)}
    for name,pc in(('CfA2Router',ROUTER_BASE),('CfA2RouterEnd',ROUTER_END),('CfP1LateEntry',LATE_BASE),
        ('CfP1Late',0xbe80),('CfP1PacketGate',0xbf55),('CfCallA',0xca0b),('CfOwnLo',0xbf49),('CfOwnHi',0xbf6d)):
        assert labels[name]==pc,(name,labels.get(name))
    return q,labels


def router(raw):
    q,s=bindings(raw);at=8192+(ROUTER_BASE&8191);old=q['carrier'][at:at+ROUTER_END-ROUTER_BASE]
    assert len(old)==291 and old[:8]==bytes.fromhex('0848ada17d488a48')
    tables=old[0xbf49-ROUTER_BASE:];assert len(tables)==72
    prefix=old[:0xbeb8-ROUTER_BASE]
    assert old[0xbeb8-ROUTER_BASE:0xbec6-ROUTER_BASE]==bytes.fromhex('ad6c01a200c9039005e903e8d0f7')
    a=Code(ROUTER_BASE)
    # Keep the complete current cookie/class check and late-owner capture.
    # Only their existing rejection branches are rebound to the merged path.
    from py65.disassembler import Disassembler
    memory=[0]*65536;memory[ROUTER_BASE:ROUTER_BASE+len(prefix)]=prefix
    dis=Disassembler(N.NesMPU(memory=memory));pc=ROUTER_BASE
    while pc<0xbeb8:
        size,_=dis.instruction_at(pc);chunk=bytes(memory[pc:pc+size])
        if chunk[0]in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
            target=pc+2+(chunk[1]if chunk[1]<128 else chunk[1]-256)
            if target==s['CfBadCookie']:a.branch(chunk[0],'Bad')
            else:a.data.extend(chunk)
        else:a.data.extend(chunk)
        pc+=size
    assert pc==0xbeb8
    a.label('Divide');a.emit('a900')
    # q[k+1] = floor((offset + q[k] + 1)/4), q[0]=0.
    # Four stages are exact floor(offset/3) on the entire byte domain.
    for _ in range(4):a.emit('386d6c016a4a')
    a.emit('aa');a.label('HaveIndex');a.emit('e024');a.branch(0xb0,'Bad')
    a.emit('bd49bf8deca2bd6dbf8deda2a9038deea2')
    a.emit('38');a.branch(0xb0,'Restore');a.label('Bad');a.emit('18')
    a.label('Restore');a.emit('babd0301a8bd04019d0301bd05019d0401989d050168a868aa68')
    a.branch(0x90,'BadFlags');a.emit('28200bca');a.absolute(0x4c,'Return')
    a.label('BadFlags');a.emit('2818')
    a.label('Return');a.data.extend(old[s['CfA2Return']-ROUTER_BASE:0xbf49-ROUTER_BASE])
    code=a.done();assert len(code)<=0xbf49-ROUTER_BASE
    spare=0xbf49-ROUTER_BASE-len(code)
    result=code+bytes([0xea])*spare+tables
    assert len(result)==len(old)==291 and result[-72:]==old[-72:]
    return old,result,dict(a.labels),spare


def late(raw):
    q,s=bindings(raw);at=16384+(LATE_BASE&8191);old=q['carrier'][at:at+172]
    assert C.H(old)=='a247fb3fd68b6b90218a96f4ec2183ddd361e9cdcebdb1ad7c4375f8745a01dc'
    prefix=old[:45]
    before=bytes.fromhex('a9008ddfc2682808488a489848');after=bytes.fromhex('a9008ddfc28a489848')
    assert prefix.count(before)==prefix.count(bytes.fromhex('2080be'))==1
    prefix=prefix.replace(before,after).replace(bytes.fromhex('2080be'),bytes.fromhex('207cbe'))
    assert len(prefix)==41
    lead=old[45:PAINT_BASE-LATE_BASE]
    assert len(lead)==80 and lead[-2:]==bytes.fromhex('a200')
    a=Code(PAINT_BASE-4);a.label('Paint');a.emit('bd02022918');a.branch(0xf0,'NoTag')
    a.emit('4a4a4ac903');a.branch(0xf0,'SetCarry');a.emit('2901cdfbc2');a.branch(0xf0,'SetCarry')
    a.emit('a9f89d0002');a.label('SetCarry');a.emit('38bd020229e79d0202');a.absolute(0x4c,'Next')
    a.label('NoTag');a.emit('bd020218');a.label('Next');a.emit('e8e8e8e8');a.branch(0xd0,'Paint')
    paint=a.done();assert len(paint)==48
    new=prefix+lead+paint+old[-3:]
    assert len(new)==len(old)==172 and new[-3:]==bytes.fromhex('4c55bf')
    return old,new,dict(a.labels,Entry=LATE_BASE,Leaf=0xbe7c),dict(old_paint=old[PAINT_BASE-LATE_BASE:-3],new_paint=paint)


def descriptor(raw):
    q,s=bindings(raw);ro,rn,rl,spare=router(raw);po,pn,pl,_=late(raw);fragments=[]
    payload=bytearray(q['carrier'])
    for name,bank,pc,old,new,labels in(('CF router',2,ROUTER_BASE,ro,rn,rl),('P1 late',3,LATE_BASE,po,pn,pl)):
        offset=(bank-1)*8192+(pc&8191);assert payload[offset:offset+len(old)]==old
        payload[offset:offset+len(old)]=new
        fragments.append(dict(name=name,physical_RAM=bank,CPU_half_open=[pc,pc+len(old)],
            carrier_offset=offset,file=CHR+935*1024+offset,bytes=len(old),changed_bytes=sum(a!=b for a,b in zip(old,new,strict=True)),
            old_SHA256=C.H(old),new_SHA256=C.H(new),old_hex=old.hex(),new_hex=new.hex(),labels=labels))
    b=q['bundle'];cookie_sites=[W.location(b,name)for name in('CfExternalCookie','CfLoaderExpectedCookie')]
    old_cookie=raw[cookie_sites[0]:cookie_sites[0]+16]
    assert all(raw[at:at+16]==old_cookie for at in cookie_sites)
    assert old_cookie==bytes((167,31,0,5))+bytes.fromhex(C.H(q['carrier']))[:12]
    new_cookie=old_cookie[:4]+bytes.fromhex(C.H(payload))[:12]
    return dict(owning_ROM_SHA256=C.CANDIDATE,reference67_SHA256=C.PIN,
        fragments=fragments,private_router_tables72_anchored_BF49_BF6D_exact=True,
        router_exact_code_bytes=219-spare,router_owned_gap_after_code=spare,
        private_header15_compares_plus_separate_class_check_unchanged=True,outer_full_validation_unchanged=True,
        division_domain='all256 offsets, floor(offset/3), reject quotient>=36 exactly as original',
        repeated_SFC_low_reads_require_actual_ISR_preservation_closure=True,
        old_payload_SHA256=C.H(q['carrier']),detached_new_payload_SHA256=C.H(payload),
        required_full_integrity_digest_updates=[dict(file=at,bytes=16,old_hex=old_cookie.hex(),new_hex=new_cookie.hex(),only_digest12_changes=True)for at in cookie_sites],
        P1_public_entry_BE53_anchored=True,P1_private_leaf_rebind=dict(old=0xbe80,new=0xbe7c,known_internal_JSR_count=1,complete_ingress_census_pending=True),
        P1_hidden_attributes_still_clear=True,P1_empty_tag_writes_omit_only_identical_RAM_values=True,
        no_new_RAM_CHR_or_spare_unowned_bytes=True,no_new_whole_ROM_or_mount_or_native=True,
        premount_proposal_only=True,source_or_native_ROM_lease_requested=False,outputs=0)


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    def deny(*a,**kw):raise AssertionError('Detached proposal attempted output/native')
    with __import__('unittest.mock',fromlist=['patch']).patch.object(Path,'write_bytes',deny),__import__('unittest.mock',fromlist=['patch']).patch.object(Path,'write_text',deny):
        q=descriptor(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
