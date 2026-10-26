"""Finite SPSC admission, original voice schedules, real lag-NMI producer boundaries."""
from pathlib import Path
import argparse,copy,hashlib,itertools,json,re
from check_tmnt_render_oa import load,address,location
from cv3_remaining_sfx_queue256_support_v1 import init,sound,EVENTS,target_voices,source_voices
from cv3_primary_sfx_source_v1 import Original,CV3
from cv3_dmc_complete_cpu_v1 import apu,regs
from verify_native_relocation import NesMPU

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def slot(q):return(q.get('Cv3FxQueueHead')-q.get('Cv3FxQueueTail'))&255
def setup(b,age=0,event=None,counter=0):
 q=init(b,2);q.put(Cv3FxQueueHead=counter,Cv3FxQueueTail=counter,Cv3FxQueueOverflow=0)
 if event:
  sound(q,event)
  for _ in range(age):q.invoke('AudioUpdate')
 q.put(NmiDisable=255,NmiSkipped=0,DisableScreenFlag=0,Sprite0HitDetectFlag=1,Mirror_PPUMASK=30,Mirror_PPUCTRL=128,CurrentBank=212,CurrentBankC=156)
 q.m[0x5115]=212;q.m.page(1,84);q.m.page(2,28);return q
def start(q,name='Cv3FxProducerFast',a=5):
 bank=(location(q.b,name)-16)//8192;pc=address(q.b,name);q.m.page(1,bank);q.put(CurrentBank=128|bank);q.m[0x5115]=128|bank;q.m.writes=[]
 c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,3,0x71,0x69,0xfd;c.stPushWord(0x5aff);return c
def finish(c,limit=3000):
 for _ in range(limit):
  if c.pc==0x5b00:return
  c.step()
 raise AssertionError(('main timeout',hex(c.pc)))
def nmi(q,c):
 resume,sp,registers=c.pc,c.sp,regs(c);begin=c.processorCycles;at=len(q.m.writes);c.nmi();assert c.pc==address(q.b,'NonMaskableInterrupt')
 for count in range(50000):
  if c.pc==resume and c.sp==sp:
   assert regs(c)==registers,('NMI registers',registers,regs(c));return dict(instructions=count,cycles=c.processorCycles-begin,APU=[w for w in q.m.writes[at:]if 0x4000<=w[0]<=0x4017])
  c.step()
 raise AssertionError(('NMI timeout',hex(c.pc),q.m.banks))
