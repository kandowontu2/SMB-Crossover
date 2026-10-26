"""Real IRQ boundaries and icon-tail flag liveness for the private scan gate."""
from pathlib import Path
import argparse
import json
from check_tmnt_render_oa import load, address
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, sha
from tmnt_native_storage_irq_cpu import ordinary, registers
from tmnt_equipment_empty_scans_cpu_v1 import setup, execute, qualified_cache


def finish(c,m):
    for _ in range(30000):
        if c.pc==0x7f00:return
        c.step()
    raise AssertionError(('Final draw timeout',hex(c.pc)))


def result(c,m):
    excluded=set(range(0x1a0,0x200))|{0x2005,0x2006,0x5128,0x5130}
    return (registers(c),bytes(m[i] for i in range(0x8000) if i not in excluded),tuple(m.banks),
            tuple((at,v) for at,v in m.writes if 0x200<=at<0x300 or 0x2000<=at<0x5c00))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['baseline','candidate','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate)
    for b,path in [(old,a.baseline),(new,a.candidate)]:qualified_cache[id(b)]=qualified(path)
    tail=address(new,'TnEquipmentIconResume');helper=address(new,'TnSkipEmptyEquipmentScans')
    end=next(int(s['start'],0)+int(s['size'],0) for s in new['segs'].values() if s.get('name')=='"TMNT_CORE"')
    assert helper==0xb020 and end<=0xb080
    irq_rows=[];irq_hardware=set();maxdepth=0
    configs=[dict(shots=[(0,73,2),(1,74,2),(2,75,2)],flags=0x20),
             dict(shots=[(0,73,2)],drops=[(2,1)],flags=0xe9),
             dict(shots=[(0,73,2)],pickups=[(3,4,19,0xb4,0x2e,128,1)],flags=0x69)]
    for cfg in configs:
        c,m=setup(new,cfg);m[0x5204]=128;m.writes=[]
        trace=[]
        for index in range(30000):
            if c.pc==0x7f00:break
            if m.banks[1]==87 and helper<=c.pc<end:trace.append((index,c.pc,c.x))
            c.step()
        else:raise AssertionError('Reference draw timeout')
        expected=result(c,m)
        for at,pc,x in trace:
            d,n=setup(new,cfg);n[0x5204]=128;n.writes=[]
            for index in range(30000):
                if d.pc==0x7f00:break
                if index==at:
                    state=registers(d),ordinary(n),tuple(n.banks)
                    assert not d.p&4
                    start=len(n.writes);d.irq();assert d.pc==0x8000
                    depth=d.sp
                    for _ in range(300):
                        if d.pc==state[0][0] and d.sp==state[0][-1]:break
                        depth=min(depth,d.sp);d.step()
                    else:raise AssertionError(('IRQ return timeout',hex(pc)))
                    assert (registers(d),ordinary(n),tuple(n.banks))==state
                    hw=[(k,v) for k,v in n.writes[start:] if 0x2000<=k<0x6000]
                    assert hw and all(k in [0x2005,0x2006,0x5128,0x5130] for k,v in hw)
                    irq_hardware.update(k for k,v in hw);maxdepth=max(maxdepth,255-depth)
                    # Remove only the explicitly observed IRQ log segment; no
                    # emulated memory/register is restored or rewritten.
                    del n.writes[start:]
                d.step()
            else:raise AssertionError('Interrupted draw timeout')
            assert result(d,n)==expected,('IRQ changed complete draw result',cfg,hex(pc),x)
            irq_rows.append(dict(cfg=cfg,helper_pc=pc,shot_index=x))
    # At the actual icon-tail boundary A and C/N/Z may differ. Its LDA kills
    # A/N/Z and every route overwrites C before use. X/Y, V/D/I, scratch/RAM,
    # bank/stack and ordered final output remain exact, including gear=0.
    tails=[]
    flags=[0x20|(i&15)|((i&16)<<2)|((i&32)<<2) for i in range(64)]
    for flags_in in flags:
        for gear in [0,1]:
            for queue in [0,78,255]:
                cfg=dict(shots=[(0,73,2)],seed={'TnGearSelected':gear},flags=flags_in,queue=queue,hud_ammo=98)
                c,m,_,_=execute(old,cfg,tail);d,n,_,_=execute(new,cfg,tail)
                assert (c.pc,c.x,c.y,c.p&0x4c,c.sp,ordinary(m),tuple(m.banks))==(d.pc,d.x,d.y,d.p&0x4c,d.sp,ordinary(n),tuple(n.banks))
                before=[c.a,c.p&0xcf];after=[d.a,d.p&0xcf]
                finish(c,m);finish(d,n)
                assert result(c,m)==result(d,n)
                tails.append(dict(flags=flags_in,gear=gear,queue=queue,baseline_ACNZ=before,candidate_ACNZ=after))
    proof=dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
        actual_compiled_IRQ_injections=len(irq_rows),maximum_stack_depth=maxdepth,IRQ_hardware_writes=sorted(irq_hardware),
        full_draw_final_IRQ_result_exact=True,IRQ_memory_exceptions_only_discarded_stack_and_actual_IRQ_hardware_cells=True,
        icon_tail_cases=len(tails),icon_tail_XY_VDI_SP_PC_scratch_ordinaryRAM_banks_exact=True,
        dead_A_CNZ_difference_permitted_only_before_real_original_tail=True,complete_tail_final_ABI_exact=True,
        checker_sha256=sha(Path(__file__)),limits='CPU executes actual vector/IRQ/RTI at helper boundaries; no PPU clock, real NMI scheduling, DMA or native draw-cadence claim. IRQ log segment alone is removed from comparison; emulated state is never restored.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    (a.output/'cases.json').write_text(json.dumps(dict(irq=irq_rows,tail=tails),separators=(',',':'))+'\n')
    print(json.dumps(proof))


if __name__=='__main__':main()
