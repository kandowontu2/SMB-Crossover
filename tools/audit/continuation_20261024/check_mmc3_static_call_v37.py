from pathlib import Path
import hashlib,itertools,json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-static-call-v37';O=V/'abi-cpu-v1';O.mkdir(exist_ok=False);sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
source=(D/'check_mmc3_sophia_support_v27.py').read_text();defs=source[source.index('class Memory'):source.index("old=load(")]
defs=defs.replace('def run(b,char,variant,mode,flags,case):','def run(b,char,variant,mode,flags,case,func="InventorySupported",seed=None,selector=71):').replace("location(b,'InventorySupported')","location(b,func)").replace('BankShadow=71','BankShadow=selector').replace("pc=address(b,'InventorySupported')","pc=address(b,func)")
defs=defs.replace("m[0x1fe]=255;", "m.selector=selector&7;state=seed(m,b,case)if seed else{};m[0x1fe]=255;")
defs=defs.replace('c.p=flags;minimum=255','c.p=flags;minimum=255\n for n,v in state.items():setattr(c,n,v)')
defs=defs.replace("excluded=set(range(0x100,0x200))|{0x8000,0x8001}","excluded=set(range(0x100,0x200))|{0x8000,0x8001}\n for g in b['segs'].values():\n  if g.get('name')=='\"SMCCODE\"':excluded.update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))\n for n in ('BillNativeReturnA','BillNativeReturnP','BillNativeReturnSelector'):\n  if n in b['syms']:excluded.add(address(b,n))")
defs=defs.replace('(c.a,c.x,c.y,c.p&0xcf,c.sp),application','(c.a,c.x,c.y,c.p&0xcf,c.sp,m[address(b,"CurrentBank")],m[address(b,"CurrentBankC")],m[address(b,"BankShadow")],m.selector),application')
exec(compile(defs,str(D/'check_mmc3_sophia_support_v27.py'),'exec'),globals())
old=load(D/'mmc3-ship-lives-v25/candidate.nes');new=load(V/'candidate.nes');rows=[]
def compare(x,y,tag):
 assert x[:4]==y[:4],(tag,x[0],y[0],[(hex(j),x[1][j],y[1][j])for j in range(32768)if x[1][j]!=y[1][j]][:12],x[3],y[3])
cases=list(itertools.product(range(20),[0,1,3,255],[0,1],[0x30,0x31,0x71,0xf1,0x39,0x3d,0xee,0xff]))+list(itertools.product(range(20,256),[0],[0],[0x30,0xee]))
for i,(char,variant,mode,flags)in enumerate(cases):
 x=run(old,char,variant,mode,flags,i);y=run(new,char,variant,mode,flags,i);compare(x,y,('support',char,variant,mode,flags));rows.append(dict(kind='support',parent_cycles=x[4],candidate_cycles=y[4]))
cell_cases=list(itertools.product([0,1,2,3,4,5,6,7,9,10,11,13,19,255],[0,1],[0,7,15],[0,10,11,12],[0x30,0x71,0x39,0xff],[0,1,2]))
for i,(char,page,column,row,flags,terrain)in enumerate(cell_cases):
 def seed(m,b,case):
  base=address(b,'Block_Buffer_1')+page*208+column;index=page*208+column+row*16
  m[address(b,'R6')]=base&255;m[address(b,'R7')]=base>>8
  m[address(b,'GuestTerrainColumn')+row]=0 if terrain==0 else 0x54;m[address(b,'MetatileBuffer')+row]=0x52 if terrain==2 else 0x54
  for n in ['MmBrickHealth','MmCoinHits','MmSolidTerrain']:
   for delta in[-1,0,1]:m[address(b,n)+(index+delta)%416]=0x97
  m[address(b,'M0')]=0x12;m[address(b,'M1')]=0x34;m.page(1,3);m[address(b,'CurrentBank')]=3
  return dict(a=case*37&255,x=row,y=row*16)
 selector=64+i%8;x=run(old,char,0,0,flags,i,func='MegaManResetBlockHealth',seed=seed,selector=selector);y=run(new,char,0,0,flags,i,func='MegaManResetBlockHealth',seed=seed,selector=selector);compare(x,y,('cell',char,page,column,row,flags,terrain,selector));rows.append(dict(kind='cell',parent_cycles=x[4],candidate_cycles=y[4]))
q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),support_cases=len(cases),cell_cases=len(cell_cases),total_cases=len(rows),owned_scratch_exclusions=['discarded CPU stack','actual SMCCODE segment/tiny operands','safecall scratch','BillNativeReturnA/P/Selector'],scope='Actual assembled MMC3 bank dispatcher exercised through full raw-ID inventory matrix and relocated parser cell-reset body. Exact A/X/Y/meaningfulP/SP, bank shadows/actual selector, other application RAM, ordered nonbank I/O and final physical banks. Native IRQ/NMI/stack, history-gap ownership, audio, timing and campaign admission remain separate.')
(O/'cases.json').write_text(json.dumps(rows,separators=(',',':')));(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
