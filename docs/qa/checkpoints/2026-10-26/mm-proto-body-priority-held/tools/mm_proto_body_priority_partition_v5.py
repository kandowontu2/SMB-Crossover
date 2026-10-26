"""Independent allocation-first reference using unchanged clean731 emitters.

The reference is NOT the unmodified parent's contract: at its genuine pre-shot
boundary it reserves R physical bytes, and at the genuine post-shot boundary
it starts the unchanged world loop without adding R a second time. The rest
of the compiled parent emitter/caller runs unchanged. Every reference mutation
is logged; no candidate observations are used to calculate it.
"""
from pathlib import Path
import argparse, collections, hashlib, itertools, json, traceback
import mm_proto_body_priority_cpu_v1 as probe
import mm_proto_shot_mux_cpu_v1 as base
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def setup(b,cfg):
    c,m,before=base.setup(b,cfg)
    def put(n,v,i=0):m[address(b,n)+i]=v&255
    for n,v in dict(OperMode_Task=cfg.get('task',3),GameEngineSubroutine=cfg.get('engine',8),
                    OperMode=cfg.get('mode',1),RgOamFirst=cfg.get('first',0),
                    RgOamUsed=cfg.get('used',160),SpriteShuffleOffset=cfg.get('shuffle',0),
                    PlayerOutlinesOff=cfg.get('outlines',1),Player_X_Position=cfg.get('px',112),
                    Player_Y_Position=cfg.get('py',176),Player_Y_HighPos=cfg.get('pyhigh',1),
                    ObjectVerticalFlip=cfg.get('flip',0)).items():put(n,v)
    if cfg.get('variant') and cfg.get('proto_pose') is not None:
        target=address(b,'ProtoSetPose')
        bank=(location(b,'ProtoSetPose')-16)//8192
        m.page(1,bank);put('CurrentBank',bank|128)
        setter=NesMPU(memory=m,pc=target);setter.sp=253;setter.p=0x20;setter.x=cfg['proto_pose'];setter.stPushWord(0x7eff)
        for _ in range(1000):
            if setter.pc==0x7f00:break
            setter.step()
        else:raise AssertionError('Actual ProtoSetPose timeout')
        m.page(1,4);put('CurrentBank',132)
    if cfg.get('pose') and not cfg.get('variant'):
        put('ObjectMetasprite',address(b,cfg['pose']))
    if cfg.get('hidden'):
        put('ObjectMetasprite',0)
    for slot in range(1,cfg.get('world',0)+1):
        put('ObjectMetasprite',address(b,'METASPRITE_GOOMBA_WALKING_1'),slot)
        for n,v in [('SprObject_X_Position',96+slot*3),('SprObject_PageLoc',0),
                    ('SprObject_Y_Position',192),('SprObject_Y_HighPos',1),('PlayerFacingDir',1)]:put(n,v,slot)
    for slot in range(cfg.get('special',0)):
        for n,v in dict(RgShotType=cfg.get('specialtype',9),RgShotX=100+slot*4,
                        RgShotPage=0,RgShotY=176,RgShotYHigh=1,RgShotDir=1,SsArt=cfg.get('specialart',0)).items():put(n,v,slot)
    for slot in range(cfg.get('drops',0)):
        for n,v in dict(InvDropKind=1,InvDropX=96+slot*12,InvDropPage=0,InvDropY=176).items():put(n,v,slot)
    for slot in range(cfg.get('numbers',0)):
        for n,v in dict(FloateyNum_Control=1,FloateyNum_X_Pos=96+slot*12,FloateyNum_Y_Pos=176).items():put(n,v,slot)
    for slot in range(cfg.get('fireowners',0)):
        for n,v in dict(Enemy_Flag=1,Enemy_ID=0x1b,FirebarPartCount=cfg.get('fireparts',12)).items():put(n,v,slot)
        put('ObjectMetasprite',0,slot+1)
        for part in range(cfg.get('fireparts',12)):
            put('FirebarPartX',64+part*8,slot*12+part)
            put('FirebarPartY',[24,32,239,240][part%4]if cfg.get('fireedge')else 176,slot*12+part)
    if cfg.get('pose_pointer') is not None:
        # Explicit malformed/large-record controls, not a natural player pose.
        put('HpNativeDrawHi',0)
    m[0x5204]=128;m.writes=[]
    return c,m,before


