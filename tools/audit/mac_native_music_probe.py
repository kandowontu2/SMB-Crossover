"""Original Punch-Out NSF calls, operand provenance and music-only footprint."""
from pathlib import Path
from collections import Counter
import argparse,gzip,hashlib,json,struct
from verify_native_relocation import NesMPU
ROOT=Path(__file__).resolve().parents[2]
SOURCE=next((ROOT/'reference/new-roster-audio/mac').glob('*.nsf'))
EXPECTED='9a7a3ae5f16b745f74296478ec208b5b87ad5ec2773a14b243f7e631a2dd8d68'
TRACKS=[1,2,4,6,7,9,20,22,23]
class Bus(list):
 def __init__(self,raw):
  super().__init__([0]*65536);self[32768:]=raw[128:];self.events=[];self.reads=set();self.low=set();self.io=Counter();self.high=[]
 def __getitem__(self,a):
  if isinstance(a,int):
   self.reads.add(a)
   if 0x2000<=a<0x4000 or a in [0x4015,0x4016,0x4017]:self.io[a]+=1
  return super().__getitem__(a)
 def __setitem__(self,a,v):
  if isinstance(a,int):
   if a>=32768:self.high.append((a,v));return
   if a<0x2000 and not 256<=a<512:self.low.add(a)
   if 0x4000<=a<=0x4017:self.events.append((a,v))
  super().__setitem__(a,v)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--calls',type=int,default=18000);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 raw=SOURCE.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED and len(raw)==32896 and raw[112:120]==bytes(8)and raw[123]==0
 base,init,play=struct.unpack_from('<HHH',raw,8);assert(base,init,play)==(32768,40832,32768)
 seen=set();data_reads=set();access={};parts=set();apu={};ram=set();songs={};allIO=Counter()
 for song in TRACKS:
  m=Bus(raw);c=NesMPU(memory=m);origin={};regs=dict(a=None,x=None,y=None);minimum=255
  def effective(pc,mode):
   v=m[pc+1];word=v+256*m[pc+2]
   if mode=='zpg':return v
   if mode=='zpx':return(v+c.x)&255
   if mode=='zpy':return(v+c.y)&255
   if mode=='abs':return word
   if mode=='abx':return(word+c.x)&65535
   if mode=='aby':return(word+c.y)&65535
   if mode in ['inx','iny','ind']:
    ptr=(v+c.x)&255 if mode=='inx'else v if mode=='iny'else word;hi=(ptr+1)&255 if mode!='ind'else(ptr&65280)|((ptr+1)&255)
    at=m[ptr]+256*m[hi]
    if at>=32768 and origin.get(ptr)is not None and origin.get(hi)is not None:parts.add((origin[ptr],origin[hi]))
    return(at+(c.y if mode=='iny'else 0))&65535
   return None
  def call(pc,number=None):
   nonlocal minimum
   c.pc=pc;c.sp=253;c.p=36;c.a=number if number is not None else 0;c.x=c.y=0
   m[510]=255;m[511]=126;m.events=[];before=c.processorCycles
   if number is not None:regs.update(a=None,x=None,y=None)
   for _ in range(100000):
    if c.pc==0x7f00:break
    pc=c.pc;assert pc>=32768,hex(pc);seen.add(pc);op,mode=c.disassemble[m[pc]];at=effective(pc,mode);minimum=min(minimum,c.sp)
    if at is not None:
     access.setdefault(pc,set()).add(at)
     if at<0x2000:ram.add(at)
    if op in ['LDA','LDX','LDY']:
     regs[op[-1].lower()]=at if at is not None and at>=32768 else pc+1 if mode=='imm'else origin.get(at)
     if at is not None and at>=32768:data_reads.add(at)
    elif op in ['STA','STX','STY']:
     origin[at]=regs[op[-1].lower()]
     if at is not None and 0x4000<=at<=0x4017:apu.setdefault(pc,set()).add(at)
    elif op in ['TAX','TAY']:regs[op[-1].lower()]=regs['a']
    elif op in ['TXA','TYA']:regs['a']=regs[op[1].lower()]
    elif op in ['PLA','ADC','SBC','AND','ORA','EOR','ASL','LSR','ROL','ROR']:regs['a']=None
    elif op in ['INX','DEX']:regs['x']=None
    elif op in ['INY','DEY']:regs['y']=None
    if op in ['INC','DEC','ASL','LSR','ROL','ROR']and at is not None:origin[at]=None
    c.step()
   else:raise AssertionError(('Timeout',song,hex(c.pc)))
   assert c.sp==255
   return dict(cycles=c.processorCycles-before,writes=m.events[:],active=m[246],ram=list(m[1792:1840]),zp=list(m[240:256]))
  calls=[call(init,song-1)];complete=[]
  for i in range(a.calls):
   q=call(play);calls.append(q)
   if q['active']==0 and(not i or calls[-2]['active']!=0):complete.append(i)
  assert not m.high and not m.io,(m.high,m.io)
  packed=gzip.compress(json.dumps(calls,separators=(',',':')).encode(),mtime=0);f=a.output/f'song-{song:02d}.json.gz';f.write_bytes(packed)
  costs=[q['cycles']for q in calls[1:]];allIO.update(m.io)
  songs[str(song)]=dict(calls=a.calls,source_complete_calls=complete,mean_cycles=sum(costs)/len(costs),peak_cycles=max(costs),init_cycles=calls[0]['cycles'],minimum_source_SP=minimum,APU_writes=sum(len(q['writes'])for q in calls),DMC_active_calls=sum(any(at==0x4015 and v&16 for at,v in q['writes'])for q in calls),capture_sha256=hashlib.sha256(packed).hexdigest())
  print(song,songs[str(song)],flush=True)
 q=dict(passed=True,accepted=False,source=str(SOURCE),source_sha256=EXPECTED,init=init,play=play,source_period_us=struct.unpack_from('<H',raw,110)[0],seen_instructions=sorted(seen),ROM_data_reads=sorted(data_reads),pointer_components=sorted(map(list,parts)),accesses={str(k):sorted(v)for k,v in access.items()},APU_stores={str(k):sorted(v)for k,v in apu.items()},RAM_accesses=sorted(ram),songs=songs,unmodeled_IO_reads=dict(allIO),tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Original source calls and complete-song music-only footprint, not a hardware capture or integrated engine. Source SFX queues remain zero; nine declared music tracks only. No host auto-advance or fabricated loop.' )
 (a.output/'coverage.json').write_text(json.dumps(q,indent=2));print('COMPLETE',len(seen),len(data_reads),sorted(parts))
if __name__=='__main__':main()
