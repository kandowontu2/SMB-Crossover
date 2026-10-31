"""Finite physical owner/load/auth/retire controls; no WWF host hook/native run."""
from pathlib import Path
import itertools,json,sys,traceback,hashlib
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_wram_host_controls_v7 as H
from ff_wram_host_isr_v4 import clone
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
J=R/'build/wwf-first-hogan-host-v6/joint';S=J.parent/'source-stage.json'
O=R/'build/wwf-first-hogan-owner-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def make(b):
 m=H.make(b);H.put(m,SelectedCharacter=29,FmGroups=0,FamilyMainCommit=1,OperMode=1,GamePauseStatus=0)
 return m

def run(m,name,a=0x53,x=17,y=91,p=0x71,hook=None,limit=600000):
 m.raw_page(1,0xe0);H.put(m,CurrentBank=0xe0)
 c=NesMPU(memory=m,pc=address(m.bundle,name));c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5aff)
 before=dict(maps=m.rawtags[:],smc=bytes(m[0x15a:0x17b]),scratch=bytes(m[3:11]),upper=bytes(m[0x1e1:0x200]));low=c.sp
 for step in range(limit):
  if c.pc==0x5b00:break
  if hook:hook(m,c,step)
  low=min(low,c.sp);assert m[c.pc]!=0,('Owner BRK',name,hex(c.pc),m.rawtags)
  c.step()
 else:raise AssertionError(('Owner bound',name,hex(c.pc),m.rawtags))
 assert(c.a,c.x,c.y,c.sp)==(a,x,y,224),(name,'Native AXY/SP',c.a,c.x,c.y,c.sp)
 assert(c.p&0xfe)==(p&0xfe),(name,'Caller P except C',c.p,p)
 assert before['maps']==m.rawtags and bytes(m[0x15a:0x17b])==before['smc']
 assert bytes(m[3:11])==before['scratch'] and bytes(m[0x1e1:0x200])==before['upper']
 return c,low

def expected():
 out=[bytearray((J/n).read_bytes())for n in ['a1.bin','c2.bin','a3.bin']]
 for image in out[1:]:image[0x1fe0:0x1ff0]=(J/'cookie.bin').read_bytes()
 return out

