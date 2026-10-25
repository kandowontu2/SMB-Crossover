"""Instruction-level source-song study without an NSF host advancing tracks.

This is an offline probe, not an installed soundtrack or a hardware audio proof.
Unmodeled APU/PPU reads are recorded explicitly and prevent acceptance claims.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import struct
import sys
from collections import Counter
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/reference'))
from build_playlist_audio import cycle
from build_new_roster_audio import encode,lz


class Memory:
    def __init__(self,raw):
        self.rom=raw[128:];self.ram=bytearray(0x8000);self.banks=list(raw[112:120]);self.writes=[]
        self.io_reads=Counter();self.bank_writes=0;self.apu_image={};self.seen=set()

    def __getitem__(self,at):
        at&=65535
        if at>=0x8000:
            offset=self.banks[(at-0x8000)//4096]*4096+(at&4095)
            assert offset<len(self.rom),('Source bank outside payload',at,self.banks)
            return self.rom[offset]
        if at<0x2000:return self.ram[at&2047]
        if 0x2000<=at<0x4020:
            self.io_reads[at]+=1
            return 0x80 if at==0x2002 else 0
        return self.ram[at]

    def __setitem__(self,at,value):
        at&=65535;value&=255
        if 0x5ff8<=at<=0x5fff:
            self.banks[at-0x5ff8]=value;self.bank_writes+=1;return
        assert at<0x8000,('Unexpected write to source code/mapper',hex(at),value)
        if 0x4000<=at<=0x4017:
            self.writes.append((at-0x4000,value));self.apu_image[at-0x4000]=value
        self.ram[at&2047 if at<0x2000 else at]=value


def invoke(cpu,pc,a=0,x=0,y=0):
    cpu.memory.ram[0x1fe]=0xff;cpu.memory.ram[0x1ff]=0x7e
    cpu.pc=pc;cpu.sp=0xfd;cpu.a=a;cpu.x=x;cpu.y=y;cpu.p=0x24
    before=cpu.processorCycles
    for _ in range(200000):
        if cpu.pc==0x7f00:break
        assert cpu.pc>=0x8000,('Unexpected source execution',hex(cpu.pc))
        cpu.memory.seen.add((tuple(cpu.memory.banks),cpu.pc));cpu.step()
    else:raise AssertionError(('Source driver timeout',hex(cpu.pc)))
    assert cpu.sp==0xff
    return cpu.processorCycles-before


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--tracks',type=int,nargs='+',default=[2,13]);p.add_argument('--calls',type=int,default=15000);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    source=next((ROOT/'reference/new-roster-audio/kirby').glob('*.nsf'));raw=source.read_bytes()
    digest=hashlib.sha256(raw).hexdigest();assert digest=='eecc93d7b56379d399896c3608ef83a304a0cc54bef4f715fac585054c8eda17'
    assert raw[123]==0 and struct.unpack_from('<H',raw,8)[0]==0x8000
    init,play=struct.unpack_from('<HH',raw,10);report={}
    for track in a.tracks:
        assert 1<=track<=raw[6]
        m=Memory(raw);cpu=NesMPU(memory=m);initialize=invoke(cpu,init,track-1)
        init_writes=m.writes[:];m.writes=[];events=[];canonical=[];last={};cost=[]
        for call in range(a.calls):
            m.writes=[];cost.append(invoke(cpu,play));events.append(m.writes[:]);frame={}
            for reg,value in m.writes:
                if reg>15 and reg!=21:continue
                if reg==21:value&=15
                if reg in (3,7,11,15,21)or last.get(reg)!=value:frame[reg]=value
                last[reg]=value
            canonical.append(tuple(sorted(frame.items())))
        found=cycle(canonical)
        packed=None
        if found:
            start,period=found
            packed=len(lz(encode(canonical[:start])+b'\xfe'))+len(lz(encode(canonical[start:start+period])+b'\xff'))
        capture=json.dumps(dict(initialization=init_writes,play_calls=events),separators=(',',':')).encode()
        file=a.output/('track-'+str(track).zfill(2)+'-source-events.json.gz');file.write_bytes(gzip.compress(capture,mtime=0))
        assert gzip.decompress(file.read_bytes())==capture
        q=dict(track=track,play_calls=len(events),source_song_reinitializations=0,initialization_cycles=initialize,
            CPU_mean=sum(cost)/len(cost),CPU_peak=max(cost),bank_writes=m.bank_writes,
            source_instruction_addresses=len(m.seen),unmodeled_IO_reads={hex(k):v for k,v in m.io_reads.items()},
            canonical_loop=dict(start=found[0],period=found[1])if found else None,
            estimated_existing_codec_bytes=packed,source_events_sha256=hashlib.sha256(capture).hexdigest(),
            lossless_capture=dict(path=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
        report[str(track)]=q;print(json.dumps(q),flush=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    q=dict(probe_complete=True,accepted=False,game_changes=False,source=str(source),source_sha256=digest,
        driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),tracks=report,
        scope='Actual original banked NSF initialization once, then fixed requested play calls; no NSF host can auto-advance songs. NES2A03 arithmetic,4KiB NSF banking and ordered APU stores are modeled. APU/PPU reads, if any, are unmodeled and reported; DPCM timing is not emulated. Loop/size measurements are provisional until independent source-native call and hardware comparisons, DPCM handling, codec/playback timing and native port performance pass. No source or game asset is modified.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print('Finished provisional source study')


if __name__=='__main__':main()
