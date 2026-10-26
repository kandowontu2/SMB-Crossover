"""Read-only measured common-audio spans and actual duplicate cleanup callers."""
from pathlib import Path
from collections import Counter
import argparse,json,traceback
import smb3_host_current3b_cpu_v1 as core
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

P=core.D/'smb3-host-hot6-v2';N=core.D/'smb3-host-current3b-native-ready-v1'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True);b=scoped_load(P/'candidate.nes');assert core.sha(P/'candidate.nes')=='64ccd5038c26cabd3c57c4c3ed13b1fe467b275238610f3a227ceaa48e1ac2b6'
 names=['GuestAudioBegin','GuestAudioFinish','GuestAudioNativeFlush','GuestExpansionFlush','GuestExpansionSweepClock','GuestExpansionSweepTarget','BassAudioBegin','MegaManRushLandCharacterReset','X5NativeNoiseMask','Cv3DmcResetOwner','Cv3FxOwnerInit'];ranges=[]
 for n in names:
  s=b['syms'][n];lo=address(b,n);size=int(s['size'],0);bank=(location(b,n)-16)//8192;assert bank==29 and size>0,(n,s);ranges.append((lo,lo+size,n))
 assert all(x[1]<=y[0]for x,y in zip(sorted(ranges),sorted(ranges)[1:])),ranges
 begin=address(b,'GuestAudioBegin');cost=Counter();pcost=Counter();cleanups=[];pending=[]
 class CPU(core.NesMPU):
  def step(self):
   m=self.memory;host=isinstance(m,core.HostMemory)
   if not host:return super().step()
   pc=self.pc;bank=m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
   if pending and pc==pending[-1]['return_PC']and self.sp==pending[-1]['entry_SP']:
    r=pending.pop();r['cycles']=self.processorCycles-r.pop('start');r['exit_AXYP_SP']=[self.a,self.x,self.y,self.p&207,self.sp];r['ordered_writes']=[(at,v)for at,v in m.writes[r.pop('write_start'):]if not 256<=at<512];cleanups.append(r)
   if bank==29 and m[pc]==0x20 and (m[pc+1]|m[pc+2]<<8)==address(b,'BassAudioBegin'):
    pending.append(dict(caller_PC=pc,return_PC=pc+3,entry_SP=self.sp,start=self.processorCycles,write_start=len(m.writes),entry_AXYP_SP=[self.a,self.x,self.y,self.p&207,self.sp]))
   before=self.processorCycles;out=super().step();elapsed=self.processorCycles-before
   if bank==29:
    selected=[n for lo,hi,n in ranges if lo<=pc<hi];g=selected[0]if selected else'OriginalSharedSfx'if 0xa000<=pc<begin else'other-bank29';cost[g]+=elapsed;pcost[(g,pc)]+=elapsed
   return out
 try:
  core.NesMPU=CPU
  world=[json.loads(s)for s in (N/'native/smb3-music-native.jsonl').read_text().splitlines()];world=[r for r in world if r['kind']=='whole-audio-return'and r['entry']['frame']>=433];assert len(world)==768
  f=core.Fixture(b,0,0);whole=[];cold=None
  for tick,r in enumerate(world):
   for name,v in zip(['Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'],r['worldQueues']):f.q.set(name,v)
   n=f.invoke(('AreaMusicQueue',1)if tick==0 else None,flags=0x24);assert not pending
   if tick==0:cold=dict(whole=n,bank29=dict(cost));cost.clear();pcost.clear();cleanups.clear()
   else:whole.append(n)
  callers=sorted(set(r['caller_PC']for r in cleanups));bycaller=[]
  for pc in callers:
   rr=[r for r in cleanups if r['caller_PC']==pc];bycaller.append(dict(caller_PC=pc,calls=len(rr),total=sum(r['cycles']for r in rr),mean=sum(r['cycles']for r in rr)/len(rr),minimum=min(r['cycles']for r in rr),maximum=max(r['cycles']for r in rr),first_call=rr[0]))
  assert len(callers)==2 and all(r['calls']==767 for r in bycaller)
  summary=dict(passed=True,source_only=True,native_run=False,ROM_sha256=core.sha(P/'candidate.nes'),calls=767,actual_opening_queues_sha256=core.sha(N/'native/smb3-music-native.jsonl'),cold=cold,whole_mean=sum(whole)/len(whole),bank29_total=sum(cost.values()),bank29_mean=sum(cost.values())/767,exclusive_spans=[dict(name=n,start=lo,end=hi)for lo,hi,n in ranges],exclusive_instruction_costs={n:dict(total=v,mean=v/767)for n,v in sorted(cost.items())},actual_BassAudioBegin_callers=bycaller,top_instruction_costs=[dict(owner=g,PC=pc,total=v,mean=v/767)for(g,pc),v in pcost.most_common(35)],source_original_sameinput_assertions_preserved=True,checker_sha256=core.sha(__file__),limits='Same arranged I1 wholeAudio source CPU fixture; real incoming queues only, not full native entryRAM/PPU/interrupt/DMC-DMA. Declared actual symbol extents partition bank29; no invented function labels. Observes genuine JSR entry/return/SP for duplicate cleanup. No code or source/state/APU/output change. Any removal needs cold/owner/first-reset/intermediate-observation proof before implementation.')
  core.put(a.output/'proof.json',summary);print(json.dumps(dict(passed=True,bank29_mean=summary['bank29_mean'],exclusive_instruction_costs=summary['exclusive_instruction_costs'],callers=bycaller)))
 except Exception as e:core.put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
