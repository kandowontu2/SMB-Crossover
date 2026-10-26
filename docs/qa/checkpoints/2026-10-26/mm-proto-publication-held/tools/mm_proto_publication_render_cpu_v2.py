"""Independent unchanged731 emitters for both publication-priority partitions."""
from pathlib import Path
import argparse,hashlib,itertools,json,traceback
import mm_proto_body_priority_partition_v6 as prior
import mm_proto_shot_mux_cpu_v1 as base
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
STATE=0x5ff8


def setup(b,cfg):
    c,m,before=prior.setup(b,cfg)
    m[STATE]=cfg.get('display',0)
    m[address(b,'NmiDisable')]=255
    m.writes=[]
    return c,m,before


def owned(cfg):
    return (cfg.get('char',1)==1 and cfg.get('mode',1)==1 and cfg.get('task',3)==3 and cfg.get('engine',8)==8 and not cfg.get('dead') and not cfg.get('hidden') and not cfg.get('flip',0)&128)


def run(b,cfg,reference=False,irq=None):
    c,m,before=setup(b,cfg);l=lambda n:address(b,n)
    active=owned(cfg);shot=bool(cfg.get('display',0)&64)
    reserved=44 if cfg.get('variant') else 40
    ref_pre=l('DrawAllMetasprites')+0xf4;ref_post=l('DrawAllMetasprites')+0x110
    init=l('DrawAllMetasprites::InitObjectLoop');body=l('DrawMetasprite')
    trace=[];mutations=[];rows=[];phase='clear';clear=0;body_writes=[];irqwrites=[]
    for index in range(150000):
        if c.pc==0x7f00:break
        bank=m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        if reference and cfg.get('char',1)==1 and bank==4 and c.pc==ref_pre:
            if active:
                for n,v in [('GuestOamRotationActive',192 if shot else 128),('RgOamRotation',(-reserved)&255 if shot else 0),('CurrentOAMOffset',reserved)]:
                    mutations.append(dict(pc=c.pc,field=n,old=m[l(n)],new=v));m[l(n)]=v
            else:m[STATE]&=127
        if reference and active and bank==4 and c.pc==ref_post:
            count=m[l('CurrentOAMOffset')]-reserved;assert 0<=count<=255-reserved
            m[l('RgOamPlayerStart')]=count;m[l('RgOamRotation')]=0
            c.a=0;c.x=cfg.get('variant',0);c.pc=init
            mutations.append(dict(field='same_logical_capacity_world_partition',real_shot_bytes=count,reservation=reserved))
        if bank==4 and c.pc==body and c.y==0:
            if reference and active and not shot:m[l('CurrentOAMOffset')]=0
            phase='body'
        if reference and active and bank==4 and c.pc==l('DrawAllMetasprites::DoneDrawingPlayer'):
            logical=m[l('CurrentOAMOffset')]+(0 if shot else m[l('RgOamPlayerStart')]);assert logical<256
            first=m[l('RgOamFirst')];physical=(logical-first)&255;rot=(-first)&255
            overflow=bool((physical^rot)&(physical^logical)&128)
            m[l('CurrentOAMOffset')]=logical;c.x=physical;c.y=0;c.p=(c.p&~64)|(64 if overflow else 0)
            m[STATE]=192 if shot else 128
            mutations.append(dict(field='mathematical_original_return_and_completed_tag',logical=logical,physical=physical,V=overflow,tag=m[STATE]))
        if bank==4 and c.pc==init:phase='world'
        if bank==4 and c.pc==l('MegaManDrawShots'):phase='ordinary'
        if irq==index:
            from verify_native_relocation import NesMPU
            saved=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]))
            assert not c.p&4
            start=len(m.writes);c.irq()
            for _ in range(500):
                if c.pc==saved[0] and c.sp==saved[5]:break
                c.step()
            else:raise AssertionError(('IRQ failed',cfg,index))
            now=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]))
            assert now==saved,('IRQ state',cfg,index)
            irqwrites=m.writes[start:];del m.writes[start:]
        start=len(m.writes);trace.append((index,c.pc,bank,c.p));c.step()
        for at,v in m.writes[start:]:
            if 0x200<=at<0x300:
                rows.append(dict(phase=phase,address=at,value=v,pc=trace[-1][1],bank=bank))
                if phase=='body':body_writes.append((at,v))
                if phase=='clear' and (cfg.get('char',1)==1 or cfg.get('char',1)>=3):
                    clear+=1
                    if clear==64:phase='special'
    else:raise AssertionError(('DrawAll timeout',cfg,hex(c.pc)))
    assert c.sp==253
    for n,v in before.items():assert bytes(m[l(n):l(n)+4])==v,('Live ordinary shot altered',cfg,n)
    if active and (reference or "MmPublicationState" in b["syms"]):
        assert m[STATE]==(192 if shot else 128)
        assert m[l('GuestOamRotationActive')]==(192 if shot else 128) and m[l('RgOamRotation')]==0
        p=m[l('RgOamPlayerStart')]
        assert all((0x200+p<=at<0x200+p+reserved) if shot else (0x200<=at<0x200+reserved) for at,v in body_writes),('Body partition escaped',cfg,p,body_writes)
    return c,m,trace,dict(active=active,shot=shot,reserved=reserved,reference_mutations=mutations,body_writes=body_writes,OAM_writes=rows,IRQ=irqwrites)


