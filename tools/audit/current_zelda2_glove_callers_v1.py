"""Finite whole GameLoop differential outside the intended Z2 Easy brick fix."""
from pathlib import Path
import hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_zelda2_earned_cpu_v1 import scene

R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))

def main():
    old=scoped_load(B/'roster-20261028-fixes.nes');new=scoped_load(B/'zelda2_easy_glove.nes');rows=[];injections=[]
    source=[(4,v,m,f,t)for v,m,f,t in itertools.product([0,1],[0,1],[1,2],[0,1,2])]
    source += [(c,0,m,1,1)for c,m in itertools.product([0,1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],[0,1])]
    for char,variant,mode,face,tier in source:
        outcomes=[];mask=set()
        for b in [old,new]:
            q=Arena(b,char);q.put(CrossoverBehaviorVersion=mode,Z2Variant=variant,PlayerStatus=tier,OperMode_Task=3,AreaType=1);scene(q);q.set('PlayerFacingDir',face);q.array('GameTimerDisplay',[3,9,9])
            end=address(b,'E_GroundArea2')-1;assert b['raw'][location(b,'E_GroundArea2')-1]==255;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
            saved=NesMPU.step
            def step(c):
                if b is new and c.pc==address(new,'EasyWhipEligible::Link')and q.m.banks[(c.pc-32768)//8192]==22:
                    mask.update([256+c.sp,256+(c.sp-1)%256])
                saved(c)
            NesMPU.step=step
            try:
                states=[];cycles=0
                for bits in [0]*4+[64]*2+[0]*10:
                    q.put(SavedJoypadBits=bits,SavedJoypad1Bits=bits);c,_=q.invoke('GameLoop');states.append((c.a,c.x,c.y,c.p&0xcf,c.sp));cycles+=c.processorCycles
                outcomes.append((q,states,cycles))
            finally:NesMPU.step=saved
        (a,sa,ca),(z,sz,cz)=outcomes
        assert sa==sz,('Full GameLoop AXYP/SP',char,variant,mode,face,tier)
        diff=[at for at in range(0x8000)if a.m[at]!=z.m[at]and at not in mask]
        assert not diff,('Only exact helper-return dead stack bytes differ',char,variant,mode,face,tier,diff[:12])
        assert all(at<0x1fc for at in mask),'Original active caller return/lower live stack is not masked'
        rows.append(dict(character=char,variant=variant,mode=mode,face=face,tier=tier,actual_GameLoops=16,full_AXYP_SP_application_RAM_exact=True,exact_extra_dead_stack=sorted(mask),cycles_old=ca,cycles_new=cz,delta=cz-ca))
    # Repeat genuine interrupt return checks with all five executable SMC
    # operands explicitly captured, separate from the complete source suite.
    fields=[address(new,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(new,'FarcallJmpTarget_SMC')+2]
    for variant,which in itertools.product([0,1],['NMI','IRQ']):
        q=Arena(new,4);q.put(CrossoverBehaviorVersion=0,Z2Variant=variant,MmBulletType=14,NmiDisable=255,Sprite0HitDetectFlag=1)
        fired=False;saved=NesMPU.step
        def step(c):
            nonlocal fired
            if not fired and c.pc==address(new,'Z2LegacyEasyProbeType'):
                fired=True;before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),[q.m[a]for a in fields])
                if which=='NMI':c.nmi()
                else:c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(new,'IrqScrollSplit')
                for _ in range(20000):
                    saved(c)
                    if c.pc==before[5]and c.sp==before[4]:break
                else:raise AssertionError('Real RTI required')
                after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),[q.m[a]for a in fields]);assert before==after
            saved(c)
        NesMPU.step=step
        try:q.invoke('EasyWhipEligible')
        finally:NesMPU.step=saved
        assert fired;injections.append(dict(variant=variant,interrupt=which,AXYP_SP_actual_banks_and_5SMC_exact=True))
    basehard=json.loads((B/'current-ee115-zelda2-earned-source-v1-hard.json').read_text());fixedhard=json.loads((B/'zelda2_easy_glove_source_1.json').read_text());assert all(basehard[n]==fixedhard[n]for n in ['GameLoop_calls','rows','events','owner_counts'])
    out=B/'zelda2_easy_glove_callers.json';assert not out.exists();out.write_text(json.dumps(dict(passed=True,native_run=False,Lua_VM_executed=False,parent_sha256=sha(B/'roster-20261028-fixes.nes'),candidate_sha256=sha(B/'zelda2_easy_glove.nes'),full_caller_cases=rows,actual_GameLoops=sum(r['actual_GameLoops']for r in rows),interrupt_5SMC=injections,Hard_full_earned_campaign_rows_events_counts_exact=True,limitations='Typed CPU arenas, no native frame/poll/PPU/timing result. Differential covers no new brick target: actual intended Easy Glove fix and full progression are separate 2183-call campaigns.',bindings=[bind(p)for p in [Path(__file__),B/'zelda2_easy_glove_controls.json',B/'current-ee115-zelda2-earned-source-v1-hard.json',B/'zelda2_easy_glove_source_1.json']]),indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,proof=str(out),sha256=sha(out),cases=len(rows),GameLoops=sum(r['actual_GameLoops']for r in rows))))

if __name__=='__main__':main()
