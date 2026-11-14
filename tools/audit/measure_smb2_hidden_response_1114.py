"""Uncomposed source-response supplement measurement; no new allocation."""
from hashlib import sha256
import argparse
import json
from compose_metal_head_bridge_1112 import assemble_segments
import compose_smb2_hidden_head_1114 as Cache


def recipe(public):
    M=Cache.Measure
    b,source,old,code,labels,newlabels=M.recipe(public)
    before='''S2HiddenReturn:
 txa
 beq HiddenZero
 lda #$ff
 bne HiddenStore
HiddenZero:
 sec
HiddenStore:
 sta S2Math0
 pla
 tax
 rts
'''
    after='''S2HiddenReturn:
 txa
 bcc HiddenSolid
 beq HiddenStore
HiddenSolid:
 lda #$ff
HiddenStore:
 sta S2Math0
 pla
 tax
 rts
 nop
'''
    assert source.count(before)==1;source=source.replace(before,after)
    names=('R0','R2','R4','R5','R6','R7','S2X','S2Y','S2Page','S2YPage',
           'S2ProbeDirection','S2HeadX','S2HeadPage','S2HeadY','S2Math0',
           'S2DF011','S2DF055','GetBlockBufferAddr','MTileAttribute','S2VY')
    constants={n:Cache.W.address(b,n)for n in names}
    response,response_labels=assemble_segments(source,M.ORIGINS,constants)
    assert all(response[n]==code[n]for n in code if n!='HIDDEN_RETURN')
    assert response['HIDDEN_RETURN'].hex()=='8a9002f002a9ff8d0e5c68aa60ea'
    assert len(response['HIDDEN_RETURN'])==14
    assert response_labels['S2FlagProbe']==0xb128 and response_labels['S2FlagSharedReturn']==0xb1d5
    return b,source,old,response,labels,response_labels


def measure():
    public=Cache.public_image(Cache.parent_image())
    b,source,_,code,_,labels=recipe(public)
    return dict(passed=True,measurement_only=True,formal_behavior_supplement_grant=False,
        reference_ROM_SHA256=sha256(public).hexdigest(),
        generated_source_SHA256=sha256(source.encode()).hexdigest(),
        main174_and_predicate9_VY4_unchanged_from_fc69=True,
        return14_CPU_half_open=[0xbc96,0xbca4],file_half_open=[973990,974004],
        earlier_cache_only_proposal_hex='8af004a9ffd001388d0e5c68aa60',
        measured_return14_hex=code['HIDDEN_RETURN'].hex(),
        behavior='Only upward player0 negativeVY direction0/1 tile60 returnsFF through the original source ceiling response. Hidden direction>=2 remains0/C1. All non60 unchanged.',
        mechanism='Original direction CMP carry0 survives publisher loads/stores; return TXA/BCC gives FF for upward, while carry1 plus X0 gives empty for hidden sides/feet. Normal solid X1 remainsFF.',
        new_RAM_CHR_geometry_padding_bytes=0,ROM_mutations=0,outputs=0,Mesen_run=False)


def units():
    public=Cache.public_image(Cache.parent_image())
    b,_,_,code,_,labels=recipe(public);W,N=Cache.W,Cache.N
    oldcode=Cache.Measure.recipe(public)[3]
    memories=[bytearray(65536),bytearray(65536)]
    at=W.location(b,'MTileAttribute');pc=W.address(b,'MTileAttribute')
    for m,q in zip(memories,(oldcode,code),strict=True):
        m[pc:pc+256]=public[at:at+256]
        for name,data in q.items():m[Cache.Measure.ORIGINS[name]:Cache.Measure.ORIGINS[name]+len(data)]=data
    addr={n:W.address(b,n)for n in('S2VY','S2ProbeDirection','S2Math0','S2HeadX','S2HeadPage','S2HeadY')}
    def call(m,tile,owner,p,direction,vy):
        m[7],m[8],m[5]=0,4,128
        m[addr['S2VY']],m[addr['S2ProbeDirection']]=vy,direction
        for name,value in(('S2Math0',77),('S2HeadX',11),('S2HeadPage',22),('S2HeadY',33)):m[addr[name]]=value
        m[0x1fb:0x1fe]=bytes([owner,0xee,0xbe])
        c=N.NesMPU(memory=m,pc=labels['ProbeOtherTile']);c.a,c.x,c.y,c.p,c.sp=tile,owner,96,p,250
        for _ in range(80):
            if(c.pc,c.sp)==(0xbeef,253):break
            c.step()
        else:raise AssertionError('Response leaf bound')
        return(c.a,c.x,c.y,c.p,c.sp,c.pc),tuple(m[addr[n]]for n in('S2Math0','S2HeadX','S2HeadPage','S2HeadY'))
    ordinary=hidden=0
    for tile in range(256):
        for owner in(0,1,128,255):
            for p in(0,65,255):
                for direction in range(8):
                    for vy in(0,128):
                        a=call(memories[0],tile,owner,p,direction,vy)
                        z=call(memories[1],tile,owner,p,direction,vy)
                        yes=tile==96 and owner==0 and vy>=128 and direction<2
                        if yes:
                            assert a[0][:3]==z[0][:3]and a[0][4:]==z[0][4:]and a[0][3]^z[0][3]==1
                            assert z[0][3]&1==0,'Normal upward solid response carry'
                        else:assert a[0]==z[0],(tile,owner,p,direction,vy,a,z)
                        if tile!=96:assert a[1]==z[1];ordinary+=1
                        else:
                            assert z[1]==((255,0,4,128)if yes else(0,11,22,33)),(tile,owner,p,direction,vy,z)
                            hidden+=1
    # Carry from direction CMP is live across the publisher. Exhaust the
    # tail's actual two role values and all256 incoming status values.
    tail=0
    for owner in(0,1):
        for p in range(256):
            m=memories[1];m[0x1fb:0x1fe]=bytes([71,0xee,0xbe])
            c=N.NesMPU(memory=m,pc=0xbc96);c.a,c.x,c.y,c.p,c.sp=31,owner,17,p,250
            for _ in range(12):
                if(c.pc,c.sp)==(0xbeef,253):break
                c.step()
            else:raise AssertionError('Tail bound')
            assert m[addr['S2Math0']]==(255 if owner or not p&1 else 0)
            assert(c.a,c.x,c.y,c.p&0x7d,c.sp)==(71,71,17,(p&0x7d)&~2,253)
            assert c.p&1==p&1;tail+=1
    return dict(passed=True,measurement_only=True,non60_leaf_pairs=ordinary,
        hidden_orientation_role_pairs=hidden,all256_P_return_tail_cases=tail,
        AXYP_SP_PC_and_cache_exact_except_intended_upward_Math0_and_C0=True,
        ROM_mutations=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--units',action='store_true');args=p.parse_args()
    print(json.dumps(units()if args.units else measure(),separators=(',',':')),flush=True)