def run(b,cfg,reference=False,irq=None):
    c,m,before=setup(b,cfg)
    l=lambda n:address(b,n)
    active=(cfg.get('char',1)==1 and cfg.get('mode',1)==1 and cfg.get('task',3)==3 and cfg.get('engine',8)==8 and not cfg.get('dead') and not cfg.get('hidden') and not cfg.get('flip',0)&128)
    reserved=44 if cfg.get('variant') else 40
    ref_pre=l('DrawAllMetasprites')+0xf4
    ref_post=l('DrawAllMetasprites')+0x110
    init=l('DrawAllMetasprites::InitObjectLoop')
    body=l('DrawMetasprite')
    trace=[];mutations=[];rows=[];phase='clear';clear_count=0;body_before=None;body_writes=[];newnonbody=[];irqlog=[]
    for index in range(150000):
        if c.pc==0x7f00:break
        bank=m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if reference and active and bank==4 and c.pc==ref_pre:
            # The source-owned whole-ring phase has already advanced once.
            assert m[l('GuestOamRotationActive')]==1
            for name,value in [('GuestOamRotationActive',128),('RgOamRotation',0),('CurrentOAMOffset',reserved)]:
                mutations.append(dict(pc=c.pc,field=name,before=m[l(name)],after=value));m[l(name)]=value
        if reference and active and bank==4 and c.pc==ref_post:
            count=m[l('CurrentOAMOffset')]-reserved
            assert 0<=count<=255-reserved
            mutations.append(dict(pc=c.pc,field='RgOamPlayerStart',before=m[l('RgOamPlayerStart')],after=count))
            m[l('RgOamPlayerStart')]=count
            c.a=count;c.x=cfg.get('variant',0)
            c.p=(c.p&~0xc3)|0x81|(2 if not count&128 else 0)
            c.pc=init
        if reference and active and bank==4 and c.pc==l('DrawAllMetasprites::DoneDrawingPlayer'):
            logical=m[l('CurrentOAMOffset')]+m[l('RgOamPlayerStart')]
            assert logical<256
            first=m[l('RgOamFirst')]
            physical=(logical-first)&255
            old_rotation=(-first)&255
            overflow=bool((physical^old_rotation)&(physical^logical)&128)
            mutations.append(dict(pc=c.pc,field='original_exit_contract',body_logical=m[l('CurrentOAMOffset')],shot_count=m[l('RgOamPlayerStart')],logical=logical,physical_X=physical,V=int(overflow)))
            m[l('CurrentOAMOffset')]=logical
            c.x=physical;c.y=0;c.p=(c.p&~64)|(64 if overflow else 0)
        if bank==4 and c.pc==body and c.y==0:
            assert body_before is None,('Repeated player draw',cfg)
            if reference and active:
                mutations.append(dict(pc=c.pc,field='CurrentOAMOffset',before=m[l('CurrentOAMOffset')],after=0))
                m[l('CurrentOAMOffset')]=0
            body_before=bytes(m[0x200:0x300]);phase='body'
        if bank==4 and c.pc==init:
            phase='world'
        # All pre-body nonclear writes must stay out of the allocated prefix.
        # The first64 clear writes are Y-only and intentionally touch allslots.
        if bank==4 and c.pc==l('MegaManDrawShots'):
            phase='ordinary'
        if irq==index:
            state=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]),tuple(m.banks))
            assert not c.p&4
            first=len(m.writes);c.irq();assert c.pc==0x8000
            for _ in range(300):
                if c.pc==state[0]and c.sp==state[5]:break
                c.step()
            else:raise AssertionError(('IRQ timeout',cfg,index))
            assert(c.pc,c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]),tuple(m.banks))==state,('IRQ damaged complete state',cfg,index)
            irqlog=m.writes[first:]
            assert all(at in [0x2005,0x2006,0x5128,0x5130]or 0x100<=at<0x200 for at,v in irqlog)
            del m.writes[first:]
        first=len(m.writes)
        trace.append((index,c.pc,bank,c.p))
        c.step()
        for at,value in m.writes[first:]:
            if 0x200<=at<0x300:
                row=dict(phase=phase,address=at,value=value,pc=trace[-1][1],bank=bank)
                rows.append(row)
                if phase=='body':body_writes.append((at,value))
                elif phase!='clear':newnonbody.append((at,value))
                elif bank==4 and 0xa02d<=trace[-1][1]<0xa0f4:
                    assert at%4==0 and value==248
                    clear_count+=1
                    if clear_count==64:phase='special'
    else:raise AssertionError(('Render timeout',cfg,hex(c.pc),m.banks))
    assert c.sp==253
    for name,value in before.items():assert bytes(m[l(name):l(name)+4])==value,('Live shot modified',name,cfg)
    if active and body_before is not None and m[l('GuestOamRotationActive')]==128:
        assert all(body_before[i]==248 for i in range(0,reserved,4)),('Nonbody overwrote body reservation',cfg)
        assert all(at>=0x200+reserved for at,v in newnonbody),('Nonbody store entered protected prefix',cfg,newnonbody)
        assert all(0x200<=at<0x200+reserved for at,v in body_writes),('Body escaped reservation',cfg,body_writes)
        assert m[l('RgOamRotation')]==0 and m[l('GuestOamRotationActive')]==128
    return c,m,trace,dict(active=active,reserved=reserved,reference_mutations=mutations,body_writes=body_writes,OAM_writes=rows,IRQ=irqlog)


