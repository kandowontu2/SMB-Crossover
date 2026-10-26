"""Trace twelve immutable original SMB3 selections; no relocation or native run.

The output is dynamic closure for this exact cold NSF contract and call bound.
Original source addresses/data/pointers, every voice/store/sample and4017 remain.
"""
from pathlib import Path
from collections import Counter
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import struct

from mike_parodius_music_probe import Bus, spans
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'reference/new-roster-audio/mario3/crossover-named.nsf'
NSFE=ROOT/'reference/crossover2/extracted/binaryData/254_com.explodingRabbit.cross.games.GameSuperMarioBros3_Nsfe.bin'
EXPECTED='4f22166e5baf4db867564b57c3d152dacb85b6365f7bf94cf0883d612e7f915c'
SIZES=dict(imp=1,acc=1,imm=2,zpg=2,zpx=2,zpy=2,inx=2,iny=2,rel=2,abs=3,abx=3,aby=3,ind=3)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
RAM_ADDRESSES=list(range(0x100))+list(range(0x200,0x800))+list(range(0x6000,0x8000))


class TraceBus(Bus):
    def __init__(self,raw):
        super().__init__(raw)
        self.fetch=set();self.pc=0;self.pc_physical=0
        self.data_reads=set();self.bindings=set();self.nonstack_writes=[]
        self.written=set();self.cold_reads=set();self.cold_read_sites=set()
        self.sample_configs=set()

    def __getitem__(self,a):
        if a>=0x8000:
            p=self.physical(a)
            self.bindings.add((a,p))
            if a not in self.fetch:self.data_reads.add(p)
        elif a<0x2000 or 0x6000<=a<0x8000:
            k=a&0x7ff if a<0x2000 else a
            if not 0x100<=k<0x200 and k not in self.written:
                self.cold_reads.add(k);self.cold_read_sites.add((self.pc,self.pc_physical,k))
        return super().__getitem__(a)

    def __setitem__(self,a,v):
        if a<0x2000 or 0x6000<=a<0x8000:
            k=a&0x7ff if a<0x2000 else a
            if not 0x100<=k<0x200:
                self.written.add(k)
                self.nonstack_writes.append((k,v&255))
        super().__setitem__(a,v)
        if a==0x4015 and v&16:
            start=0xc000+self.apu[18]*64
            count=self.apu[19]*16+1
            physical=tuple(self.physical((start+i)&0xffff)for i in range(count))
            self.sample_configs.add((self.apu[16],self.apu[17],self.apu[18],self.apu[19],start,count,
                                     physical[0],physical[-1],tuple(self.maps)))


def source_state(m):
    return bytes(list.__getitem__(m,slice(0,0x100)))+bytes(list.__getitem__(m,slice(0x200,0x800)))+bytes(list.__getitem__(m,slice(0x6000,0x8000)))


