"""Read-only recheck with explicit original6502 RMW dummy bus writes, no native rerun."""
from pathlib import Path
from collections import Counter
import argparse,json,traceback
import smb3_host_current3b_native_verify_v1 as original
from smb3_host_current3b_cpu_v1 import TraceBus,RAW,sha,put
from smb3_original_music_closure_v3 import source_state
from verify_native_relocation import NesMPU

RMW={0x06,0x16,0x0e,0x1e,0x26,0x36,0x2e,0x3e,0x46,0x56,0x4e,0x5e,0x66,0x76,0x6e,0x7e,0xc6,0xd6,0xce,0xde,0xe6,0xf6,0xee,0xfe}
class OriginalBusWrites(TraceBus):
 instances=[]
 def __init__(self,raw):
  self.dummy_writes=0;self.dummy_sites=Counter();super().__init__(raw);self.instances.append(self)
 def __setitem__(self,a,v):
  # NMOS6502 memory RMW writes the old byte, then the modified byte. The
  # semantic py65 model accounts the instruction cycles but emits only the
  # final memory store. Add the missing ORIGINAL bus store before it; never
  # delete, coalesce or mask any native raw write, including equal values.
  if(a<0x2000 or 0x6000<=a<0x8000)and not 0x100<=(a&0x7ff if a<0x2000 else a)<0x200 and getattr(self,'pc',0)>=0x8000 and self.peek(self.pc)in RMW:
   super().__setitem__(a,self.peek(a));self.dummy_writes+=1;self.dummy_sites[(self.pc,a)]+=1
  super().__setitem__(a,v)

def semantic_controls():
 rows=[]
 for flags in [32,36]:
  old,new=TraceBus(RAW),OriginalBusWrites(RAW)
  for tick in range(9):
   pair=[]
   for m in [old,new]:
    m.events=[];m.mapper=[];m.nonstack_writes=[];c=NesMPU(memory=m);c.pc=0x9000 if tick==0 else 0xa000;c.a=8 if tick==0 else 0;c.x=c.y=0;c.p=flags;c.sp=253;c.stPushWord(0x7eff)
    for _ in range(10000):
     if c.pc==0x7f00:break
     m.pc=c.pc;m.pc_physical=m.physical(c.pc);c.step()
    else:raise AssertionError('Semantic control timeout')
    pair.append(([c.a,c.x,c.y,c.p,c.sp,c.processorCycles],source_state(m),m.events[:],m.mapper[:]))
   assert pair[0]==pair[1],('Bus annotation changed source semantics',flags,tick)
  assert new.dummy_writes>0;rows.append(dict(flags=flags,calls=9,old_and_new_AXYP_SP_cycles_state_APU_virtualmaps_exact=True,original_RMW_extra_bus_writes=new.dummy_writes))
 OriginalBusWrites.instances=[]
 return rows
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 try:
  controls=semantic_controls();original.TraceBus=OriginalBusWrites;proof=original.verify(a.packet)
  proof.update(original_failed_native_verifier_preserved=str(a.packet/'native-failure.json'),original_verifier_sha256=sha(Path(original.__file__)),bus_model_checker_sha256=sha(__file__),raw_native_RAM_stream_unmodified=True,normalization='Expected ORIGINAL raw bus now includes old-value writes for real memory RMW opcodes. Native logs are compared literally in original order; no write is discarded. FinalRAM/APU/order/AXYP/SP assertions remain.',semantic_controls=controls,original_RMW_dummy_bus_writes=sum(q.dummy_writes for q in OriginalBusWrites.instances),original_RMW_sites=[dict(sourcePC=pc,address=at,count=n)for(pc,at),n in sorted(sum((q.dummy_sites for q in OriginalBusWrites.instances),Counter()).items())])
  put(a.output/'proof.json',proof);print(json.dumps({k:proof[k]for k in ['passed','actual_source_calls','original_ordered_logical_APU_stores','complete256_DMA_epochs','scoped_enable_epochs','original_RMW_dummy_bus_writes']}))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
