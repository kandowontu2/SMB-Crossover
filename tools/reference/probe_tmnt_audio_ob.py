"""Observe pinned original TMNT NSF instructions, pointers, state and APU writes."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'reference/new-roster-audio/tmnt/Teenage Mutant Ninja Turtles [Gekikame Ninja Den] (1989-05-12)(Konami).nsf'
EXPECTED = 'f220e8d069e321f392526d41e46f5d0f72966d5a22e56d2b269607c678bd58d9'


class Bus(list):
    def __init__(self, raw):
        super().__init__([0]*65536); self.events=[]; self.low=set(); self.high={}
        self[0x8000:0x8000+len(raw)-128] = raw[128:]

    def __setitem__(self, at, value):
        if isinstance(at,int):
            if 0x4000 <= at <= 0x4017: self.events.append((at,value))
            if at < 0x2000 and not 0x1d0 <= at < 0x200: self.low.add(at)
            if at >= 0x8000:
                self.high.setdefault(at,set()).add(value)
                return # NSF leaves its supplied ROM fixed; no NSF bank registers.
        super().__setitem__(at,value)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True)
    p.add_argument('--frames',type=int,default=500); a=p.parse_args(); assert a.frames>=200
    a.output.mkdir(parents=True,exist_ok=False); raw=SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED and raw[112:120]==bytes(8) and raw[123]==0
    base,init,play=(int.from_bytes(raw[k:k+2],'little')for k in [8,10,12]); end=base+len(raw)-128
    seen=set();words=set();components=set();accesses={};ram=set();songs={};apu_stores={};high={};rom_reads=set()
    for song in range(raw[6]):
        m=Bus(raw);c=MPU(memory=m);origin={};registers=dict(a=None,x=None,y=None);events=[];minimum_sp=0xff
        def effective(pc,mode):
            v=m[pc+1];absolute=v+256*m[pc+2]
            if mode=='zpg':return v
            if mode=='zpx':return(v+c.x)&255
            if mode=='zpy':return(v+c.y)&255
            if mode=='abs':return absolute
            if mode=='abx':return(absolute+c.x)&65535
            if mode=='aby':return(absolute+c.y)&65535
            if mode in ('inx','iny','ind'):
                ptr=(v+c.x)&255 if mode=='inx'else v if mode=='iny'else absolute
                hi=(ptr+1)&255 if mode!='ind'else(ptr&0xff00)|((ptr+1)&255)
                address=m[ptr]+256*m[hi];lo_origin,hi_origin=origin.get(ptr),origin.get(hi)
                if lo_origin is not None and hi_origin is not None and base<=address<end:
                    components.add((lo_origin,hi_origin))
                    if hi_origin==lo_origin+1 and base<=m[lo_origin]+256*m[hi_origin]<end:words.add(lo_origin)
                return(address+(c.y if mode=='iny'else 0))&65535
            return None
        def call(pc,song_number=None):
            nonlocal minimum_sp
            if song_number is not None:c.a=song_number;c.x=c.y=0;registers.update(a=None,x=None,y=None)
            c.sp=0xfd;m[0x1fe]=0xff;m[0x1ff]=0x01;c.pc=pc;m.events=[];start=c.processorCycles
            for _ in range(50000):
                pc=c.pc
                if pc==0x0200:return c.processorCycles-start,list(m.events)
                assert base<=pc<end,('PC escaped NSF',song+1,hex(pc))
                seen.add(pc);op,mode=c.disassemble[m[pc]];target=effective(pc,mode)
                minimum_sp=min(minimum_sp,c.sp)
                if target is not None:
                    accesses.setdefault(pc,set()).add(target)
                    if target<0x2000:ram.add(target)
                if op in ('LDA','LDX','LDY'):
                    registers[op[-1].lower()]=(target if target is not None and target>=base else pc+1 if mode=='imm'else origin.get(target))
                    if target is not None and base<=target<end:rom_reads.add(target)
                elif op in ('STA','STX','STY'):
                    origin[target]=registers[op[-1].lower()]
                    if target is not None and 0x4000<=target<=0x4017:apu_stores.setdefault(pc,set()).add(target)
                elif op in ('TAX','TAY'):registers[op[-1].lower()]=registers['a']
                elif op in ('TXA','TYA'):registers['a']=registers[op[1].lower()]
                elif op in ('PLA','ADC','SBC','AND','ORA','EOR','ASL','LSR','ROL','ROR'):registers['a']=None
                elif op in ('INX','DEX'):registers['x']=None
                elif op in ('INY','DEY'):registers['y']=None
                c.step()
            raise AssertionError(('NSF call timeout',song+1,hex(c.pc)))
        n,ev=call(init,song);events.append(dict(call=-1,cycles=n,writes=ev))
        for frame in range(a.frames):
            n,ev=call(play);events.append(dict(call=frame,cycles=n,writes=ev))
        data=json.dumps(events,separators=(',',':')).encode();f=a.output/f'song-{song+1:02d}.json.gz';f.write_bytes(gzip.compress(data,mtime=0))
        songs[str(song+1)]=dict(calls=a.frames,APU_events=sum(len(x['writes'])for x in events),
                              maximum_play_cycles=max(x['cycles']for x in events[1:]),
                              DMC_enabled_calls=sum(any(at==0x4015 and v&16 for at,v in x['writes'])for x in events),
                              state_writes=sorted(m.low),minimum_CPU_SP=minimum_sp,capture_sha256=hashlib.sha256(f.read_bytes()).hexdigest())
        assert minimum_sp>=0x1d0-0x100, ('Stack/state overlap requires separate proof',song+1,minimum_sp)
        for at,values in m.high.items():high.setdefault(at,set()).update(values)
        print('song',song+1,'peak',songs[str(song+1)]['maximum_play_cycles'],'DMC',songs[str(song+1)]['DMC_enabled_calls'],flush=True)
    report=dict(passed=True,source=str(SOURCE),source_sha256=EXPECTED,load=base,init=init,play=play,payload_bytes=len(raw)-128,
                seen_instructions=sorted(seen),pointer_words=sorted(words),pointer_components=sorted(map(list,components)),accesses={str(k):sorted(v)for k,v in accesses.items()},
                RAM_accesses=sorted(ram),ROM_data_reads=sorted(rom_reads),APU_stores={str(k):sorted(v)for k,v in apu_stores.items()},
                high_writes={str(k):sorted(v)for k,v in high.items()},songs=songs,
                scope='Original NSF execution only; fixed supplied NSF ROM, NTSC initX0. No game assets changed or integration claim.')
    (a.output/'coverage.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in ['passed','source_sha256','payload_bytes','RAM_accesses','high_writes']}),flush=True)


if __name__=='__main__':main()
