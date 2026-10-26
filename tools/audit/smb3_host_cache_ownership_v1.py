"""Source-only feasibility of unallocated7600..79FF music-cache lifetime."""
from pathlib import Path
import argparse,json,traceback
from smb3_host_current3b_cpu_v1 import D,R,Fixture,ROLES,FIELDS,native_address,sha,put,CLOSURE
from smb3_host_current3b_boundaries_v2 import execute
from smb3_host_current3b_owners_v2 import PeripheralMemory
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

LOW,HIGH=0x7600,0x7a00
class Probe(PeripheralMemory):
 def __init__(self,b):
  self.armed=False;self.written=set();self.read_before=[];super().__init__(b)
 def __getitem__(self,a):
  if self.armed and isinstance(a,int)and LOW<=a<HIGH and a not in self.written:self.read_before.append(a)
  return super().__getitem__(a)
 def __setitem__(self,a,v):
  if self.armed and isinstance(a,int)and LOW<=a<HIGH:self.written.add(a)
  super().__setitem__(a,v)
def ordinary(m):return bytes(m[:256]+m[512:2048]+m[0x6000:LOW]+m[HIGH:0x8000])
def outputs(c,m):return([c.a,c.x,c.y,c.p&207,c.sp],ordinary(m),m.banks[:],[(a,v)for a,v in m.writes if not 0x100<=a<0x200 and not LOW<=a<HIGH],c.processorCycles)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);packet=D/'smb3-host-current3b-v3';b=scoped_load(packet/'candidate.nes');rows=[]
 try:
  mapped={native_address(b,x,False)for x in FIELDS}|{native_address(b,x,True)for x in FIELDS}|set(range(address(b,'B3SavedCpuZp'),address(b,'B3SavedCpuZp')+6))|set(range(address(b,'B3VirtualMaps'),address(b,'B3WorkEnd')))
  assert not any(LOW<=x<HIGH for x in mapped)
  # Actual selected-source continuations retain original source state/APU
  # assertions with those bytes poisoned; this does not allocate a cache.
  source=[]
  for role,(queue,bit,track)in ROLES.items():
   f=Fixture(b,0,0);f.m[LOW:HIGH]=[(i*53+19)&255 for i in range(HIGH-LOW)];sentinel=bytes(f.m[LOW:HIGH]);f.invoke((queue,bit),flags=0x24)
   for _ in range(32):f.invoke(flags=0x24)
   assert bytes(f.m[LOW:HIGH])==sentinel;source.append(dict(role=role,calls=33,bytes_unchanged=1024))
  # Real warm SMB3 owner -> every foreign slot, including four ship variants.
  # Check read-before-write, not just final APU equality, so a zero value or
  # current mixer cannot hide a stale-history consumer.
  f=Fixture(b,0,0);f.invoke(('AreaMusicQueue',1))
  for _ in range(32):f.invoke()
  snapshot=list(f.m);banks=f.m.banks[:];hw=f.m.hw[:];hwdmc=f.m.hwdmc
  for char in range(20):
   if char==17:continue
   for mode in [0,1]:
    for variant in ([0,1,2,3]if char==18 else[0]):
     pair=[]
     for poisoned in [False,True]:
      m=Probe(b);list.__setitem__(m,slice(None),snapshot);m.banks=banks[:];m.hw=hw[:];m.hwdmc=hwdmc
      if poisoned:list.__setitem__(m,slice(LOW,HIGH),[(i*71+23)&255 for i in range(HIGH-LOW)])
      for name,value in [('SelectedCharacter',char),('CrossoverBehaviorVersion',mode),('AreaMusicQueue',1),('EventMusicQueue',0),('GamePauseStatus',0)]:m[address(b,name)]=value
      if char==18:m[address(b,'VvVariant')]=variant
      m.armed=True;pair.append(m)
     for tick in range(128):
      c0,_=execute(b,pair[0],'AudioUpdate');c1,_=execute(b,pair[1],'AudioUpdate')
      assert outputs(c0,pair[0])==outputs(c1,pair[1]),('Foreign output changed by cache bytes',char,mode,variant,tick)
      assert not pair[1].read_before,('Foreign history reads cache before overwrite',char,mode,variant,tick,pair[1].read_before[:12])
     rows.append(dict(character=char,mode=mode,variant=variant,ticks=128,cache_read_before_own_write=0,cache_bytes_overwritten=len(pair[1].written)))
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(packet/'candidate.nes'),proposed_unallocated_range=[LOW,HIGH],existing_projected_source_and_adapter_owned_bytes_disjoint=True,all12_roles_selected_source_sentinel=source,foreign_owner_transitions=rows,foreign_calls=len(rows)*128*2,original_2048_history_clear_proof=str(packet/'boundaries-v2/proof.json'),cache_bytes_only_excluded_from_final_state_and_write_comparison=True,strict_no_foreign_read_before_own_write=True,physical_E_preserved_on_entry=True,checker_sha256=sha(__file__),limits='Finite arranged CPU source states, not allocation/native/menu/entire-track proof. Only default alternate except all four ships; other variants and original compressed-stream encoder/reset authentication remain to finish before a cache proposal. No original song clock, sample, voice, image or code is changed.'))
  print(json.dumps(dict(passed=True,source_cells=len(source),foreign_profiles=len(rows))))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),profiles_done=len(rows)));raise
if __name__=='__main__':main()
