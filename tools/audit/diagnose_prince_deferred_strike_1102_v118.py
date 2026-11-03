"""Read the first deferred-strike FF-lag difference and real minimum cut."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_deferred_strike_1102_v117 as U
C,N,O=U.C,U.N,U.O


def main():
 e,_=U.V.environment();(seed,ref,lab,epoch),_,_=U.episode(e);r=N.fork(seed);e['run'](r,'GameLoop',lab);actual=N.NesMPU;isr=[]
 class Trace(actual):
  def nmi(self):
   self.outer=(self.pc,self.sp);self.before_native=bytes(self.memory[0x200:0x800]);return super().nmi()
  def step(self):
   if getattr(self,'outer',None)==(self.pc,self.sp):
    after=bytes(self.memory[0x200:0x800]);isr.extend((0x200+i,a,z)for i,(a,z)in enumerate(zip(self.before_native,after))if a!=z);self.outer=None
   return super().step()
 N.NesMPU=Trace;rows=[]
 try:
  selected=[(346,152,3,0),min(ref['cuts'],key=lambda c:c[1])]
  for cut in selected:
   z=N.fork(seed);before=len(isr)
   try:
    got=e['run'](z,'GameLoop',lab,('lagNMI',cut));private=[(bank,hex(i),a,v)for bank in range(4)for i,(a,v)in enumerate(zip(r.ram[bank],z.ram[bank]))if a!=v];native=[(hex(i),r[i],z[i])for i in range(0x200,0x800)if r[i]!=z[i]]
    rows.append(dict(cut=cut,returned_regs=got['regs'],reference_regs=ref['regs'],minSP=got['minSP'],private_differences=private,native_final_differences=native,actual_ISR_native_changes=isr[before:]))
   except Exception as error:rows.append(dict(cut=cut,error=repr(error),actual_ISR_native_changes=isr[before:]))
 finally:N.NesMPU=actual
 q=dict(diagnostic=True,qualified=False,ROM_written=False,source_injected=True,earned_epoch=epoch,foreground_minSP=ref['minSP'],replays=rows,bindings={p.relative_to(R).as_posix():C.C.C.M.sha(p.read_bytes())for p in [Path(__file__),Path(U.__file__),O/'deferred-strike-measurement-v116.json',O/'deferred-strike-negative-v117.json']})
 (O/'deferred-strike-diagnostic-v118.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
