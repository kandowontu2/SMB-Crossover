"""Original NMI/frame lifecycle after an explicit accepted-contact fixture."""
import json
import metal_storm_cpu_1101_v2 as M
O=M.ROOT/'build/metal-storm-hurt-1101-v21'
FIELDS=[0x33,0x34,0x35,0x5d0,0x648,0x74b,0x528,0x70,0x540,0x7e7]

def main():
 O.mkdir(exist_ok=True);runs=[]
 for armor in [0,128]:
  c=M.boot()
  for t in range(600):M.frame(c,0x10 if t in [120,121,300,301,480,481] else 0)
  mem=c.memory;resume=c.pc
  # Explicit contact fixture, not controller-earned armor or natural overlap.
  for a,v in {0x60:4,0x61:0,0x604:3,0x52c:0,0x5d0:armor,0x648:0,0x660:0,0x630:0}.items():mem[a]=v
  before={hex(a):mem[a] for a in FIELDS}
  M.call(c,0xe5a2,x=4);c.pc=resume
  rows=[];old=None;pcs={}
  def observe(cpu):
   if cpu.pc in [0x957e,0x95bb,0x9589,0x961f]:pcs[hex(cpu.pc)]=pcs.get(hex(cpu.pc),0)+1
  for tick in range(240):
   state=[mem[a] for a in FIELDS]
   # Frame clock alone would create a row every tick; retain event edges and cadence samples.
   key=state[1:]
   if key!=old:
    rows.append(dict(frame=tick,values=state));old=key
   M.frame(c,0,trace=observe)
  runs.append(dict(armor=armor,before=before,fields=[hex(a) for a in FIELDS],transitions=rows,hits=pcs,final=[mem[a] for a in FIELDS]))
 q=dict(donor_sha256=M.EXPECTED,frames_per_case=240,controlled_contact_fixture=True,native=False,runs=runs,scope='Original scene dispatcher and NMI after unit contact. No injected RTS/API handlers. Armor and overlap are test setup, not earned gameplay.')
 (O/'lifecycle.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps([dict(armor=r['armor'],transitions=len(r['transitions']),hits=r['hits'],final=r['final']) for r in runs]))
if __name__=='__main__':main()
