"""Detached constant-time Wf query successor to the rejected sparse fit."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import plan_battletoads_flat_resolver_1115 as Previous

Code,C,Input,N,W=Previous.Code,Previous.C,Previous.Input,Previous.N,Previous.W
OLD_ROUTER=Previous.router
OLD_SEED=Previous.detached_seed


def router(base=0xb020,*,new=False,helper=None):
    if not new:return OLD_ROUTER(base,new=False,helper=helper)
    if helper is None:helper=0xb799
    a=Code(base)
    for _ in range(36):a.absolute(0x4c,'Router')
    a.mark('Unavailable');a.emit('1860');a.mark('Router');a.emit('08488a489848ad026038e91bc907')
    a.branch(0xb0,'No');a.emit('4a');a.branch(0xb0,'No');a.emit('a8ad6c0138e920aa8a8d6a01c003')
    a.branch(0xd0,'Common');a.emit('8a29b3c913');a.branch(0xf0,'No')
    a.emit('e033');a.branch(0xf0,'Portrait');a.emit('e04e');a.branch(0xf0,'Colors');a.emit('a2ad')
    a.mark('Common');a.absolute(0xb9,helper+63);a.emit('8d6c01a9'+bytes((helper>>8,)).hex()+'8d6d01a9e0205a01')
    a.branch(0x90,'No');a.mark('Target');a.emit('8d620168a868aa688d6a01284c5d01')
    a.mark('No');a.emit('68a868aa688d6a01281860')
    a.mark('Portrait');a.emit('a911');a.branch(0xd0,'Cold')
    a.mark('Colors');a.emit('a991');a.mark('Cold');a.emit('8d6c01a9b08d6d01a9c8');a.branch(0xd0,'Target')
    out=a.done();assert len(out)==224,(len(out),a.labels)
    return out,a.labels


def helper(raw,base=0xb799):
    off=lambda pc:16+96*8192+(pc&8191)
    assert raw[off(0xb2cb):off(0xb2cb)+4]==bytes.fromhex('38601860')
    # The real existing group predicate, with its C1/C0 returns, no X/Y write.
    assert raw[off(0xb639):off(0xb639)+13]==bytes.fromhex('ade85f2907c906b00238601860')
    table=bytearray(raw[Previous.WF_AT+67:Previous.WF_END]);assert len(table)==108
    for slot in range(36):
        lo,hi,bank=table[3*slot:3*slot+3];word=lo+256*hi
        if(bank,word)==(224,0xb799):table[3*slot:3*slot+2]=(0xb2cd).to_bytes(2,'little')
        elif(bank,word)==(224,0xb79b):table[3*slot:3*slot+2]=(0xb2cb).to_bytes(2,'little')
    a=Code(base);a.mark('Foreign');a.emit('a92b8d6c01a9b28d6d01a9c34c5a01')
    a.mark('Own');a.emit('a82039b6');a.branch(0x90,'Return')
    a.absolute(0xb9,base+67);a.emit('8d6c01');a.absolute(0xb9,base+68);a.emit('8d6d01');a.absolute(0xb9,base+69)
    a.mark('Return');a.emit('60');assert a.pc-base==37
    a.mark('Fast');a.emit('a9c08d6c018e6d01a9dd205a01');a.branch(0x90,'Foreign');a.emit('8d6c01a9a08d6d019860')
    assert a.pc-base==62;a.emit('ea');a.mark('Entries')
    for label in('Foreign','Own','Foreign','Fast'):a.code.append(a.labels[label]&255)
    a.mark('Targets');a.code.extend(table);out=a.done();assert len(out)==175
    a.labels['Visible']=0xb2cb;a.labels['NoOp']=0xb2cd
    return out,a.labels,list(table)


def shapes(parent,image):
    assert OLD_ROUTER()[0]==Previous.OldRouter()[0]==image[Previous.ROUTER_AT:Previous.ROUTER_AT+224]
    h,hl,_=helper(image);r,rl=router(new=True);rows=[]
    for at,code in((Previous.ROUTER_AT,r),(Previous.WF_AT,h)):
        old=image[at:at+len(code)];rows.append(dict(file=[at,at+len(code)],old_hex=old.hex(),new_hex=code.hex(),
            old_SHA256=sha256(old).hexdigest(),new_SHA256=sha256(code).hexdigest(),changed=sum(a!=b for a,b in zip(old,code,strict=True))))
    return dict(reference_SHA256=C.CANDIDATE,detached_envelopes=rows,owned_bytes=399,Router_labels=rl,helper_labels=hl,
        fit=dict(Router=224,foreign=15,own_dense=22,raw33_fast=25,helper_NOP=1,cohort_entry_lows=4,dense_targets=108,helper_total=175),
        old_sparse_fit_rejected_for_all_six_WWF_extra1618_cycles_per_Main=True,
        full_BtCheck_unchanged=True,all_other_real_Wf_target_triplets_exact=True,
        existing_group_suffix=dict(PRG=96,CPU=0xb639,bytes='ade85f2907c906b00238601860'),
        existing_NoOp_Visible_aliases=dict(PRG=96,SEC_RTS=0xb2cb,CLC_RTS=0xb2cd,bytes='38601860'),
        query_Y_is_canonical_cohort_0_to3=True,raw33_X_register_value_is_AD=True,
        no_mounted_overlay=True,no_new_whole_image=True)


def detached_seed(seed,new):
    m,labels=OLD_SEED(seed,new)
    m.flat_unit=True
    if new:m.flat_extra_leaves=(0xb2cb,0xb2cd)
    return m,labels


def status_units(parent,image):
    b=Previous.Base.symbols(image);m=N.Bus(b);m.raw_page(1,224)
    N.put(m,CurrentBank=224,CurrentBankC=m.rawtags[2],SelectedCharacter=29)
    group_at=W.address(b,'FmGroups');cases=0
    for group in range(256):
        m[group_at]=group;value=group&7
        for p in range(256):
            if not p&32:continue
            for x,y in((0,255),(173,3)):
                c=N.NesMPU(memory=m,pc=0xb639);c.a=85;c.x=x;c.y=y;c.p=p;c.sp=236;c.stPushWord(0x5aff)
                for _ in range(20):
                    if(c.pc,c.sp)==(0x5b00,236):break
                    c.step()
                else:raise AssertionError(('Group suffix return',group,p,x,y,c.pc))
                assert(c.a,c.x,c.y,c.sp)==(value,x,y,236)
                assert c.p&0x4c==p&0x4c and bool(c.p&1)==(value<6)
                assert bool(c.p&128)==(value<6)and bool(c.p&2)==(value==6)
                cases+=1
    print('PROGRESS '+json.dumps(dict(group_suffix_cases=cases,all256_groups_all128_valid_P=True)),flush=True)
    pair=[]
    for new in(False,True):
        z,labels=detached_seed(m,new);z.flat_visible=labels['Visible']if new else-1;pair.append(z)
    table=image[Previous.WF_AT+67:Previous.WF_END]
    slots=[i for i in range(36)if table[3*i+2]==224 and int.from_bytes(table[3*i:3*i+2],'little')in(0xb799,0xb79b)]
    public=0;deltas=set()
    for slot in slots:
        for p in range(256):
            if not p&32:continue
            for a,x,y in((0,0,255),(255,173,3)):
                out=[]
                for z in pair:
                    list.__setitem__(z,slice(0x100,0x200),list.__getitem__(m,slice(0x100,0x200)))
                    z[group_at]=0;out.append(Previous.public_call(z,slot,a,x,y,p))
                assert all(out[0][k]==out[1][k]for k in('PC','A','X','Y','P','SP'))and out[0]['PC']==0x5b00
                Previous.Base.M.Research.compare(pair,out,('Dense full-status public NoOp/Visible',slot,p,a,x,y))
                delta=tuple(at for at in range(0x15a,0x17b)if pair[0][at]!=pair[1][at]);assert set(delta)<={0x16c,0x16d}
                deltas.add(delta);public+=1
    return dict(group_suffix_cases=cases,all256_groups_all128_valid_P_two_XY=True,
        valid_roles_0_to5_invalid_6_7_with_all_high_bits=True,exact_group_A_X_Y_SP_D_I_V_and_consumed_C_N_Z=True,
        complete_public_NoOp_Visible_cases=public,slots=slots,all128validP_two_AXY=True,
        explicit_opaque_SMC_differences=[list(x)for x in sorted(deltas)],component_fixtures_only=True,
        no_mounted_overlay=True,no_new_whole_image=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('shapes','public','status','wwf-profile','components'));args=ap.parse_args()
    parent,image,info=Input.load()
    def deny(*a,**kw):raise AssertionError('Detached dense proposal attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',deny),\
        patch.object(Previous,'router',router),patch.object(Previous,'helper',helper),patch.object(Previous,'shapes',shapes),patch.object(Previous,'detached_seed',detached_seed):
        fn={'shapes':shapes,'public':Previous.public_units,'status':status_units,'wwf-profile':Previous.wwf_profile,
            'components':lambda p,z:dict(status=status_units(p,z),WWF=Previous.wwf_profile(p,z))}[args.mode]
        q=fn(parent,image)
    q.update(info,mode=args.mode,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
