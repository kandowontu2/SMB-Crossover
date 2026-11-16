"""Detached RP2A03 CF fragment proof; no NesBus, whole image or overlay."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import plan_contra_force_idle_dispatch_1115 as P

C,N=P.C,P.N


class Memory(list):
    def __init__(self):
        super().__init__([0]*65536);self.watch=False;self.reads=Counter();self.writes=set()
    def __getitem__(self,at):
        if self.watch and isinstance(at,int):self.reads[at]+=1
        return super().__getitem__(at)
    def __setitem__(self,at,v):
        if self.watch and isinstance(at,int):self.writes.add(at)
        return super().__setitem__(at,v)


def router(raw):
    old,new,labels,_=P.router(raw);q,s=P.bindings(raw);memories=[]
    b=q['bundle'];ci=P.W.location(b,'CfExternalCookie');cookie=raw[ci:ci+16]
    for code in(old,new):
        m=Memory();m[P.ROUTER_BASE:P.ROUTER_END]=code;m[0xca0b]=0x60;memories.append(m)
    costs=Counter();cases=0;minimum=255;weighted={};headers=Counter();max_SFC_reads=0
    def one(offset,p,variant=0,fault=None,fm=None,a=85,x=71,y=37,sp=224,loan=0,bank=139,weight=False):
        nonlocal cases,minimum,max_SFC_reads
        results=[]
        for m in memories:
            m.watch=False;m.reads.clear();m.writes.clear()
            m[0x100:0x200]=[(i*29+offset)&255 for i in range(256)]
            m[0x100+((sp+1)&255)]=239;m[0x100+((sp+2)&255)]=255
            m[0xbfe0:0xbff0]=cookie;m[0xbfe2]=variant;m[0xcf86:0xcf96]=cookie
            if fault is not None:m[0xbfe0+fault]^=1
            m[0x7da1]=bank;m[0x5116]=bank;m[0x16c]=offset;m[0x5fe8]=(variant<<3)if fm is None else fm
            m[0xa2df]=loan;m[0xbdd1]=74;m[0xa2ec:0xa2ef]=[43,97,11]
            c=N.NesMPU(memory=m,pc=P.ROUTER_BASE);c.sp=sp;c.a=a;c.x=x;c.y=y;c.p=p;m.watch=True;seen=[]
            for _ in range(1100):
                if c.pc==0xfff0:break
                if c.pc==0xca0b:
                    seen.append((c.a,c.x,c.y,c.p,c.sp,m[0xa2ec]+256*m[0xa2ed],m[0xa2ee]))
                    c.a=a^167;c.x=(x+13)&255;c.y=y^128;c.p=(p^197)|32
                minimum=min(minimum,c.sp);c.step()
            else:raise AssertionError(('Detached router timeout',offset,p,fault,c.pc))
            m.watch=False
            valid=offset<108 and fault is None and((m[0x5fe8]>>3)&3)==variant
            assert len(seen)==int(valid),(offset,p,variant,fault,fm,seen)
            if valid:
                target=old[0xbf49-P.ROUTER_BASE+offset//3]+256*old[0xbf6d-P.ROUTER_BASE+offset//3]
                assert seen[0]==(a,x,y,p|48,(sp-3)&255,target,3),seen
            else:assert(c.a,c.x,c.y,c.p)==(a,x,y,(p|48)&254),(offset,p,fault,c.a,c.x,c.y,c.p)
            assert c.sp==(sp+2)&255 and m[0x7da1]==m[0x5116]==bank
            checks=tuple(m.reads[0xcf86+i]for i in range(16))
            max_SFC_reads=max(max_SFC_reads,m.reads[0x16c])
            results.append((c,m,seen,checks))
        left,right=results
        assert(left[0].a,left[0].x,left[0].y,left[0].p,left[0].sp)==(right[0].a,right[0].x,right[0].y,right[0].p,right[0].sp)
        assert left[2:]==right[2:]
        assert left[1][0x100:0x200]==right[1][0x100:0x200],('Stack mismatch',offset,p,fault)
        addresses=left[1].writes|right[1].writes
        assert all(left[1][i]==right[1][i]for i in addresses),('Changed protocol/scratch',offset,p,fault,[(hex(i),left[1][i],right[1][i])for i in addresses if left[1][i]!=right[1][i]])
        delta=left[0].processorCycles-right[0].processorCycles
        costs[('valid'if left[2]else'reject'),delta]+=1;headers[left[3]]+=1;cases+=1
        if weight:weighted[offset]=delta
    for offset in range(256):
        for p in range(256):
            if p&32:one(offset,p,variant=(offset//7)&3,a=(offset*73)&255,x=(offset*17)&255,y=p^91)
        if offset%64==63:print('PROGRESS '+json.dumps(dict(router_offsets=offset+1,cases=cases)),flush=True)
    statuses=cases
    for variant in range(4):
        for fault in range(16):
            for offset in(0,18,42,105,108,255):
                for p in(32,49,105,229):one(offset,p,variant,fault)
    faults=cases-statuses
    for fm in range(256):
        for offset in(0,18,42,105,108,255):one(offset,0x69,(fm>>3)&3,fm=fm,loan=128)
    groups=cases-statuses-faults
    for sp in(128,200,247):
        for offset in(0,18,42,105,108,255):
            for p in(32,49,105,229):
                for a,x,y in((0,0,0),(255,255,255),(71,109,23)):
                    one(offset,p,a=a,x=x,y=y,sp=sp,loan=128,bank=2 if p&1 else 255)
    corners=cases-statuses-faults-groups
    frequencies={0:1,3:1,6:1,18:1,27:1,30:1,36:1,39:1,42:4,87:1,102:1}
    for offset in frequencies:one(offset,49,weight=True)
    return dict(cases=cases,all256_offsets_all128_hardware_status=statuses,
        fault_cases=faults,all256_FmGroups_with_six_offset_corners=groups,register_stack_bank_corners=corners,
        actual_profile_service_weights=frequencies,weighted_savings_cycles_per14callback_Main=sum(frequencies[o]*weighted[o]for o in frequencies),
        service_savings=[dict(offset=o,calls=frequencies[o],saved_cycles=weighted[o])for o in frequencies],
        cycle_deltas=[dict(kind=k,saved_cycles=d,cases=n)for(k,d),n in sorted(costs.items())],
        full_AXYP_SP_entire_page1_and_all_written_data_equal=True,
        private_full_expected_header_reads_identical=True,header_read_signatures=len(headers),
        maximum_SFC_low_reads=max_SFC_reads,minimum_SP=minimum,
        unchanged_private_worker_represented_by_explicit_return_fixture=True,
        actual_CfCallA_or_public_FarCall_or_ISR_not_executed=True,no_NesBus_mount_or_whole_image=True)


def paint(raw):
    old,new,labels,parts=P.late(raw);memories=[];cases=0;costs=Counter()
    for pc,code in((P.PAINT_BASE,parts['old_paint']),(labels['Paint'],parts['new_paint'])):
        m=Memory();m[pc:pc+len(code)]=code;m[P.PAINT_END:P.PAINT_END+3]=bytes.fromhex('4c55bf');memories.append((m,pc))
    for attr in range(256):
        for choice in(0,1):
            for p in range(256):
                if not p&32:continue
                results=[]
                for m,pc in memories:
                    m.watch=False;m.reads.clear();m.writes.clear();m[0x2fc:0x300]=[attr^165,99,attr,197];m[0xc2fb]=choice
                    c=N.NesMPU(memory=m,pc=pc);c.sp=224;c.a=85;c.x=252;c.y=p^41;c.p=p;m.watch=True
                    for _ in range(80):
                        if c.pc==0xbf55:break
                        c.step()
                    else:raise AssertionError(('Paint timeout',attr,choice,p,c.pc))
                    m.watch=False;results.append((c,m))
                a,b=results
                assert(a[0].a,a[0].x,a[0].y,a[0].p,a[0].sp)==(b[0].a,b[0].x,b[0].y,b[0].p,b[0].sp),(attr,choice,p)
                assert a[1][0x2fc:0x300]==b[1][0x2fc:0x300]
                assert a[1][0xc2fb]==b[1][0xc2fb]==choice
                assert b[1].writes<=a[1].writes and all(a[1][i]==b[1][i]for i in a[1].writes)
                costs[attr&24,choice,a[0].processorCycles-b[0].processorCycles]+=1;cases+=1
    return dict(cases=cases,all256_attributes_both_legal_choices_all128_hardware_status=True,
        exact_final_AXYP_SP_and_all_data_bytes=True,hidden_rows_not_special_cased=True,
        row_fixture_starts_X252_for_exact_lastrow_flags=True,
        choice0_1_is_internal_domain_overwritten_by_complete_leaf=True,
        per_row_savings=[dict(attribute_tag=t,choice=q,saved_cycles=d,cases=n)for(t,q,d),n in sorted(costs.items())],
        no_NesBus_mount_or_whole_image=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('router','paint'));args=ap.parse_args()
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No mutable Nightly reread'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Detached primitive attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q={'router':router,'paint':paint}[args.mode](raw)
    q.update(mode=args.mode,owning_ROM_SHA256=C.CANDIDATE,no_actual_game_code_mounted=True,outputs=0)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