def exact(m):
 assert[bytes(m.ram[i])for i in [1,2,3]]==list(map(bytes,expected()))
 assert m.protection==[2,1]
 assert not any(a in[0x5102,0x5103,0x5113]for a,v in m.writes)

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,source=True,native=False,no_host_hooks=True,checks={})
 stage=json.loads(S.read_text())
 for p,h in stage['bindings'].items():assert sha(p)==h,p
 b=qualified(J/'candidate.nes');minsp=224
 try:
  # Dirty hardware, foreign stale cookies, no external publication checkpoint.
  loads=[]
  for wide,reload in itertools.product([0,1],[0,1]):
   m=make(b);H.put(m,X5WideChrActive=wide,ReloadCHRBank=reload)
   for i in range(12):m[address(b,'CurrentCHRBank')+i]=(868+i)&255;m[address(b,'X5ChrMode')+i]=0x83 if i%2 else 0
   m.ram[2][0x1fe0:0x1ff0]=bytes([167,31])+bytes(14);m.ram[3][0x1fe0:0x1ff0]=bytes([167,22])+bytes(14)
   oracle,cpu=clone(m,NesMPU(memory=m));H.native_publish(oracle);desired=oracle.chr_latches[:]
   original0=bytes(m.ram[0]);m.writes.clear();m.ram_writes.clear();reads=m.ppu_reads;opcodes=[]
   def no_cache(mem,c,step):
    if c.pc>=0x8000:
     raw=mem.rawtags[(c.pc-0x8000)//8192]
     assert raw not in[1,2,3],('Cache opcode before load verification',hex(c.pc),raw)
   c,lo=run(m,'WfLoad',hook=no_cache);minsp=min(minsp,lo);assert c.p&1;exact(m)
   assert bytes(m.ram[0])==original0
   assert m.ram_writes[:2]==[(2,0x1fe0,0),(3,0x1fe0,0)]
   assert m.ram_writes[-1]==(2,0x1fe0,167)
   assert m.ppu_reads-reads==49200
   assert m.chr_latches==desired and m.upper==0 and m.toggle==0 and m.ppuctrl==H.get(m,'Mirror_PPUCTRL')
   assert H.get(m,'ReloadCHRBank')==reload
   loads.append(dict(wide=wide,reload=reload,PPU_reads=m.ppu_reads-reads,minimum_SP=lo))
  q['checks']['real_buffered_24KiB_load']=dict(passed=True,cases=len(loads),rows=loads,external_checkpoint=False,first_C2_then_RAM3_invalidate=True,last_C2_valid=True)
  # Every precondition rejected before any write to selected RAM or PPU read.
  cases=0
  for name,value in [('SelectedCharacter',28),('FmGroups',1),('FamilyMainCommit',0),('OperMode',0),('Mirror_PPUMASK',24),('DisableScreenFlag',0),('NmiDisable',0),('GamePauseStatus',1)]:
   for bits in range(64):
    m=make(b);H.put(m,**{name:value});m.ram_writes.clear();reads=m.ppu_reads
    c,lo=run(m,'WfLoad',p=0x30|(bits&15)|((bits&48)<<2));assert not c.p&1 and not m.ram_writes and m.ppu_reads==reads;cases+=1
  q['checks']['cold_precondition_allflags']=dict(passed=True,cases=cases)
  faults=[]
  for kind,corrupt in [('locked',None),('A1',(1,0x123)),('C2',(2,0x345)),('A3',(3,0x789))]:
   m=make(b);m.protection=[0,0]if kind=='locked'else[2,1];m.corrupt_at=corrupt
   c,lo=run(m,'WfLoad');assert not c.p&1
   assert m.ram[2][0x1fe0]!=167 and m.ram[3][0x1fe0]!=167
   faults.append(kind)
  q['checks']['protection_readback_failures']=dict(passed=True,cases=faults)
  base=make(b);run(base,'WfLoad');ready=address(b,'WfHostReady')-0xc000
  poison=0
  for index,bits in itertools.product(range(16),range(64)):
   m,cpu=clone(base,NesMPU(memory=base));m.ram[2][0x1fe0+index]^=1;m.ram_writes.clear();guest=[]
   def check_first(mem,c,step):
    if c.pc>=0xc000 and mem.rawtags[2]==2:guest.append(c.pc)
   c,lo=run(m,'WfCheck',p=0x30|(bits&15)|((bits&48)<<2),hook=check_first)
   assert not c.p&1 and not guest and not m.ram_writes;poison+=1
  q['checks']['full16_poison_before_first_cache_opcode']=dict(passed=True,cases=poison)
  constructor=[]
  for bits in range(64):
   m,cpu=clone(base,NesMPU(memory=base));calls=[]
   def entered(mem,c,step):
    if c.pc==address(b,'WfHostCold'):calls.append(c.pc)
   c,lo=run(m,'WfConstructCold',p=0x30|(bits&15)|((bits&48)<<2),hook=entered);minsp=min(minsp,lo)
   assert c.p&1 and len(calls)==1 and m.ram[2][ready]==167
   assert m.ram[2][0x2b]==5 and m.ram[2][0x2a]==0 and m.ram[2][0x76]==32
   assert m.ram[2][0x79]==m.ram[2][0x7a]==0
   state=bytes(m.ram[2]);calls.clear();c,lo=run(m,'WfConstructCold',p=0x30|(bits&15)|((bits&48)<<2),hook=entered)
   assert c.p&1 and not calls and bytes(m.ram[2])==state
   constructor.append(bits)
  q['checks']['genuine_constructor_once_allflags']=dict(passed=True,cases=len(constructor),original_Hogan_ID5=True,original_intro_countdown32=True,HP_or_ready_preload=False)
  # Independent pure retirement, including malformed own cookie and foreign families.
  count=0
  for family,bits in itertools.product([9,22,27,29,31,32,33],range(64)):
   m=make(b);H.put(m,SelectedCharacter=0,FmGroups=255,FamilyMainCommit=0)
   for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=bytes([97,family])+bytes(range(14))
   before=[bytes(z)for z in m.ram];c,lo=run(m,'WfRetire',p=0x30|(bits&15)|((bits&48)<<2))
   assert c.p==(0x30|(bits&15)|((bits&48)<<2))
   for bank in range(4):
    image=bytearray(before[bank])
    if family==29 and bank in[2,3]:image[0x1fe0]=0
    assert m.ram[bank]==image
   count+=1
  q['checks']['retirement_allflags_foreign_exact']=dict(passed=True,cases=count,physical_hooks_installed=False)
  # Real SFC caller NZ follows native final saved-A load, separately from
  # allflag direct entry. Retain the first incorrect observer expectation.
  m=make(b);c,lo=H.invoke(m,'WfLoad',a=0x53,x=17,y=91,p=0xb1);assert[c.a,c.x,c.y,c.p,c.sp]==[0x53,17,91,0x31,224]
  c,lo=H.invoke(m,'WfConstructCold',a=0x53,x=17,y=91,p=0xb1);assert[c.a,c.x,c.y,c.p,c.sp]==[0x53,17,91,0x31,224]
  q['checks']['genuine_SFC_NZ_contract']=dict(passed=True,cases=2,retained_negative=str(J.parent/'proxy-first-negative.json'),note='FarCallCommon final LDA of positive sourceA sets NZ before the worker; inputP N is not a worker entry invariant.')
  q.update(passed=True,minimum_SP=minsp,candidate=stage['candidate'],limits=stage['limits'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),S,J/'candidate.nes',J/'candidate.dbg',J/'cookie.bin',J/'template.bin',R/'tools/audit/verify_native_relocation.py',R/'tools/audit/ff_wram_host_controls_v7.py',R/'tools/audit/ff_wram_host_isr_v4.py']}
  save(O/'controls.json',q)
 print(json.dumps(dict(passed=True,checks={k:v.get('cases')for k,v in q['checks'].items()},SHA256=sha(O/'controls.json'))))

if __name__=='__main__':main()
