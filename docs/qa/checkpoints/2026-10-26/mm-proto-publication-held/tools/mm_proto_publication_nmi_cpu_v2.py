"""Full original NMI/owned audio acknowledgement differential, no native run."""
from pathlib import Path
import argparse, hashlib, itertools, json, traceback
from current3cee_postdma_mask_cpu_v4 import Bus, seed, app
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

STATE=0x5ff8
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FLAGS=[0x20|sum((n>>i&1)*v for i,v in enumerate([1,2,4,8,64,128])) for n in range(64)]

def run(b,spec,inject=None):
    char,variant,state,lag,p,sp,scene=spec
    q=seed(b,char,1,lag,0,0,0)
    q.put(ProtoVariant=variant,OperMode_Task=3,GameEngineSubroutine=8,MmDeathFlag=0)
    for name,value in scene.items():q.set(name,value)
    q.m[STATE]=state
    m=Bus(b,bytes(q.m[:0x8000]),(0xa5,0x5a));l=lambda n:address(b,n)
    m[l('CurrentBank')]=215;m[l('CurrentBankC')]=141
    smc=[l(n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[l('FarcallJmpTarget_SMC')+2]
    original_smc=[m[x]for x in smc]
    c=NesMPU(memory=m,pc=0x5b00);c.a,c.x,c.y,c.p,c.sp=0xa7,73,19,p,sp;m.cpu=c;c.nmi()
    m.writes=[];m.stamps=[];trace=[];irq_stores=[];core_entries=[]
    for index in range(100000):
        if c.pc==0x5b00 and c.sp==sp:break
        bank=m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if c.pc==l('ProtoNmiAudioCore') and bank==(location(b,'ProtoNmiAudioCore')-16)//8192:core_entries.append([index,c.processorCycles,c.sp])
        if index==inject:
            assert not c.p&4
            saved=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),app(m),[m[x]for x in smc])
            at=len(m.writes);c.irq()
            for _ in range(2000):
                if c.pc==saved[0]and c.sp==saved[5]:break
                c.step()
            else:raise AssertionError(('IRQ timeout',spec,inject))
            now=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),app(m),[m[x]for x in smc])
            assert now==saved,('IRQ state/SMC/banks',spec,inject)
            irq_stores=m.writes[at:];del m.writes[at:]
        trace.append([index,c.pc,bank,c.p,c.processorCycles]);c.step()
    else:raise AssertionError(('NMI timeout',spec,hex(c.pc),m.banks))
    assert(c.a,c.x,c.y,c.p&207,c.sp)==(0xa7,73,19,p&207,sp)
    assert[m[x]for x in smc]==original_smc
    assert m.serial==([0,0]if lag else[8,8])
    final=bytearray(app(m));state_index=256+(0x800-0x200)+(STATE-0x5c00);final[state_index]=0
    writes=[(at,v)for at,v in m.writes if not 0x100<=at<0x200 and at!=STATE]
    return dict(regs=[c.a,c.x,c.y,c.p&207,c.sp],ram=bytes(final),banks=m.banks[:],writes=writes,
                reads=m.palette_reads,serial=m.serial,state=m[STATE],cycles=c.processorCycles,
                trace=trace,core_entries=core_entries,IRQ_stores=irq_stores,
                state_stores=[(at,v)for at,v in m.writes if at==STATE],
                APU=[(at,v)for at,v in m.writes if 0x4000<=at<=0x4015])

