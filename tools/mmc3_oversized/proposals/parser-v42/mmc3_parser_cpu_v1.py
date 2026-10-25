from pathlib import Path
import argparse, hashlib, itertools, json, sys, time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);ap.add_argument('--baseline');ap.add_argument('--out',default='cpu-v1');args=ap.parse_args()
 V=D/args.candidate;O=V/args.out;O.mkdir(exist_ok=False)
 source=(D/'check_mmc3_static_call_v37.py').read_text()
 # Reuse the previously admitted actual-mapper CPU harness definitions.
 head=source[source.index("source=(D/'check_mmc3_sophia_support_v27.py')"):source.index("old=load(D/'mmc3-ship-lives-v25/candidate.nes')")]
 head=head.replace("exec(compile(defs,str(D/'check_mmc3_sophia_support_v27.py'),'exec'),globals())", "defs=defs.replace('application=bytes(0 if i in excluded else m[i]for i in range(0x8000))', 'application=bytearray(m[:0x8000])\\n for i in excluded:\\n  if i<0x8000:application[i]=0\\n application=bytes(application)')\nexec(compile(defs,str(D/'check_mmc3_sophia_support_v27.py'),'exec'),globals())")
 exec(compile(head,str(D/'check_mmc3_static_call_v37.py'),'exec'),globals())
 old=load(D/'mmc3-ship-lives-v25/candidate.nes');base=load(Path(args.baseline)if args.baseline else D/'mmc3-static-call-v39/candidate.nes');new=load(V/'candidate.nes');rows=[]
 def compare(x,y,tag):
  assert x[:4]==y[:4],(tag,x[0],y[0],[(hex(j),x[1][j],y[1][j])for j in range(32768)if x[1][j]!=y[1][j]][:12],x[3],y[3])
 cases=list(itertools.product(range(20),[0,1,3,255],[0,1],[0x30,0x31,0x71,0xf1,0x39,0x3d,0xee,0xff]))+list(itertools.product(range(20,256),[0],[0],[0x30,0xee]))
 for i,(char,variant,mode,flags)in enumerate(cases):
  x=run(base,char,variant,mode,flags,i);y=run(new,char,variant,mode,flags,i);compare(x,y,('support',char,variant,mode,flags));rows.append(dict(kind='support',parent_cycles=x[4],candidate_cycles=y[4]))
 cell_cases=list(itertools.product([0,1,2,3,4,5,6,7,9,10,11,13,19,255],[0,1],[0,7,15],[0,10,11,12],[0x30,0x71,0x39,0xff],[0,1,2]))
 for i,(char,page,column,row,flags,terrain)in enumerate(cell_cases):
  def seed(m,b,case):
   buf=address(b,'Block_Buffer_1')+page*208+column;index=page*208+column+row*16
   m[address(b,'R6')]=buf&255;m[address(b,'R7')]=buf>>8
   m[address(b,'GuestTerrainColumn')+row]=0 if terrain==0 else 0x54;m[address(b,'MetatileBuffer')+row]=0x52 if terrain==2 else 0x54
   for n in ['MmBrickHealth','MmCoinHits','MmSolidTerrain']:
    for delta in[-1,0,1]:m[address(b,n)+(index+delta)%416]=0x97
   m[address(b,'M0')]=0x12;m[address(b,'M1')]=0x34;m.page(1,3);m[address(b,'CurrentBank')]=3
   return dict(a=case*37&255,x=row,y=row*16)
  selector=64+i%8
  x=run(base,char,0,0,flags,i,func='MegaManResetBlockHealth',seed=seed,selector=selector);y=run(new,char,0,0,flags,i,func='MegaManResetBlockHealth',seed=seed,selector=selector);compare(x,y,('cell',char,page,column,row,flags,terrain,selector))
  z=run(old,char,0,0,flags,i,func='MegaManResetBlockHealth',seed=seed,selector=selector);compare(z,y,('native_cell',i));assert z[4]==y[4],('native_cell_cycles',i,z[4],y[4])
  rows.append(dict(kind='cell',native_cycles=z[4],parent_cycles=x[4],candidate_cycles=y[4]))
 (O/'cases.json').write_text(json.dumps(rows,separators=(',',':')))
 print('Support and cell cases pass:',len(rows),flush=True)
 flags=[0x00,0x01,0x04,0x08,0x40,0x80,0x81,0x89,0xc1,0xcf,0x30,0x31,0x71,0x39,0xee,0xff]
 warp_cases=list(itertools.product(range(256),[0,1,0x7f,0x80,0xff],flags))
 warp_cases+=list(itertools.product([0,10,11,127,255],range(256),flags))
 warp_cases+=list(itertools.product([0,10,11,127,255],[0,1,0x7f,0x80,0xff],range(256)))
 warp_rows=[]
 for i,(xreg,a,flag)in enumerate(warp_cases):
  def seed(m,b,case):
   m.page(1,3);m[address(b,'CurrentBank')]=3
   return dict(a=a,x=xreg,y=(i*53)&255)
  selector=(i*71)&255
  x=run(base,0,0,0,flag,i,func='BillNativeReadWarp',seed=seed,selector=selector);y=run(new,0,0,0,flag,i,func='BillNativeReadWarp',seed=seed,selector=selector)
  compare(x,y,('warp',xreg,a,flag,selector))
  assert y[0][0]==a and y[0][1]==xreg and y[0][-2:]==(71,7),(xreg,a,flag,y[0])
  warp_rows.append((x[4],y[4],y[5]))
  if(i+1)%10000==0:print('Warp cases:',i+1,flush=True)
 q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),parent_ROM_sha256=hashlib.sha256(base['raw']).hexdigest(),native_reference_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),support_cases=len(cases),cell_cases=len(cell_cases),warp_cases=len(warp_cases),parser_added_cycles_vs_native=[min(z['candidate_cycles']-z['native_cycles']for z in rows if z['kind']=='cell'),max(z['candidate_cycles']-z['native_cycles']for z in rows if z['kind']=='cell')],parser_saved_cycles_vs_v39=[min(z['parent_cycles']-z['candidate_cycles']for z in rows if z['kind']=='cell'),max(z['parent_cycles']-z['candidate_cycles']for z in rows if z['kind']=='cell')],support_added_cycles=[min(z['candidate_cycles']-z['parent_cycles']for z in rows if z['kind']=='support'),max(z['candidate_cycles']-z['parent_cycles']for z in rows if z['kind']=='support')],warp_added_cycles=[min(y-x for x,y,_ in warp_rows),max(y-x for x,y,_ in warp_rows)],minimum_warp_stack_pointer=min(z for _,_,z in warp_rows),scope='Actual assembled code with real MMC3 mapper, immutable common, tiny SMC, and rare ABI. Exact A/X/Y/meaningfulP/SP, selector, application RAM excluding declared stack/SMC/return scratch, final bank maps and ordered nonbank I/O. Native parser cycle parity with V25 and230-cycle saving against V39. Full256 indexed warp source bytes exercised; all rawX/allA/all256P/all256 incoming selectors covered in pairwise matrices. No native IRQ/NMI/game-loop/audio/60Hz qualification.')
 (O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)

if __name__=='__main__':main()
