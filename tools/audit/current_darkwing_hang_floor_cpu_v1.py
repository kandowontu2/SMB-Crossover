"""Actual compiled hang/carry/full-GameLoop controls; no native/route claim."""
from pathlib import Path
import hashlib,itertools,json
from current_darkwing_arrow_route_source_v1 import scene,world
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'build'
OLD=BUILD/'kirby-mike-polish-production.nes';NEW=BUILD/'darkwing_hang_floor.nes'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
KINDS=['stable','stable-jump-through','falling-free','falling-floor','bad-type','bad-actor-ID','bad-actor-tag','absent-actor','fresh-jump','fresh-drop','released-delay','scrooge']

def setup(b,kind='stable',face=1):
    q=scene(b);end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
    px=721 if face==1 else 769;sx=740 if face==1 else 780;ay=185 if kind=='falling-floor'else 160
    q.put(Player_X_Position=px&255,Player_PageLoc=px>>8,MmOldX=px&255,Player_Y_Position=176 if kind=='falling-floor'else ay-3,Player_State=0 if kind=='falling-floor'else 1,PlayerFacingDir=face,Player_MovingDir=face,DwPrevious=face,SavedJoypadBits=face,DwHang=136,DwGas=1,DwAdaptor=2,DwMode=1,NmiDisable=255)
    q.array('MmVX',[0,0,0]);q.array('MmVY',[0,0,0])
    for n,v in dict(RgShotType=6,RgShotDir=face,RgShotX=sx&255,RgShotPage=sx>>8,RgShotY=ay-2 if kind=='falling-floor'else ay,RgShotAge=0 if kind.startswith('falling')else 200,RgShotImpact=5,SsMode=int(kind.startswith('falling')),RgShotVYLo=191,RgShotVYHi=1).items():q.set(n,v,8)
    state=168 if kind in ['falling-floor','stable-jump-through']else 40
    for n,v in dict(Enemy_Flag=1,Enemy_ID=38,Enemy_State=state,Enemy_X_Position=(sx-12)&255,Enemy_PageLoc=(sx-12)>>8,Enemy_Y_Position=ay,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=4,Enemy_Y_MoveForce=128,Enemy_Y_Speed=1,PlatformCollisionFlag=255).items():q.set(n,v,4)
    if kind=='bad-type':q.set('RgShotType',5,8)
    if kind=='bad-actor-ID':q.set('Enemy_ID',37,4)
    if kind=='bad-actor-tag':q.set('Enemy_State',39,4)
    if kind=='absent-actor':q.set('Enemy_Flag',0,4)
    if kind=='fresh-jump':q.put(ScFresh=128,SavedJoypadBits=128|face)
    if kind=='fresh-drop':q.put(ScFresh=4,SavedJoypadBits=4|face)
    if kind=='released-delay':q.put(DwHang=8)
    if kind=='scrooge':q.put(DarkwingVariant=0,DwHang=0)
    # Keep the actual RAM SMC code in page1 intact. Compare the entire lower
    # region after the call; it is not scratch available for a canary.
    return q

def invoke(q,name,flags=0x20,interrupt_at=None,interrupt_kind=None):
    b=q.b;pc=address(b,name);bank=(location(b,name)-16)//8192;window=(pc-32768)//8192
    q.m.page(window,bank)
    if window in [1,2]:q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
    q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,7,3,flags,253
    if name=='GameLoop':c.a=c.x=c.y=0
    c.stPushWord(0x5aff)
    ticks=0;trace=[];irq_result=None;injected=False
    smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
    for _ in range(160000):
        if c.pc==0x5b00:break
        k=q.m.banks[(c.pc-32768)//8192]if c.pc>=32768 else-1
        if not injected and interrupt_at==(c.pc,k):
            injected=True
            saved=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(q.m.banks),[q.m[i]for i in smc],q.get('CurrentBank'),q.get('CurrentBankC'))
            if interrupt_kind=='IRQ':assert not c.p&4;c.irq()
            else:c.nmi()
            for count in range(60000):
                if c.pc==saved[0]and c.sp==saved[5]:break
                c.step()
            else:raise AssertionError(('actual interrupt timeout',interrupt_kind,hex(c.pc)))
            after=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(q.m.banks),[q.m[i]for i in smc],q.get('CurrentBank'),q.get('CurrentBankC'))
            assert saved==after,('actual ISR return/5SMC/banks',interrupt_kind,saved,after)
            irq_result=dict(kind=interrupt_kind,pc=saved[0],bank=k,instructions=count+1,AXYP_SP_mapper_shadow_5SMC_exact=True,virtual_B_U_only_excluded_from_interrupted_py65_P=True)
        trace.append((c.pc,k));start=len(q.m.writes);c.step();ticks+=1
    else:raise AssertionError(('full caller timeout',name,hex(c.pc)))
    assert c.sp==253
    return c,trace,irq_result

def state(c,q):return(c.a,c.x,c.y,c.p,c.sp,tuple(q.m.banks),bytes(q.m[:32768]))

