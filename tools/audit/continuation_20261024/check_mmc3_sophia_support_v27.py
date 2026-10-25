from pathlib import Path
import hashlib,itertools,json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-sophia-stack-v27';O=V/'predicate-cpu-v1';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
class Memory(list):
 def __init__(self,b):
  super().__init__([0]*65536);self.b=b;self.banks=[254,0,36,255];self.selector=7;self.writes=[]
  for i,k in enumerate(self.banks):self.page(i,k)
  for g in b['segs'].values():
   if g.get('name')=='"SMCCODE"':start,size,pos=(int(g[k],0)for k in('start','size','ooffs'));list.__setitem__(self,slice(start,start+size),b['raw'][pos:pos+size])
 def page(self,w,k):self.banks[w]=k;list.__setitem__(self,slice(0x8000+w*8192,0xa000+w*8192),self.b['raw'][16+k*8192:16+(k+1)*8192])
 def __setitem__(self,a,v):
  if isinstance(a,slice):list.__setitem__(self,a,v);return
  self.writes.append((a,v));list.__setitem__(self,a,v)
  if a==0x8000:self.selector=v&7
  if a==0x8001:
   if self.selector==6:self.page(2,v)
   elif self.selector==7:self.page(1,v)
def run(b,char,variant,mode,flags,case):
 m=Memory(b);physical=(location(b,'InventorySupported')-16)//8192;m.page(1,physical)
 for n,v in dict(CurrentBank=physical,CurrentBankC=36,BankShadow=71,SelectedCharacter=char,RlVariant=variant,Cv3Variant=variant,Z2Variant=variant,CrossoverBehaviorVersion=mode).items():m[address(b,n)]=v
 m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[];c=NesMPU(memory=m,pc=address(b,'InventorySupported'));c.sp=0xfd;c.a=case*37&255;c.x=case*71&255;c.y=case*53&255;c.p=flags;minimum=255
 for _ in range(10000):
  if c.pc==0x7f00:break
  c.step();minimum=min(minimum,c.sp)
 else:raise AssertionError(('Support predicate timeout',char,variant,mode,flags,hex(c.pc),m.banks))
 # Discarded CPU stack and declared self-modifying operands are scratch.
 # Mapper latches are compared separately through exact resulting bank maps.
 excluded=set(range(0x100,0x200))|{0x8000,0x8001}
 for n in('safecall_a','SafecallA'):
  if n in b['syms']:excluded.add(address(b,n))
 application=bytes(0 if i in excluded else m[i]for i in range(0x8000))
 io=[(a,v)for a,v in m.writes if 0x2000<=a<0x6000]
 return(c.a,c.x,c.y,c.p&0xcf,c.sp),application,io,list(m.banks),c.processorCycles,minimum
old=load(D/'mmc3-ship-lives-v25/candidate.nes');new=load(V/'candidate.nes');rows=[];cases=list(itertools.product(range(20),[0,1,3,255],[0,1],[0x30,0x31,0x71,0xf1,0x39,0x3d,0xee,0xff]))+list(itertools.product(range(20,256),[0],[0],[0x30,0xee]))
for i,(char,variant,mode,flags)in enumerate(cases):
 x=run(old,char,variant,mode,flags,i);y=run(new,char,variant,mode,flags,i)
 assert x[:4]==y[:4],(char,variant,mode,hex(flags),x[0],y[0],[(hex(j),x[1][j],y[1][j])for j in range(32768)if x[1][j]!=y[1][j]][:8])
 rows.append(dict(character=char,variant=variant,mode=mode,flags=flags,parent_cycles=x[4],candidate_cycles=y[4],parent_minSP=x[5],candidate_minSP=y[5]))
fast=[z for z in rows if z['character']==11];other=[z for z in rows if z['character']!=11];q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),cases=len(rows),sophia_cases=len(fast),saved_Sophia_cycles=[min(z['parent_cycles']-z['candidate_cycles']for z in fast),max(z['parent_cycles']-z['candidate_cycles']for z in fast)],saved_Sophia_stack_bytes=[min(z['candidate_minSP']-z['parent_minSP']for z in fast),max(z['candidate_minSP']-z['parent_minSP']for z in fast)],other_added_cycles=[min(z['candidate_cycles']-z['parent_cycles']for z in other),max(z['candidate_cycles']-z['parent_cycles']for z in other)],scope='Actual assembled MMC3 InventorySupported with real bank-switch/SMC code on both candidates, every raw character ID, both modes/alternate/flag combinations for20internal IDs and varying incoming A/X/Y. Exact outputs A/X/Y/meaningfulP/SP, application RAM excluding discarded stack/SMC operands, nonbank hardware writes and final physical banks. No native audio/NMI or campaign claim.')
(O/'cases.json').write_text(json.dumps(rows,separators=(',',':')));(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
