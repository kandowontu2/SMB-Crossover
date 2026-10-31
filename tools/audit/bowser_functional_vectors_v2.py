"""Real vectors across final Bowser loader, ROM callbacks and loaded source helpers."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_actual_host_checks_v1 as A
import bowser_gameplay_component_controls_v2 as C
T=A.T;H=A.H;V=T.V;J=A.J;O=R/'build/bowser-functional-vectors-v2'
from check_tmnt_render_oa import load,address
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def begin(m,name,slot=None):
 c=H.start(m,name,p=0x30)
 if slot is not None:
  p=address(m.bundle,name)+slot*3;m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=p&255;m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=p>>8
 return c

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,source_CPU=True,rows=[])
 try:
  b=load(J/'candidate.nes');cold=T.make(b);warm=T.fork(cold);T.call(warm,'BwLoad');C.rc(warm,'BwConstruct')
  plans=[('coldload',cold,'BwLoad',None,False),('movement',warm,'BwServiceVeneers',0,True),('graphics',warm,'BwServiceVeneers',1,True),('coldportrait',cold,'BwServiceVeneers',17,True),('colors',warm,'BwServiceVeneers',26,True),('status',warm,'BwServiceVeneers',30,True)]
  for family,seed,name,slot,active in plans:
   m=T.fork(seed);H.put(m,NmiDisable=0 if active else 255);c=begin(m,name,slot);seen=set();snapshots=[]
   for step in range(500000):
    if c.pc==0x5b00:break
    tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
    own=(tag in[196,164,212,195,211,216,215,3]and 0xa000<=c.pc<0xc000)or 0x15a<=c.pc<0x17b
    key=(tag,c.pc)
    if own and key not in seen:
     # Snapshot only actual first unique instruction occurrences, including
     # mapper/shadow gaps; no guessed return stacks or manual source physics.
     snapshots.append((step,T.fork(m),(c.pc,c.a,c.x,c.y,c.p,c.sp,c.processorCycles)))
     seen.add(key)
    c.step()
   else:raise AssertionError(('actual source trace bound',family))
   baseline=bytes(m.ram[3]);endmaps=m.rawtags[:]
   for step,snap,regs in snapshots:
    kinds=[('NMI',0,0),('NMI',255,0),('NMI',0,1)]if active else [('NMI',255,0)]
    if not regs[4]&4:kinds.append(('IRQ',255,0))
    for kind,lag,pause in kinds:
     z=T.fork(snap);H.put(z,NmiDisable=lag,GamePauseStatus=pause)
     from verify_native_relocation import NesMPU
     cc=NesMPU(memory=z,pc=regs[0]);cc.a,cc.x,cc.y,cc.p,cc.sp,cc.processorCycles=regs[1:]
     r=V.interrupt(z,cc,kind);H.finish(z,cc)
     assert cc.sp==224 and bytes(z.ram[3])==baseline and z.rawtags==endmaps,(family,step,kind)
     q['rows'].append(dict(family=family,step=step,PC=regs[0],lag=lag,pause=pause,**r))
  q.update(passed=True,actual_vector_cases=len(q['rows']),normal_lag_pause_legalIRQ=True,all33SMC_liveAXYP_SP_page1_rawmaps_and_completeRAM3_preserved=True)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(V.__file__),Path(A.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings']}));assert q['passed']
if __name__=='__main__':main()
