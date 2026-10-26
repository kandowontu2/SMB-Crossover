"""Bound original exit arithmetic, true lag-NMI ownership and source pressure."""
from pathlib import Path
import argparse, collections, hashlib, itertools, json, traceback
import mm_proto_body_priority_partition_v6 as fixture
from current3cee_postdma_mask_cpu_v4 import Bus
from check_tmnt_render_oa import Memory,address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


class ReadBus(Bus):
    def __init__(self,b,initial):
        self.watch=set();self.watched_reads=[]
        super().__init__(b,initial,(0,0))
    def __getitem__(self,at):
        if isinstance(at,int) and at in self.watch:self.watched_reads.append(at)
        return super().__getitem__(at)


def arithmetic(b):
    m=Memory(b);m.page(1,4)
    l=lambda n:address(b,n)
    start=l('MmBodyPriorityExit');stop=l('MmBodyPriorityRosterTail')
    c=NesMPU(memory=m)
    count=0;minimum=99999;maximum=0
    for logical,first,flags in itertools.product(range(256),range(256),[0x20,0x61,0xa2,0xeb]):
        for name,value in [('CurrentOAMOffset',logical),('RgOamPlayerStart',0),('RgOamFirst',first),('RgOamRotation',0)]:m[l(name)]=value
        c.pc=start;c.a,c.x,c.y,c.p,c.sp=85,73,19,flags,249;c.processorCycles=0;m.writes=[]
        for _ in range(100):
            if c.pc==stop:break
            c.step()
        else:raise AssertionError('Arithmetic helper failed to terminate')
        physical=(logical-first)&255;rotation=(-first)&255
        expected_V=64 if (physical^rotation)&(physical^logical)&128 else 0
        assert(c.x,c.y,c.p&64,c.sp,m[l('CurrentOAMOffset')],m[l('RgOamRotation')],m[l('RgOamFirst')])==(physical,0,expected_V,249,logical,0,first),(logical,first,flags)
        assert c.p&12==flags&12
        assert set(at for at,v in m.writes)<={l('CurrentOAMOffset'),l('RgOamRotation')}
        count+=1;minimum=min(minimum,c.processorCycles);maximum=max(maximum,c.processorCycles)
    return dict(cases=count,domain='All256 logical end bytes ×all256 original phase bytes ×4physical flag contexts; p0 representative of the post-ADC logical sum. Nonzero p decompositions additionally covered by full callers.',helper_cycle_range=[minimum,maximum],original_final_SBC_V_physical_X_and_logical_cursor_exact=True,source_helper_C_N_Z_not_an_external_ABI='Its continuation consumes no C/N/Z before original PLA/LDA/CMP overwrites them; full DrawAll AXYP is independently exact.')


def nmi(b):
    l=lambda n:address(b,n)
    owned=['CurrentOAMOffset','RgOamPlayerStart','RgOamRotation','RgOamFirst','RgOamUsed','GuestOamRotationActive']
    smc=[l(n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[l('FarcallJmpTarget_SMC')+2]
    rows=[]
    for variant,first in itertools.product([0,1],[0,112]):
        cfg=dict(entry='DrawAllMetasprites',variant=variant,types=[1,1,1,1],first=first,flags=0x20)
        c,m,before=fixture.setup(b,cfg);m[l('NmiDisable')]=255
        for _ in range(100000):
            if c.pc==l('MmBodyPriorityExit'):break
            c.step()
        else:raise AssertionError('No actual exit helper reached')
        for index in range(100):
            if c.pc==l('MmBodyPriorityRosterTail'):break
            # Copy the genuine current instruction boundary, including its
            # transient old rotation. No renderer ownership field is seeded.
            q=ReadBus(b,bytes(m[:0x8000]))
            for slot,bank in enumerate(m.banks):q.page(slot,bank)
            q.watch={l(name)for name in owned}
            snapshot=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),tuple(m[at]for at in smc),tuple(m[l(n)]for n in owned),m[l('CurrentBank')],m[l('CurrentBankC')])
            d=NesMPU(memory=q,pc=c.pc);d.a,d.x,d.y,d.p,d.sp=c.a,c.x,c.y,c.p,c.sp;q.cpu=d;q.writes=[];q.watched_reads=[]
            d.nmi()
            for steps in range(100000):
                if d.pc==snapshot[0]and d.sp==snapshot[5]:break
                d.step()
            else:raise AssertionError(('NMI timeout',variant,index))
            reads=q.watched_reads[:];q.watch=set()
            after=(d.pc,d.a,d.x,d.y,d.p&207,d.sp,tuple(q.banks),tuple(q[at]for at in smc),tuple(q[l(n)]for n in owned),q[l('CurrentBank')],q[l('CurrentBankC')])
            assert after==snapshot,('True lag NMI changed render contract',variant,first,index,snapshot,after)
            assert not reads,('NMI read transient allocation state',variant,first,index,reads)
            assert all(at!=0x4014 and not 0x200<=at<0x300 for at,value in q.writes)
            assert q[l('NmiSkipped')]==(m[l('NmiSkipped')]+1)&255
            rows.append(dict(variant=variant,first=first,pc=c.pc,registers=list(snapshot[:6]),owned_state=list(snapshot[8]),NMI_steps=steps,APU_stores=sum(0x4000<=at<=0x4017 or 0x5000<=at<=0x5015 for at,v in q.writes)))
            c.step()
        else:raise AssertionError('Exit helper exceeds finite range')
    return rows