def compare(old,new,kind,face,entry,flags):
    qa,qb=setup(old,kind,face),setup(new,kind,face)
    ca,ta,_=invoke(qa,entry,flags);cb,tb,_=invoke(qb,entry,flags)
    x,y=state(ca,qa),state(cb,qb);d=[i for i,(a,b)in enumerate(zip(x[-1],y[-1]))if a!=b]
    # Page1 below180 is application/SMC storage, not dead stack.
    stack=[i for i in d if 0x180<=i<512];nonstack=[i for i in d if i not in stack]
    assert bytes(qa.m[0x180:0x1c0])==bytes(qb.m[0x180:0x1c0]),('lower live stack',kind,entry)
    if kind!='falling-floor':
        assert x[:6]==y[:6]and not nonstack,(kind,face,entry,flags,x[:6],y[:6],[(hex(i),qa.m[i],qb.m[i])for i in nonstack[:20]])
        assert [(a,v)for a,v in qa.m.writes if not 0x180<=a<512]==[(a,v)for a,v in qb.m.writes if not 0x180<=a<512],('ordered nonstack writes',kind,entry)
    else:
        assert qb.get('DwHang')==8 and qb.get('Player_Y_Position')<=176 and qa.get('DwHang')==136
        if entry=='GameLoop':assert world(qa)==735 if face==1 else world(qa)==783
        assert abs(world(qb)-(721 if face==1 else 769))<=2
        # Independent actor lifetime/equipment are not erased by releasing hang.
        assert qa.get('DwGas')==qb.get('DwGas')==1 and qa.get('DwAdaptor')==qb.get('DwAdaptor')==2
        for n in ['RgShotType','RgShotAge','SsMode','RgShotX','RgShotPage','RgShotY']:
            assert qa.get(n,8)==qb.get(n,8),('Arrow owner mutated by release',n)
    return dict(kind=kind,face=face,entry=entry,flags=flags,old_cycles=ca.processorCycles,new_cycles=cb.processorCycles,delta=cb.processorCycles-ca.processorCycles,dead_return_stack_differences=stack,nonstack_differences=[dict(address=i,before=qa.m[i],after=qb.m[i])for i in nonstack],ending=dict(old=[world(qa),qa.get('Player_Y_Position'),qa.get('DwHang')],new=[world(qb),qb.get('Player_Y_Position'),qb.get('DwHang')])),tb

def actor_transition(b,face,terrain):
    q=setup(b,'falling-free',face);q.put(RgSlot=8)
    q.set('Enemy_Y_Position',185,4);q.set('RgShotY',183,8)
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    if terrain:
        x=q.get('RgShotX',8)+256*q.get('RgShotPage',8)
        q.set('Block_Buffer_1',84,x//256%2*208+(185-32)//16*16+x%256//16)
    q.invoke('DwArrowActor',x=8)
    floor_disabled=bool(q.get('Enemy_State',4)&128)
    assert floor_disabled==terrain
    invoke(q,'DwScroogePhysics')
    assert(q.get('DwHang')==8)==terrain
    return dict(face=face,solid_below=terrain,actor_release_bit=floor_disabled,hang_after=q.get('DwHang'),actor_preserved=q.get('Enemy_Flag',4)==1)

def main():
    receipt=json.loads((BUILD/'darkwing_hang_floor_build.json').read_text());assert sha(OLD)==receipt['parent_sha256']and sha(NEW)==receipt['candidate_sha256']
    old,new=scoped_load(OLD),scoped_load(NEW);rows=[];seams=[]
    for kind,face,entry,flags in itertools.product(KINDS,[1,2],['DwScroogePhysics','GameLoop'],[0x20,0x61]):
        row,trace=compare(old,new,kind,face,entry,flags);rows.append(row)
    transitions=[actor_transition(new,face,terrain)for face,terrain in itertools.product([1,2],[False,True])]
    # Every genuine new helper instruction receives both actual IRQ and lagNMI.
    for kind in ['stable','falling-free','falling-floor','bad-actor-ID']:
        q=setup(new,kind);_,trace,_=invoke(q,'DwScroogePhysics')
        pcs=sorted(set((pc,k)for pc,k in trace if address(new,'DwValidateHang')<=pc<address(new,'DwValidateHang')+19 and k==67))
        for pc,which in itertools.product(pcs,['IRQ','NMI-lag']):
            q=setup(new,kind);c,tr,proof=invoke(q,'DwScroogePhysics',interrupt_at=pc,interrupt_kind=which);assert proof
            if kind=='falling-floor':assert q.get('DwHang')==8 and q.get('Player_Y_Position')<=176
            seams.append(dict(case=kind,**proof))
    output=BUILD/'darkwing_hang_floor_controls.json';assert not output.exists()
    z=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(OLD),candidate_ROM_sha256=sha(NEW),cases=len(rows),rows=rows,actual_ArrowActor_terrain_then_full_physics=transitions,actual_interrupt_seams=seams,
        stack='Lower actual stack180..1BF exact; page1below180 remains applicationRAM/SMC and is compared. Only enumerated returned dead call-stack bytes differ, never a broad page1/application-RAM exclusion.',
        affected_case='Observed native hang/Arrow fields plus a fully typed legal floor/pipe environment; actual complete GameLoop reproduces parent721->735/Y182 and candidate721/Y176/released8. Missing native RAM is disclosed typed setup, not a raw savestate replay.',
        control_limits='Actual source CPU only; no native/graphics/campaign/cadence proof. IRQ31 and lagNMI restore real AXYP/SP/banks/shadows/5SMC, not a new whole-NMI timing certification. Source native acquisition and controller remain separately unqualified.',
        bindings={str(p):sha(p)for p in [Path(__file__).resolve(),OLD,OLD.with_suffix('.dbg'),NEW,NEW.with_suffix('.dbg'),BUILD/'darkwing_hang_floor_build.json',ROOT/'tools/audit/current_darkwing_arrow_route_source_v1.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py']})
    output.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,cases=len(rows),interrupts=len(seams),path=str(output),sha256=sha(output),deltas=sorted(set(r['delta']for r in rows)))))

if __name__=='__main__':main()
