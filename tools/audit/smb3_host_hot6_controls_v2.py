"""Full byte-index/physical-flags caller and retained compatibility controls."""
from pathlib import Path
import argparse,json,statistics,traceback
from smb3_host_current3b_cpu_v1 import D,IMAGE,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU

BASE=D/'smb3-host-current3b-v3'
def run(b,site,index,page,flags,hot):
 m=Memory(b);m.page(1,86);m.page(2,38);m[address(b,'CurrentBank')]=214;m[address(b,'CurrentBankC')]=166
 lo,hi=address(b,'B3VirtualMaps'),address(b,'B3WorkEnd')
 for at in range(lo,hi):m[at]=(at*37+index)&255
 for i in range(8):m[lo+i]=(i+3)%9
 m[lo+6]=page;m[3:5]=[0xa5,0x5a];m.writes=[]
 c=NesMPU(memory=m);c.pc=address(b,site['new_helper']if hot else site['original_helper']);c.sp=0xf0;c.stPushWord(0x5aff);c.p=flags;c.a=0x39
 reg=site['load'][-1];c.x,c.y=(index,index^0x5b)if reg=='x'else(index^0x5b,index);xy=(c.x,c.y)
 for _ in range(300):
  if c.pc==0x5b00:break
  c.step()
 else:raise AssertionError(('Reader timeout',site,index,page,flags,hex(c.pc)))
 data=int(site['load'][1:5],16);value=IMAGE[page*4096+((data+index)&4095)];p=(flags&0x7d)|(0x80 if value&128 else 0)|(2 if value==0 else 0)
 assert [c.a,c.x,c.y,c.p&207,c.sp]==[value,*xy,p&207,0xf0],('Actual original LDA AXYP/SP',site,index,page,flags,[c.a,c.x,c.y,c.p&207,c.sp],value,p)
 assert m[3:5]==[0xa5,0x5a]and m[address(b,'CurrentBank')]==214 and m[address(b,'CurrentBankC')]==166
 assert m.banks==[126,93 if hot else 86,38,127],m.banks
 allowed=set(range(lo,hi))|set(range(256,512))|{0x5115}
 assert all(at in allowed for at,v in m.writes),('Unowned write',m.writes)
 memory=bytes(m[:256]+m[512:2048]+m[0x6000:lo]+m[hi:0x8000])
 return dict(AXYP_SP=[c.a,c.x,c.y,c.p&207,c.sp],memory=memory,cycles=c.processorCycles,ordered_bus=[(at,v)for at,v in m.writes if not 256<=at<512])

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True)
 old,new=scoped_load(BASE/'candidate.nes'),scoped_load(a.packet/'candidate.nes');sites=json.loads((a.packet/'preparation.json').read_text())['actual_private_sites'];counts={'private_all_indices':0,'private_all64flags_3boundaryindices':0,'compatibility_all_indices':0,'compatibility_all64flags_9maps_3indices':0};savings=[]
 try:
  # Retained compatibility helper bytes, pointers, map helpers and all DMC/image
  # writers are literal. The only old core edits are genuine source JSR operands.
  lo=location(old,'B3ReadAbsX');hi=location(old,'B3CoreEnd');assert old['raw'][lo:hi]==new['raw'][lo:hi]
  for site in sites:
   for index in range(256):
    before=run(old,site,index,3,0x24 if index&1 else 0xed,False);after=run(new,site,index,3,0x24 if index&1 else 0xed,True)
    assert before['AXYP_SP']==after['AXYP_SP']and before['memory']==after['memory'];assert before['cycles']>after['cycles'];savings.append(before['cycles']-after['cycles']);counts['private_all_indices']+=1
    page=(index+site['source_PC'])%9;b=run(old,site,index,page,0x24,False);n=run(new,site,index,page,0x24,False);assert b==n;counts['compatibility_all_indices']+=1
   for bits in range(64):
    flags=32|sum(1<<bit for j,bit in enumerate([0,1,2,3,6,7])if bits>>j&1)
    for index in [0,127,255]:
     b=run(old,site,index,3,flags,False);n=run(new,site,index,3,flags,True);assert b['AXYP_SP']==n['AXYP_SP']and b['memory']==n['memory'];counts['private_all64flags_3boundaryindices']+=1
  # X/Y addressing representative compatibility readers retain their complete
  # arbitrary virtual-map contract, distinct from source-only fixed-map admission.
  reps={}
  for site in sites:reps.setdefault(site['load'][-1],site)
  for site in reps.values():
   for bits in range(64):
    flags=32|sum(1<<bit for j,bit in enumerate([0,1,2,3,6,7])if bits>>j&1)
    for page in range(9):
     for index in [0,127,255]:assert run(old,site,index,page,flags,False)==run(new,site,index,page,flags,False);counts['compatibility_all64flags_9maps_3indices']+=1
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(BASE/'candidate.nes'),ROM_sha256=sha(a.packet/'candidate.nes'),counts=counts,cases=sum(counts.values()),private13_sites_all256indices_and_all64flags=True,compatibility_original_helpers_all_bytes_and_bus_AXYP_SP_cycles_exact=True,additional_RAM_bytes=0,hot_helper_A_bank93_intentional_source_owned_lease=True,foreign_foreground_A_and_C_shadows_literal=True,saved_reader_cycles=dict(min=min(savings),max=max(savings),mean=statistics.mean(savings)),private_adapter_metadata_exception='Existing21B B3VirtualMaps..B3WorkEnd scratch may retain prior SavedY/Value; no original RAM/APU/source fields overlap. Restored outer A86 bridge and whole-call continuation checked separately.',checker_sha256=sha(__file__),limits='Finite assembled source-only byte-index/flags and compatibility cases. No physical IRQ/DMA/PPU/native cadence assertion. Fixed-map admission is the authenticated original map6=3 source path, not an invented arbitrary-map contract.'))
  print(json.dumps(dict(passed=True,counts=counts,saved_reader_cycles=statistics.mean(savings))))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),counts=counts));raise
if __name__=='__main__':main()
