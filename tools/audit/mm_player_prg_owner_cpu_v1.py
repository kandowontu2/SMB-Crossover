"""Finite dynamic-player bank/full-render/IRQ/source-arsenal controls; no native."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import traceback

R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
import mm_proto_body_priority_partition_v6 as fixture
import current_mega_arsenal_prepare_v1 as arsenal
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OLD=B/'bill_early_cache.nes';NEW=B/'mm_player_prg_owner.nes'
EXPECTED='8fd3f3766486c9d6093c1ebe0cff92b6ff3a35c84829f448c5cbc32b93abbffc'
FLAGS=[0x20|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)]


def outcome(c,m):
    return c.a,c.x,c.y,c.p,c.sp,bytes(m[:0x8000]),tuple(m.banks),tuple(m.writes)


def run(b,cfg,reference=False,irq=None):
    c,m,before=fixture.setup(b,cfg);at=lambda n:address(b,n)
    if cfg.get('mega_pose'):
        ptr=at(cfg['mega_pose'])
        for n,v in dict(ObjectMetasprite=at('METASPRITE_SAMUS_BODY'),SmPosePtr=ptr&255,SmChrBank=170).items():m[at(n)]=v
        m[at('SmPosePtr')+1]=ptr>>8
    if cfg.get('entry')=='DrawMetasprite':
        c.x=at('METASPRITE_SAMUS_BODY');c.y=cfg.get('object',0)
        ptr=at(cfg.get('mega_pose','SsMegaFISTRight'))
        m[at('HpNativeDrawLo')+c.y]=ptr&255;m[at('HpNativeDrawHi')+c.y]=ptr>>8
        m.page(2,cfg.get('cbank',12));m[at('CurrentBankC')]=m.banks[2]|128
    m.writes=[];trace=[];body=False;bodywrites=[];renders=[];mutations=0
    for index in range(160000):
        if c.pc==0x7f00:break
        bank=m.banks[(c.pc-32768)//8192]if c.pc>=32768 else-1
        if bank==4 and c.pc==at('DrawMetasprite')and c.y==0:body=True
        if bank==4 and c.pc==at('DrawAllMetasprites::DoneDrawingPlayer'):body=False
        if reference and bank==4 and c.pc==at('HpNativePointerEnd')-5 and c.y==0 and m[at('SelectedCharacter')]==1:
            owner=(location(b,'ProtoArtBegin'if m[at('ProtoVariant')]else'SsMegaTHROWRight')-16)//8192
            # Explicit reference intervention, not an executed native proof:
            # source's real indirect player pointer must own its actual bank.
            m[at('CurrentBankC')]=owner|128;m[0x5116]=owner|128;mutations+=1
        if bank==4 and c.pc==at('MetaspriteRenderLoop')and(body or cfg.get('entry')=='DrawMetasprite'):
            ptr=m[at('R0')]+256*m[at('R1')];renders.append(dict(pointer=ptr,header=m[ptr],bank=m.banks[2],offset=m[at('CurrentOAMOffset')]))
        if irq==index:
            saved=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]))
            assert not c.p&4;start=len(m.writes);c.irq()
            for _ in range(500):
                if c.pc==saved[0]and c.sp==saved[5]:break
                c.step()
            else:raise AssertionError('Actual IRQ return timeout')
            restored=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]))
            assert saved==restored,('IRQ state damage',cfg,index,hex(saved[0]))
            assert all(at in [0x2005,0x2006,0x5128,0x5130]or 0x100<=at<0x200 for at,v in m.writes[start:])
            del m.writes[start:]
        trace.append((index,c.pc,bank));start=len(m.writes);c.step()
        if body or cfg.get('entry')=='DrawMetasprite':bodywrites.extend((at,v)for at,v in m.writes[start:]if 0x200<=at<0x300)
    else:raise AssertionError(('Full draw timeout',cfg,hex(c.pc)))
    assert c.sp==253
    for n,v in before.items():assert bytes(m[at(n):at(n)+4])==v,('Live projectile changed',cfg,n)
    if m[at('GuestOamRotationActive')]in [128,129]and bodywrites:
        reserve=44 if cfg.get('variant',0)else 40
        assert all(0<=p-512<reserve for p,v in bodywrites),('Body exceeded reserved physical budget',cfg,bodywrites)
    return c,m,trace,dict(renders=renders,body_stores=len(bodywrites),reference_publications=mutations)


def campaigns(b):
    prior=arsenal.Arena.invoke;rows=[];active=False;body=False;counts={}
    def invoke(q,name,*args,**kwargs):
        nonlocal body
        if name!='GameLoop':return prior(q,name,*args,**kwargs)
        step0=NesMPU.step;body=False
        def step(c):
            nonlocal body
            k=q.m.banks[(c.pc-32768)//8192]if c.pc>=32768 else-1
            if k==4 and c.pc==address(b,'DrawMetasprite')and c.y==0:body=True
            if k==4 and c.pc==address(b,'DrawAllMetasprites::DoneDrawingPlayer'):body=False
            if body and k==4 and c.pc==address(b,'MetaspriteRenderLoop')and q.get('ObjectMetasprite')==address(b,'METASPRITE_SAMUS_BODY'):
                want=(location(b,'ProtoArtBegin'if q.get('ProtoVariant')else'SsMegaTHROWRight')-16)//8192
                ptr=q.get('R0')+256*q.get('R1');h=q.m[ptr]
                assert q.m.banks[2]==want and q.get('CurrentBankC')==want|128,('Actual player renderer lost owner',q.get('ProtoVariant'),hex(ptr),q.m.banks[2])
                assert h and h%4==0 and h<=(44 if q.get('ProtoVariant')else 40),('Actual body record capacity',h)
                key=f'{q.get("ProtoVariant")}:{h}:{want}';counts[key]=counts.get(key,0)+1
            step0(c)
        NesMPU.step=step
        try:return prior(q,name,*args,**kwargs)
        finally:NesMPU.step=step0
    arsenal.Arena.invoke=invoke
    try:
        for var in [0,1]:
            proof=arsenal.campaign(b,var);assert proof['passed']
            rows.append(dict(variant=var,full_GameLoop_calls=proof['complete_GameLoop_calls'],component_rows=len(proof['rows'])if'rows'in proof else len(proof.get('cases',[]))))
    finally:arsenal.Arena.invoke=prior
    return dict(campaigns=rows,actual_dynamic_player_render_counts=counts)


def main():
    result=dict(passed=False,source_only=True,native_run=False)
    output=B/'mm_player_prg_owner_controls.json';assert not output.exists()
    try:
        assert sha(NEW)==EXPECTED;old,new=scoped_load(OLD),scoped_load(NEW);rows=[];irqs=[]
        mega=[f'SsMega{pose}{face}'for pose in ['THROW','AIR_THROW','FIST','AIR_FIST','CARRY','CARRY_STEP','CARRY_WALK1','CARRY_WALK2','CARRY_WALK3','CARRY_JUMP']for face in ['Left','Right']]
        records=[dict(name=n,pointer=address(new,n),bank=(location(new,n)-16)//8192,length=new['raw'][location(new,n)])for n in mega]
        assert {r['bank']for r in records}=={33}and{r['length']for r in records}=={28,32,36}
        def check(tag,cfg,repair):
            c,m,_,r=run(old,cfg,reference=repair);d,n,t,s=run(new,cfg)
            assert outcome(c,m)==outcome(d,n),(tag,cfg,(c.a,c.x,c.y,c.p),(d.a,d.x,d.y,d.p),[(hex(i),m[i],n[i])for i in range(32768)if m[i]!=n[i]][:20])
            rows.append(dict(tag=tag,cfg=cfg,delta_vs_correct_bank_reference=d.processorCycles-c.processorCycles,renders=s['renders'],body_stores=s['body_stores']))
            return t,s
        for pose,phase,outline in itertools.product(mega,[0,1],[0,1]):
            check('Mega_all20_special_records_both_turns',dict(entry='DrawAllMetasprites',char=1,variant=0,mega_pose=pose,types=[1]*4,shuffle=phase,world=3,numbers=2,outlines=outline,flags=0x61),True)
        for pose,phase in itertools.product([0,1,2,3,8,12,16,17,18,19,20,21],[0,1]):
            check('Proto_actual_source_pose_both_turns',dict(entry='DrawAllMetasprites',char=1,variant=1,proto_pose=pose,types=[1]*4,shuffle=phase,world=3,numbers=2,flags=0x61),True)
        for var,phase,flags in itertools.product([0,1],[0,1],FLAGS):
            check('all64_flags_real_full_draw',dict(entry='DrawAllMetasprites',char=1,variant=var,mega_pose='SsMegaFISTRight'if not var else None,proto_pose=16 if var else None,types=[1,2,3,6],shuffle=phase,flags=flags),True)
        for char in [c for c in range(20)if c!=1]:
            for phase in [0,1]:
                check('foreign_normal_complete_draw',dict(entry='DrawAllMetasprites',char=char,variant=0,types=[1]*4,shuffle=phase,world=3,flags=0x61),False)
        for var,phase in itertools.product([0,1],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',char=1,variant=var,mega_pose='SsMegaFISTRight'if not var else None,proto_pose=16 if var else None,types=[1,2,3,6],shuffle=phase,special=6,drops=4,numbers=6,world=6,fireowners=6,fireparts=12,flags=0x61)
            check('crowded_capacity_firebars_and_drops',cfg,True)
        for char,obj,offset in itertools.product([0,1,2,3,19],[0,1,6],[0,40,216,220,252]):
            check('direct_dynamic_pointer_full_body_caller',dict(entry='DrawMetasprite',char=char,variant=0,mega_pose='SsMegaFISTRight',object=obj,types=[0]*4,offset=offset,flags=0xe1,cbank=12),char==1 and obj==0)
        cfg=dict(entry='DrawAllMetasprites',char=1,variant=1,proto_pose=16,types=[1,2,3,6],shuffle=0,world=3,numbers=2,flags=0x61)
        c,m,t,s=run(new,cfg);helper=address(new,'MmDynamicPlayerPrgOwner');size=int(new['syms']['MmDynamicPlayerPrgOwner']['size'],0);seen=set()
        for idx,pc,bank in t:
            if bank==4 and helper<=pc<helper+size and pc not in seen:
                seen.add(pc);run(new,cfg,irq=idx);irqs.append(dict(pc=pc,index=idx))
        result.update(passed=True,parent_sha256=sha(OLD),candidate_sha256=sha(NEW),cases=len(rows),actual_IRQ_boundaries=len(irqs),Mega_immutable_record_capacity=records,
                      comparisons='Complete AXYP/SP, entire64KiB-lower application/stack image, all ordered writes, final physical banks. Owned reference explicitly publishes the real source player bank at original taken5NOP point; all other compiled parent instructions execute unchanged.',
                      group_costs={tag:dict(cases=len(z:=[r for r in rows if r['tag']==tag]),min_delta=min(r['delta_vs_correct_bank_reference']for r in z),max_delta=max(r['delta_vs_correct_bank_reference']for r in z))for tag in sorted({r['tag']for r in rows})},rows=rows,IRQ=irqs)
        result['actual_arsenal_source_campaigns']=campaigns(new)
    except Exception as e:
        result.update(error=repr(e),traceback=traceback.format_exc());output.write_text(json.dumps(result,indent=2)+'\n');raise
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ['rows','Mega_immutable_record_capacity','IRQ']}))


if __name__=='__main__':main()
