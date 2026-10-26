"""Finite original-owner regression and new SMB3 cloned-E DMC preemption controls."""
from pathlib import Path
import argparse,itertools,json,traceback
from smb3_host_current3b_boundaries_v2 import execute
from smb3_host_current3b_cpu_v1 import D,HostMemory,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

FLAGS=[32|sum((1<<bit)for k,bit in enumerate([0,1,2,3,6,7])if n>>k&1)for n in range(64)]
def memory(b,name,owner,e,active=True):
 m=HostMemory(b);pc=address(b,name);slot=(pc-0x8000)//8192
 if slot!=3:m.page(slot,(location(b,name)-16)//8192)
 m.page(3,e)
 for key,value in [('BassDmcActive',owner),('Cv3DmcPriority',128 if owner>=3 else 0),('GuestCombinedEnable',31),('SelectedCharacter',0x2e),('AvAudioRequest',4)]:m[address(b,key)]=value
 m.hw[17]=73;m.hwdmc=active
 return m
def signature(c,m):
 return ([c.a,c.x,c.y,c.p&207,c.sp],bytes(m[:256]+m[512:2048]+m[0x6000:0x8000]),m.banks[:],[(a,v)for a,v in m.writes if not 0x100<=a<0x200],c.processorCycles)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old=scoped_load(D/'root-current-roster-composition-v1/candidate.nes');new=scoped_load(a.packet/'candidate.nes');ordinary=[];preempt=[];resets=[]
 try:
  # Changed BEQ->BCS admits only new owner4 in the actual valid0..4 domain.
  # Existing0..3 calls have literal output, complete state, bus and cycle equality.
  for name,owner,flags in itertools.product(['Cv3DmcResetOwner','GuestDmcStatus'],range(4),FLAGS):
   pair=[]
   for b in [old,new]:
    m=memory(b,name,owner,127,False);c,_=execute(b,m,name,a=31,flags=flags);pair.append(signature(c,m))
   assert pair[0]==pair[1],('Existing owner change',name,owner,flags)
   ordinary.append([name,owner,flags])
  # Existing fixed resident writer must preempt the new lease while the CPU
  # still executes its genuine E70/E97 copy; no invoke helper remaps E first.
  for e,incoming,flags in itertools.product([70,97],range(4),FLAGS):
   m=memory(new,'Cv3DmcOwnerWrite',4,e);c,_=execute(new,m,'Cv3DmcOwnerWrite',a=incoming,flags=flags)
   assert[c.a,c.x,c.y,c.p&207,c.sp]==[incoming,41,90,flags&207,253]
   assert m[address(new,'BassDmcActive')]==incoming and m[address(new,'Cv3DmcPriority')]==0 and m.banks[3]==127 and m.hw[17]==73 and not m.hwdmc
   writes=[(at,v)for at,v in m.writes if not 0x100<=at<0x200]
   assert writes==[(address(new,'BassDmcActive'),incoming),(0x4015,15),(0x5117,255),(address(new,'Cv3DmcPriority'),0)],writes
   preempt.append([e,incoming,flags])
  # New owner4 has the source-lane reset semantics already established by
  # genuine original owner3: leave sentinel live until fixed stop/restore runs.
  for e,flags in itertools.product([70,97],FLAGS):
   pair=[]
   for b,owner in [(old,3),(new,4)]:
    m=memory(b,'Cv3DmcResetOwner',owner,e if b is new else 125);c,_=execute(b,m,'Cv3DmcResetOwner',a=0xab,flags=flags);pair.append(signature(c,m))
   assert pair[0]==pair[1],('Reset owner4 differs from original source lease',e,flags)
   resets.append([e,flags])
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(D/'root-current-roster-composition-v1/candidate.nes'),candidate_ROM_sha256=sha(a.packet/'candidate.nes'),valid_existing_owner_calls=len(ordinary),actual_cloned_E_preemption_calls=len(preempt),owner4_reset_vs_original_source_owner3_calls=len(resets),physical_flags=FLAGS,old_owner_state_bus_ABI_and_cycles_literal=True,new_lease_stop_precedes_E127_restore=True,DAC_held=73,complete_new_owner_AXYP_SP_preserved=True,checker_sha256=sha(__file__),limits='Actual assembled entries with modeled DMC status and genuine cloned-E code. No DMA waveform, physical clock, NMI/render deadline, gameplay scene or native preemption claim. Actual permitted ownership domain is0..4; corrupt owner>=5 is not claimed.'))
  print(json.dumps(dict(passed=True,ordinary=len(ordinary),preempt=len(preempt),reset=len(resets))))
 except Exception as e:
  put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),ordinary_done=len(ordinary),preempt_done=len(preempt),reset_done=len(resets)));raise
if __name__=='__main__':main()
