"""Compact original-ROM Prince reset/NMI/controller call discovery."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as P
O=R/'build/prince-actor-1101-v1'


def main():
 O.mkdir(exist_ok=True);executed={};calls={};summary=[];writes={}
 def trace(c):
  pc=c.pc;bank=c.memory.bank if pc<0xc000 else 7;k=f'{bank}:{pc:04X}'
  executed[k]=executed.get(k,0)+1
  if c.memory[pc]in [0x20,0x4c]:
   target=c.memory[pc+1]|c.memory[pc+2]<<8
   key=f'{bank}:{pc:04X}->{target:04X}';calls[key]=calls.get(key,0)+1
 c=P.boot(trace)
 for f in range(1400):
  pad=0x10 if 120<=f<124 or 300<=f<304 or 600<=f<604 else(1 if 900<=f<1050 else(0x81 if 1050<=f<1080 else(8 if 1120<=f<1150 else 0)))
  P.frame(c,pad,trace)
  for at,value in c.memory.writes:
   if at>=0x500:writes[at]=writes.get(at,0)+1
  if f%30==0:summary.append(dict(frame=f,bank=c.memory.bank,ctrl=c.memory.ctrl,mask=c.memory.mask,pad=pad,zero_page=list(c.memory[:128]),actor610=list(c.memory[0x610:0x640]),state700=list(c.memory[0x700:0x720])))
  if f in [599,899,1199]:
   # Exactly three compact initialized states; no frame/state forest.
   (O/f'state-{f}.bin').write_bytes(bytes(c.memory[:2048]))
 q=dict(passed=True,donor=str(P.DONOR),donor_sha256=P.SHA,source_CPU_only=True,native=False,frames=1400,scope='Originalreset/NMI/foreground/controller instructions. Untimed alternating PPUSTATUS readiness, original bank writes and CHRRAM uploads. No hostintegration or sourcephysics classification yet.',summary=summary,calls=calls,executed=executed,application_writes={f'{a:04X}':n for a,n in sorted(writes.items())},end_OAM=list(c.memory.oam),end_PPUCTRL=c.memory.ctrl,bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(P.__file__)]})
 (O/'discovery.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(passed=True,frames=1400,instruction_boundaries=len(executed),call_edges=len(calls),final_actor610=list(c.memory[0x610:0x630]),final_zero_page=list(c.memory[:96]))))


if __name__=='__main__':main()
