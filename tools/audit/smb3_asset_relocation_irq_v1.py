"""Actual IRQ/RTI through relocated art consumers and late native lifts."""
from pathlib import Path
import argparse,hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from z2_platform_late_check import Machine
from smb3_asset_relocation_cpu_v4 import setup,execute,canonical

R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
IRQ_PORTS={0x2005,0x2006,0x5128,0x5130}

def projected(b,c,m,cfg,new=False,irq=False):
    v=list(canonical(b,c,m,cfg,new));ram=bytearray(v[5])
    if irq:
        # Hardware effects of the actually executed split IRQ are classified
        # separately. Nothing in the emulated machine is restored/overwritten.
        for at in IRQ_PORTS:ram[at-0x60]=0
    v[5]=bytes(ram)
    return tuple(v)

def ordinary(m):return bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000])
def regs(c):return(c.pc,c.a,c.x,c.y,c.p&207,c.sp)

def run(b,cfg,target=None):
    c,m=setup(b,cfg);m[0x5204]=128;m.writes=[];trace=[];irqlog=None
    for index in range(60000):
        if c.pc==0x7f00:break
        if index==target:
            before=regs(c),ordinary(m),tuple(m.banks);assert not c.p&4
            first=len(m.writes);c.irq();assert c.pc==0x8000
            for _ in range(300):
                if c.pc==before[0][0]and c.sp==before[0][-1]:break
                c.step()
            else:raise AssertionError(('IRQ failed to return',cfg,target))
            assert(regs(c),ordinary(m),tuple(m.banks))==before,('IRQ changed state',cfg,target)
            irqlog=m.writes[first:];hardware=[(at,v)for at,v in irqlog if 0x2000<=at<0x6000]
            assert hardware and all(at in IRQ_PORTS for at,v in hardware),hardware
            # Project only separately validated IRQ event stores from the
            # foreground log. Actual CPU/memory/bank state is untouched.
            del m.writes[first:]
        bank=m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        trace.append((index,c.pc,bank))
        c.step()
    else:raise AssertionError(('Caller timeout',cfg,hex(c.pc)))
    assert c.sp==253
    if target is not None:assert irqlog is not None
    return c,m,trace,irqlog

def late(b,slot,rel,offset,rotation,area,world,ident):
    q=Machine(b);q.setup(slot=slot,rel=rel,offset=offset,rotation=rotation,area=area,world=world,ident=ident)
    entry='Z2DrawLateSmallLifts';bank=(location(b,entry)-16)//8192
    q.m.page(1,bank);q.put('CurrentBank',bank|128)
    c=NesMPU(memory=q.m,pc=address(b,entry));c.a,c.x,c.y,c.p,c.sp=85,3,7,0x60,253
    c.stPushWord(0x7eff);q.m.writes=[]
    for _ in range(30000):
        if c.pc==0x7f00:break
        c.step()
    else:raise AssertionError('Late lift timeout')
    return c,q.m

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.resolve().is_relative_to(R);a.output.mkdir(parents=True,exist_ok=False)
    old,new=scoped_load(a.parent),scoped_load(a.candidate);latecases=[];irqrows=[];stores=set()
    for slot,rel,offset,rot,mode,ident in itertools.product([0,3,5],[-16,-1,0,100,239,255],[0,240,252],[0,4,128,252],[(0x62,1),(0x62,4),(0x40,0)],[0x2b,0x2c]):
        area,world=mode;c,m=late(old,slot,rel,offset,rot,area,world,ident);d,n=late(new,slot,rel,offset,rot,area,world,ident)
        cfg=dict(owner='z2');assert canonical(old,c,m,cfg)==canonical(new,d,n,cfg,True),(slot,rel,offset,rot,mode,ident)
        latecases.append(dict(slot=slot,rel=rel,offset=offset,rotation=rot,mode=mode,ident=ident,delta=d.processorCycles-c.processorCycles))
    cfgs=[
        dict(owner='z2',entry='Z2SetPose',pose=0,flags=0x20),
        dict(owner='z2',entry='Z2DrawShots',shots=[(0,1),(1,2)],items=[(1,0xc1)],drops=[(0,0x90)],rotation=252,flags=0x20),
        dict(owner='mike',entry='JnSetPose',pose=6,face=2,flags=0x20),
        dict(owner='mike',entry='JnDraw',shots=[(0,13),(1,4)],items=[(2,0x8d)],drops=[(0,1)],rotation=4,flags=0x20),
        dict(owner='bill',entry='BillFlareLoadLate',age=1793,face=2,slot=0,flags=0x20),
        dict(owner='bill',entry='BillFlareLoadExtended',age=2432,face=1,slot=2,flags=0x20),
        dict(owner='mike',entry='DrawAllMetasprites',pose=3,shots=[(0,1)],seed={'ObjectMetasprite':address(new,'METASPRITE_SAMUS_BODY')},flags=0x20),
        dict(owner='z2',entry='DrawAllMetasprites',pose=3,shots=[(0,1)],seed={'ObjectMetasprite':address(new,'METASPRITE_SAMUS_BODY')},flags=0x20)]
    for cfg in cfgs:
        c,m,trace,_=run(new,cfg);expected=projected(new,c,m,cfg,True,True)
        o,om,ot,_=run(old,cfg);assert projected(old,o,om,cfg,irq=True)==expected,cfg
        # All distinct actual reached instruction/bank boundaries for direct
        # consumers; full DrawAll exercises new art-reference owners and both
        # resident/fixed-bank source pipelines without hundreds of duplicates.
        seen=set();targets=[]
        for index,pc,bank in trace:
            key=bank,pc
            if key in seen:continue
            seen.add(key)
            if cfg['entry']=='DrawAllMetasprites'and bank not in [69,70,71,95,96,97,98,126,127]:continue
            targets.append((index,pc,bank))
        for index,pc,bank in targets:
            d,n,_,log=run(new,cfg,index)
            assert projected(new,d,n,cfg,True,True)==expected,(cfg,index,hex(pc),bank)
            stores.update(at for at,v in log if 0x2000<=at<0x6000)
            irqrows.append(dict(entry=cfg['entry'],owner=cfg['owner'],index=index,pc=pc,bank=bank))
    ds=[q['delta']for q in latecases]
    proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),
               late_native_lift_cases=len(latecases),late_lift_cycle_delta=[min(ds),max(ds)],actual_IRQ_RTI_injections=len(irqrows),actual_IRQ_hardware_ports=sorted(stores),
               final_AXYP_SP_RAM_SMC_OAM_CHR_VRAM_banks_exact_after_typed_data_relocation=True,
               IRQ_classification='Only discarded upper stack, actual four split-IRQ hardware cells and separately validated IRQ event stores are projected. No emulated machine state is restored or forced. Actual vector/handler/RTI execute at each distinct reached tested consumer boundary.',
               checker_sha256=sha(__file__),consumer_checker_sha256=sha(Path(__file__).with_name('smb3_asset_relocation_cpu_v4.py')),
               limits='Isolated actual 6502 IRQ and art consumers. No nested NMI, PPU/DMC hardware clocks, native frame cadence or adoption claim.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');(a.output/'cases.json').write_text(json.dumps(dict(lifts=latecases,irq=irqrows),separators=(',',':'))+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
