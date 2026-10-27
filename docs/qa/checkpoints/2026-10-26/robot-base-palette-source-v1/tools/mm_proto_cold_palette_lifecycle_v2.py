"""Actual selection/reset consumers and interrupt boundaries for the cold cache."""
from pathlib import Path
import argparse
import hashlib
import json
import traceback
from mm_proto_cold_palette_cpu_v1 import configured, invoke, application
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'root-current-roster-composition-v1';C=D/'robot-cold-palette-candidate-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def call(q,name,a=0,x=0,y=0):
    s=q.b['syms'][name];g=q.b['segs'][s['seg']];pc=address(q.b,name);w=(pc-0x8000)//8192;bn=(int(g['ooffs'],0)-16)//8192
    q.m.page(w,bn)
    if w in[1,2]:q.set('CurrentBank'if w==1 else'CurrentBankC',bn|128)
    q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,0x30,0xfd;c.stPushWord(0x5aff)
    for _ in range(100000):
        if c.pc==0x5b00:break
        c.step()
    else:raise AssertionError(('call timeout',name,hex(c.pc)))
    assert c.sp==0xfd;return c


def with_interrupt(q,target=None,kind='irq',reference_pre=False):
    name='X5LegacyGetPlayerColors';b=q.b;g=b['segs'][b['syms'][name]['seg']];bn=(int(g['ooffs'],0)-16)//8192;q.m.page(1,bn);q.set('CurrentBank',bn|128)
    c=NesMPU(memory=q.m,pc=address(b,name));c.a,c.x,c.y,c.p,c.sp=0x5a,37,19,0x30,0xfd;c.stPushWord(0x5aff)
    smc=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
    boundaries=[];injected=False
    for _ in range(100000):
        if c.pc==0x5b00:break
        if not injected and(reference_pre or c.pc==target):
            before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc);owners=(q.m.banks[:],q.get('CurrentBank'),q.get('CurrentBankC'),[q.m[i]for i in smc])
            c.nmi()if kind=='nmi'else c.irq()
            for _ in range(100000):
                if(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc)==before:break
                c.step()
            else:raise AssertionError(('interrupt return timeout',kind,before,hex(c.pc)))
            assert owners==(q.m.banks[:],q.get('CurrentBank'),q.get('CurrentBankC'),[q.m[i]for i in smc])
            injected=True
        if 0xab60<=c.pc<0xaba7:boundaries.append(c.pc)
        c.step()
    else:raise AssertionError(('producer timeout',kind,hex(c.pc)))
    assert c.sp==0xfd
    return c,boundaries,injected


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    lifecycles=[];interrupts=[]
    try:
        bs=[scoped_load(P/'candidate.nes'),scoped_load(C/'candidate.nes')]
        for char,variant in[(1,0),(1,1),(9,0)]:
            qs=[configured(b,char,variant=variant,engine=8,selected=1,cache=2)for b in bs]
            # Real selection commit, including SpecialClear, must preserve the
            # legitimate next-default palette refresh despite stale Mm cache.
            for q in qs:
                q.set('MmLastPalette',1);call(q,'InventorySelectionCommit',a=0,x=char)
                assert q.get('SsLastPalette')==0 and q.get('InvSelected',char)==0
                call(q,'SpecialPalette');assert q.get('SsLastPalette')==1 and q.get('MmLastPalette')==0
            assert application(qs[0])==application(qs[1])
            lifecycles.append(dict(char=char,variant=variant,real_selection_commit_and_SpecialClear=True,default_refresh_preserved=True))
            for death in[0,1]:
                qs=[configured(b,char,variant=variant,cache=7)for b in bs]
                for q in qs:
                    q.set('MmDeathFlag',death);call(q,'SpecialClear');assert q.get('SsLastPalette')==0
                    call(q,'GetPlayerColors');call(q,'MegaManPaletteState')
                    q.set('GameEngineSubroutine',8);call(q,'SpecialPalette');call(q,'MegaManPaletteState')
                # Both logical cache values converge; intended queue reduction
                # remains the same cold-reentry event, never a lost selection.
                assert qs[0].get('SsLastPalette')==qs[1].get('SsLastPalette')==1
                assert qs[0].get('MmLastPalette')==qs[1].get('MmLastPalette')
                assert qs[0].get('VRAM_Buffer1_Offset')==50 and qs[1].get('VRAM_Buffer1_Offset')==25
                lifecycles.append(dict(char=char,variant=variant,death_flag=death,real_SpecialClear_then_cold_reentry=True,logical_cache_converges=True))
        b=bs[1]
        for engine in[0,8]:
            q=configured(b,1,variant=1,engine=engine);reference,boundaries,_=with_interrupt(q)
            qr=configured(b,1,variant=1,engine=engine);cr,_,_=with_interrupt(qr,kind='irq',reference_pre=True)
            expected=application(qr);regs=(cr.a,cr.x,cr.y,cr.p&0xcf,cr.sp)
            qn=configured(b,1,variant=1,engine=engine);cn,_,_=with_interrupt(qn,kind='nmi',reference_pre=True)
            expected_nmi=application(qn);nregs=(cn.a,cn.x,cn.y,cn.p&0xcf,cn.sp)
            for pc in sorted(set(boundaries)):
                for kind in['irq','nmi']:
                    test=configured(b,1,variant=1,engine=engine);cpu,_,done=with_interrupt(test,pc,kind)
                    assert done
                    assert(cpu.a,cpu.x,cpu.y,cpu.p&0xcf,cpu.sp)==(regs if kind=='irq'else nregs)
                    assert application(test)==(expected if kind=='irq'else expected_nmi),('Full interrupted state',engine,kind,hex(pc))
                    interrupts.append(dict(engine=engine,kind=kind,PC=pc,full_return_application_state_exact=True,banks_and_five_SMC_restored=True))
        put(a.output/'lifecycle-cases.json',lifecycles);put(a.output/'interrupt-cases.json',interrupts)
        put(a.output/'proof.json',dict(passed=True,native_run=False,actual_selection_and_reset_cases=len(lifecycles),
            actual_IRQ_cases=sum(x['kind']=='irq'for x in interrupts),actual_lag_NMI_cases=sum(x['kind']=='nmi'for x in interrupts),
            cold_and_warm_actual_helper_instruction_boundaries=True,all_return_AXY_physicalP_SP_application_RAM_banks_five_SMC_exact=True,
            physical_status_mask=207,status_note='Only virtual B/U excluded after actual interrupt RTI; N,V,D,I,Z,C exact. No RAM/OAM masks.',
            IRQ_model='Reference also executes one genuineIRQ before producer, including its realPPUADDR/scroll IO; no comparison to a nonexistent noIRQ hardware state.',NMI_model='Real lag NMI withNmiDisable255. Full final state compared to sameproducer with one genuine lag NMI before entry; no omitted audio effects or synthetic empty ISR.',
            lifecycle_sha256=sha(a.output/'lifecycle-cases.json'),interrupts_sha256=sha(a.output/'interrupt-cases.json'),tool_sha256=sha(__file__),
            limits='Source CPU only, no native scheduling/visual recovery claim. Configured actual selection/reset/producer routes, not a full death/area playthrough.'))
        print((a.output/'proof.json').read_text())
    except BaseException as e:
        put(a.output/'failure.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc(),completed_lifecycle=len(lifecycles),completed_interrupts=len(interrupts)))
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
