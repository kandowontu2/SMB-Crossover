"""Read-only assembled IRQ continuation, current clear-path and DMC lease controls."""
from pathlib import Path
import argparse,hashlib,json,traceback
from smb3_host_current3b_cpu_v1 import D,R,Fixture,HostMemory,put,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU

def execute(b,m,name,a=0,flags=0x20,inject=None,record=False):
 c=NesMPU(memory=m);c.pc=address(b,name);c.a=a;c.x=0x29;c.y=0x5a;c.p=flags;c.sp=253;c.stPushWord(0x5aff);m.writes=[];trace=[];done=False
 for _ in range(100000):
  if c.pc==0x5b00:break
  bank=m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1;key=(c.pc,bank)
  if inject==key and not done:
   assert not c.p&4,('IRQ unexpectedly blocked',key);c.irq();done=True;continue
  if record:trace.append(key)
  if hasattr(m,'pc'):m.pc=c.pc
  c.step()
 else:raise AssertionError(('Timeout',name,hex(c.pc),m.banks))
 assert c.sp==253 and(inject is None or done)
 return c,trace
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True);b=scoped_load(a.packet/'candidate.nes');old=scoped_load(D/'root-current-roster-composition-v1/candidate.nes')
 try:
  # Complete fetch ended: execute the real fixed entry while E is STILL70/97,
  # rather than an invoke helper which would prematurely map E127 on entry.
  completion=[]
  for bank in [70,97]:
   for dac in [0,47,127]:
    m=HostMemory(b);m.page(3,bank);m[address(b,'BassDmcActive')]=4;m[address(b,'Cv3DmcPriority')]=128;m[address(b,'GuestCombinedEnable')]=31;m[0x4011]=dac;m.hwdmc=False
    c,_=execute(b,m,'GuestDmcStatus',a=31);assert c.a==15 and m.banks[3]==127 and m[address(b,'BassDmcActive')]==0 and m[address(b,'Cv3DmcPriority')]==0 and m.hw[17]==dac
    events=[(at,v)for at,v in m.writes if at in [0x4015,0x5117,0x4011]];assert events==[(0x4015,15),(0x5117,255)],events;completion.append(dict(start_E=bank,DAC=dac,ordered_events=events))
  # Cold foreground clear paths must preserve the FULL2048B history, not only
  # fields that the new driver happened to read in a music prefix.
  clears=[]
  for name in ['InitializeMemory','RosterClearState']:
   q=Arena(b,17);lo=address(b,'XgLzHistory');sentinel=bytes((i*67+13)&255 for i in range(2048));q.m[lo:lo+2048]=sentinel
   q.invoke(name);assert bytes(q.m[lo:lo+2048])==sentinel;clears.append(dict(callee=name,history_bytes_preserved=2048))
  # The current linked DECODE segment contains no decoder. All named history
  # consumers are music families; capture exact source evidence and caveat.
  decode=[g for g in b['segs'].values()if g['name']=='"DECODE"'];assert not decode or all(int(g['size'],0)==0 for g in decode)
  consumers=[]
  for file in sorted((a.packet/'source/src').rglob('*')):
   if file.suffix not in ['.s','.inc']:continue
   lines=file.read_text().splitlines()
   for n,line in enumerate(lines,1):
    if 'XgLzHistory'in line:consumers.append(dict(path=str(file.relative_to(a.packet/'source')).replace('\\','/'),line=n,text=line.strip()))
  # Snapshot a genuine dispatched cold init, then compare complete first-play
  # continuation with/without the actual hardware-vector IRQ at EVERY reached
  # instruction PC in the new imported core/cold window and fixed audio entry.
  q=Arena(b,17);q.put(OperMode=1,AreaMusicQueue=1,XgAudioCharacter=255,GuestAudioCharacter=255,GamePauseStatus=0);q.invoke('AudioUpdate');snapshot=list(q.m);banks=q.m.banks[:]
  def fresh():
   m=Memory(b);list.__setitem__(m,slice(None),snapshot);m.banks=banks[:];return m
  base=fresh();c,trace=execute(b,base,'AudioUpdate',record=True)
  candidates=sorted({(pc,bank)for pc,bank in trace if(bank==38 and address(b,'B3CoreStart')<=pc<address(b,'B3CoreEnd'))or(bank==86 and address(b,'B3ColdStart')<=pc<address(b,'B3ColdEnd'))or pc==address(b,'AudioUpdate')})
  ioignore={0x2005,0x2006,0x5204};raw=lambda m:bytes(m[:256]+m[512:2048]+m[0x6000:0x8000]);ordered=lambda m:[(at,v)for at,v in m.writes if not 0x100<=at<0x200 and at not in ioignore]
  expected=(c.a,c.x,c.y,c.p&207,c.sp,raw(base),base.banks,ordered(base));deltas=[]
  for key in candidates:
   m=fresh();after,_=execute(b,m,'AudioUpdate',inject=key);got=(after.a,after.x,after.y,after.p&207,after.sp,raw(m),m.banks,ordered(m));assert got==expected,('Actual IRQ continuation difference',key)
   assert m[address(b,'CurrentBank')]==base[address(b,'CurrentBank')]and m[address(b,'CurrentBankC')]==base[address(b,'CurrentBankC')]and m[address(b,'IrqNewScroll')]==base[address(b,'IrqNewScroll')]
   deltas.append(after.processorCycles-c.processorCycles)
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(a.packet/'candidate.nes'),actual_E_source_completion_controls=completion,foreground_clear_controls=clears,compiled_graphics_DECODE_bytes=sum(int(g['size'],0)for g in decode),named_history_consumers=consumers,actual_IRQ_cases=len(candidates),actual_IRQ_PCs=candidates,IRQ_extra_cycles=sorted(set(deltas)),complete_continuation_RAM_OAM_metadata_AXYP_SP_banks_ordered_APU_mapper_exact=True,checker_sha256=sha(__file__),limits='Actual resident IRQ instruction execution via hardware vector in CPU memory model, not physical PPU/DMA/IRQ timing or a universal arbitrary foreground/main concurrency proof. No graphics decompressor exists in currentDECODE; six ZP bytes conservatively borrowed regardless. Full native transition/render/performance qualification remains.'))
  print(json.dumps(dict(passed=True,IRQ_cases=len(candidates),IRQ_extra_cycles=sorted(set(deltas)),history_clear_cases=2,completion_controls=len(completion))))
 except Exception as e:
  put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
