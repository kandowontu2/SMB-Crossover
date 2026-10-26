"""Complete new-emitter callers, exact hardware store order and real IRQ."""
from pathlib import Path
from collections import Counter
import argparse
import itertools
import json
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from tmnt_equipment_empty_scans_cpu_v1 import setup,execute,outcome,qualified_cache
from tmnt_equipment_empty_scans_irq_v1 import result
from tmnt_native_storage_irq_cpu import ordinary,registers
from tmnt_native_storage_driver import ROOT,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate)
    for b,path in[(old,a.baseline),(new,a.candidate)]:qualified_cache[id(b)]=qualified(path)
    flags=[32|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)];rows=[]
    # Full legal actual private callers, queue/ammo updates and all four icons.
    for entry,equipment,variant,offset,rotation,flag in itertools.product(['TnDraw','TnDrawDispatch'],range(1,5),range(4),[0,48,240,252],[0,128],flags):
        cfg=dict(entry=entry,equipment=equipment,variant=variant,offset=offset,rotation=rotation,flags=flag,
            ammo=99,hud_ammo=98,shots=[(0,73,2),(1,74,2),(2,75,2)])
        c,m,_,_=execute(old,cfg);d,n,_,_=execute(new,cfg)
        assert outcome(c,m)==outcome(d,n),('Whole actual draw caller',cfg)
        rows.append(dict(cfg=cfg,delta=d.processorCycles-c.processorCycles))
    ranges=[(address(new,n),address(new,n)+int(new['syms'][n]['size'],0))for n in['TnExactIconRender','TnExactShurikenRender']if n in new['syms']]
    assert ranges and ranges[0][0]==0xb700 and max(hi for lo,hi in ranges)<=0xc000
    # The admission span remains exactly54B and real RenderActors is unchanged.
    start=qualified(a.candidate)['TnDrawEquipment','RenderActors']-54;ranges+=[(start,start+54)]
    configs=[]
    for equipment in range(1,5):
        configs += [dict(equipment=equipment,flags=0x20),dict(equipment=equipment,offset=240,rotation=128,flags=0xe9)]
    for pose,face in itertools.product(range(73,76),[1,2]):
        configs.append(dict(shots=[(1,pose,2)],face=face,flags=0x20))
    configs += [dict(shots=[(1,60,3)],flags=0xe9),dict(shots=[(1,73,2)],x=7,flags=0x20),
        dict(shots=[(1,73,2)],page=1,flags=0x20),dict(shots=[(1,73,2)],y=23,flags=0xe9),
        dict(seed={'TnGearSelected':0},flags=0x20),dict(seed={'TnGearSelected':0},drops=[(2,1)],flags=0xe9)]
    irq_rows=[];maxdepth=0;caller_entries=Counter()
    for cfg in configs:
        c,m=setup(new,cfg);m[0x5204]=128;m.writes=[];trace=[]
        for index in range(30000):
            if c.pc==0x7f00:break
            if m.banks[1]==87 and any(lo<=c.pc<hi for lo,hi in ranges):trace.append((index,c.pc))
            if c.pc in[lo for lo,hi in ranges[:-1]]and m.banks[1]==87:
                assert m.banks[2]==88 and m[address(new,'R3')]==0 and m[address(new,'R7')]==1
                if c.pc==ranges[0][0]:
                    assert [m[address(new,k)]for k in['R4','R5','R6']]==[128,0,23]
                caller_entries[c.pc]+=1
            c.step()
        else:raise AssertionError('Emitter IRQ reference timeout')
        expected=result(c,m)
        for index_at,pc in trace:
            d,n=setup(new,cfg);n[0x5204]=128;n.writes=[]
            for index in range(30000):
                if d.pc==0x7f00:break
                if index==index_at:
                    before=registers(d),ordinary(n),tuple(n.banks)
                    assert not d.p&4;first=len(n.writes);d.irq();assert d.pc==0x8000;minimum=d.sp
                    for _ in range(300):
                        if d.pc==before[0][0]and d.sp==before[0][-1]:break
                        minimum=min(minimum,d.sp);d.step()
                    else:raise AssertionError(('Actual IRQ did not return',hex(pc)))
                    assert(registers(d),ordinary(n),tuple(n.banks))==before
                    hw=[(at,v)for at,v in n.writes[first:]if not 0x100<=at<0x200]
                    assert hw==[(0x2006,0),(0x5128,0),(0x2005,32),(0x2005,0),(0x2006,128)]
                    maxdepth=max(maxdepth,255-minimum)
                    # Only the independently exact IRQ log segment is removed;
                    # no emulated state/register/mapper value is restored.
                    del n.writes[first:]
                d.step()
            else:raise AssertionError('Interrupted renderer timeout')
            assert result(d,n)==expected,('Full render changed after real IRQ',cfg,hex(pc))
            irq_rows.append(dict(cfg=cfg,PC=pc))
    representative=[]
    for equipment,pose,rotation in itertools.product(range(1,5),range(73,76),[0,128]):
        cfg=dict(equipment=equipment,shots=[(1,pose,2)],ammo=98,hud_ammo=98,rotation=rotation)
        c,m,_,_=execute(old,cfg);d,n,_,_=execute(new,cfg);assert outcome(c,m)==outcome(d,n)
        representative.append(dict(equipment=equipment,pose=pose,rotation=rotation,baseline_cycles=c.processorCycles,
            candidate_cycles=d.processorCycles,delta=d.processorCycles-c.processorCycles))
    (a.output/'cases.json').write_text(json.dumps(dict(callers=rows,IRQ=irq_rows,representative=representative),separators=(',',':'))+'\n')
    q=dict(passed=True,source_only=True,native_run=False,accepted=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
        complete_actual_callers=len(rows),full64P=True,all_four_icons_and_variants=True,all_capacity_and_rotation_controls=True,
        full_AXYP_SP_RAM_SMC_banks_ordered_OAM_VRAM_hardware_exact=True,actual_compiled_IRQ_injections=len(irq_rows),
        max_total_stack_depth=maxdepth,all_five_actual_IRQ_nonstack_stores_exact=True,new_emitter_entry_source_invariants_verified=dict(caller_entries),
        genuine_new_ranges=ranges,representative=representative,case_file_sha256=sha(a.output/'cases.json'),checker_sha256=sha(Path(__file__)),
        limits='Arranged complete callers and actual compiled IRQ. No full captured foreground RAM, native/NMI/DMC DMA/PPU timing or recovered-frame claim.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='representative'}))


if __name__=='__main__':main()
