"""Paired exact common-audio whole-call state/bus and practical opening cost."""
from pathlib import Path
import argparse,json,traceback
import smb3_host_current3b_cpu_v1 as core
from smb3_host_current3b_owners_v2 import PeripheralMemory
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import Memory,address

N=core.D/'smb3-host-current3b-native-ready-v1'
class CaptureCPU(core.NesMPU):
 def step(self):
  m=self.memory
  if not isinstance(m,Memory):return super().step()
  b=m.b if hasattr(m,'b')else self.host_bundle
  pc=self.pc;bank=m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
  if pc==address(b,'AudioUpdate'):m.removed_first=set();m.first_pending=None
  first=address(b,'GuestAudioBegin')+7
  if bank==29 and pc==first:m.first_pending=(len(m.writes),self.sp)
  if bank==29 and pc==first+3 and m.first_pending and self.sp==m.first_pending[1]:m.removed_first.update(range(m.first_pending[0],len(m.writes)));m.first_pending=None
  m.pc=pc;out=super().step()
  if self.pc==0x5b00:m.finalregs=[self.a,self.x,self.y,self.p&207,self.sp]
  return out

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);layout=json.loads((a.packet/'layout.json').read_text());base=Path(layout['parent_directory']);bs=[scoped_load(q/'candidate.nes')for q in [base,a.packet]];rows=[]
 try:
  core.NesMPU=CaptureCPU;world=[json.loads(s)for s in (N/'native/smb3-music-native.jsonl').read_text().splitlines()];world=[r for r in world if r['kind']=='whole-audio-return'and r['entry']['frame']>=433];assert len(world)==768
  if layout['parent_name']=='hot6':qs=[core.Fixture(b,0,0)for b in bs]
  else:
   qs=[]
   for b in bs:
    q=Arena(b,17);q.m=PeripheralMemory(b);q.put(SelectedCharacter=17,CrossoverBehaviorVersion=0,M3Variant=0,PlayerStatus=1,OperMode=1,GameEngineSubroutine=8,XgAudioCharacter=255,GuestAudioCharacter=255,GamePauseStatus=0);qs.append(q)
  def mem(q):return q.m
  def setq(q,n,v):q.q.set(n,v)if hasattr(q,'q')else q.set(n,v)
  def invoke(q,b,tick):
   if hasattr(q,'q'):return q.invoke(('AreaMusicQueue',1)if tick==0 else None,flags=0x24)
   if tick==0:q.set('AreaMusicQueue',1)
   m=q.m;m.writes=[];c=CaptureCPU(memory=m);c.host_bundle=b;c.pc=address(b,'AudioUpdate');c.a=c.x=c.y=0;c.p=0x24;c.sp=253;c.stPushWord(0x5aff)
   for _ in range(100000):
    if c.pc==0x5b00:break
    c.step()
   else:raise AssertionError(('Generic wholeAudio timeout',hex(c.pc)))
   assert c.sp==253;return c.processorCycles
  for tick,r in enumerate(world):
   cc=[]
   for q,b in zip(qs,bs):
    for n,v in zip(['Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'],r['worldQueues']):setq(q,n,v)
    cc.append(invoke(q,b,tick))
   m0,m1=map(mem,qs);raw=lambda m:bytes(m[:256]+m[512:2048]+m[0x6000:0x8000]);assert raw(m0)==raw(m1),('All RAM/OAM including private adapter state',tick)
   assert m0.finalregs==m1.finalregs and m0.banks==m1.banks and m0.hw==m1.hw,('Whole AXYP/SP/banks/hardware',tick)
   bus=lambda m,removed:[(at,v)for i,(at,v)in enumerate(m.writes)if not 256<=at<512 and (not removed or i not in m.removed_first)]
   assert bus(m0,True)==bus(m1,False),('Literal whole bus except genuine removed first cleanup',tick)
   assert cc[1]<=cc[0],('Slower practical whole call',tick,cc)
   rows.append(dict(call=tick,cold=tick==0,before=cc[0],after=cc[1],delta=cc[1]-cc[0],removed_duplicate_nonstack_stores=sum(not 256<=m0.writes[i][0]<512 for i in m0.removed_first)))
  hot=rows[1:]
  core.put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=core.sha(base/'candidate.nes'),ROM_sha256=core.sha(a.packet/'candidate.nes'),calls=768,cold_delta=rows[0]['delta'],steady_before_mean=sum(r['before']for r in hot)/767,steady_after_mean=sum(r['after']for r in hot)/767,steady_delta_mean=sum(r['delta']for r in hot)/767,steady_delta_range=[min(r['delta']for r in hot),max(r['delta']for r in hot)],all_nonstack_application_RAM_OAM_private_images_AXYP_SP_hw_and_final_banks_literal=True,ordered_whole_bus_after_only_actual_first_cleanup_span_removed_exact=True,original_SMB3_sameinput_oracle=layout['parent_name']=='hot6',per_call=rows,actual_incoming_queue_source_sha256=core.sha(N/'native/smb3-music-native.jsonl'),checker_sha256=core.sha(__file__),limits='Arranged I1 CPU states using actual767 incoming world queues. Not complete native entryRAM/PPU/DMC-DMA/IRQ clocks. Original source oracle executes only for the private hot6 SMB3 parent; independent current3b uses its existing recorded/native dispatch. No native cadence acceptance.'))
  print(json.dumps(dict(passed=True,parent=layout['parent_name'],cold_delta=rows[0]['delta'],steady_delta_mean=sum(r['delta']for r in hot)/767,steady_delta_range=[min(r['delta']for r in hot),max(r['delta']for r in hot)])))
 except Exception as e:core.put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),calls_done=len(rows)));raise
if __name__=='__main__':main()
