"""Actual original E4A3 pixel owner with declared external terrain/support."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import rogue_dawn_map_v1 as ref
from py65.devices.mpu6502 import MPU
O=R/'docs/qa/rogue-dawn-original-down-pixel-2026-10-29.json'

def pixel(raw,y,phase,pflags):
 m=bytearray(ref.cpu_image(raw,lower_bank=2))
 m[0x300]=1;m[0x301]=15;m[0x30d]=y;m[0x30f]=phase;m[0x52]=128;m[0x55]=1
 c=MPU(memory=m,pc=0xe4a3);c.sp=224;c.p=pflags;c.stPushWord(0x5aff)
 path=[];probes=[]
 for _ in range(1000):
  if c.pc==0x5b00:break
  path.append(c.pc)
  if c.pc==0xe7ad:
   # Real native E4A3 alignment/gateway executes; room decoding is the named
   # external solid floor at208, not invented original Metroid room RAM.
   probes.append(m[0x30d]+m[0x301]);c.p=(c.p&~1)|int(m[0x30d]+m[0x301]<208)
   c.pc=(c.stPopWord()+1)&65535;continue
  if c.pc==0xd976:
   m[0x307]=m[0x7d]=0;c.pc=(c.stPopWord()+1)&65535;continue
  assert m[c.pc]!=0,hex(c.pc)
  c.step()
 else:raise AssertionError('Original pixel timeout')
 blocked=y+15==208
 assert m[0x30d]==y+(not blocked)
 assert m[0x30f]==(phase-(not blocked))&255
 assert bool(c.p&1)==(not blocked)
 assert (0xe4ec in path)==(not blocked)
 return dict(y_before=y,y_after=m[0x30d],bottom_before=y+15,
  jumpDistance_before=phase,jumpDistance_after=m[0x30f],flags=pflags,
  probe_current_bottoms=probes,actual_E4EC=0xe4ec in path,carry_committed=bool(c.p&1),
  source_path=[hex(p)for p in path])

def main():
 assert not O.exists(),'Preserve original source proof'
 raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
 rows=[pixel(raw,y,j,p)for y in range(185,194)for j in[0,12,255]for p in[0x30,0x31,0x70,0x71]]
 proof=dict(passed=True,source_CPU_only=True,native_run=False,cases=len(rows),rows=rows,
  finding='Actual E4A3 permits bottom207->208, then E4AE calls E7AD with CURRENT aligned bottom208 and returnsCclear. Every genuine committed downpixel executes E4EC DEC030F, including00->FF. Blockedpixel changes neither center norjumpDistance.',
  caller_effect='030F is the source signed net upward-distance accumulator: E49E increments after an up pixel; E4EC decrements after a down pixel. Run CCC9/CCDC/CCEC tests it for airborne animation thresholds18/20hex; leaving it unchanged on descent preserves stale ascent distance. This is distinct from the early floor-stop bug.',
  external_boundaries='Only E7AD room probe and D976 actor-support callback supplied; real source E4A3 alignment/branch/body/INC030D/DEC030F/RTS executed. No source room RAM or native snapshot fabricated. Legal no-overlap floor208 contexts185..193.',
  bindings=[ref.binding(p)for p in[Path(__file__),ref.ROM,R/'src/rogue_dawn_core.s',R/'src/rogue_dawn_control.s']])
 O.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,cases=len(rows),report=ref.binding(O)),indent=2))
if __name__=='__main__':main()
