"""Matched whole-call/physical-store cost controls; no native emulator launch."""
from pathlib import Path
from collections import Counter
import argparse,json,traceback
import smb3_host_current3b_cpu_v1 as core
from smb3_host_current3b_cpu_v1 import D,Fixture,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

BASE=D/'smb3-host-current3b-v3';N=D/'smb3-host-current3b-native-ready-v1'
class CaptureCPU(core.NesMPU):
 def step(self):
  out=super().step()
  if self.pc==0x5b00 and isinstance(self.memory,core.HostMemory):self.memory.finalregs=[self.a,self.x,self.y,self.p&207,self.sp]
  return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True);old,new=(scoped_load(q/'candidate.nes')for q in [BASE,a.packet]);rows=[]
 try:
  source=[json.loads(s)for s in (N/'native/smb3-music-native.jsonl').read_text().splitlines()];world=[r for r in source if r['kind']=='whole-audio-return'and r['entry']['frame']>=433];assert len(world)==768
  core.NesMPU=CaptureCPU
  f0,f1=(Fixture(b,0,0)for b in [old,new]);private={address(new,'B3SavedY'),address(new,'B3Value')};diffs=Counter()
  def observable(f):
   # Full real RAM/OAM outside two explicitly private reader scratch bytes;
   # IO/ROM are assessed as ordered physical stores instead of flat bus bytes.
   return bytes(f.m[i]for i in list(range(256))+list(range(512,2048))+list(range(0x6000,0x8000))if i not in private)
  def events(f):return[(at,v)for at,v in f.m.writes if 0x4000<=at<=0x4017 or at in [0x5116,0x5117]]
  for tick,r in enumerate(world):
   costs=[]
   for f in [f0,f1]:
    for name,v in zip(['Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'],r['worldQueues']):f.q.set(name,v)
    costs.append(f.invoke(('AreaMusicQueue',1)if tick==0 else None,flags=0x24))
   assert observable(f0)==observable(f1),('Full nonprivate RAM/OAM',tick)
   assert f0.m.finalregs==f1.m.finalregs,('Whole AudioUpdate AXYP/SP',tick,f0.m.finalregs,f1.m.finalregs)
   assert events(f0)==events(f1),('Physical APU/E/C bank order',tick,events(f0),events(f1))
   assert f0.m.banks==f1.m.banks and f0.q.get('CurrentBank')==f1.q.get('CurrentBank')and f0.q.get('CurrentBankC')==f1.q.get('CurrentBankC')
   for at in private:
    if f0.m[at]!=f1.m[at]:diffs[at]+=1
   rows.append(dict(call=tick,cold=tick==0,baseline_cycles=costs[0],candidate_cycles=costs[1],delta=costs[1]-costs[0]))
  hot=rows[1:];worse=[r for r in hot if r['delta']>0];equal=[r for r in hot if r['delta']==0]
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(BASE/'candidate.nes'),ROM_sha256=sha(a.packet/'candidate.nes'),actual_recorded_queue_source_sha256=sha(N/'native/smb3-music-native.jsonl'),calls=len(rows),cold_delta=rows[0]['delta'],steady_mean_before=sum(r['baseline_cycles']for r in hot)/len(hot),steady_mean_after=sum(r['candidate_cycles']for r in hot)/len(hot),steady_mean_delta=sum(r['delta']for r in hot)/len(hot),per_call_delta_min=min(r['delta']for r in hot),per_call_delta_max=max(r['delta']for r in hot),slower_calls=len(worse),equal_calls=len(equal),faster_calls=len(hot)-len(worse)-len(equal),slower_rows=worse,full_nonprivate_RAM_OAM_and_ordered_physical_APU_E_C_stores_and_final_banks_exact=True,original_sameinput_source_AXYP_SP_RAM_APU_maps_asserted_inside_both_Fixtures=True,private_reader_scratch_difference_calls={hex(at):n for at,n in diffs.items()},per_call=rows,checker_sha256=sha(__file__),limits='Arranged wholeAudio CPU I1 continuations using actual767 opening input queue cells, not full native entryRAM/PPU/DMC-DMA/IRQ timing. B3Value/B3SavedY private liveness declaration separate; no whole-game cadence acceptance.'))
  print(json.dumps(dict(passed=True,calls=len(rows),steady_mean_delta=sum(r['delta']for r in hot)/len(hot),slower_calls=len(worse),equal_calls=len(equal),delta_min=min(r['delta']for r in hot),delta_max=max(r['delta']for r in hot))))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),calls_done=len(rows)));raise
if __name__=='__main__':main()
