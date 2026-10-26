"""Finite full-index/flags/page caller controls for private absolute readers."""
from pathlib import Path
import argparse, hashlib, json, statistics, traceback
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'smb3-native-core-v5'
IMAGE=(R/'reference/new-roster-audio/mario3/crossover-named.nsf').read_bytes()[128:]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def run(b,site,index,page,flags):
 m=Memory(b);m.page(1,86);m.page(2,38);m[address(b,'CurrentBank')]=214;m[address(b,'CurrentBankC')]=166
 work=range(address(b,'B3VirtualMaps'),address(b,'B3WorkEnd'))
 for at in work:m[at]=(at*37+index)&255
 for i in range(8):m[address(b,'B3VirtualMaps')+i]=(i+3)%9
 m[address(b,'B3VirtualMaps')+site['logical_page']]=page
 m[3],m[4]=0xa5,0x5a;m.writes=[]
 c=NesMPU(memory=m);c.pc=address(b,f"B3Source{site['source_PC']:04X}");end=c.pc+5;c.sp=0xf0;c.p=flags;c.a=0x39
 c.x,c.y=(index,index^0x5b)if site['index_register']=='X'else(index^0x5b,index)
 originalXY=(c.x,c.y);initial=c.processorCycles
 for _ in range(300):
  if c.pc==end:break
  c.step()
 else:raise AssertionError(('Reader caller timeout',site,index,page,flags,hex(c.pc)))
 value=IMAGE[page*4096+((site['source_address']+index)&4095)]
 expectedP=(flags&0x7d)|(0x80 if value&128 else 0)|(2 if value==0 else 0)
 assert[c.a,c.x,c.y,c.p&207,c.sp]==[value,*originalXY,expectedP&207,0xf0],('Original LDA contract',site,index,page,flags,c.a,c.x,c.y,c.p,c.sp,value,expectedP)
 assert m[3:5]==[0xa5,0x5a]and m.banks==[126,86,38,127]and m[address(b,'CurrentBank')]==214 and m[address(b,'CurrentBankC')]==166
 allowed=set(work)|set(range(0x100,0x200))|{3,4,0x5115}
 assert all(at in allowed for at,_ in m.writes),('Unowned reader write',site,index,page,flags,m.writes)
 # Complete final nonstack RAM outside the declared21B adapter image.
 memory=bytes(m[:256]+m[512:address(b,'B3VirtualMaps')]+m[address(b,'B3WorkEnd'):32768])
 return dict(AXYP_SP=[c.a,c.x,c.y,c.p&207,c.sp],memory=hashlib.sha256(memory).hexdigest(),mapper=[(at,v)for at,v in m.writes if at==0x5115],cycles=c.processorCycles-initial)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);a=p.parse_args();o=a.packet/'reader-controls-v1';o.mkdir(exist_ok=False)
 old,new=scoped_load(BASE/'candidate.nes'),scoped_load(a.packet/'candidate.nes');sites=json.loads((a.packet/'known-sites.json').read_text());assert len(sites)==39
 costs=[];counts={'all_indices_each_site':0,'full_physical_flags_each_helper_kind':0};representatives={}
 def check(site,index,page,flags,kind):
  before,after=(run(b,site,index,page,flags)for b in [old,new]);assert {k:v for k,v in before.items()if k!='cycles'}=={k:v for k,v in after.items()if k!='cycles'},('Caller divergence',site,index,page,flags,before,after)
  assert after['cycles']<before['cycles'];costs.append(before['cycles']-after['cycles']);counts[kind]+=1
 try:
  for site in sites:
   representatives.setdefault((site['logical_page'],site['index_register']),site)
   for index in range(256):check(site,index,(index+site['source_PC'])%9,0x24 if index&1 else 0xed,'all_indices_each_site')
  for site in representatives.values():
   for bits in range(64):
    flags=32|sum(1<<bit for j,bit in enumerate([0,1,2,3,6,7])if bits>>j&1)
    for page in range(9):
     for index in [0,127,255]:check(site,index,page,flags,'full_physical_flags_each_helper_kind')
  for name,end in [('B3ReadAbsX','B3CoreEnd')]:
   start=location(old,name);stop=location(old,end);nstart=location(new,name);assert old['raw'][start:stop]==new['raw'][nstart:nstart+stop-start]
  put(o/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(a.packet/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),cases=sum(counts.values()),counts=counts,helper_kinds=len(representatives),all_39_sites_all_byte_indices=True,all_64_physical_flags_9_page_values_3_indices_per_helper_kind=True,original_generic_indirect_helpers_exact=True,original_source_value_AXYP_SP_nonstack_RAM_bank_shadow_and_ordered_mapper_writes_exact=True,adapter_metadata_exception='Existing21B private image may differ; no new RAM. R0/R1 literally restored/unchanged. Stack contents may differ, liveSP/flags exact.',saved_cycles=dict(min=min(costs),max=max(costs),mean=statistics.mean(costs)),tool_sha256=sha(__file__),limits='Standalone old-a4be source-owned readers only; no current641/3b source composition, native playback or host NMI/RAM/mixer/lifecycle qualification.'))
  print((o/'proof.json').read_text())
 except Exception as e:
  put(o/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),completed=counts));raise
if __name__=='__main__':main()