def memory(q):return bytes(q.m[i]for i in range(0x8000)if not 0x100<=i<0x200)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);old=load(a.rom.parent/'baseline.nes');raw=CV3.read_bytes();schedules=[]
 # Original requests and tick execution define raw source order and independent
 # voice lifetimes. Compare ordered source-owned native register image stores;
 # the normal final target hardware flush retains its established order.
 for event,mode in itertools.product(EVENTS,[0,1]):
  q=init(b,2 if event in[0x24,0x21,0x1e]else 3);q.put(CrossoverBehaviorVersion=mode);sound(q,event);o=Original(raw);o.call(0xe227);o.call(0xe25f,a=event);frames=[]
  for frame in range(100):
   before=source_voices(o);o.m.trace=[];o.call(0xe24e);c,_=q.invoke('AudioUpdate')
   for idx,registers in[(0,[0x4000,0x4001,0x4002,0x4003]),(1,[0x400c,0x400e,0x400f])]:
    if before[idx]:
     expected=sorted((r['address'],r['value'])for r in o.m.trace if r['address']in registers);actual=sorted(w for w in apu(q)if w[0]in registers);assert actual==expected,(hex(event),mode,frame,idx,actual,expected)
   assert target_voices(q)==source_voices(o),(hex(event),mode,frame,target_voices(q),source_voices(o));frames.append(c.processorCycles)
  assert q.get('Cv3FxOwned')==q.get('Cv3NoiseActive')==0 and slot(q)==0
  schedules.append(dict(event=event,mode=mode,frames=100,cycles_min=min(frames),cycles_max=max(frames)))
 (a.output/'schedules.json').write_text(json.dumps(schedules,indent=2)+'\n')
 priorities=[]
 for current,incoming,age in itertools.product(EVENTS,EVENTS,[0,1,5,12,27,42,88]):
  q=init(b);sound(q,current);o=Original(raw);o.call(0xe227);o.call(0xe25f,a=current)
  for _ in range(age):q.invoke('AudioUpdate');o.call(0xe24e)
  sound(q,incoming);o.call(0xe25f,a=incoming);wanted=source_voices(o);o.m.trace=[];o.call(0xe24e);q.invoke('AudioUpdate')
  for idx,registers in[(0,[0x4000,0x4001,0x4002,0x4003]),(1,[0x400c,0x400e,0x400f])]:
   if wanted[idx]:
    expected=sorted((r['address'],r['value'])for r in o.m.trace if r['address']in registers);actual=sorted(w for w in apu(q)if w[0]in registers);assert actual==expected,(hex(current),hex(incoming),age,idx,actual,expected)
  assert target_voices(q)==source_voices(o),(current,incoming,age,target_voices(q),source_voices(o));priorities.append(dict(current=current,incoming=incoming,age=age))
 (a.output/'priorities.json').write_text(json.dumps(priorities,separators=(',',':'))+'\n')
 # Full counters wrap independently from the slot mask. All64 slots can be
 # committed without overwrite; a defensive65th request leaves them intact.
 ring=[]
 for counter in range(256):
  q=init(b,2);q.put(Cv3FxQueueHead=counter,Cv3FxQueueTail=counter,Cv3FxQueueOverflow=0)
  for i in range(64):q.invoke('Cv3FxProducer',a=1+i%5,x=3)
  assert slot(q)==64;slots=[q.get('Cv3FxQueue',i)for i in range(256)];head=q.get('Cv3FxQueueHead');q.invoke('Cv3FxProducer',a=5,x=3)
  assert q.get('Cv3FxQueueHead')==head and q.get('Cv3FxQueueOverflow')==1 and slots==[q.get('Cv3FxQueue',i)for i in range(256)]
  q.invoke('AudioUpdate');assert slot(q)==0 and q.get('Cv3FxNoiseID')==0x24 and q.get('Cv3FxPulseID')==0x24;ring.append(dict(counter=counter,committed=64,overflow_rejected_without_overwrite=True))
 (a.output/'ring.json').write_text(json.dumps(ring,separators=(',',':'))+'\n')
 boundaries=[]
 for event,age,counter,incoming in itertools.product([None,0x1f,0x21],[0,12],[0,255],[1,4,5,6]):
  # Each instruction boundary independently gets a complete real lag NMI.
  probe=setup(b,age,event,counter);c=start(probe,a=incoming);trace=[];initial=probe.get('Cv3FxQueueHead');legacy=probe.get('AvAudioRequest');
  published=False
  for _ in range(300):
   if c.pc==0x5b00:break
   pc=c.pc;write_at=len(probe.m.writes);c.step();published|=any(at in [address(b,'Cv3FxQueueHead'),address(b,'AvAudioRequest')]for at,v in probe.m.writes[write_at:]);trace.append(dict(pc=pc,committed=published))
  else:raise AssertionError('producer trace timeout')
  for boundary in range(len(trace)+1):
   q=setup(b,age,event,counter);c=start(q,a=incoming)
   for _ in range(boundary):c.step()
   committed=trace[boundary-1]['committed']if boundary else False;before=regs(c);receipt=nmi(q,c);assert regs(c)==before;finish(c)
   ref=setup(b,age,event,counter);d=start(ref,a=incoming)
   if committed:finish(d);expected=nmi(ref,d)
   else:expected=nmi(ref,d);finish(d)
   assert receipt['APU']==expected['APU'],('publication APU',event,age,counter,incoming,boundary,committed)
   assert memory(q)==memory(ref),('publication RAM',event,age,counter,incoming,boundary,committed,[(hex(i),q.m[i],ref.m[i])for i in range(0x8000)if not 0x100<=i<0x200 and q.m[i]!=ref.m[i]][:10])
   assert q.m.banks==ref.m.banks and(c.x,c.p&12,c.sp)==(3,0x69&12,253)and slot(q)<=1
   boundaries.append(dict(current=event,age=age,counter=counter,incoming=incoming,boundary=boundary,committed=committed,**{k:v for k,v in receipt.items()if k!='APU'}))
 (a.output/'nmi-boundaries.json').write_text(json.dumps(boundaries,separators=(',',':'))+'\n')
 result=dict(passed=True,accepted=False,status='INITIAL_QUEUE_CPU_PASSED_NOT_NATIVE_READY',ROM_sha256=sha(a.rom),held_parent_ROM_sha256=sha(a.rom.parent/'baseline.nes'),source_schedule_cases=len(schedules),strict_source_priority_cases=len(priorities),ring_full_wrap_cases=len(ring),real_full_lag_NMI_producer_instruction_boundaries=len(boundaries),all_raw_source_values_including400F_exact=True,scope='Initial original-source/actual producer/NMI protocol checks. Full scene/death/reset/ordinary/IRQ/cost/source catalog qualification still required. No native timing or adoption.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
