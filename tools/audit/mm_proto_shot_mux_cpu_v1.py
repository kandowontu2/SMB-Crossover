"""Exact original filtered-render oracle and unchanged live projectile state."""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU

R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIELDS=['MmBulletType','MmBulletX','MmBulletPage','MmBulletY','MmBulletFracLo','MmBulletFracHi','MmBulletDir','MmBulletAge']
FLAGS=[0x20|(n&15)|((n&16)<<2)|((n&32)<<2)for n in range(64)]

def chosen(cfg):
    alive=[i for i in range(3,-1,-1)if cfg['types'][i]]
    if not alive:return None
    phase=cfg.get('frame',0)%3 if len(alive)==3 else cfg.get('frame',0)&3
    return alive[phase%len(alive)]

def setup(b,cfg,filtered=False):
    m=Memory(b);entry=cfg.get('entry','ProtoLegacyDrawShotsCold');bank=(location(b,entry)-16)//8192
    window=(address(b,entry)-0x8000)//8192;m.page(window,bank);m.page(2,12)
    def put(n,v,i=0):m[address(b,n)+i]=v&255
    for i in range(256):m[0x200+i]=(i*73+29)&255
    seed=dict(CurrentBank=m.banks[1]|128,CurrentBankC=140,SelectedCharacter=cfg.get('char',1),ProtoVariant=cfg.get('variant',0),
              MmDeathFlag=cfg.get('dead',0),MmDeathAge=1,MmDeathY=128,MmDeathYHigh=1,OperMode=1,GameEngineSubroutine=8,
              FrameCounter=cfg.get('frame',0),PlayerFacingDir=cfg.get('face',1),Player_X_Position=112,Player_Rel_XPos=112,Player_PageLoc=0,
              Player_Y_Position=176,Player_Y_HighPos=1,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,
              CurrentOAMOffset=cfg.get('offset',0),GuestOamRotationActive=cfg.get('rotate',1),RgOamRotation=cfg.get('rotation',0),
              ObjectMetasprite=address(b,'METASPRITE_MM_HAIR_WALK3'),SmChrBank=0,PlayerOutlinesOff=1)
    for n,v in seed.items():put(n,v)
    pick=chosen(cfg)
    for i,t in enumerate(cfg['types']):
        put('MmBulletType',t if not filtered or i==pick else 0,i)
        for n,v in dict(MmBulletX=cfg.get('x',128)+i*16,MmBulletPage=cfg.get('page',0),MmBulletY=cfg.get('y',192),
                        MmBulletFracLo=i*13,MmBulletFracHi=i*17,MmBulletDir=cfg.get('face',1),MmBulletAge=cfg.get('age',1)).items():put(n,v,i)
    if cfg.get('variant')and entry=='DrawAllMetasprites':
        # Actual source pose publication before the complete DrawAll caller.
        pc=address(b,'ProtoSetPose');m.page(1,(location(b,'ProtoSetPose')-16)//8192);put('CurrentBank',m.banks[1]|128)
        c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,3,7,0x20,253;c.stPushWord(0x7eff)
        for _ in range(10000):
            if c.pc==0x7f00:break
            c.step()
        else:raise AssertionError('Proto pose setup timeout')
        m.page(window,bank)
        if window==1:put('CurrentBank',bank|128)
    m[0x5204]=128
    c=NesMPU(memory=m,pc=address(b,entry));c.a,c.x,c.y,c.p,c.sp=85,3,7,cfg.get('flags',0x60),253;c.stPushWord(0x7eff);m.writes=[]
    before={n:bytes(m[address(b,n):address(b,n)+4])for n in FIELDS}
    return c,m,before

def run(b,cfg,filtered=False,irq=None):
    c,m,before=setup(b,cfg,filtered);trace=[];irqs=[]
    for index in range(100000):
        if c.pc==0x7f00:break
        if irq==index:
            state=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]),tuple(m.banks));assert not c.p&4
            first=len(m.writes);c.irq();assert c.pc==0x8000
            for _ in range(300):
                if c.pc==state[0]and c.sp==state[5]:break
                c.step()
            else:raise AssertionError(('IRQ return timeout',cfg,index))
            assert(c.pc,c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]),tuple(m.banks))==state,('IRQ damage',cfg,index)
            irqs=m.writes[first:];assert all(at in [0x2005,0x2006,0x5128,0x5130]or 0x100<=at<0x200 for at,v in irqs),irqs
            del m.writes[first:]
        trace.append((index,c.pc,m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1));c.step()
    else:raise AssertionError(('Render timeout',cfg,hex(c.pc),m.banks))
    assert c.sp==253
    for n,v in before.items():assert bytes(m[address(b,n):address(b,n)+4])==v,('Render changed live projectile',cfg,n)
    return c,m,trace,irqs

