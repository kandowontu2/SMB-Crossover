"""Read-only actual expansion-sweep target/clock ownership and liveness costs."""
from pathlib import Path
from collections import defaultdict
import argparse,json,traceback
import smb3_host_current3b_cpu_v1 as core
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

P=core.D/'smb3-host-hot6-v2';N=core.D/'smb3-host-current3b-native-ready-v1'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True);b=scoped_load(P/'candidate.nes');pending=[];observations=[]
 targets={address(b,n):n for n in ['GuestExpansionSweepClock','GuestExpansionSweepTarget']}
 def state(c,m):
  return dict(AXYP_SP=[c.a,c.x,c.y,c.p&207,c.sp],period=m[address(b,'GuestSweepPeriod'):address(b,'GuestSweepPeriod')+2],delta=m[address(b,'GuestSweepDelta'):address(b,'GuestSweepDelta')+2],control=m[address(b,'GuestSweepControl')],divider=m[address(b,'GuestSweepDivider')],reload=m[address(b,'GuestSweepReload')])
 class CPU(core.NesMPU):
  def step(self):
   m=self.memory
   if not isinstance(m,core.HostMemory):return super().step()
   pc=self.pc;bank=m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
   if pending and pc==pending[-1]['return_PC']and self.sp==pending[-1]['entry']['AXYP_SP'][-1]:
    r=pending.pop();r['exit']=state(self,m);r['cycles']=self.processorCycles-r.pop('start');r['period_changed']=r['exit']['period']!=r['entry']['period'];observations.append(r)
   if bank==29 and m[pc]==0x20:
    target=m[pc+1]|m[pc+2]<<8
    if target in targets:pending.append(dict(routine=targets[target],caller_PC=pc,return_PC=pc+3,entry=state(self,m),start=self.processorCycles))
   return super().step()
 try:
  core.NesMPU=CPU;world=[json.loads(s)for s in (N/'native/smb3-music-native.jsonl').read_text().splitlines()];world=[r for r in world if r['kind']=='whole-audio-return'and r['entry']['frame']>=433];assert len(world)==768;f=core.Fixture(b,0,0)
  for tick,r in enumerate(world):
   for name,v in zip(['Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'],r['worldQueues']):f.q.set(name,v)
   f.invoke(('AreaMusicQueue',1)if tick==0 else None,flags=0x24);assert not pending
   if tick==0:observations.clear()
  groups=defaultdict(list)
  for r in observations:
   control=r['entry']['control'];groups[(r['routine'],r['caller_PC'],bool(control&128),control&7)].append(r)
  stats=[]
  for (n,pc,enabled,shift),rows in sorted(groups.items()):stats.append(dict(routine=n,caller_PC=pc,sweep_enabled=enabled,shift=shift,calls=len(rows),cycles_total=sum(r['cycles']for r in rows),cycles_per_whole_update=sum(r['cycles']for r in rows)/767,minimum=min(r['cycles']for r in rows),maximum=max(r['cycles']for r in rows),period_changed_calls=sum(r['period_changed']for r in rows),first=rows[0]))
  core.put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=core.sha(P/'candidate.nes'),calls=767,actual_opening_queues_sha256=core.sha(N/'native/smb3-music-native.jsonl'),groups=stats,observations=len(observations),source_original_sameinput_contracts_preserved=True,checker_sha256=core.sha(__file__),limits='Actual assembled caller/return/SP and current source fields in arranged wholeAudio CPU inputI1; no native entryRAM/PPU/timing or optimization. Costs include JSR and any nested sweep calls, so nested totals must not be added as exclusive costs.'))
  print(json.dumps(dict(passed=True,observations=len(observations),groups=[{k:v for k,v in r.items()if k!='first'}for r in stats])))
 except Exception as e:core.put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
