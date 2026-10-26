"""All-mask common flush and actual Begin cleanup/liveness caller controls."""
from pathlib import Path
from collections import Counter
import argparse,json,statistics,traceback
from smb3_host_current3b_cpu_v1 import D,sha,put
from smb3_host_current3b_owners_v2 import PeripheralMemory
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

def ordinary(m):return bytes(m[:256]+m[512:2048]+m[0x6000:0x8000])
class Probe(PeripheralMemory):
 def __init__(self,b):self.pc=0;self.window=False;self.window_reads=[];self.private={address(b,n)for n in ['BassAudioInit','BassAudioPreviousMask','BassAudioLastDeath','BassAudioLastGround','BassSourceId','BassDmcActive']};super().__init__(b)
 def __getitem__(self,at):
  v=super().__getitem__(at)
  if self.window and isinstance(at,int)and at in self.private:self.window_reads.append([self.pc,self.banks[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1,at,v])
  return v

def execute(b,m,name,flags=0x20):
 c=NesMPU(memory=m);c.pc=address(b,name);c.a=0x39;c.x=0x29;c.y=0x5a;c.p=flags;c.sp=0xf0;c.stPushWord(0x5aff);m.writes=[];trace=[];windowtrace=[];first_start=None;removed=set();infirst=False
 first=address(b,'GuestAudioBegin')+7;first_return=first+3;late=address(b,'GuestAudioBegin')+135
 # Verify actual bound JSR sites, not old numeric callable aliases.
 assert m[first]==0x20 and (m[first+1]|m[first+2]<<8)==address(b,'BassAudioBegin')
 assert m[late]==0x20 and (m[late+1]|m[late+2]<<8)==address(b,'BassAudioBegin')
 for _ in range(100000):
  if c.pc==0x5b00:break
  if name=='GuestAudioBegin':
   if c.pc==first:infirst=True;first_start=len(m.writes)
   if c.pc==first_return:
    if infirst:removed.update(range(first_start,len(m.writes)));infirst=False
    m.window=True
   if c.pc==late:m.window=False
  m.pc=c.pc;key=[c.pc,m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1]
  trace.append(key)
  if m.window:windowtrace.append(key)
  c.step()
 else:raise AssertionError(('Timeout',name,hex(c.pc)))
 m.window=False;assert c.sp==0xf0
 return dict(AXYP_SP=[c.a,c.x,c.y,c.p&207,c.sp],RAM=ordinary(m),banks=m.banks[:],hw=m.hw[:],bus=[(at,v)for at,v in m.writes if not 256<=at<512],bus_without_first_cleanup=[(at,v)for i,(at,v)in enumerate(m.writes)if not 256<=at<512 and i not in removed],cycles=c.processorCycles,windowtrace=windowtrace,windowreads=m.window_reads[:])

def memory(b,seed=0):
 m=Probe(b);m.page(1,29);m.page(2,38);m[address(b,'CurrentBank')]=157;m[address(b,'CurrentBankC')]=166
 for n in ['GuestNativeApu','GuestFxApu','GuestNativeDirty','GuestFxDirty','GuestApuLast']:
  lo=address(b,n)
  for i in range(16):m[lo+i]=(seed*71+i*23+11)&255
 return m
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);layout=json.loads((a.packet/'layout.json').read_text());base=Path(layout['parent_directory']);old,new=(scoped_load(q/'candidate.nes')for q in [base,a.packet]);exp=[];beg=[];read_diffs=Counter();cases={'mask_changed_dirty_image':0,'physical_flags':0,'cleanup_owners_coldwarm':0}
 try:
  # Prefix/sweep byte identity authenticates the unchanged original clocks.
  for lo,hi in [('GuestExpansionFlush','X5ExpansionOutputChannel2')]:pass
  at=address(old,'GuestExpansionFlush');prefix=address(old,'GuestExpansionFlush::Output')if 'GuestExpansionFlush::Output'in old['syms']else at+148
  # Output starts atAB49 in both literal current parents; do not invent an alias.
  prefix=0xab49
  def raw(b,pc,n):bank=29;return b['raw'][16+bank*8192+pc-0xa000:16+bank*8192+pc-0xa000+n]
  assert raw(old,at,prefix-at)==raw(new,at,prefix-at)
  assert raw(old,address(old,'GuestExpansionSweepClock'),address(old,'BassAudioBegin')-address(old,'GuestExpansionSweepClock'))==raw(new,address(new,'GuestExpansionSweepClock'),address(new,'BassAudioBegin')-address(new,'GuestExpansionSweepClock'))
  def flush(mask,changed,dirty,image,flags,period=0x345,control=0xa7):
   pair=[]
   for b in [old,new]:
    m=memory(b,image);m[address(b,'GuestMixMask')]=mask;m[address(b,'GuestMixChanged')]=changed
    for i in range(8):m[address(b,'GuestFxApu')+i]=(i*37+image*17+9)&255;m[address(b,'GuestExpansionLast')+i]=m[address(b,'GuestFxApu')+i]if image==0 else(i*41+3)&255;m[address(b,'GuestFxDirty')+i]=255 if dirty>>i&1 else 0
    m[address(b,'GuestSweepPeriod')]=period&255;m[address(b,'GuestSweepPeriod')+1]=period>>8;m[address(b,'GuestSweepControl')]=control;m[address(b,'GuestSweepDivider')]=image;m[address(b,'GuestSweepReload')]=image&1
    pair.append(execute(b,m,'GuestExpansionFlush',flags))
   x,y=pair
   assert {k:v for k,v in x.items()if k not in ['cycles','windowtrace','windowreads']}=={k:v for k,v in y.items()if k not in ['cycles','windowtrace','windowreads']},('Full flush state/bus/AXYP/SP',mask,changed,dirty,image,flags,period,control)
   assert y['cycles']<x['cycles'];exp.append(y['cycles']-x['cycles'])
  for mask in range(16):
   for changed in range(16):
    for dirty in [0,255,85,170,2,8]:
     for image in [0,1]:flush(mask,changed,dirty,image,0x24 if image else 0xed);cases['mask_changed_dirty_image']+=1
  for bits in range(64):
   flags=32|sum(1<<bit for j,bit in enumerate([0,1,2,3,6,7])if bits>>j&1)
   for mask in range(4):
    for changed in range(4):
     for period in [7,8,0x7ff]:flush(mask,changed,255,bits&1,flags,period,[0,0x87,0xff][period%3]);cases['physical_flags']+=1
  # Genuine first and second cleanup sites are instrumented separately. Only
  # old first-cleanup duplicate writes may be removed from the bus comparator.
  for char in range(20):
   for cold in [0,1]:
    for owner in range(5):
     for seed in [0,1,2]:
      for flags in [0x20,0xed]:
       pair=[]
       for b in [old,new]:
        m=memory(b,seed)
        for n,v in [('SelectedCharacter',char),('GuestAudioCharacter',(char+1)%20 if cold else char),('BassDmcActive',owner),('Cv3DmcPriority',128 if owner>=3 else seed),('Square1SoundQueue',seed*85),('Square2SoundQueue',seed*71),('NoiseSoundQueue',seed*43),('GuestWorldQueues',255),('Player_State',seed&1),('GameEngineSubroutine',8),('MmDeathFlag',seed&1)]:m[address(b,n)]=v
        for n in ['BassAudioInit','BassAudioPreviousMask','BassAudioLastDeath','BassAudioLastGround','BassSourceId']:m[address(b,n)]=(seed*83+17)&255
        m.page(3,125 if owner==3 else 70 if owner==4 and layout['parent_name']=='hot6'else 127);m.hwdmc=bool(owner);m.hw[21]=31 if owner else 15
        pair.append(execute(b,m,'GuestAudioBegin',flags))
       x,y=pair;keys=['AXYP_SP','RAM','banks','hw'];assert all(x[k]==y[k]for k in keys),('Begin state/ABI',char,cold,owner,seed,flags,[(k,x[k],y[k])for k in keys if x[k]!=y[k]][:1])
       if char>=6 and char!=9:
        assert x['bus_without_first_cleanup']==y['bus'],('Only duplicate first cleanup removed',char,cold,owner,seed,flags)
        assert x['windowtrace']==y['windowtrace'],('Intermediate routing differs',char,cold,owner,seed,flags)
        for r,s in zip(x['windowreads'],y['windowreads']):
         if r!=s:read_diffs[tuple(r[:3]+[r[3],s[3]])]+=1
        assert len(x['windowreads'])==len(y['windowreads'])
       else:assert x['bus']==y['bus']and x['cycles']==y['cycles'],('Unchanged selected owner path',char,cold,owner,seed,flags)
       beg.append(y['cycles']-x['cycles']);cases['cleanup_owners_coldwarm']+=1
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(base/'candidate.nes'),ROM_sha256=sha(a.packet/'candidate.nes'),cases=cases,expansion_cycle_delta=dict(min=min(exp),max=max(exp),mean=statistics.mean(exp)),begin_cycle_delta=dict(min=min(beg),max=max(beg)),all_flush_RAM_images_sweep_dirty_ordered_hardware_bus_AXYP_SP_exact=True,actual_duplicate_cleanup_only_removed=True,intermediate_compiled_PC_path_literal=True,intermediate_private_read_value_differences=[dict(PC=k[0],bank=k[1],address=k[2],old_value=k[3],new_value=k[4],cases=n)for k,n in sorted(read_diffs.items())],unmodified_original_sweep_prefix_and_both_sweep_helpers_literal=True,checker_sha256=sha(__file__),limits='Finite arranged assembled caller states and modeled DMC status, not physical PPU/APU/IRQ timing. Intermediate PC path is literal; changed private reads are enumerated rather than masked. Actual complete IRQ continuation and full-roster wholeAudio remain separate.'))
  print(json.dumps(dict(passed=True,cases=cases,expansion_delta=[min(exp),max(exp)],begin_delta=[min(beg),max(beg)],intermediate_read_differences=len(read_diffs))))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),cases=cases));raise
if __name__=='__main__':main()