def outcome(b,c,m,cfg,normalize=False,irq=False):
    ram=bytearray(m[:0x8000])
    if normalize:
        for i,v in enumerate(cfg['types']):ram[address(b,'MmBulletType')+i]=v
    if irq:
        for at in [0x2005,0x2006,0x5128,0x5130]:ram[at]=0
    return(c.a,c.x,c.y,c.p&207,c.sp,bytes(ram[:0x1c0]+ram[0x200:]),tuple(m.banks),tuple((at,v)for at,v in m.writes if 0x200<=at<0x300 or 0x2000<=at<0x5c00))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--quick',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=scoped_load(a.parent),scoped_load(a.candidate);rows=[];irqs=[]
    def check(tag,cfg,foreign=False):
        c,m,_,_=run(old,cfg,filtered=not foreign);d,n,trace,_=run(new,cfg)
        left=outcome(old,c,m,cfg,normalize=not foreign);right=outcome(new,d,n,cfg)
        assert left==right,(tag,cfg,left[:5],right[:5],[(hex(i),m[i],n[i])for i in range(0x8000)if not 0x1c0<=i<0x200 and m[i]!=n[i]][:16])
        f,fm,_,_=run(old,cfg)
        if foreign or not any(cfg['types']):assert f.processorCycles==d.processorCycles,(tag,'Unchanged path slowed',cfg)
        rows.append(dict(tag=tag,cfg=cfg,pick=chosen(cfg),baseline_full_cycles=f.processorCycles,candidate_cycles=d.processorCycles,delta=d.processorCycles-f.processorCycles,
                         original_OAM_stores=sum(0x200<=at<0x300 for at,v in fm.writes),candidate_OAM_stores=sum(0x200<=at<0x300 for at,v in n.writes)))
        return d,n,trace
    for mask,frame in itertools.product(range(16),range(256)if not a.quick else range(4)):
        check('all_masks_phase',dict(types=[1 if mask>>i&1 else 0 for i in range(4)],frame=frame,flags=FLAGS[frame%64]))
    for typ,face,mask,edge in itertools.product(range(1,7),[1,2],[1,3,7,15],range(8)if not a.quick else[0]):
        x,y,off,rot=[(128,192,0,0),(0,24,240,252),(7,23,248,4),(255,255,252,128),(128,0,255,255),(8,32,16,0),(248,232,128,64),(128,192,1,4)][edge]
        check('all_types_art_edges',dict(types=[typ if mask>>i&1 else 0 for i in range(4)],frame=edge,face=face,x=x,y=y,offset=off,rotation=rot,age=edge*13,flags=FLAGS[(typ*8+edge)%64]))
    for char,var,flag in itertools.product([v for v in range(20)if v!=1],[0,1],FLAGS if not a.quick else[0x20]):
        check('foreign_exact',dict(entry='ProtoDrawShots',types=[1,1,1,1],char=char,variant=var,flags=flag),foreign=True)
    for entry,var,dead,mask,frame in itertools.product(['ProtoDrawShots','DrawAllMetasprites'],[0,1],[0,1],[0,1,3,7,15],[0,1,2,255]):
        cfg=dict(entry=entry,types=[1 if mask>>i&1 else 0 for i in range(4)],variant=var,dead=dead,frame=frame,flags=0x20)
        check('real_callers',cfg,foreign=bool(dead))
    # Every distinct helper boundary, including before/between the two deliberate
    # inner return-address PLA instructions, executes an actual IRQ/RTI.
    helper=address(new,'MmProtoShotMuxAdmission')
    for frame in [0,1]:
        cfg=dict(types=[1,1,1,0],frame=frame,flags=0x20)
        c,m,trace,_=run(new,cfg);expected=outcome(new,c,m,cfg,irq=True);seen=set()
        for index,pc,bank in trace:
            if bank!=66 or not helper<=pc<helper+200 or pc in seen:continue
            seen.add(pc);d,n,_,log=run(new,cfg,irq=index)
            assert outcome(new,d,n,cfg,irq=True)==expected,('IRQ changed complete draw',frame,index,hex(pc))
            irqs.append(dict(frame=frame,pc=pc,index=index))
    grouped={}
    for tag in sorted({r['tag']for r in rows}):
        rr=[r for r in rows if r['tag']==tag];deltas=[r['delta']for r in rr]
        grouped[tag]=dict(cases=len(rr),min_delta=min(deltas),max_delta=max(deltas),sum_delta=sum(deltas))
    result=dict(passed=True,source_only=True,native_run=False,quick=a.quick,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),
                cases=len(rows),grouped=grouped,actual_IRQ_cases=len(irqs),all_live_projectile_fields_unchanged=True,
                original_selected_shot_art_emitter_ordered_OAM_CHR_SMC_banks_and_complete_caller_ABI_exact=True,
                oracle='Original renderer with nonselected type slots absent BEFORE arranged renderer invocation; its four input type bytes are normalized back only in the comparison image. Candidate always keeps all original live fields untouched. No observed native state is altered.',
                no_new_RAM=True,foreign_and_owned_empty_cycles_exact=True,checker_sha256=sha(__file__),
                limits='Temporal fairness across source constructions only; skipped DMA publications may alias phases. No native visibility/cadence improvement or all-body/all-projectile fix claim. Owned single/live-source cost regressions remain measured.')
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');(a.output/'cases.json').write_text(json.dumps(dict(cases=rows,irq=irqs),separators=(',',':'))+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
