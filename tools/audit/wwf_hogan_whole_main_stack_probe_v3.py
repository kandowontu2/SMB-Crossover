"""Deepest genuine cold GameLoop stack, including its actual real vector."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_hogan_natural_controls_v5 as N
from ff_wram_host_isr_v4 import clone
from wwf_first_hogan_owner_isr_v1 import interrupt
H=N.H;C=N.C;J=R/'build/wwf-hogan-natural-source-v15/joint';O=R/'build/wwf-hogan-whole-main-stack-probe-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,rows=[])
 try:
  b=H.C.qualified(J/'candidate.nes');m=C.fresh(b,0)
  H.put(m,CrossoverMenuIndex=28,FmGroups=0,FmAlts=0)
  for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:N.invoke(m,n)
  H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
  z=N.invoke(m,'CrossoverMenuInput');N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',**dict(zip(['a','x','y','p'],z['AXYP'][:4])))
  N.invoke(m,'PauseRoutine',a=0)
  snapshot=None;lo=224;active_snapshot=None;active_low=224
  for age in range(600):
   if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
   H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
   def watch(mem,cpu,step):
    nonlocal lo,snapshot
    if cpu.sp<lo:lo=cpu.sp;snapshot=(age,*clone(mem,cpu))
   c=H.start(m,'GameLoop');H.finish(m,c,watch);C.A.consume(m)
  for age in range(180):
   keys=(1 if 70<=age<140 else 0)|(128 if 95<=age<113 else 0)|(64 if 145<=age<149 else 0)
   H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
   def active(mem,cpu,step):
    nonlocal lo,snapshot,active_snapshot,active_low
    if cpu.sp<lo:lo=cpu.sp;snapshot=(600+age,*clone(mem,cpu))
    if cpu.sp<active_low:active_low=cpu.sp;active_snapshot=(600+age,*clone(mem,cpu))
   c=H.start(m,'GameLoop');H.finish(m,c,active);C.A.consume(m)
  assert snapshot
  age,s,c=snapshot;q['deepest']=dict(age=age,SP=c.sp,PC=c.pc,rawmaps=s.rawtags[:],DisableScreenFlag=H.get(s,'DisableScreenFlag'),NmiDisable=H.get(s,'NmiDisable'))
  for kind in ['NMI','IRQ']:
   z,d=clone(s,c)
   if kind=='IRQ'and d.p&4:continue
   low=interrupt(z,d,kind)
   H.finish(z,d)
   q['rows'].append(dict(vector=kind,minimum_SP=low))
  assert active_snapshot
  age,s,c=active_snapshot;q['active_deepest']=dict(age=age,SP=c.sp,PC=c.pc,rawmaps=s.rawtags[:],DisableScreenFlag=H.get(s,'DisableScreenFlag'),NmiDisable=H.get(s,'NmiDisable'))
  for kind in ['NMI','IRQ']:
   z,d=clone(s,c)
   if kind=='IRQ'and d.p&4:continue
   low=interrupt(z,d,kind);H.finish(z,d);q['rows'].append(dict(scope='active',vector=kind,minimum_SP=low))
  # Discovery follows a genuine lag NMI. Inject the nested IRQ at the
  # deepest *legally unmasked* instruction, never forcing I or native CLI.
  z,d=clone(s,c);original=(d.pc,d.a,d.x,d.y,d.p,d.sp);d.nmi();nmi_low=d.sp;legal=None;legal_low=256
  for i in range(100000):
   if (d.pc,d.a,d.x,d.y,d.p,d.sp)==original:break
   nmi_low=min(nmi_low,d.sp)
   if not d.p&4 and d.sp<legal_low:legal_low=d.sp;legal=(i,*clone(z,d))
   d.step()
  assert legal
  step,z,d=legal;low=interrupt(z,d,'IRQ')
  for i in range(100000):
   if (d.pc,d.a,d.x,d.y,d.p,d.sp)==original:break
   d.step()
  else:raise AssertionError('Nested actual NMI return bound')
  assert bytes(z[0x15a:0x17b])==bytes(s[0x15a:0x17b]) and [bytes(a)for a in z.ram]==[bytes(a)for a in s.ram]
  H.finish(z,d)
  q['rows'].append(dict(scope='active_nested',vector='NMI then legalIRQ',NMI_minimum_SP=nmi_low,nested_entry_SP=legal_low,minimum_SP=low))
  q.update(passed=True,candidate=sha(J/'candidate.nes'))
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(N.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in['passed','deepest','rows','error']}))
if __name__=='__main__':main()
