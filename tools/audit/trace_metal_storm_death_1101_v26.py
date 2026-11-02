"""Trace the real donor lethal scene and animation, without fabricated returns."""
import json
import metal_storm_cpu_1101_v2 as M
O=M.ROOT/'build/metal-storm-natural-armor-1101-v26'
FIELDS=[0x34,0x35,0x510,0x528,0x4e0,0x4f8,0x480,0x498,0x4b0,0x4c8,0x5b8,0x588,0x6f8]

def main():
 c=M.boot()
 for t in range(600):M.frame(c,16 if t in [120,121,300,301,480,481] else 0)
 m=c.memory;resume=c.pc
 for a,v in {0x60:4,0x61:0,0x604:3,0x52c:0,0x5d0:0,0x648:0,0x660:0,0x630:0}.items():m[a]=v
 M.call(c,0xe5a2,x=4);c.pc=resume
 rows=[];dec=[];previous=None;tick=0;executed={}
 def trace(cpu):
  mem=cpu.memory;p=cpu.pc;op=mem[p]
  if mem[0x34]==2 and p>=0x8000:
   key=f'{mem.banks[(p-0x8000)//8192]}:{p:04x}';executed[key]=executed.get(key,0)+1
  if op in [0xc6,0xd6,0xce,0xde]:
   a=mem[p+1]+(256*mem[p+2] if op in [0xce,0xde] else 0)+(cpu.x if op in [0xd6,0xde] else 0)
   if 0x420<=a<0x440:dec.append(dict(frame=tick,pc=hex(p),banks=mem.banks[:],address=hex(a),before=mem[a]))
 for tick in range(360):
  values=[m[a] for a in FIELDS]
  if values!=previous:rows.append(dict(frame=tick,values=values));previous=values
  M.frame(c,0,trace=trace)
 q=dict(donor_sha256=M.EXPECTED,controlled_lethal_contact=True,native=False,frames=360,fields=list(map(hex,FIELDS)),transitions=rows,counter_decrements=dec,scene2_executed=executed,scope='Original donor frame/NMI dispatch after accepted-contact fixture. No stubs, timing emulation is untimed; not host gameplay proof.')
 (O/'donor-death.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(transitions=len(rows),decrements=dec,scene2_instructions=len(executed))))
if __name__=='__main__':main()