def expected(spec):
    char,variant,state,lag,p,sp,scene=spec
    if char!=1 or lag or not state&128 or scene.get("OperMode",1)==0:return state
    valid=all(scene.get(n,d)==d for n,d in [('OperMode',1),('OperMode_Task',3),('GameEngineSubroutine',8),('MmDeathFlag',0)])
    return state^192 if valid else 0

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['parent','candidate','output']:ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[];irq=[]
    old,new=[scoped_load(p)for p in[a.parent,a.candidate]]
    try:
        def check(kind,spec):
            left,right=[run(b,spec)for b in[old,new]]
            for field in ['regs','ram','banks','writes','reads','serial','APU']:
                assert left[field]==right[field],('Original NMI outcome',kind,spec,field,
                    [(i,x,y)for i,(x,y)in enumerate(zip(left[field],right[field]))if x!=y][:12])
            assert bool(right['core_entries'])==(spec[0]==1 and spec[6].get('OperMode',1)!=0)
            assert left['state']==spec[2] and right['state']==expected(spec),('Acknowledged state',spec,left['state'],right['state'],expected(spec))
            assert bool(right['state_stores'])==(expected(spec)!=spec[2])
            rows.append(dict(kind=kind,spec=spec,delta=right['cycles']-left['cycles'],parent_cycles=left['cycles'],candidate_cycles=right['cycles'],old_state=spec[2],new_state=right['state'],APU_stores=len(right['APU']),core_entries=right['core_entries']))
            return right
        for variant,state,lag,p,sp in itertools.product([0,1],[0,64,128,192],[0,1],FLAGS,[253,192]):
            check('owned_all64physical_flags_both_stack_depths',(1,variant,state,lag,p,sp,{}))
        for char,lag,state in itertools.product([i for i in range(20)if i!=1],[0,1],[0,192]):
            check('foreign_original_full_NMI',(char,0,state,lag,0x71,253,{}))
        for variant,state,lag,scene in itertools.product([0,1],[128,192],[0,1],[{'OperMode':0},{'OperMode_Task':2},{'GameEngineSubroutine':7},{'MmDeathFlag':1}]):
            check('real_scene_death_guards',(1,variant,state,lag,0x61,253,scene))
        for variant,state,lag in itertools.product([0,1],[0,64,128,192],[0,1]):
            spec=(1,variant,state,lag,0x20,253,{})
            ref=run(new,spec);seen=set();lo=address(new,'MmPublicationAudioCore')
            for index,pc,bank,p,clock in ref['trace']:
                if bank!=66 or not lo<=pc<0xbb50 or pc in seen or p&4:continue
                seen.add(pc);r=run(new,spec,index)
                for field in ['regs','ram','banks','writes','reads','serial','APU','state']:
                    assert r[field]==ref[field],('Whole IRQ outcome',spec,index,pc,field)
                irq.append(dict(spec=spec,index=index,PC=pc,bank=bank,full_state_exact=True))
        groups={k:dict(cases=len(v:=[r for r in rows if r['kind']==k]),cycle_delta=[min(r['delta']for r in v),max(r['delta']for r in v)])for k in sorted({r['kind']for r in rows})}
        assert groups['foreign_original_full_NMI']['cycle_delta']==[0,0]
        (a.output/'cases.json').write_text(json.dumps(dict(cases=rows,IRQ=irq),separators=(',',':'))+'\n')
        proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),complete_NMI_cases=len(rows),actual_IRQ_cases=len(irq),groups=groups,
                   original_full_AXYP_SP_application_RAM_5SMC_banks_input_APU_and_other_ordered_writes_exact=True,
                   only_new_lifecycle_byte=STATE,foreign_full_NMI_cycles_exact=True,original_stack_dead_writes_excluded=True,
                   physical_status_mask=207,IRQ_note='Only virtual B/U excluded at RTI boundary; all six physical condition/control flags compared.',
                   acknowledgement='Only a pending bit7 at genuine regular outer AudioUpdate return E3FC, with live scene1/task3/engine8/death0, consumes bit6 via XOR C0. Lag, no-pending, foreign, and original OperMode0 vanilla-audio routes do not consume; scene reset is separately owned by MoveAllSpritesOffscreen.',
                   limits='Assembled complete source NMI/IRQ only. No physical DMA/PPU/DMC timing, displayed fairness, or cadence claim.',checker_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
    except BaseException as e:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),completed=len(rows),IRQ_completed=len(irq)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise

if __name__=='__main__':main()
