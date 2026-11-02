"""Locate original damage/armor transitions using controller-driven donor code."""
from pathlib import Path
import json
from py65.disassembler import Disassembler
import metal_storm_cpu_1101_v2 as M
O=M.ROOT/'build/metal-storm-damage-1101-v20'

def main():
 O.mkdir(exist_ok=True);c=M.boot()
 for t in range(600):M.frame(c,0x10 if t in [120,121,300,301,480,481] else 0)
 events=[];pcs={};tick=0
 watch=set(range(0x438,0x440))|{0x6f8,0x588,0x510,0x630}
 def observe(cpu):
  mem=cpu.memory;p=cpu.pc;op=mem[p]
  if op not in [0x8d,0x9d,0x99,0xee,0xce]:return
  a=mem[p+1]+256*mem[p+2]+(cpu.x if op==0x9d else cpu.y if op==0x99 else 0)
  if a not in watch:return
  old=mem[a];v=cpu.a if op in [0x8d,0x9d,0x99] else (old+(1 if op==0xee else -1))&255
  if v==old:return
  key=(tuple(mem.banks),p)
  if key not in pcs:
   d=Disassembler(cpu);lines=[];at=max(0x8000,p-16)
   # This vicinity is only a discovery aid; entry boundaries are not proven.
   while at<p+36:
    n,text=d.instruction_at(at);lines.append(f'{at:04x}: {text}');at+=n
   pcs[key]=lines
  if len(events)<300:events.append(dict(frame=tick,pc=hex(p),banks=mem.banks[:],address=hex(a),old=old,new=v))
 for tick in range(1200):M.frame(c,1,trace=observe)
 q=dict(donor_sha256=M.EXPECTED,controller_only=True,source_CPU_untimed=True,native=False,frames=1200,events=events,sites=[dict(banks=list(k[0]),pc=hex(k[1]),disassembly=v) for k,v in pcs.items()],scope='Discovery only. Adjacent disassembly is not an instruction-boundary proof or a host implementation.')
 (O/'discovery.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(events=len(events),sites=len(pcs),final_banks=c.memory.banks)))
if __name__=='__main__':main()
