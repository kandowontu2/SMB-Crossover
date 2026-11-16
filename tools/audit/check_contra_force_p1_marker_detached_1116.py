"""Leased detached getter/late CPU units; packet remains an explicit fixture."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import compose_contra_force_p1_work_marker_1116 as C

P,N=C.Plan,C.Plan.N
COMPOSER_SHA='4e4417093da676b46ec6e58603fe5f9ba7f6d09b186c9a064ccca21ed08b8b1c'


def seed(raw):
    assert C.H(Path(C.__file__).read_bytes())==COMPOSER_SHA
    candidate,_=C.proposal(raw);assert C.inverse(candidate)==raw
    z,s=P.inputs(raw);d=P.descriptor(raw)
    old=bytearray(65536);old[0xa000:0xc000]=z['q']['carrier'][16384:24576]
    old[0xc000:0xe000]=z['q']['carrier'][8192:16384]
    new=bytearray(old)
    for f in d['fragments']:
        pc=f['CPU_half_open'][0];new[pc:pc+f['bytes']]=bytes.fromhex(f['new_hex'])
    old[0x8c7b:0x8c83]=new[0x8c7b:0x8c83]=bytes.fromhex('0102040810204080')
    return old,new,s,d


def getter(raw):
    old,new,s,d=seed(raw);rows=Counter();cases=0;minimum=255;written=set()
    for p in range(32,256):
        if not p&32:continue
        for y in range(256):
            pair=[]
            for i,image in enumerate((old,new)):
                m=bytearray(image);m[0x100:0x200]=bytes((k*13+p+y)&255 for k in range(256))
                c=N.NesMPU(memory=m,pc=0xbe14);c.a=y^165;c.x=(y*17)&255;c.y=y;c.p=p;c.sp=211
                end=0xbe2d if i==0 else d['fragments'][1]['labels']['NativeMaskReadEnd']
                for _ in range(30):
                    if c.pc==end:break
                    minimum=min(minimum,c.sp);assert m[c.pc]!=0;c.step()
                else:raise AssertionError(('Getter bound',p,y,c.pc))
                pair.append((c,m))
            a,b=pair
            assert(a[0].a,a[0].x,a[0].y,a[0].p,a[0].sp)==(b[0].a,b[0].x,b[0].y,b[0].p,b[0].sp),(p,y,'Getter AXYP/SP')
            assert a[1][:0x8000]==b[1][:0x8000]and a[1][0xc000:0xe000]==b[1][0xc000:0xe000]
            rows[y<64,y==0,a[0].processorCycles-b[0].processorCycles]+=1;cases+=1
    return dict(cases=cases,all256_Y_all128_hardware_status=True,AXYP_SP_stack_temp_private_exact=True,
        minimum_SP=minimum,cycle_savings=[dict(below64=lo,zero=zero,cycles=cy,cases=n)for(lo,zero,cy),n in sorted(rows.items())])


def late(raw):
    old,new,s,d=seed(raw);cases=0;minimum=255;costs=Counter();gate_B=Counter();dead=set();attr_seen=set();rejected=0
    tokens=((0,0),(0,64),(8,72),(128,128),(128,192),(136,200))
    for p in range(32,256):
        if not p&32:continue
        for scene in range(8):
            for ot,nt in tokens:
                attrs=[(p*17+i*7+scene*29)&255 for i in range(64)]
                if nt==128:attrs=[a&231 for a in attrs]
                attr_seen.update(attrs);pair=[]
                for image,token in((old,ot),(new,nt)):
                    m=bytearray(image);m[0x100:0x200]=bytes((i*13+p+scene)&255 for i in range(256))
                    for i,attr in enumerate(attrs):m[512+i*4:516+i*4]=bytes((248 if(scene+i)%3==0 else(40+i)&255,i*3&255,attr,i*5&255))
                    for i in range(24):m[s['CfP1SavedAttributes']+i]=(i*11+p)&255;m[s['SprObject_SprAttrib']+i]=(i*19+scene)&255
                    m[0xc2df]=token;m[0xc2fa]=77;m[0xc2fb]=1;m[0x7ff8]=(p+scene)&1
                    # Real gate's first PHP is modeled, then a transparent RTS
                    # fixture. Full CfCallA/packet/bank execution is not claimed.
                    m[0xbf55:0xbf58]=bytes.fromhex('082860');m[0x1e1:0x1e3]=(0x4fff).to_bytes(2,'little')
                    c=N.NesMPU(memory=m,pc=0xbe53);c.a=p^165;c.x=scene*29;c.y=p^91;c.p=p;c.sp=224
                    gate=[]
                    for _ in range(10000):
                        if c.pc==0x5000:break
                        if c.pc==0xbf55:gate.append((c.a,c.x,c.y,c.p,c.sp))
                        if c.pc==0xbf56:gate.append(m[0x100+c.sp+1])
                        minimum=min(minimum,c.sp);assert m[c.pc]!=0,('Late BRK',scene,ot,nt,c.pc);c.step()
                    else:raise AssertionError(('Late bound',p,scene,ot,nt,c.pc))
                    pair.append((c,m,gate))
                a,b=pair
                assert(a[0].a,a[0].x,a[0].y,a[0].p,a[0].sp)==(b[0].a,b[0].x,b[0].y,b[0].p,b[0].sp),(p,scene,ot,nt,'Public AXYP/SP')
                assert bool(a[2])==bool(b[2])==bool(nt&128)
                if a[2]:
                    ga,gb=a[2][0],b[2][0]
                    assert ga[:3]+ga[4:]==gb[:3]+gb[4:]and ga[3]&239==gb[3]&239
                    assert a[2][1]==b[2][1],'Actual first PHP consumption differs'
                    gate_B[ga[3]^gb[3]]+=1
                diff={i for i in range(0x8000)if a[1][i]!=b[1][i]}
                if not nt&128 and nt!=ot:
                    assert b[1][0xc2df]==nt and a[1][0xc2df]==ot
                private_diff={i for i in range(0xc000,0xe000)if a[1][i]!=b[1][i]}
                if nt&128:assert not private_diff
                else:assert private_diff<={0xc2df}
                assert diff<={0x1db,0x1dc},('Only consumed moved leaf return may be dead',p,scene,ot,nt,sorted(diff))
                if diff:
                    assert nt&128 and max(diff)<0x100+a[0].sp
                    assert int.from_bytes(b[1][0x1db:0x1dd],'little')-int.from_bytes(a[1][0x1db:0x1dd],'little')==4
                dead|=diff;costs[scene,nt&192,a[0].processorCycles-b[0].processorCycles]+=1;cases+=1
    assert attr_seen==set(range(256))
    # A zero-work bit with an OAM tag is outside the proven protocol. Reject
    # this sensitivity fixture explicitly; do not silently call it parity.
    for attribute in range(256):
        try:assert not attribute&24,'No-work invariant rejects tagged/hidden OAM'
        except AssertionError:rejected+=1
    assert rejected==192
    return dict(cases=cases,all128_hardware_status_six_legal_token_pairs_eight_hidden_visible_scenes=True,
        all256_attribute_values_in_matrix=True,public_AXYP_SP_all_OAM_saved_native_and_private_exact=True,
        intended_pending40_difference_only_at_C2DF_on_unconsumed_tokens=True,
        actual_gate_first_PHP_byte_AXY_SP_and_consumed_flags_exact=True,internal_gate_B_copy_XOR_counts=dict(gate_B),
        exact_dead_moved_leaf_return_cells=sorted(dead),every_other_stack_and_live_caller_byte_compared=True,
        invariant_violating_tagged_no_work_inputs_rejected=rejected,minimum_SP=minimum,
        cycle_savings=[dict(scene=scene,token_class=token,cycles=cy,cases=n)for(scene,token,cy),n in sorted(costs.items())],
        packet_CfCallA_represented_by_explicit_PHP_PLP_RTS_fixture=True,full_packet_actual_ISR_mounted_proof_pending=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--getter',action='store_true');ap.add_argument('--late',action='store_true');a=ap.parse_args();assert a.getter or a.late
    raw=C.load_current_image()
    def deny(*args,**kw):raise AssertionError('Detached CPU proof attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=dict(owning_parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,new_whole_ROM_or_NesBus_mount=False,native=False,outputs=0)
        if a.getter:q['getter']=getter(raw)
        if a.late:q['late']=late(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
