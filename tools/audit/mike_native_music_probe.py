"""Authenticated StarTropics native-music golden states and pointer provenance.

Writes only an external evidence directory. No linked replacement, game patch,
Mesen execution, or native-performance claim is made by this source probe.
"""
from pathlib import Path
from collections import Counter
import argparse,gzip,hashlib,json
from mike_parodius_music_probe import Bus,SOURCE,EXPECTED,TRACKS
from verify_native_relocation import NesMPU

ZP=[*range(0xa0,0xa6),0xac,0xad,*range(0xf0,0xf8)]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--calls',type=int,default=18000);a=p.parse_args()
 out=a.output.resolve();root=Path(__file__).resolve().parents[2];assert not out.is_relative_to(root);out.mkdir(parents=True,exist_ok=False)
 raw=SOURCE.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
 seen=set();data=set();access={};pairs=set();unknown=set();apu={};songs={};allcode=set()
 for song in TRACKS:
  m=Bus(raw);c=NesMPU(memory=m);origin={};regs=dict(a=None,x=None,y=None);stack_origin={};minimum=255;completions=[];last_active=None
  def read(at):return m.peek(at)
  def romorigin(at):return m.physical(at) if at>=32768 else origin.get(at)
  def effective(pc,mode):
   v=read(pc+1);word=v+256*read(pc+2)
   if mode=='zpg':return v
   if mode=='zpx':return(v+c.x)&255
   if mode=='zpy':return(v+c.y)&255
   if mode=='abs':return word
   if mode=='abx':return(word+c.x)&65535
   if mode=='aby':return(word+c.y)&65535
   if mode in ['inx','iny','ind']:
    ptr=(v+c.x)&255 if mode=='inx'else v if mode=='iny'else word
    hi=(ptr+1)&255 if mode!='ind'else(ptr&65280)|((ptr+1)&255)
    at=read(ptr)+256*read(hi)
    if at>=32768:
     lo_origin,hi_origin=origin.get(ptr),origin.get(hi)
     if lo_origin is None or hi_origin is None:unknown.add((pc,ptr,at,lo_origin,hi_origin))
     else:pairs.add((lo_origin,hi_origin,at,m.physical(at)))
    return(at+(c.y if mode=='iny'else 0))&65535
   return None
  costs=[];stores=0;capture=out/f'song-{song:02d}.jsonl.gz'
  with gzip.open(capture,'wt',encoding='utf-8',newline='\n') as stream:
   for step in range(a.calls+1):
    c.pc=0xfe13 if step==0 else 0xf6a4;c.sp=253;c.p=36;c.a=song-1 if step==0 else 0;c.x=c.y=0
    list.__setitem__(m,510,255);list.__setitem__(m,511,126);m.events=[];before=c.processorCycles
    if step==0:regs.update(a=None,x=None,y=None)
    for _ in range(200000):
     if c.pc==0x7f00:break
     pc=c.pc;assert pc>=32768;physical=m.physical(pc);seen.add((pc,physical));allcode.add(physical)
     op,mode=c.disassemble[read(pc)];at=effective(pc,mode);minimum=min(minimum,c.sp)
     if at is not None:access.setdefault(pc,set()).add(at)
     if op in ['LDA','LDX','LDY']:
      regs[op[-1].lower()]=m.physical(pc+1) if mode=='imm'else romorigin(at)
      if at is not None and at>=32768:data.add(m.physical(at))
     elif op in ['STA','STX','STY']:
      origin[at]=regs[op[-1].lower()]
      if at is not None and 0x4000<=at<=0x4017:apu.setdefault(pc,set()).add(at)
     elif op in ['TAX','TAY']:regs[op[-1].lower()]=regs['a']
     elif op in ['TXA','TYA']:regs['a']=regs[op[1].lower()]
     elif op=='PHA':stack_origin[c.sp]=regs['a']
     elif op=='PLA':regs['a']=stack_origin.get((c.sp+1)&255)
     elif op in ['ADC','SBC','AND','ORA','EOR']:regs['a']=None
     elif op in ['ASL','LSR','ROL','ROR']and mode=='acc':regs['a']=None
     elif op in ['INX','DEX','TSX']:regs['x']=None
     elif op in ['INY','DEY']:regs['y']=None
     if op in ['INC','DEC','ASL','LSR','ROL','ROR']and at is not None:origin[at]=None
     c.step()
    else:raise AssertionError(('Timeout',song,step,hex(c.pc)))
    assert c.sp==255 and not m.bad_writes and not m.mapper and not m.io_reads
    elapsed=c.processorCycles-before;stores+=len(m.events)
    if step:costs.append(elapsed)
    active=(read(0x7170)&read(0x7171)&read(0x7172)&read(0x7173)&read(0x7174)&read(0x7175))==255
    if active and not last_active:completions.append(step)
    last_active=active
    state=ZP+list(range(0x7160,0x7200))
    stream.write(json.dumps(dict(step=step,cycles=elapsed,writes=m.events,zp=[read(x)for x in ZP],ram=[read(x)for x in range(0x7160,0x7200)],origins=[origin.get(x)for x in state],all_channels_finished=active),separators=(',',':'))+'\n')
  songs[str(song)]=dict(calls=a.calls,source_APU_writes=stores,mean_play_cycles=sum(costs)/len(costs),peak_play_cycles=max(costs),minimum_SP=minimum,all_channels_finish_calls=completions,capture_sha256=hashlib.sha256(capture.read_bytes()).hexdigest())
  print(song,songs[str(song)],flush=True)
 q=dict(status='ORIGINAL_SOURCE_ONLY',source=str(SOURCE),source_sha256=EXPECTED,calls_per_track=a.calls,tracks=TRACKS,ZP=ZP,RAM_span=[0x7160,0x7200],seen_instructions=sorted(map(list,seen)),ROM_data_reads=sorted(data),pointer_components=sorted(map(list,pairs)),unknown_pointer_origins=sorted(map(list,unknown)),accesses={str(k):sorted(v)for k,v in access.items()},APU_stores={str(k):sorted(v)for k,v in apu.items()},songs=songs,tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),production_changes=False,native_emulator_launched=False)
 (out/'coverage.json').write_text(json.dumps(q,indent=2)+'\n');print('COMPLETE',len(allcode),len(data),len(pairs),len(unknown))
if __name__=='__main__':main()
