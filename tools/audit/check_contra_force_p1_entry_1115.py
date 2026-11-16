"""Detached complete P1 entry/gate contract, including hidden tags and faults."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_idle_dispatch_1115 as P
from check_contra_force_idle_dispatch_1115 import Memory

C,N=P.C,P.N


def run(raw):
    old,new,labels,_=P.late(raw);memories=[]
    for code in(old,new):
        m=Memory();m[P.LATE_BASE:P.LATE_END]=code;m[0xbf55]=0x60;memories.append(m)
    costs=Counter();gate_status=Counter();cases=0;minimum=255;all_differences=set();empty_savings=set()
    def one(p,tag,scene):
        nonlocal cases,minimum
        results=[]
        for m in memories:
            m.watch=False;m.reads.clear();m.writes.clear()
            m[0x100:0x200]=[(i*17+p)&255 for i in range(256)]
            m[0x1e1:0x1e3]=[239,255]
            attrs=[];oam=[]
            for i in range(64):
                kind=(0,8,16,8,16,8 if i&1 else 16,24,(i*37+p)&24)[scene]
                y=248 if scene in(1,2)or(scene==0 and i>=8)else(80+i)%240
                attr=((i*73+p)&231)|kind
                oam.extend((y,i*3&255,attr,i*5&255));attrs.append(attr)
            m[0x200:0x300]=oam
            m[0xddb9:0xddd1]=[(i*37+p)&255 for i in range(24)]
            m[0x587:0x59f]=[i^219 for i in range(24)]
            m[0xc2df]=tag;m[0xc2fa]=(p*11+scene)&255;m[0xc2fb]=(p*13+scene*7)&255;m[0x7ff8]=(p*17+scene*19)&255
            c=N.NesMPU(memory=m,pc=P.LATE_BASE);c.sp=224;c.a=p^165;c.x=scene*29;c.y=p^91;c.p=p;m.watch=True;gate=None
            for _ in range(4500):
                if c.pc==0xfff0:break
                if c.pc==0xbf55:
                    assert gate is None
                    # The unchanged gate's first opcode is PHP. It consumes
                    # exactly this normalized byte, including C/V/I/D/N/Z.
                    gate=(c.a,c.x,c.y,c.p,c.p|48,c.sp)
                minimum=min(minimum,c.sp);c.step()
            else:raise AssertionError(('Complete late instruction bound',p,tag,scene,c.pc))
            m.watch=False
            assert(c.a,c.x,c.y,c.p,c.sp)==(p^165,scene*29,p^91,((p|48)if tag&128 else((p|48)&254)),226),(p,tag,scene,c.a,c.x,c.y,c.p,c.sp)
            assert bool(gate)==bool(tag&128)
            if tag&128:assert m[0xc2fb]in(0,1),'The actual leaf overwrites incoming Choice before Paint'
            results.append((c,m,gate))
        a,b=results
        if a[2]is not None:
            assert a[2][:3]+a[2][4:]==b[2][:3]+b[2][4:],('Gate consumed tuple',p,tag,scene,a[2],b[2])
            assert a[2][3]^b[2][3]in(0,16)
            gate_status[a[2][3]^b[2][3]]+=1
            # All legal SFC worker entries already normalize B via PLP.
            if p&16:assert a[2]==b[2]
        differences={i for i in a[1].writes|b[1].writes if a[1][i]!=b[1][i]}
        assert differences<={0x1db,0x1dc},('Late data difference',p,tag,scene,[(hex(i),a[1][i],b[1][i])for i in differences])
        assert a[1][0x1e1:0x200]==b[1][0x1e1:0x200]
        if differences:
            assert tag&128
            assert(a[1][0x1db]+256*a[1][0x1dc])-(b[1][0x1db]+256*b[1][0x1dc])==4
        all_differences.update(differences)
        delta=a[0].processorCycles-b[0].processorCycles;costs[scene,bool(tag&128),delta]+=1
        if scene==0 and tag&128:empty_savings.add(delta)
        cases+=1
    for p in range(256):
        if not p&32:continue
        for tag in(0,1,127,128,129,255):
            for scene in range(8):one(p,tag,scene)
    assert empty_savings=={718}
    return dict(cases=cases,full_entry_all128_hardware_status_six_token_values_eight_OAM_scenes=True,
        exact_public_AXYP_SP_and_all_private_OAM_attribute_palette_data=True,
        gate_PHP_byte_and_AXY_SP_equal=True,gate_internal_B_copy_XOR_counts=dict(gate_status),
        every_legal_SFC_normalized_P_gate_tuple_bit_exact=True,
        synthetic_B0_input_copy_difference_only_normalized_by_unchanged_first_PHP=True,
        exact_dead_stack_differences=sorted(all_differences),
        dead_bytes_are_leaf_JSR_return_word_discarded_before_public_return=True,
        every_other_written_stack_byte_and_live_caller_page1_byte_equal=True,
        actual_packet_and_CfCallA_represented_by_explicit_gate_RTS_fixture=True,
        naturally_invoked_empty_tag_saving_cycles=718,
        scene_cycle_savings=[dict(scene=s,admitted=t,saved_cycles=d,cases=n)for(s,t,d),n in sorted(costs.items())],
        minimum_SP=minimum,no_NesBus_mount_actual_ISR_or_whole_ROM=True,outputs=0)


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No mutable Nightly reread'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Detached P1 proof attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(raw)
    q.update(owning_ROM_SHA256=C.CANDIDATE,no_actual_game_code_mounted=True)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
