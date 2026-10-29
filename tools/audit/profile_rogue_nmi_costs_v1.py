"""Compare original and real host NMI costs; profile actual executed instruction cycles."""
from pathlib import Path
from collections import Counter
import json
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
from checkpoint_roster_packets_v1 import verify

OUT=ROOT/'build/rogue-nmi-profile-v1'
HP=ROOT/'build/rogue-dawn-side-v1/handoff.json'


def profiled(m):
    buckets=Counter();calls=Counter();step=v.NesMPU.step
    addresses={v.address(m.bundle,n):n for n in ['RdaReadRomValue','RdaReadE6Y','RdaReadECY',
        'RdaRead8002Y','RdaRead8003Y','RdaRead801AY','RdaRead804CY']}
    def measured(c):
        pc=c.pc;bank=m.banks[(pc-0x8000)//8192]if pc>=0x8000 else -1
        before=c.processorCycles
        if bank in [62,97]and pc in addresses:calls[addresses[pc]]+=1
        step(c)
        key=('raw_reader_C97'if bank==97 and pc<0xc077 else 'original_audio_C97'if bank==97
            else 'audio_adapter_A62'if bank==62 else 'physical_bank_'+str(bank))
        buckets[key]+=c.processorCycles-before
    v.NesMPU.step=measured
    try:result=v.nmi(m)
    finally:v.NesMPU.step=step
    # Seven CPU cycles enter NMI before the first executed instruction.
    assert sum(buckets.values())+7==result['CPU']
    return result,dict(buckets),dict(calls)


def main():
    assert not(OUT/'profile.json').exists(),'Keep this cost observation immutable'
    h=json.loads(HP.read_text());seen={};verify(h,seen)
    b=v.scoped_load(Path(h['candidate']['path']));raw=v.ref.ROM.read_bytes()
    rows=[]
    for area in [0,1]:
        source=v.src.source(raw,3);source[0x23]=area;source[0x680]=source[0x62c]=1
        host=v.prepared(b,area)
        for tick in range(4):
            if tick==1:source[0x685]=[16,1][area]
            count=tick%3 if tick else 0
            for _ in range(count):v.src.call(source,0xc000)
            source.requests=[];c=v.NesMPU(memory=source,pc=0x5b00);c.sp=237;c.p=0x61
            original=v.src.nmi(source,c)
            host[0x5fb6]=count*2;v.put(host,NmiDisable=255)
            actual,buckets,calls=profiled(host)
            assert actual['requests']==[q for q in source.requests if q[0]!=0x4014]
            v.compare_state(source,host)
            rows.append(dict(area=area,tick=tick,completed_Main_fixture=count,
                original_NMI_CPU=original['cycles'],host_NMI_CPU=actual['CPU'],
                additional_host_CPU=actual['CPU']-original['cycles'],actual_instruction_buckets=buckets,
                actual_reader_call_counts=calls,ordered_source_APU_and_state_exact=True))
    OUT.mkdir(exist_ok=True)
    result=dict(status='Read-only original/host cycle profile; no optimization or native FPS claim',
        cases=rows,bindings=[v.ref.binding(p)for p in [HP,Path(__file__),Path(h['candidate']['path']),
            Path(h['candidate']['path']).with_suffix('.dbg'),Path(h['candidate']['path']).with_suffix('.lbl'),
            ROOT/'tools/rogue_dawn_scheduler_controls_v3.py']],
        limits='Eight finite initialized source/real-host NMI observations, excluding DMA stall, DMC steals and PPU timing. Native source-ascent route is independent. No queues, clock cadence, music channels or original instructions altered.')
    (OUT/'profile.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(profile=v.ref.binding(OUT/'profile.json'),cases=rows)))


if __name__=='__main__':main()