def pressure(b,cfg):
    c,m,t,meta=fixture.run(b,cfg)
    # Last writer owns a record, preserving clipped/hidden and exact physical
    # order. This is Y eligibility only; it is not an opaque pixel emulator.
    owner={}
    for row in meta['OAM_writes']:
        owner[(row['address']-0x200)//4]=row['phase']
    result=collections.Counter();max_body=0;worst=[]
    for line in range(240):
        eligible=[i for i in range(64)if m[0x200+4*i]<240 and m[0x200+4*i]+1<=line<=m[0x200+4*i]+16]
        selected=eligible[:8]
        body=[i for i in eligible if owner.get(i)=='body']
        max_body=max(max_body,len(body))
        for typ in ['body','ordinary','special','world']:
            demand=sum(owner.get(i)==typ for i in eligible);admitted=sum(owner.get(i)==typ for i in selected)
            result[typ+'_eligible_part_rows']+=demand;result[typ+'_selected_part_rows']+=admitted
        if len(eligible)>8:worst.append(dict(line=line,eligible=len(eligible),body=len(body),first8=[dict(slot=i,owner=owner.get(i))for i in selected]))
    return dict(counts=dict(result),maximum_body_parts_on_one_row=max_body,overflow_rows=len(worst),example_rows=worst[:2])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['parent','candidate','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
    try:
        old,new=[scoped_load(q)for q in[a.parent,a.candidate]]
        for variant,mask,first,world,fireowners,hidden in itertools.product([0,1],[0,1,7,15],[0,112],[0,6],[0,6],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,types=[mask>>i&1 for i in range(4)],first=first,world=world,fireowners=fireowners,fireparts=12,hidden=hidden,flags=0x61)
            c,m,_,meta=fixture.run(old,cfg);d,n,_,extra=fixture.run(new,cfg)
            excluded=set(range(0x100,0x300))|{address(old,name)for name in['RgOamRotation','GuestOamRotationActive']}
            differences=[(at,m[at],n[at])for at in range(0x8000)if at not in excluded and m[at]!=n[at]]
            assert not differences,('Unexpected owned RAM delta',cfg,differences[:10])
            assert(c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks))==(d.a,d.x,d.y,d.p&207,d.sp,tuple(n.banks))
            rows.append(dict(cfg=cfg,cycle_delta=d.processorCycles-c.processorCycles))
        geometry=[]
        for variant,kind in itertools.product([0,1],['four-busters','crowded-firebars']):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,types=[1,1,1,1],first=112,world=6 if kind=='crowded-firebars'else 0,fireowners=6 if kind=='crowded-firebars'else 0,fireparts=12,flags=0x20)
            geometry.append(dict(variant=variant,kind=kind,cfg=cfg,parent=pressure(old,cfg),candidate=pressure(new,cfg)))
        arith=arithmetic(new);nm=nmi(new)
        proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),whole_owned_RAM_cases=len(rows),only_intentional_guest_owner_and_rotation_fields_plus_physical_OAM=True,complete_AXYP_SP_banks_SMC_exact=True,arithmetic=arith,actual_lag_NMI_cases=len(nm),NMI_no_allocation_reads_and_exact_register_stack_bank_5SMC_renderer_state_restore=True,source_geometry=geometry,limits='Source geometric eight-sprite admission only. Body priority can starve world/projectile parts; no opaque RGB, actual publication fairness or native cadence claim. True lag-NMI CPU controls are not physical PPU validation.',checker_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');(a.output/'cases.json').write_text(json.dumps(dict(owned_RAM=rows,NMI=nm),separators=(',',':'))+'\n');print(json.dumps(proof,indent=2))
    except BaseException as error:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(error),traceback=traceback.format_exc(),completed_owned_RAM=len(rows),checker_sha256=sha(__file__)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
