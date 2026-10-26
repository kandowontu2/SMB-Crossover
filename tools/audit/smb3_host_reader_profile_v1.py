"""Source-only opcode cost split of held7469, using the recorded opening cues."""
from pathlib import Path
from collections import Counter
import argparse,bisect,json,traceback
import smb3_host_current3b_cpu_v1 as core
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load

P=core.D/'smb3-host-current3b-v3';N=core.D/'smb3-host-current3b-native-ready-v1'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=scoped_load(P/'candidate.nes');assert core.sha(P/'candidate.nes')=='7469d9f62af3161c896b844546ead66002bb425ba8b5143692b1c2ae1d9f1219'
 costs=Counter();pcs=Counter();readpages=Counter();readsites=Counter();bankwrites=Counter();calls=Counter();source_original=0
 # Genuine top-level B3 labels own contiguous helper spans; source-site labels
 # are separately classified, so local generated symbols cannot invent costs.
 labels=[]
 for n,s in b['syms'].items():
  if not n.startswith('B3')or'::'in n or n.startswith('B3Source')or s.get('type')!='lab':continue
  try:at=location(b,n);bank=(at-16)//8192
  except (AssertionError,KeyError,TypeError):continue
  if bank in [38,86]:labels.append((bank,address(b,n),n))
 labels.sort();ranges={bank:sorted((pc,n)for page,pc,n in labels if page==bank)for bank in [38,86]}
 starts={bank:[pc for pc,n in rows]for bank,rows in ranges.items()}
 def routine(pc,bank):
  rows=ranges.get(bank,[]);i=bisect.bisect_right(starts.get(bank,[]),pc)-1
  return rows[i][1]if i>=0 else'original-sites'
 def group(pc,bank,inside):
  n=routine(pc,bank)
  if inside:
   if bank==86 or bank==38 and pc<address(b,'B3ReadAbsX'):return'original-sites/native-translation'
   if n.startswith('B3Known'):return'known-readers'
   if n.startswith('B3Read')or n=='B3BorrowPointer':return'generic-readers'
   if n.startswith('B3Image'):return'APU-image-writers'
   if n.startswith('B3Write')or n.startswith('B3Sample'):return'DMC-status-address-adapter'
   return'inside-source/other:'+n
  if n in ['B3Borrow','B3Restore']:return'host-ZP-borrow-restore'
  if bank in [38,86]and n.startswith('B3'):return'host-B3-adapter:'+n
  return'host-other/bank'+str(bank)
 class ProfileMemory(core.HostMemory):
  def __getitem__(self,at):
   value=super().__getitem__(at)
   if isinstance(at,int)and self.in_source and 0xb000<=at<0xc000 and self.banks[1]in [78,86,90,93,95,96,98,118,119]:
    page=[78,86,90,93,95,96,98,118,119].index(self.banks[1]);key=(page,(at&4095)//256);readpages[key]+=1;readsites[(self.pc,page,at&4095)]+=1
   return value
  def __setitem__(self,at,v):
   if isinstance(at,int)and at in [0x5115,0x5116,0x5117]:bankwrites[(self.in_source,at)]+=1
   super().__setitem__(at,v)
 class ProfileCPU(core.NesMPU):
  def step(self):
   m=self.memory;native=isinstance(m,ProfileMemory);pc=self.pc;bank=m.banks[(pc-0x8000)//8192]if native and pc>=0x8000 else-1;before=self.processorCycles
   if native:
    g=group(pc,bank,m.in_source)
    if m[pc]==0x20:
     target=m[pc+1]|m[pc+2]<<8;name=routine(target,m.banks[(target-0x8000)//8192])if target>=0x8000 else'RAM';calls[(m.in_source,name)]+=1
   out=super().step();elapsed=self.processorCycles-before
   if native:costs[g]+=elapsed;pcs[(bank,pc,g)]+=elapsed
   else:costs['ORIGINAL-source-engine']+=elapsed
   return out
 try:
  core.HostMemory=ProfileMemory;core.NesMPU=ProfileCPU
  rows=[json.loads(z)for z in(N/'native/smb3-music-native.jsonl').read_text().splitlines()];world=[r for r in rows if r['kind']=='whole-audio-return'and r['entry']['frame']>=433];assert len(world)==768
  f=core.Fixture(b,0,0);cold=None;whole=[]
  for tick,row in enumerate(world):
   for name,value in zip(['Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'],row['worldQueues']):f.q.set(name,value)
   n=f.invoke(('AreaMusicQueue',1)if tick==0 else None,flags=0x24)
   if tick==0:
    cold=dict(whole=n,costs=dict(costs));costs.clear();pcs.clear();readpages.clear();readsites.clear();bankwrites.clear();calls.clear()
   else:whole.append(n)
  assert len(f.sourcecalls)==768
  top=[dict(payload_page=page,offset_lo=slice*256,offset_hi=slice*256+255,reads=n)for(page,slice),n in readpages.most_common()]
  native_sum=sum(n for g,n in costs.items()if g!='ORIGINAL-source-engine');assert native_sum==sum(whole)
  proof=dict(passed=True,source_only=True,native_run=False,ROM_sha256=core.sha(P/'candidate.nes'),actual_cue_source=str(N/'native/smb3-music-native.jsonl'),actual_cue_source_sha256=core.sha(N/'native/smb3-music-native.jsonl'),calls=767,cold=cold,steady_whole_mean=sum(whole)/767,steady_whole_peak=max(whole),exclusive_cycle_categories={g:dict(total=n,mean=n/767)for g,n in sorted(costs.items())},native_cycle_sum= native_sum,original_sameinput_reference_preserved=True,ordered_source_APU_RAM_virtualmaps_finalstate_AXYP_SP_assertions_preserved=True,physical_payload_256_slices=top,source_reader_data_reads=sum(readpages.values()),top4_slice_read_fraction=sum(r['reads']for r in top[:4])/sum(readpages.values()),source_PRG_register_writes=[dict(inside_source=inside,register=at,writes=n)for(inside,at),n in sorted(bankwrites.items())],actual_helper_call_counts=[dict(inside_source=inside,routine=name,calls=n)for(inside,name),n in sorted(calls.items())],top_native_instruction_costs=[dict(bank=bank,PC=pc,category=g,total=n)for(bank,pc,g),n in pcs.most_common(50)],checker_sha256=core.sha(__file__),limits='Arranged wholeAudioUpdate/source CPU replay using actual recorded incoming shared queues and767normal ticks with I1. Source sameinput reference remains exact. Omits actual Main/PPU/DMC-DMA/IRQ clocks and does not claim complete native entryRAM reproduction. Native elapsed1737 is not directly equated to this instruction-only partition. Cache feasibility/ownership and fresh native cadence remain separate.')
  core.put(a.output/'proof.json',proof);print(json.dumps({k:proof[k]for k in ['passed','steady_whole_mean','steady_whole_peak','exclusive_cycle_categories','top4_slice_read_fraction']}))
 except Exception as e:core.put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
