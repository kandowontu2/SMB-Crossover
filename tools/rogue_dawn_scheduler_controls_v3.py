"""Real-linked scheduler/state/IRQ closure; finite CPU evidence, never native."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v1 as q
import rogue_dawn_live_cue_semantics_v1 as src
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU
O=R/'build/rogue-dawn-scheduler-v3';ref=q.ref;get,put=q.get,q.put
graph=json.loads((R/'docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json').read_text())['graph']
sites={}
for z in graph['instructions']:
 a=bytes.fromhex(z['bytes'])
 if len(a)==3 and 0x4000<=int.from_bytes(a[1:],'little')<=0x4017:sites[z['pc']+0x2000]=(z['instruction'].split()[0],int.from_bytes(a[1:],'little'),z['mode'])

def nmi(m,entrySP=253,IRQ=None):
 b=m.bundle;c=NesMPU(memory=m,pc=0x5b00);c.sp=entrySP;c.a,c.x,c.y,c.p=0x36,0x57,0x98,0x61
 before=(q.cpu_state(c),q.physical(m),q.image(m),bytes(m[0x101+c.sp:0x200]),bytes(m[:256]))
 zp_live=get(m,'NmiDisable')!=0;low=c.sp;trace=[];requests=[];ir=None;m.writes.clear();c.nmi()
 for _ in range(100000):
  if c.pc==before[0][0]and c.sp==before[0][5]:break
  k=q.key(m,c);trace.append((*k,c.sp));low=min(low,c.sp)
  if IRQ and ir is None and k==IRQ:
   ir=q.interrupt(m,c,'IRQ');low=min(low,ir['minimum_SP'])
  if k[1]==97:
   if c.pc in sites:
    op,a,mode=sites[c.pc];requests.append([a+(c.y if mode=='aby'else 0),c.y if op=='STY'else c.x if op=='STX'else c.a])
   elif c.pc==0xd386:requests.append([m[0xe0]+256*m[0xe1]+c.y,c.a])
  assert m[c.pc]!=0,('BRK',k,c.sp)
  c.step();low=min(low,c.sp)
 else:raise AssertionError(('NMI timeout',q.key(m,c),c.sp))
 after=(q.cpu_state(c),q.physical(m),q.image(m),bytes(m[0x101+c.sp:0x200]),bytes(m[:256]))
 assert after[:4]==before[:4]and(not zp_live or after[4]==before[4]),('real NMI context',before[:4],after[:4])
 assert not IRQ or ir is not None,('unreached IRQ',IRQ)
 return dict(CPU=c.processorCycles,minimum_SP=low,trace=trace,requests=requests,writes=list(m.writes),IRQ=q.summary(ir)if ir else None)

def compact(z):return{k:v for k,v in z.items()if k not in['trace','requests','writes']}
def prepared(b,area=0):
 m=q.make(b);put(m,AreaType=[1,1,2,1,0,3][area],WorldNumber=[1,0,0,2,0,0][area],DisableScreenFlag=0)
 return m

def compare_state(s,m):
 b=m.bundle;p=address(b,'RdaState');expected=bytearray(s[0x600:0x700]);expected[0x1f]=0
 def mapped(x):return x+0x2000 if 0xa480<=x<0xc000 else x
 expected[0xec:0xee]=mapped(int.from_bytes(expected[0xec:0xee],'little')).to_bytes(2,'little')
 actual=bytearray(m[p:p+256])
 for i in[0x80,0x81,0x83,0x84,0x85]:actual[i]=m[0x5c20+i-0x80]
 assert actual==expected,('source RAM',[(hex(i),a,z)for i,(a,z)in enumerate(zip(actual,expected))if a!=z][:12])
 zps=[0x1e,0x23,0x2e,0x2f,0x79,0xe0,0xe1,0xe2,0xe3,0xe4,0xe5,0xe6,0xe7,0xe8,0xe9,0xea,0xeb,0xec,0xed]
 expected=bytearray(s[z]for z in zps)
 for i in[5,7,9]:expected[i:i+2]=mapped(int.from_bytes(expected[i:i+2],'little')).to_bytes(2,'little')
 actual=bytes(m[address(b,'RdaZpState'):address(b,'RdaZpState')+19])
 assert all(a==z for i,(a,z)in enumerate(zip(actual,expected))if i not in[13,14]),('source ZP',actual.hex(),expected.hex())

def main():
 assert not(O/'controls.json').exists(),'Preserve completed proof'
 build=json.loads((O/'build.json').read_text())
 for z in build['bindings']:assert ref.binding(z['path'])==z,z['path']
 b=scoped_load(O/'candidate.nes');raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
 checks={};proof=dict(passed=False,source_CPU_only=True,native_run=False,checks=checks);minSP=255
 try:
  # Every changed source register helper is exercised through genuine original
  # callers/driver and the complete real host NMI, not an isolated fake driver.
  campaigns=[];worst=None;effects=[(0x680,1<<bit)for bit in range(1,8)]+[(p,1<<bit)for p in[0x681,0x683]for bit in range(8)]
  for area in range(6):
   s=src.source(raw,3);s[0x23]=area;s[0x680]=s[0x62c]=1;m=prepared(b,area);normal=[16,1,8,64,16,128][area]
   maximum=0;reads=set();ticks=0
   for tick in range(2+len(effects)*4+8):
    if tick==1:s[0x685]=normal
    if 2<=tick<2+len(effects)*4 and(tick-2)%4==0:
     at,bit=effects[(tick-2)//4];s[at]|=bit;m[0x5c20+at-0x680]|=bit
    paused=2+len(effects)*4<=tick<2+len(effects)*4+4
    s[0x1e]=5 if paused else 3;put(m,GamePauseStatus=1 if paused else 0)
    count=tick%3 if tick else 0
    for _ in range(count):src.call(s,0xc000)
    m[0x5fb6]=count*2;put(m,NmiDisable=255)
    s.requests=[];c=NesMPU(memory=s,pc=0x5b00);c.sp=237;c.p=0x61;src.nmi(s,c)
    expected=[z for z in s.requests if z[0]!=0x4014]
    z=nmi(m);assert z['requests']==expected,('source ordered requests',area,tick,expected,z['requests'])
    compare_state(s,m);assert m[0x5fb6]==0
    reads.update((pc,bank)for pc,bank,sp in z['trace']if bank==62 and pc in[address(b,n)for n in['RdaReadAbsoluteY','RdaReadE6Y','RdaReadECY']])
    maximum=max(maximum,z['CPU']);minSP=min(minSP,z['minimum_SP']);ticks+=1
    depth=min(z['trace'],key=lambda a:a[2])
    if worst is None or depth[2]<worst['depth'][2]:
     worst=dict(area=area,tick=tick,depth=depth,entrySP=253,CPU=z['CPU'])
   campaigns.append(dict(area=area,real_source_and_host_NMIs=ticks,ordered_requests_and_state_exact=True,max_NMI_CPU=maximum,actual_helper_entries=[[hex(pc),bank]for pc,bank in sorted(reads)]))
   print('source/NMI area',area,'PASS',flush=True)
  checks['changed_helpers_actual_source_requests_and_state']=campaigns
  checks['finite_deepest_NMI']=worst
  # Real catch-up proves two, rather than assuming counts from a typed leaf.
  rows=[]
  for name,bank in[('RdControlStep',124),('RdHostCall95',94),('RdaLowHealth',62)]:
   m=prepared(b);nmi(m);put(m,RdClock=0,RdHealthLo=0x69,RdHealthHi=1,SavedJoypadBits=129)
   c,z=q.mainstep(m,(address(b,name),bank,'NMI'));assert z['actual_Main_calls']==2 and m[0x5fb6]==4
   r=nmi(m);assert sum(pc==address(b,'RdaOriginalRng')and k==97 for pc,k,sp in r['trace'])==2
   assert m[0x5fb6]==0
   rows.append(dict(cut=name,actual_Main_calls=2,actual_completed_source_RNG_calls=2,Main=q.summary(z),following_NMI=compact(r)))
  checks['real_two_Main_catchup_and_RNG']=rows
  # Both the original public192 entry and natural Main receive an entire
  # real lag NMI plus genuine existing IRQ at its measured deepest path.
  rows=[]
  for action,pad in itertools.product([0,1,2,3,4,6,7,8,255],[0,128]):
   m=prepared(b);nmi(m);put(m,RdAction=action,RdHeld=pad,RdFresh=pad,RdClock=0,RdHealthLo=0x69,RdHealthHi=1)
   c,z=q.invoke(m,'RdControlStep',sp=192);cut=min(z['trace'],key=lambda a:a[2]);entrySP=cut[2]
   # Use the exact live CPU state by replaying to the genuine cut.
   m=prepared(b);nmi(m);put(m,RdAction=action,RdHeld=pad,RdFresh=pad,RdClock=0,RdHealthLo=0x69,RdHealthHi=1,NmiDisable=255)
   # NMI deepest address is known from the real full-NMI source path above.
   old_interrupt=q.interrupt
   def nested(memory,cpu,kind='NMI',nested_irq=None):
    if kind=='NMI':return old_interrupt(memory,cpu,kind,nested_irq=(worst['depth'][0],worst['depth'][1]))
    return old_interrupt(memory,cpu,kind,nested_irq)
   q.interrupt=nested
   try:c,z=q.invoke(m,'RdControlStep',sp=192,cut=(*cut[:2],'NMI'))
   finally:q.interrupt=old_interrupt
   assert z['minimum_SP']>=128,('Control192 fullNMI+IRQ guard',action,pad,z['minimum_SP'])
   minSP=min(minSP,z['minimum_SP']);rows.append(dict(action=action,pad=pad,entrySP=192,actual_cut_SP=entrySP,minimum_SP=z['minimum_SP'],ISR=q.summary(z['interrupt'])))
  checks['public_ControlStep192_real_full_NMI_and_IRQ']=rows
  proof.update(passed=True,minimum_SP=minSP,bindings=[ref.binding(p)for p in[Path(__file__),R/'tools/rogue_dawn_scheduler_controls_v1.py',O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',ref.ROM]],limits=['Finite CPU-only source comparison; no native/fullPPU deadline claim.','Original room-script area3/phase1 retained unsupported; authored normal scene themes only.','Real DMA514 and DMC hardware stalls are absent from the CPU model.'])
 except Exception as e:
  proof.update(error=repr(e),traceback=traceback.format_exc(),bindings=[ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes']])
  p=O/'controls-negative-1.json';i=2
  while p.exists():p=O/f'controls-negative-{i}.json';i+=1
  p.write_text(json.dumps(proof,indent=2)+'\n');raise
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,minimum_SP=minSP,checks=list(checks))))
if __name__=='__main__':main()
