"""Execute original post-overlap damage decisions; no host implementation claim."""
import hashlib,itertools,json
from py65.disassembler import Disassembler
import metal_storm_cpu_1101_v2 as M
from verify_native_relocation import NesMPU
O=M.ROOT/'build/metal-storm-damage-1101-v20'

def main():
 O.mkdir(exist_ok=True);base=M.donor();cases=[]
 for armor,invuln,barrier,gravity,face in itertools.product([0,128],[0,128],[0,128],[0,128],[0,0xc0]):
  mem=M.Bus(base);mem.regs[6:8]=[0,1];mem.map()
  for a,v in {0x60:4,0x61:0,0x604:3,0x52c:0,0x5d0:armor,0x648:invuln,0x660:barrier,0x630:gravity,0x540:face,0x34:7,0x35:3,0x33:19}.items():mem[a]=v
  before=bytes(mem[:2048]);c=NesMPU(memory=mem,pc=0xe5a2);c.x=4;c.sp=224;c.stPushWord(0x5ffe)
  for steps in range(300):
   # Actual collision-loop continuation is a typed boundary, not a fake RTS.
   if c.pc in [0xe581,0xe57c,0xe630]:break
   assert mem[c.pc]!=0,hex(c.pc);c.step()
  else:raise AssertionError('source decision bound')
  endpoint=c.pc
  if gravity:assert endpoint==0xe630 and bytes(mem[:0x100])==before[:0x100]
  elif invuln:assert endpoint==0xe581 and bytes(mem[:0x100])==before[:0x100]
  elif barrier:assert endpoint==0xe630 and mem[0x540]==(face&0xf0)|1
  else:
   assert endpoint==0xe57c and mem[0x34]==2 and mem[0x35]==0 and mem[0x33]==0 and mem[0x7e7]==8
   if armor:assert mem[0x648]==128 and mem[0x750]==7 and mem[0x751]==3 and mem[0x5d0]==128
   else:assert mem[0x5d0]==0 and mem[0x648]==0
  delta={hex(a):[before[a],mem[a]] for a in range(2048) if before[a]!=mem[a] and not 0x100<=a<0x200}
  cases.append(dict(armor=armor,invulnerability=invuln,barrier=barrier,gravity_attack=gravity,facing=face,endpoint=hex(endpoint),changes=delta))
 # Recover exact-boundary disassembly of the identified decision and armor-return leaves.
 c=M.machine();c.memory.regs[6:8]=[0,1];c.memory.map();d=Disassembler(c);lines=[]
 for lo,hi in [(0xe58b,0xe689),(0x957e,0x95e0)]:
  p=lo
  while p<hi:
   n,t=d.instruction_at(p);assert t!='???';lines.append(f'Donor_{p:04X}: {t} ; '+bytes(c.memory[p:p+n]).hex());p+=n
  assert p==hi
 (O/'damage-original.asm').write_text('\n'.join(lines)+'\n')
 q=dict(passed=True,donor_sha256=M.EXPECTED,source_CPU_cases=len(cases),source_assembly_sha256=hashlib.sha256((O/'damage-original.asm').read_bytes()).hexdigest(),cases=cases,
  findings={'armor':'$05D0 bit7; contact preserves armor until the original scene2 hurt sequence clears it at95BB.', 'invulnerability':'$0648 bit7 suppresses repeated contact before the hurt transition.', 'barrier':'$0660 bit7 causes source0540 low bit1 response.', 'gravity_attack':'$0630 bit7 takes separate enemy-damage logic before ordinary injury.', 'armor_return':'95BB clears05D0 and0528, sets074B=B4 and restores saved scene34/35.'},
  scope='Controlled original CPU post-overlap branch tests, not natural collision or relocated host tests. Source scene dispatch/audio still require adaptation; no host code changed.')
 (O/'damage-contract.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='cases'}))
if __name__=='__main__':main()