def outcome(c,m,irq=False):
    ram=bytearray(m[:0x8000])
    if irq:
        for at in [0x2005,0x2006,0x5128,0x5130]:ram[at]=0
    return(c.a,c.x,c.y,c.p&207,c.sp,bytes(ram[:0x1c0]+ram[0x200:]),tuple(m.banks),tuple((at,v)for at,v in m.writes if 0x200<=at<0x300 or 0x2000<=at<0x5c00))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['parent','candidate','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=[scoped_load(q)for q in [a.parent,a.candidate]];rows=[];irqs=[]
    try:
        def check(tag,cfg):
            c,m,t,meta=run(old,cfg,reference=True)
            d,n,u,extra=run(new,cfg)
            assert outcome(c,m)==outcome(d,n),('Independent partition reference mismatch',tag,cfg,(c.a,c.x,c.y,c.p),(d.a,d.x,d.y,d.p),[(hex(i),m[i],n[i])for i in range(0x8000)if not 0x1c0<=i<0x200 and m[i]!=n[i]][:24])
            f,fm,_,plain=run(old,cfg)
            assert(f.a,f.x,f.y,f.p&207,f.sp)==(d.a,d.x,d.y,d.p&207,d.sp),('Unmodified parent ABI changed',tag,cfg,(f.a,f.x,f.y,f.p&207,f.sp),(d.a,d.x,d.y,d.p&207,d.sp))
            row=dict(tag=tag,cfg=cfg,baseline_cycles=f.processorCycles,candidate_cycles=d.processorCycles,delta=d.processorCycles-f.processorCycles,
                     parent_registers=[f.a,f.x,f.y,f.p&207,f.sp],candidate_registers=[d.a,d.x,d.y,d.p&207,d.sp],reference_mutations=meta['reference_mutations'],
                     baseline_body_parts=len(plain['body_writes'])//4,candidate_body_parts=len(extra['body_writes'])//4,
                     baseline_visible_parts=sum(fm[0x200+i*4]<240 for i in range(64)),candidate_visible_parts=sum(n[0x200+i*4]<240 for i in range(64)))
            rows.append(row)
            return u
        for variant,face,mask,first,flags in itertools.product([0,1],[1,2],range(16),[0,4,80,112,156],base.FLAGS[::8]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,face=face,types=[mask>>i&1 for i in range(4)],first=first,frame=mask&1,flags=flags)
            check('live_all_masks_phases_flags',cfg)
        for variant,mode,task,engine,dead in itertools.product([0,1],[0,1,2],[0,2,3],[0,8],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,types=[1,1,1,1],mode=mode,task=task,engine=engine,dead=dead,flags=0x61)
            check('lifecycle_literal_fallback',cfg)
        poses=['METASPRITE_MM_HAIR_STAND','METASPRITE_MM_HAIR_WALK1','METASPRITE_MM_HAIR_WALK2','METASPRITE_MM_HAIR_JUMP','METASPRITE_MM_HAIR_SHOOT']
        for variant,face,pose,outlines,edge in itertools.product([0,1],[1,2],poses,[0,1],range(8)):
            px,py,pyhigh=[(112,176,1),(0,24,1),(7,23,1),(255,255,1),(128,0,1),(8,32,1),(128,255,0),(128,0,2)][edge]
            cfg=dict(entry='DrawAllMetasprites',variant=variant,face=face,types=[1,2,3,4],pose=pose,proto_pose=poses.index(pose),outlines=outlines,px=px,py=py,pyhigh=pyhigh,first=edge*20,frame=edge,flags=0x20)
            check('poses_facing_clip_outline',cfg)
        for pose,face,outlines in itertools.product(range(27),[1,2],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',variant=1,proto_pose=pose,face=face,outlines=outlines,types=[1,2,5,6],first=112,flags=0x61)
            check('all27_actual_Proto_poses',cfg)
        for variant,special,drops,world,numbers,hidden in itertools.product([0,1],[0,5,10],[0,4],[0,6,23],[0,6],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,types=[1,1,1,1],special=special,drops=drops,world=world,numbers=numbers,hidden=hidden,first=112,flags=0x20)
            check('crowded_capacity',cfg)
        for variant,owners,parts,world,special,frame,edge in itertools.product([0,1],[1,3,6],[1,6,12],[0,6,23],[0,10],[0,1],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,types=[1,1,1,1],fireowners=owners,fireparts=parts,fireedge=edge,world=world,special=special,numbers=6,first=112,frame=frame,flags=0x61)
            check('crowded_firebar_bundle',cfg)
        # Genuine actual IRQ/RTI at every reached instruction boundary of
        # changed entry/helpers and real mode2 producer/body paths.
        for variant,dead in itertools.product([0,1],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,types=[1,1,1,1],first=112,dead=dead,flags=0x20)
            c,m,t,meta=run(new,cfg);expected=outcome(c,m,irq=True);seen=set()
            for index,pc,bank,pflags in t:
                if bank!=4 or pc in seen or pflags&4 or not (0xa000<=pc<0xa155 or address(new,'MmBodyPriorityBegin')<=pc<address(new,'MmBodyPriorityFinish')+40 or 0xbf33<=pc<0xbf50):continue
                seen.add(pc)
                d,n,_,extra=run(new,cfg,irq=index)
                assert outcome(d,n,irq=True)==expected,('IRQ final outcome',variant,dead,index,hex(pc))
                irqs.append(dict(variant=variant,dead=dead,index=index,pc=pc,stores=extra['IRQ']))
        grouped={tag:dict(cases=len(rr:=[r for r in rows if r['tag']==tag]),minimum_delta=min(r['delta']for r in rr),maximum_delta=max(r['delta']for r in rr))for tag in sorted(set(r['tag']for r in rows))}
        proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),cases=len(rows),grouped=grouped,actual_IRQ_cases=len(irqs),independent_partition_reference=__doc__,complete_reference_AXYP_SP_RAM_banks_SMC_ordered_OAM_and_hardware_exact=True,
                   ordinary_live_projectile_fields_preserved=True,body_prefix_never_written_by_nonbody_in_capacity_controls=True,
                   own_unmodified_function_AXYP_SP_exact=True,limits='Dense admission prioritizes body over world/shots; no hardware first8/opaque visibility/cadence/publication or natural reachability claim. The independent reference changes allocation and reconstructs original physical-X/final-SBC mathematically; every tested unmodified-parent register outcome is also separately exact.',checker_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
        (a.output/'cases.json').write_text(json.dumps(dict(cases=rows,IRQ=irqs),separators=(',',':'))+'\n')
        print(json.dumps(proof,indent=2))
    except BaseException as error:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(error),traceback=traceback.format_exc(),completed_cases=len(rows),completed_IRQ=len(irqs),checker_sha256=sha(__file__)),indent=2)+'\n')
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
