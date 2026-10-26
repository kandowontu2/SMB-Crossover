"""Actual cold lag-NMI at every fast producer boundary, with retained unsafe control."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_dmc_complete_cpu_v1 import regs,apu
from cv3_remaining_sfx_queue256_cpu_v1 import setup,start,finish
from cv3_remaining_sfx_queue256_support_v1 import target_voices
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fields(q):return[(address(q.b,n)+i,q.m[address(q.b,n)+i])for n,ii in [('NextBank_SMC',[1]),('SafecallA_SMC',[1]),('SafereturnA_SMC',[1]),('FarcallJmpTarget_SMC',[1,2])]for i in ii]
def actual_nmi(q,c,slot_address=None):
 resume,sp,r=c.pc,c.sp,regs(c);bank=list(q.m.banks);shadow=[q.get(n)for n in ['CurrentBank','CurrentBankC']];smc=fields(q);begin=c.processorCycles;write_at=len(q.m.writes);wrong=[];minsp=sp;c.nmi()
 for steps in range(60000):
  if c.pc==resume and c.sp==sp:
   assert regs(c)==r and list(q.m.banks)==bank and [q.get(n)for n in['CurrentBank','CurrentBankC']]==shadow and fields(q)==smc
   return dict(instructions=steps,cycles=c.processorCycles-begin,minSP=minsp,slot_writes=wrong,APU=[w for w in q.m.writes[write_at:]if 0x4000<=w[0]<=0x4017])
  pc=c.pc;at=len(q.m.writes);before=q.m[slot_address]if slot_address is not None else None;physical=list(q.m.banks);c.step();minsp=min(minsp,c.sp)
  if slot_address is not None:
   for ad,v in q.m.writes[at:]:
    if ad==slot_address:wrong.append(dict(PC=pc,physical_banks=physical,address=ad,before=before,value=v,cycles_after_entry=c.processorCycles-begin))
 raise AssertionError(('Cold NMI timeout',hex(c.pc)))
def compare(q,r):
 changes=[(hex(i),q.m[i],r.m[i])for i in range(0x8000)if not 0x100<=i<0x200 and q.m[i]!=r.m[i]];assert not changes,changes[:12]
 assert q.m.banks==r.m.banks
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--unsafe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b,unsafe=load(a.rom),load(a.unsafe);rows=[]
 def make(z,event,age,counter,area,pause):
  q=setup(z,age,event,counter);q.put(GuestAudioCharacter=255,RgAudioCharacter=255,AreaMusicQueue=area,GamePauseStatus=pause);return q
 # The unsafe donor is otherwise the same protocol. A cold original upper
 # clear must overwrite a real uncommitted slot before the producer resumes.
 q=make(unsafe,None,0,255,0,0);c=start(q,a=5);slot_address=address(unsafe,'Cv3FxQueue')+255
 for _ in range(100):
  at=len(q.m.writes);c.step()
  if(slot_address,5)in q.m.writes[at:]:break
 else:raise AssertionError('Unsafe control never wrote slot')
 assert q.get('Cv3FxQueueHead')==255 and q.m[slot_address]==5;bad=actual_nmi(q,c,slot_address);finish(c);assert bad['slot_writes']and q.m[slot_address]==0
 q.invoke('AudioUpdate');assert target_voices(q)==(0,0);negative=dict(ROM_sha256=sha(a.unsafe),status='EXPECTED_FIRST_WRONG_COLD_WRITE_AND_LOST_CUE',queue_slot=slot_address,first_wrong_write=bad['slot_writes'][0],published_head_after_resume=q.get('Cv3FxQueueHead'),after_real_next_audio_voices=target_voices(q),actual_NMI=bad)
 (a.output/'unsafe-first-write.json').write_text(json.dumps(negative,indent=2)+'\n')
 for event,age,counter,typ,area,pause in itertools.product([None,0x1f,0x21],[0,12],[0,63,255],[1,5,6],[0,1],[0,1]):
  probe=make(b,event,age,counter,area,pause);c=start(probe,a=typ);trace=[];committed=False
  for _ in range(100):
   if c.pc==0x5b00:break
   pc=c.pc;at=len(probe.m.writes);c.step();committed|=any(ad==address(b,'Cv3FxQueueHead')for ad,v in probe.m.writes[at:]);trace.append(dict(PC=pc,committed=committed))
  for boundary in range(len(trace)+1):
   q=make(b,event,age,counter,area,pause);c=start(q,a=typ)
   for _ in range(boundary):c.step()
   receipt=actual_nmi(q,c,address(b,'Cv3FxQueue')+counter);finish(c);committed=trace[boundary-1]['committed']if boundary else False;ref=make(b,event,age,counter,area,pause);d=start(ref,a=typ)
   if committed:finish(d);expected=actual_nmi(ref,d)
   else:expected=actual_nmi(ref,d);finish(d)
   assert not receipt['slot_writes'],'The CV1 wrapper still touched the physical queue';assert receipt['APU']==expected['APU'];compare(q,ref)
   q.put(GamePauseStatus=0);ref.put(GamePauseStatus=0);q.invoke('AudioUpdate');ref.invoke('AudioUpdate');assert apu(q)==apu(ref);compare(q,ref)
   rows.append(dict(event=event,age=age,counter=counter,type=typ,area_request=area,pause=pause,boundary=boundary,committed_before_NMI=committed,actual_NMI_instructions=receipt['instructions'],actual_NMI_cycles=receipt['cycles'],minSP=receipt['minSP']))
 (a.output/'boundaries.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),unsafe_ROM_sha256=sha(a.unsafe),actual_cold_NMI_producer_boundaries=len(rows),first_wrong_negative=negative['first_wrong_write'],all_nonstack_RAM_next_audio_AXYP_SP_fiveSMC_mapper_exact=True,all_safe_cold_upper_queue_writes=0,scope='Assembled actual cold lag-NMI and next real AudioUpdate. Head-before-slot/after-slot/publication/reset/paused/new-music states; full byte counters and all imported cold owner writes. No native CPU/PPU/DMA deadline or source storage adoption claim.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
