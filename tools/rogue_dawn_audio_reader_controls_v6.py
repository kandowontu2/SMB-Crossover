"""Fresh source/real-call/IRQ/cost proof for the private measured reader change."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
import rogue_dawn_scheduler_deep_edges_v1 as deep
q,get,put,address=v.q,v.get,v.put,v.address
P=R/'build/rogue-dawn-backdrop-v1';O=R/'build/rogue-dawn-audio-readers-v6'

def source_call(b,pc,area,y,flags,irq=False):
 m=q.make(b);m.page(1,62);m.page(2,97);put(m,CurrentBank=190,CurrentBankC=225)
 m[0x23]=area
 c=v.NesMPU(memory=m,pc=pc);c.sp=224;c.p=flags;c.a=0xa7;c.x=11;c.y=y
 old=(q.image(m),bytes(m[0x1e1:0x200]));cycles=c.processorCycles;seam=None
 raw=address(b,'RdaReadRomValue')if'RdaReadRomValue'in b['syms']else address(b,'RdaReadRom')
 for _ in range(2000):
  if c.pc==pc+3 and c.sp==224:break
  if irq and seam is None and q.key(m,c)==(raw,97):seam=q.interrupt(m,c,'IRQ')
  assert m[c.pc]!=0,('JSR helper BRK',q.key(m,c));c.step()
 else:raise AssertionError('source caller did not return')
 assert not irq or seam is not None
 assert(q.image(m),bytes(m[0x1e1:0x200]))==old
 return m,c,c.processorCycles-cycles,seam

def main():
 assert not(O/'controls.json').exists(),'Frozen proof'
 b=v.scoped_load(O/'candidate.nes');old=v.scoped_load(P/'candidate.nes')
 build=json.loads((O/'build.json').read_text())
 for z in build['bindings']:assert v.ref.binding(z['path'])==z,z['path']
 proof=dict(passed=False,native_run=False,source_CPU_only=True,checks={});checks=proof['checks']
 try:
  rows=[];savings=[]
  sites=[0xda5c,0xda61,0xdb2b,0xdf2c]
  for pc,area,y,flags in itertools.product(sites,range(6),[0,1,127,255],[0x30,0x31,0x70,0x71,0x34,0xf3]):
   om,oc,ot,_=source_call(old,pc,area,y,flags);m,c,nt,_=source_call(b,pc,area,y,flags)
   assert q.cpu_state(c)==q.cpu_state(oc)and q.physical(m)==q.physical(om)
   # Only transient savedP.N/Z is changed by the constant operand load;
   # callerP is fully exact. This field is overwritten at every next helper.
   at=address(b,'RdaSavedC');oa=address(old,'RdaSavedC')
   assert not((m[at]^om[oa])&~0x82)
   allowed=set(range(0x100,0x1e1))-set(range(0x15a,0x17b));allowed.add(at)
   diff=[i for i in range(0x8000)if i not in allowed and m[i]!=om[i]]
   assert not diff,('actual source JSR RAM',hex(pc),area,y,flags,diff[:10])
   savings.append(ot-nt)
  for pc in sites:
   m,c,cpu,irq=source_call(b,pc,1,255,0x71,True)
   rows.append(dict(source_JSR=hex(pc),area=1,Y=255,real_IRQ=irq,CPU=cpu))
  checks['576_genuine_source_JSR_fullflags_and_RAM']=dict(cases=4*6*4*6,CPU_saved_min=min(savings),CPU_saved_max=max(savings),IRQ_cases=rows)
  print('576 genuine source JSR/flags PASS',flush=True)
  # The exported diagnostic API still returns A=data/NZ, even though the
  # true source helpers now use its smaller internal endpoint.
  count=0
  for area,ptr,flags in itertools.product(range(6),[0x8000,0x8002,0x80ff,0x8100,0x9fff,0xa000,0xa480,0xb601,0xbfff],[0x30,0x31,0x70,0xf3]):
   pair=[]
   for bundle in[old,b]:
    m=q.make(bundle);m.page(1,62);m.page(2,97);put(m,CurrentBank=190,CurrentBankC=225)
    m[0x23]=area;m[0xe8]=ptr&255;m[0xe9]=ptr>>8
    c,z=q.invoke(m,'RdaReadRom',p=flags)
    pair.append((q.cpu_state(c),q.physical(m),m[address(bundle,'RdaReadValue')]))
   assert pair[0]==pair[1],('public rawreader ABI',area,hex(ptr),flags)
   count+=1
  checks['216_exported_rawreader_ABI']=dict(cases=count,public_API_extra_CPU=12,internal_no_extra_return_layer=True)
  # Complete original source NMI versus the new real host NMI, all normal
  # themes and23 effects with original six-byte live queue semantics.
  raw=v.ref.ROM.read_bytes();effects=[(0x680,1<<bit)for bit in range(1,8)]+[(p,1<<bit)for p in[0x681,0x683]for bit in range(8)]
  campaigns=[]
  for area in range(6):
   source=v.src.source(raw,3);source[0x23]=area;source[0x680]=source[0x62c]=1
   m=v.prepared(b,area);prior=v.prepared(old,area);normal=[16,1,8,64,16,128][area]
   maximum=0;gain=[];ticks=0
   for tick in range(2+len(effects)*4+8):
    if tick==1:source[0x685]=normal
    if 2<=tick<2+len(effects)*4 and(tick-2)%4==0:
     at,bit=effects[(tick-2)//4];source[at]|=bit;m[0x5c20+at-0x680]|=bit;prior[0x5c20+at-0x680]|=bit
    paused=2+len(effects)*4<=tick<2+len(effects)*4+4
    source[0x1e]=5 if paused else 3;put(m,GamePauseStatus=int(paused));put(prior,GamePauseStatus=int(paused))
    count=tick%3 if tick else 0
    for _ in range(count):v.src.call(source,0xc000)
    for host in[m,prior]:host[0x5fb6]=count*2;put(host,NmiDisable=255)
    source.requests=[];c=v.NesMPU(memory=source,pc=0x5b00);c.sp=237;c.p=0x61;v.src.nmi(source,c)
    expected=[z for z in source.requests if z[0]!=0x4014]
    z=v.nmi(m);was=v.nmi(prior)
    assert z['requests']==was['requests']==expected,('actual ordered requests',area,tick)
    v.compare_state(source,m);assert m[0x5fb6]==0
    maximum=max(maximum,z['CPU']);gain.append(was['CPU']-z['CPU']);ticks+=1
   campaigns.append(dict(area=area,ticks=ticks,new_fullNMI_CPU_max=maximum,CPU_saved_min=min(gain),CPU_saved_max=max(gain)))
   print('source/fullNMI area',area,'PASS',flush=True)
  checks['612_original_source_and_actual_old_new_fullNMIs']=campaigns
  # Actual deepest public-control and natural-Main paths include the whole
  # changed normal-theme driver plus genuine mapperIRQ at the new endpoint.
  rows=[]
  for entry,sp in [('RdControlStep',192),('IdleLoop',253)]:
   m=v.prepared(b,1);v.nmi(m);put(m,RdAction=0,NmiDisable=255)
   z=deep.execute(m,entry,sp);cut=min(z['trace'],key=lambda a:a[2])
   m=v.prepared(b,1);v.nmi(m);put(m,RdAction=0,NmiDisable=255)
   z=deep.execute(m,entry,sp,cut,IRQ=(address(b,'RdaReadRomValue'),97,cut[2]-29))
   assert z['minimum_SP']>=128
   rows.append(dict(entry=entry,entry_SP=sp,minimum_SP=z['minimum_SP'],ISR=z['interrupt']))
  checks['complete_Control192_Main_fullNMI_IRQ']=rows
  proof.update(passed=True,bindings=[v.ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'handoff.json',v.ref.ROM,R/'tools/rogue_dawn_scheduler_controls_v1.py',R/'tools/rogue_dawn_scheduler_controls_v3.py',R/'tools/rogue_dawn_scheduler_deep_edges_v1.py']],
   limits=['Finite sourceCPU/actual compiled callers; no native/wholePPU timing or audio listening claim.','No clockskip, cue omission, source data replacement or sourcearea3phase1 support.','Changed NMI time may change native controller-poll/frame alignment; no input-prefix equality claim.'])
 except Exception as e:
  proof.update(error=repr(e),traceback=traceback.format_exc())
  p=O/'controls-negative-1.json';i=2
  while p.exists():p=O/f'controls-negative-{i}.json';i+=1
  p.write_text(json.dumps(proof,indent=2)+'\n');raise
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,checks=list(checks))))
if __name__=='__main__':main()
