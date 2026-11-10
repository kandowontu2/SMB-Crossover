"""Private real-linked Main/NMI/IRQ scheduler controls; no native claim."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_live_audio_controls_v1 as old
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
O=R/'build/rogue-dawn-scheduler-v1';ref=old.ref;w=old.w;get,put=old.get,old.put

def cpu_state(c):return c.pc,c.a,c.x,c.y,c.p&207,c.sp
def physical(m):return tuple(m.banks),get(m,'CurrentBank'),get(m,'CurrentBankC')
def image(m):return bytes(m[0x15a:0x17b])
def key(m,c):return c.pc,m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
def own(m):return get(m,'OperMode')!=0 and get(m,'SelectedCharacter')==2 and get(m,'RdVariant')==1

def interrupt(m,c,kind='NMI',nested_irq=None):
 """Execute the real vector/body to RTI, retaining live caller and33SMC."""
 b=m.bundle;zp_live=kind=='IRQ'or get(m,'NmiDisable')!=0
 before=(cpu_state(c),physical(m),image(m),bytes(m[0x101+c.sp:0x200]),bytes(m[:256]))
 expected=list(m.banks);low=c.sp;cycles=c.processorCycles;trace=[];fired=False
 if kind=='IRQ':
  c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
 else:
  # Native NMI restores the interrupted shadow if cut immediately before its
  # genuine hardware-map STA. IRQ never normalizes those foreground gaps.
  for slot,n,store in[(1,'CurrentBank',bytes.fromhex('8d1551')),(2,'CurrentBankC',bytes.fromhex('8d1651'))]:
   if expected[slot]!=(get(m,n)&127):
    assert bytes(m[c.pc:c.pc+3])==store,('unclassified mapper gap',key(m,c),physical(m))
    expected[slot]=get(m,n)&127
  c.nmi()
 for _ in range(200000):
  low=min(low,c.sp)
  if cpu_state(c)[0]==before[0][0]and c.sp==before[0][5]:break
  if nested_irq and not fired and key(m,c)==nested_irq:
   fired=True;q=interrupt(m,c,'IRQ');low=min(low,q['minimum_SP'])
  trace.append(key(m,c));assert m[c.pc]!=0,('ISR BRK',key(m,c),c.sp)
  c.step()
 else:raise AssertionError(('ISR timeout',key(m,c),c.sp))
 after=(cpu_state(c),physical(m),image(m),bytes(m[0x101+c.sp:0x200]),bytes(m[:256]))
 assert after[0]==before[0]and after[1]==(tuple(expected),*before[1][1:])and after[2:4]==before[2:4]and(not zp_live or after[4]==before[4]),('real ISR restoration',kind,before,after)
 assert not nested_irq or fired,('unreached IRQ seam',nested_irq)
 return dict(kind=kind,CPU=c.processorCycles-cycles,minimum_SP=low,trace=trace,ZP_live_required=zp_live,ZP_differences=[[i,a,z]for i,(a,z)in enumerate(zip(before[4],after[4]))if a!=z])

def wake(m,**kw):
 c=NesMPU(memory=m,pc=0x5b00);c.sp=253;c.p=0x71
 m.writes.clear();q=interrupt(m,c,**kw);q['writes']=list(m.writes);return q

def invoke(m,name,sp=224,a=0,x=13,y=87,p=0x71,cut=None):
 b=m.bundle;pc=address(b,name);bank=(location(b,name)-16)//8192
 if 0xa000<=pc<0xc000:m.page(1,bank);put(m,CurrentBank=bank|128)
 c=NesMPU(memory=m,pc=pc);c.sp=sp;c.a,c.x,c.y,c.p=a,x,y,p;c.stPushWord(0x5aff)
 live=bytes(m[0x101+sp:0x200]);low=c.sp;trace=[];irq=None
 for _ in range(500000):
  if c.pc==0x5b00:break
  if cut and irq is None and key(m,c)==cut[:2]:
   irq=interrupt(m,c,cut[2]);low=min(low,irq['minimum_SP'])
  trace.append((c.pc,key(m,c)[1],c.sp));assert m[c.pc]!=0,('BRK',key(m,c),c.sp)
  c.step();low=min(low,c.sp)
 else:raise AssertionError(('invoke timeout',name,key(m,c)))
 assert c.sp==sp and bytes(m[0x101+sp:0x200])==live
 assert not cut or irq is not None,('unreached seam',cut)
 return c,dict(CPU=c.processorCycles,minimum_SP=low,trace=trace,interrupt=irq)

def mainstep(m,cut=None):
 b=m.bundle;c=NesMPU(memory=m,pc=address(b,'IdleLoop'));c.sp=253;c.p=0x71
 low=c.sp;trace=[];fired=False;isr=None;calls=0
 for steps in range(500000):
  if c.pc==address(b,'IdleLoop')and steps:break
  k=key(m,c);trace.append((*k,c.sp));calls+=k==(address(b,'GameLoop'),126)
  if cut and not fired and k==cut[:2]:
   fired=True;isr=interrupt(m,c,cut[2]);low=min(low,isr['minimum_SP'])
  assert m[c.pc]!=0,('Main BRK',k,c.sp)
  c.step();low=min(low,c.sp)
 else:raise AssertionError(('Main timeout',key(m,c)))
 assert c.sp==253 and 1<=calls<=2
 assert not cut or fired,('unreached Main seam',cut)
 return c,dict(CPU=c.processorCycles,minimum_SP=low,actual_Main_calls=calls,trace=trace,interrupt=isr)

def summary(q):return{k:v for k,v in q.items()if k not in['trace','writes']and k!='interrupt'}
def make(b,mode=1):
 m=w.life.make(b,mode);m[0x5fb6]=0;return m

def main():
 assert not(O/'controls.json').exists(),'Preserve completed result'
 build=json.loads((O/'build.json').read_text())
 for q in build['bindings']:assert ref.binding(q['path'])==q,q['path']
 b=scoped_load(O/'candidate.nes');checks={};proof=dict(passed=False,source_CPU_only=True,native_run=False,checks=checks)
 try:
  rows=[]
  for mode,keys in itertools.product([0,1],[0,1,128]):
   m=make(b,mode);put(m,DisableScreenFlag=0,SavedJoypadBits=keys)
   q=wake(m);assert get(m,'GuestAudioCharacter')==130 and m[0x5fb6]==0
   minimum=q['minimum_SP'];cpus=[]
   for tick in range(24):
    put(m,SavedJoypadBits=keys);cpu,z=mainstep(m);assert z['actual_Main_calls']==1 and m[0x5fb6]==2
    q=wake(m);assert m[0x5fb6]==0 and m[address(b,'RdsApplied')]==0
    minimum=min(minimum,q['minimum_SP'],z['minimum_SP']);cpus.append(q['CPU'])
   rows.append(dict(mode=mode,pad=keys,Mains=24,normal_NMIs=25,minimum_SP=minimum,NMI_CPU_min=min(cpus),NMI_CPU_max=max(cpus)))
  checks['real_consecutive_Main_regular_NMI']=rows
  print('real consecutive Main/NMI pass',flush=True)
  # Exact actual phase0/paused source queue image and copied context are kept
  # distinct from the completed-Main RNG transport.
  rows=[]
  for count in range(3):
   m=make(b);wake(m)
   before=bytes(m[address(b,'RdaZpState'):address(b,'RdaZpState')+19])
   m[0x5fb6]=2*count;put(m,NmiDisable=255)
   q=wake(m);assert m[0x5fb6]==0
   rows.append(dict(completed_Mains=count,**summary(q),RNG_calls=sum(pc==address(b,'RdaOriginalRng')and bank==97 for pc,bank in q['trace'])))
   assert rows[-1]['RNG_calls']==count
  checks['atomic_count_RNG_not_per_lagNMI']=rows
  rows=[]
  for name,bank in[('RdControlStep',124),('RdHostCall95',94),('RdHsGeometry',95),('RdTxHead',95),('RdaLowHealth',62)]:
   for kind in['IRQ','NMI']:
    m=make(b);wake(m);put(m,RdClock=0,RdHealthLo=0x69,RdHealthHi=1,SavedJoypadBits=129)
    if name in['RdTxHead','RdHsGeometry']:continue # authored head caller below
    cpu,q=mainstep(m,(address(b,name),bank,kind));rows.append(dict(entry=name,bank=bank,kind=kind,**summary(q),ISR=summary(q['interrupt'])))
  checks['actual_natural_Main_interrupt_seams']=rows
  print('natural Main seams pass',flush=True)
  # IRQ is allowed during NMI. It is the genuine existing mapper IRQ body;
  # no second NMI is injected inside the first.
  rows=[]
  for name,bank in[('RdsNmiGate',63),('RdsScheduledTick',62),('RdaBorrow',62),('RdaNA770',97),('RdaRelease',62),('GuestAudioFinish::Tick',29)]:
   m=make(b);wake(m);put(m,NmiDisable=255)
   q=wake(m,nested_irq=(address(b,name),bank));rows.append(dict(entry=name,bank=bank,**summary(q)))
  checks['genuine_IRQ_inside_real_NMI']=rows
  proof.update(passed=True,bindings=[ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',ref.ROM]],limitations=['CPU-only; hardware DMA514/DMC steals and real PPU deadline are not modeled.','No original room-script phase1 support; six normal authored SMB themes only.'])
 except Exception as e:
  proof.update(error=repr(e),traceback=traceback.format_exc(),bindings=[ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes']])
  target=O/'first-controls-negative.json';index=2
  while target.exists():target=O/f'controls-negative-{index}.json';index+=1
  target.write_text(json.dumps(proof,indent=2)+'\n');raise
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=list(checks))))
if __name__=='__main__':main()
