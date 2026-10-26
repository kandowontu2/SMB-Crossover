"""Real mapper IRQ/RTI at reached Chip route/player instruction boundaries."""
from pathlib import Path
import argparse
import hashlib
import json
from check_tmnt_render_oa import load,address
from root_chip_native_adapter_cpu_v1 import Run


def registers(c):
    return c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp


def ordinary(m):
    # Preserve the executable SMC area. Only discarded hardware-stack space
    # and I/O changed by the actual scroll IRQ are excluded.
    return bytes(m[:0x1a0]+m[0x200:0x2000]+m[0x5c00:0x8000])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
    b=load(a.rom);r=Run(b);c,m=r.c,r.m;step=c.step
    seen=set();hardware=set();minimum=255;calls=0;active=False

    def injected_step():
        nonlocal minimum,active
        if active:
            return step()
        # The real NMI uses CLI before audio; make that entry condition explicit.
        if c.pc==address(b,'ChNativeAudioUpdate'):
            c.p &= ~4
        bank=m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        key=bank,c.pc
        target=(bank==78 and address(b,'ChNativeAudioUpdate')<=c.pc<0xb000) or (
                bank==62 and 0xa300<=c.pc<0xae00) or (bank==94 and 0xdfe0<=c.pc<0xe000)
        if target and key not in seen:
            seen.add(key);assert not c.p&4
            before=registers(c),ordinary(m),list(m.banks),list(m.events)
            old_count=len(m.writes)
            active=True;m[0x5204]=128;c.irq()
            assert c.pc==0x8000
            for _ in range(300):
                if c.pc==before[0][0] and c.sp==before[0][-1]:break
                minimum=min(minimum,c.sp);m.pc=c.pc;step()
            else:raise AssertionError(('IRQ failed return',key,hex(c.pc)))
            assert (registers(c),ordinary(m),list(m.banks),list(m.events))==before,('IRQ damaged music state',key)
            stores=[(at,v)for at,v in m.writes[old_count:] if 0x2000<=at<0x6000]
            assert stores and all(at in [0x2005,0x2006,0x5128,0x5130]for at,v in stores)
            hardware.update(at for at,v in stores)
            active=False;m.pc=c.pc
        return step()

    c.step=injected_step
    for area,event,paused in [(1,0,0)]+[(0,0,0)]*600+[(0,0,1),(2,0,1),(0,0,0),
                                                        (0,1,0),(0,0,0),(128,0,0),(4,0,0)]:
        r.call(area,event,paused);calls+=1
    proof=dict(passed=True,accepted=False,native_run=False,
               candidate_ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),
               actual_compiled_IRQ_injections=len(seen),executed_audio_calls=calls,
               actual_vector_handler_RTI=True,minimum_IRQ_SP=minimum,
               exact_intermediate_AXYP_SP_RAM_SMC_banks_and_ordered_APU=True,
               observed_IRQ_write_addresses=sorted(hardware),
               reached_boundaries=[dict(bank=bank,PC=pc)for bank,pc in sorted(seen)],
               checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               limits='Actual compiled IRQ/RTI under an untimed CPU bus with explicit CLI and pending mapper status. Reached unique instruction boundaries only. No real PPU/DMA/DMC timing, nested NMI or native cadence verdict.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items()if k!='reached_boundaries'}))


if __name__=='__main__':main()