def registers(c):return [c.a,c.x,c.y,c.p,c.sp]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--calls',type=int,default=18000)
    a=p.parse_args();out=a.output.resolve()
    assert a.calls==18000,'Finite fixture is18,000 play calls per selection'
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    assert sha(SOURCE)==EXPECTED
    raw=SOURCE.read_bytes();original=NSFE.read_bytes();chunks={};at=4
    while at<len(original):
        n=struct.unpack_from('<I',original,at)[0]
        chunks[original[at+4:at+8]]=original[at+8:at+8+n];at+=n+8
    assert raw[128:]==chunks[b'DATA']
    labels=chunks[b'tlbl'].rstrip(b'\0').decode('utf-8').split('\0')
    planpath=ROOT/'reference/new-roster-audio/playlist-plan.json'
    manifestpath=ROOT/'reference/new-roster-audio/captures-manifest.json'
    plan=json.loads(planpath.read_text())['mario3']['tracks']
    manifest=json.loads(manifestpath.read_text())
    assert len(plan)==12 and len(set(plan.values()))==12
    roles={};union_code=set();union_data=set();union_read=set();union_samples=set()
    union_ramread=set();union_ramwrite=set();union_pointers=set();union_bindings=set()
    dependencies=[Path(__file__),ROOT/'tools/audit/mike_parodius_music_probe.py',ROOT/'tools/audit/verify_native_relocation.py',SOURCE,NSFE,planpath,manifestpath]
    total_calls=total_stores=total_capture_stores=0
    for role,song in plan.items():
        record=manifest[f'mario3-{song:02d}'];capture=Path(record['path'])
        assert record['source_sha256']==EXPECTED
        old_raw=gzip.decompress(capture.read_bytes())
        assert hashlib.sha256(old_raw).hexdigest()==record['capture_sha256']
        reference=[(0x4000+int(r['register']),int(r['value']))for r in csv.DictReader(io.StringIO(old_raw.decode()))]
        dependencies.append(capture)
        checked=0;m=TraceBus(raw);c=NesMPU(memory=m)
        code=set();entries=set();pointers=set();indirect_stack=set();instructions={}
        pc_counts=Counter();pc_costs=Counter();costs=[];first_repeat=None;seen={}
        minsp=255;stores=mapper_count=0;peak=None;peak_trace=[];init_state=None
        folder=out/f'{role}-{song:02d}';folder.mkdir()
        log=folder/'calls.jsonl.gz'
        with gzip.open(log,'wt',encoding='utf-8',newline='\n')as f:
            for tick in range(a.calls+1):
                c.pc=0x9000 if tick==0 else 0xa000
                c.a=song-1 if tick==0 else 0;c.x=c.y=0;c.p=0x24;c.sp=0xfd
                list.__setitem__(m,510,255);list.__setitem__(m,511,126)
                m.events=[];m.mapper=[];m.nonstack_writes=[]
                before=c.processorCycles;trace=[];APU_timing=[]
                for _ in range(200000):
                    if c.pc==0x7f00:break
                    pc=c.pc;assert pc>=0x8000,(role,tick,hex(pc))
                    op=m.peek(pc);mnemonic,mode=c.disassemble[op];n=SIZES[mode]
                    physical=m.physical(pc);m.pc,m.pc_physical=pc,physical
                    m.fetch=set(range(pc,pc+n))
                    entries.add((pc,physical))
                    code.update(m.physical((pc+i)&0xffff)for i in range(n))
                    instructions[(pc,physical)]=(op,mnemonic,mode,n)
                    if mode in ['inx','iny','ind']:
                        v=m.peek(pc+1)
                        ptr=(v+c.x)&255 if mode=='inx'else v if mode=='iny'else v+256*m.peek(pc+2)
                        hi=(ptr+1)&255 if mode!='ind'else(ptr&0xff00)|((ptr+1)&255)
                        base=m.peek(ptr)+256*m.peek(hi)
                        effective=(base+(c.y if mode=='iny'else 0))&65535
                        target=m.physical(effective)if effective>=0x8000 else-1
                        pointers.add((pc,physical,mode,ptr,hi,base,c.y if mode=='iny'else 0,effective,target))
                        if 0x100<=effective<0x200:indirect_stack.add((pc,effective))
                    count=len(m.events);start=c.processorCycles
                    trace.append([pc,physical,c.a,c.x,c.y,c.p,c.sp,start-before])
                    minsp=min(minsp,c.sp);c.step()
                    elapsed=c.processorCycles-start
                    pc_counts[(pc,physical)]+=1;pc_costs[(pc,physical)]+=elapsed
                    if len(m.events)>count:
                        APU_timing.extend([c.processorCycles-before,*event]for event in m.events[count:])
                else:raise AssertionError(('Source timeout',role,tick,hex(c.pc)))
                assert c.sp==255 and not m.bad_writes and not m.io_reads,(role,tick)
                elapsed=c.processorCycles-before
                if tick:
                    costs.append(elapsed)
                    if peak is None or elapsed>peak['cycles']:
                        peak=dict(tick=tick,cycles=elapsed);peak_trace=trace
                else:
                    init_cost=elapsed;init_state={str(k):m.peek(k)for k in m.ram_writes}
                # Old observer recorded4000..4015 only, across its wall-frame
                # schedule. Compare its entire ordered stream as a prefix;
                # keep4017 and all subsequent source stores in the new log.
                for event in m.events:
                    if event[0]<=0x4015 and checked<len(reference):
                        assert event==reference[checked],('Prior native capture prefix mismatch',role,tick,checked,event,reference[checked])
                        checked+=1
                state=source_state(m)
                h=hashlib.sha256(state).hexdigest()
                if tick and first_repeat is None:
                    key=hashlib.sha256(state+bytes(m.maps)+bytes(m.apu)).hexdigest()
                    if key in seen:first_repeat=dict(first_tick=seen[key],repeat_tick=tick,period_calls=tick-seen[key])
                    else:seen[key]=tick
                f.write(json.dumps(dict(tick=tick,cycles=elapsed,post_AXY_P_SP=registers(c),APU=m.events,
                    APU_instruction_end_cycles=APU_timing,mapper=m.mapper,banks=m.maps,
                    ordered_nonstack_RAM_writes=m.nonstack_writes,full_nonstack_source_RAM_sha256=h),separators=(',',':'))+'\n')
                stores+=len(m.events);mapper_count+=len(m.mapper)
            assert checked==len(reference),(role,checked,len(reference))
        assert not indirect_stack,'Unexpected indirect stack-state input requires separate model'
        touched=(m.ram_reads|m.ram_writes)-set(range(0x100,0x200))
        endstate={str(k):m.peek(k)for k in sorted(touched)}
        (folder/'peak.json').write_text(json.dumps(dict(**peak,trace=peak_trace),separators=(',',':'))+'\n')
        footprint=dict(executed_PC_physical_entries=sorted(map(list,entries)),code_byte_ranges=spans(code),
            actual_ROM_data_read_ranges=spans(m.data_reads),all_actual_ROM_read_ranges=spans(m.rom_reads),
            source_logical_physical_read_bindings=sorted(map(list,m.bindings)),
            indirect_pointer_accesses=sorted(map(list,pointers)),
            pointer_columns=['PC','physical_PC','mode','low_cell','high_cell','base_value','Y_index','effective_CPU','physical_target_or_minus1'],
            RAM_read_ranges=spans(m.ram_reads),RAM_write_ranges=spans(m.ram_writes),
            cold_zero_read_before_first_write_ranges=spans(m.cold_reads),
            cold_zero_read_sites=sorted(map(list,m.cold_read_sites)),
            DPCM_sample_ranges_inclusive=spans(m.sample_ranges),DPCM_configs=sorted(map(list,m.sample_configs)),
            instruction_rows=[dict(PC=k[0],physical_PC=k[1],opcode=v[0],mnemonic=v[1],mode=v[2],bytes=v[3],calls=pc_counts[k],cycles=pc_costs[k])for k,v in sorted(instructions.items())],
            post_init_written_state=init_state,final_observed_live_state=endstate)
        (folder/'footprint.json').write_text(json.dumps(footprint,indent=2)+'\n')
        result=dict(role=role,one_based_track=song,label=labels[song-1],source_calls=a.calls+1,play_calls=a.calls,
            init_cycles=init_cost,mean_play_cycles=sum(costs)/len(costs),p95_nearest_rank=sorted(costs)[math.ceil(.95*len(costs))-1],
            peak=peak,minimum_source_SP=minsp,ordered_APU_stores=stores,source_bank_writes=mapper_count,
            original_native_capture_ordered_prefix_stores=checked,original_native_capture_frames=record['frames'],
            exact_call_boundary_state_repeat=first_repeat,code_bytes=len(code),ROM_data_bytes=len(m.data_reads),
            all_ROM_read_bytes=len(m.rom_reads),sample_bytes=len(m.sample_ranges),required_observed_ROM_union=len(m.rom_reads|m.sample_ranges),
            state_bytes_excluding_stack=len(touched),cold_zero_inputs=len(m.cold_reads),
            RAM_reads=spans(m.ram_reads),RAM_writes=spans(m.ram_writes),DPCM_ranges=spans(m.sample_ranges),
            unmodeled_IO_reads=dict(m.io_reads),unexpected_ROM_writes=m.bad_writes,
            output_files={str(q.relative_to(out)):sha(q)for q in [log,folder/'footprint.json',folder/'peak.json']})
        roles[role]=result
        union_code|=code;union_data|=m.data_reads;union_read|=m.rom_reads;union_samples|=m.sample_ranges
        union_ramread|=m.ram_reads;union_ramwrite|=m.ram_writes;union_pointers|=pointers;union_bindings|=m.bindings
        total_calls+=a.calls+1;total_stores+=stores;total_capture_stores+=checked
        print(role,song,'mean',round(result['mean_play_cycles'],3),'peak',peak,'repeat',first_repeat,'sourceAPU',stores,'oldcapture',checked,flush=True)
    closure=dict(code_byte_ranges=spans(union_code),code_bytes=len(union_code),ROM_data_ranges=spans(union_data),ROM_data_bytes=len(union_data),
        all_observed_ROM_read_ranges=spans(union_read),all_observed_ROM_read_bytes=len(union_read),
        DPCM_ranges_inclusive=spans(union_samples),DPCM_bytes=len(union_samples),
        required_observed_ROM_ranges=spans(union_read|union_samples),required_observed_ROM_bytes=len(union_read|union_samples),
        RAM_reads=spans(union_ramread),RAM_writes=spans(union_ramwrite),
        logical_physical_ROM_read_bindings=sorted(map(list,union_bindings)),
        indirect_pointer_accesses=sorted(map(list,union_pointers)),
        preserve_unobserved_source_payload=True,universal_reachability_proved=False,
        interpretation='Every actually observed CPU read/pointer effective address and requested DPCM byte in12 cold selections and18,000 calls each. Not static all-input reachability; no payload bytes removed or declared free.')
    (out/'dynamic-closure.json').write_text(json.dumps(closure,indent=2)+'\n')
    proof=dict(passed=True,source_only=True,native_emulator_launched=False,game_source_mutation=False,allocation_or_integration=False,
        source=str(SOURCE),source_sha256=EXPECTED,source_NSFE_sha256=sha(NSFE),exact_NSFE_DATA_payload=True,
        source_payload_bytes=len(raw)-128,original_load_init_play=[0x8000,0x9000,0xa000],original_NSF_period_us=16639,
        original_NSF_banks=list(raw[112:120]),source_entry_contract='Cold all source RAM zero; initA=track-1; each playA/X/Y=0,P24,SPFD,stackreturn7F00. Source writes/stores/ticks unchanged.',
        source_calls=total_calls,ordered_original_APU_stores=total_stores,prior_native_capture_prefix_stores=total_capture_stores,
        roles=roles,dynamic_closure_sha256=sha(out/'dynamic-closure.json'),dependencies={str(q):sha(q)for q in dependencies},
        limits='Original CPU-only trace, fixed finite cold contract. Old native observer prefix is compared by full ordered4000..4015 stream, independent of wall-frame grouping;4017 is retained only in the new full source trace. Call cost excludes hardware DMC DMA, NMI/IRQ, PPU, mixer/adapter. Repeated canonical source RAM/maps/latchedAPU shows CPU-state recurrence only; no physical sample-completion or universal reachability claim. No A62/C94/124/125 space allocated.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,source_calls=total_calls,ordered_APU=total_stores,proof=str(out/'proof.json'),sha256=sha(out/'proof.json'))),flush=True)


if __name__=='__main__':main()
