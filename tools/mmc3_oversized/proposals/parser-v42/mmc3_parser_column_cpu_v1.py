from pathlib import Path
import hashlib,itertools,json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-parser-v42';O=V/'column-cpu-v1';O.mkdir(exist_ok=False)
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
source=(D/'check_mmc3_static_call_v37.py').read_text();head=source[source.index("source=(D/'check_mmc3_sophia_support_v27.py')"):source.index("old=load(D/'mmc3-ship-lives-v25/candidate.nes')")]
head=head.replace("exec(compile(defs,str(D/'check_mmc3_sophia_support_v27.py'),'exec'),globals())", "defs=defs.replace('application=bytes(0 if i in excluded else m[i]for i in range(0x8000))', 'application=bytearray(m[:0x8000])\\n for i in excluded:\\n  if i<0x8000:application[i]=0\\n application=bytes(application)')\nexec(compile(defs,str(D/'check_mmc3_sophia_support_v27.py'),'exec'),globals())")
exec(compile(head,str(D/'check_mmc3_static_call_v37.py'),'exec'),globals())
old=load(D/'mmc3-ship-lives-v25/candidate.nes');base=load(V/'baseline.nes');new=load(V/'candidate.nes');rows=[]
cases=list(itertools.product([0,1,4,7,11,13,19,255],[0,1],range(16),range(4),[0x30,0x71,0xff]))
for i,(char,page,col,pattern,flags)in enumerate(cases):
 def seed(m,b,case):
  p=address(b,'Block_Buffer_1')+page*208+col;m[address(b,'R6')]=p&255;m[address(b,'R7')]=p>>8
  for row in range(13):
   tile=[0,0x52,0x54,0xc1][(row+pattern)%4]
   m[address(b,'MetatileBuffer')+row]=tile;m[address(b,'GuestTerrainColumn')+row]=tile if pattern%2 else 0
   for name in ['MmBrickHealth','MmCoinHits','MmSolidTerrain']:
    m[address(b,name)+page*208+col+row*16]=0x97
  return dict(a=case*37&255,x=0,y=0)
 def execute(b):return run(b,char,0,0,flags,i,func='ChkMTLow',seed=seed,selector=64+i%8)
 x=execute(base);y=execute(new);z=execute(old)
 assert x[:4]==y[:4],('column',i,x[0],y[0])
 assert z[:4]==y[:4],('native_column',i,z[0],y[0])
 assert z[4]==y[4]and x[4]-y[4]==2990,('column_cycles',i,z[4],x[4],y[4])
 rows.append(dict(character=char,page=page,column=col,pattern=pattern,flags=flags,native_cycles=z[4],baseline_cycles=x[4],candidate_cycles=y[4]))
(O/'cases.json').write_text(json.dumps(rows,separators=(',',':')))
q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),cases=len(rows),rows_per_column=13,candidate_column_cycles=[min(r['candidate_cycles']for r in rows),max(r['candidate_cycles']for r in rows)],saved_cycles_per_column=[min(r['baseline_cycles']-r['candidate_cycles']for r in rows),max(r['baseline_cycles']-r['candidate_cycles']for r in rows)],native_column_cycle_delta=0,scope='Execute actual native ChkMTLow13-row column commit loop, real fixed MTileAttribute, actual parser bank and all13 native cell resets. Both block pages/all16 columns,8 character IDs, four mixed terrain/tile patterns, flags/selectors. Exact registers/meaningfulP/SP, bank maps/selector, application RAM and ordered nonbank I/O; native V25 cycle parity. Excludes ProcessAreaData/layout-generation earlier in AreaParserCore, IRQ/NMI and native frame cadence.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