def outcome(c,m,irq=False):return prior.outcome(c,m,irq)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','candidate','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[];irqs=[]
    old,new=[scoped_load(p) for p in [a.parent,a.candidate]]
    try:
        def check(tag,cfg):
            c,m,t,meta=run(old,cfg,True);d,n,u,extra=run(new,cfg)
            assert outcome(c,m)==outcome(d,n),('Independent reference',tag,cfg,(c.a,c.x,c.y,c.p),(d.a,d.x,d.y,d.p),[(hex(i),m[i],n[i]) for i in range(0x8000) if not 0x1c0<=i<0x200 and m[i]!=n[i]][:18])
            f,fm,_,plain=run(old,cfg)
            assert (f.a,f.x,f.y,f.p&207,f.sp)==(d.a,d.x,d.y,d.p&207,d.sp),('Original AXYP/SP',tag,cfg,(f.a,f.x,f.y,f.p&207,f.sp),(d.a,d.x,d.y,d.p&207,d.sp))
            assert [v for at,v in fm.writes if 0x200<=at<0x300]==[v for at,v in n.writes if 0x200<=at<0x300],('Original OAM count/values',tag,cfg)
            rows.append(dict(tag=tag,cfg=cfg,delta=d.processorCycles-f.processorCycles,parent_cycles=f.processorCycles,candidate_cycles=d.processorCycles,original_regs=[f.a,f.x,f.y,f.p&207,f.sp],pending=n[STATE],body_stores=len(extra['body_writes']),OAM_stores=len(extra['OAM_writes'])))
            return u
        for variant,display,mask,first,face in itertools.product([0,1],[0,64,128,192],range(16),[0,112],[1,2]):
            check('both_partitions_all_live_masks',dict(entry='DrawAllMetasprites',variant=variant,display=display,types=[mask>>i&1 for i in range(4)],first=first,face=face,flags=0x61))
        for char,flags in itertools.product([i for i in range(20) if i!=1],base.FLAGS):
            check('foreign_all64flags',dict(entry='DrawAllMetasprites',char=char,display=192,types=[1]*4,first=112,flags=flags))
        for variant,display,flags in itertools.product([0,1],[0,64],base.FLAGS):
            check('owned_all64flags',dict(entry='DrawAllMetasprites',variant=variant,display=display,types=[1,2,5,6],first=112,flags=flags))
        for variant,display,which in itertools.product([0,1],[128,192],range(6)):
            opt=[dict(mode=0),dict(task=2),dict(engine=7),dict(dead=1),dict(hidden=1),dict(flip=128)][which]
            check('lifecycle_ineligible_literal_mapping',dict(entry='DrawAllMetasprites',variant=variant,display=display,types=[1]*4,first=112,flags=0x61,**opt))
        for variant,display,owners,parts,world,special in itertools.product([0,1],[0,64],[1,6],[1,12],[0,23],[0,10]):
            check('crowded_capacity_firebars',dict(entry='DrawAllMetasprites',variant=variant,display=display,types=[1]*4,first=112,fireowners=owners,fireparts=parts,world=world,special=special,numbers=6,flags=0x61))
        for variant,display,pose,face,outlines,edge in itertools.product([0,1],[0,64],range(6),[1,2],[0,1],range(4)):
            x,y,h=[(112,176,1),(0,23,1),(255,239,1),(128,255,0)][edge]
            cfg=dict(entry='DrawAllMetasprites',variant=variant,display=display,types=[1,2,5,6],first=112,face=face,outlines=outlines,px=x,py=y,pyhigh=h,flags=0x20)
            if variant:cfg['proto_pose']=pose
            else:cfg['pose']=['METASPRITE_MM_HAIR_STAND','METASPRITE_MM_HAIR_WALK1','METASPRITE_MM_HAIR_WALK2','METASPRITE_MM_HAIR_JUMP','METASPRITE_MM_HAIR_SHOOT','METASPRITE_MM_HAIR_STAND'][pose]
            check('actual_poses_faces_edges_outlines',cfg)
        for variant,display in itertools.product([0,1],[0,64]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,display=display,types=[1]*4,first=112,special=10,flags=0x20)
            c,m,t,extra=run(new,cfg);expected=outcome(c,m,True);seen=set()
            for index,pc,bank,p in t:
                if bank!=4 or pc in seen or p&4 or not (0xa000<=pc<0xa155 or 0xa1b0<=pc<0xa2b0 or address(new,'MmBodyPriorityBegin')<=pc<address(new,'MmBodyPriorityFinish')+40 or 0xbf33<=pc<0xbf8b):continue
                seen.add(pc);d,n,_,info=run(new,cfg,irq=index)
                assert outcome(d,n,True)==expected,('IRQ complete outcome',cfg,index,pc)
                irqs.append(dict(cfg=cfg,index=index,pc=pc,exact=True))
        groups={tag:dict(cases=len(v:=[x for x in rows if x['tag']==tag]),cycle_delta=[min(x['delta'] for x in v),max(x['delta'] for x in v)]) for tag in sorted({r['tag'] for r in rows})}
        assert groups['foreign_all64flags']['cycle_delta'][1]<=0,groups['foreign_all64flags']
        proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),cases=len(rows),grouped=groups,actual_IRQ_cases=len(irqs),independent_two_partition_reference=True,complete_original_AXYP_SP_and_ordered_OAM_values_counts_exact=True,complete_independent_reference_RAM_banks_SMC_and_hardware_exact=True,foreign_no_positive_render_cycle_delta=True,new_state_only=STATE,limits='Synthetic source rendering only. LogicalR reservation/capacity retained on both turns. No physical first8/pixels/publication/cadence/natural all-weapon/death or native fairness claim.',checker_sha256=sha(__file__))
        (a.output/'cases.json').write_text(json.dumps(dict(cases=rows,IRQ=irqs),separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
    except BaseException as e:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),completed_cases=len(rows),completed_IRQ=len(irqs),tool_sha256=sha(__file__)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
