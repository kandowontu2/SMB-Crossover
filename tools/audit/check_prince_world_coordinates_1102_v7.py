"""Original-binary differential and finite state-reader closure for v7."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import recover_prince_world_coordinates_1102_v7 as W
P,O=W.P,W.O


def main():
 q=json.loads((O/'world-coordinate-recovery-v7.json').read_text());lab=P.T.labels(O/'world-coordinates-v7.lbl')
 core=(O/'contact-core.bin').read_bytes();code=(O/'world-coordinates-v7.bin').read_bytes();seed=(O/'state-899.bin').read_bytes()
 graph=json.loads((O/'contact-recovery.json').read_text())['instructions'];graph.update(q['instructions'])
 slots=[(0x100,0x200),(0x235,0x360)];fields=(0x78,0xa6);consumers=[];indirect=[]
 for origin,v in graph.items():
  mode=v['mode'];a=v['value'];mn=v['mn']
  if mn in ['JMP','JSR']:continue
  if mode in ['abs','zpg','abx','aby','zpx','zpy']and a<2048:
   hi=min(2048,a+(256 if mode in ['abx','aby','zpx','zpy']else 1))
   assert not any(a<end and hi>start for start,end in slots+[fields]),(origin,v)
   consumers.append((origin,a,hi))
  if mode in ['iny','inx','ind']:
   assert(mn,mode,a)in [('LDA','iny',0x21),('JMP','ind',0x23)],(origin,v)
   indirect.append((origin,mn,mode,a))
 counts={};cost=[]
 def compare(name,ram,args):
  d=P.machine();d.memory.switch(5);list.__setitem__(d.memory,slice(0,2048),ram)
  got=P.call(d,W.ROOTS[name],a=args[0],x=args[1],y=args[2],p=args[3],limit=10000)
  discard={0x1fc,0x1fd}|{a for a,v in d.memory.writes if 0x100<=a<0x200}
  m=[0]*65536;m[0xa000:0xa000+len(core)]=core;m[0xc000:0xc800]=ram
  m[0xc100:0xc200]=code[:256];m[0xc235:0xc235+len(code)-256]=code[256:]
  before=bytes(m[0xc000:0xc800]);c=P.T.NesMPU(memory=m,pc=lab[name]);c.a,c.x,c.y,c.p=args;c.sp=253;c.stPushWord(0x5ffe)
  for _ in range(10000):
   if c.pc==0x5fff:break
   assert m[c.pc]!=0,(name,hex(c.pc));c.step()
  else:raise AssertionError(('World coordinate bound',name))
  diff=[a for a in range(2048)if a not in discard and not any(lo<=a<hi for lo,hi in slots+[fields])and d.memory[a]!=m[0xc000+a]]
  assert not diff,(name,args,[(hex(a),d.memory[a],m[0xc000+a])for a in diff[:8]])
  assert got[:3]==(c.a,c.x,c.y)and got[3]&0xef==c.p&0xef and got[4]==c.sp,(name,args,got,(c.a,c.x,c.y,c.p,c.sp))
  for lo,hi in slots:assert bytes(m[0xc000+lo:0xc000+hi])==before[lo:hi]
  assert not any(m[:256])and not any(m[0x200:0x800]);cost.append(c.processorCycles);counts[name]=counts.get(name,0)+1
 for name in W.ROOTS:
  if name in ['PpWorldRow','PpWorldRowAdjusted']:
   fixtures=itertools.product([0,28,29,35,36,63,64,127,128,191,192,255],range(10),[0,3,4,14],[0x20,0x21,0x61,0xa1])
   for y,col,action,flags in fixtures:
    ram=bytearray(seed);ram[0x611]=y;ram[0x17]=y;ram[0x4b1]=ram[0x4b2]=col;ram[0x616]=action;ram[0x6d1]=5
    compare(name,ram,(85,19,73,flags))
  else:
   for x,face,phase,action,flags in itertools.product([0,1,4,5,19,20,31,32,159,255,256,287,319,320,511,32768,65535],[0,255],[0,1],[0,3,4,18,21,32],[0x20,0x61]):
    ram=bytearray(seed);ram[0x60f:0x611]=x.to_bytes(2,'little');ram[0x17:0x19]=x.to_bytes(2,'little');ram[0x615]=face;ram[0x4fe]=phase;ram[0x616]=action;ram[0x6d1]=5
    compare(name,ram,(85,34,73,flags))
 out=dict(passed=True,source_CPU_only=True,host_callable=False,proposed_state_code_only=True,source_original_PC_bytes_exact=q['original_PC_bytes_exact'],source_original_SHA256=q['original_SHA256'],compiled_bytes=len(code),proposed_state_code_half_open=q['proposed_state_code_half_open'],original_calls=counts,total_cases=sum(counts.values()),CPU=[min(cost),max(cost)],source_application_RAM_AXYP_SP_exact=True,host_ZP_preserved=True,code_slots_preserved=True,finite_reader_closure=dict(instruction_boundaries=len(graph),all_direct_and_indexed_domains=len(consumers),indexed_domains_expand_full256=True,no_reader_or_writer_in_proposed_slots_or_owned_fields=True,indirect_operands=indirect,indirect_closure='Original (21),Y reads are translated to the authenticated immutable script section; JMP(23) contains only translated command code targets. No pointer can address native packet or proposed executable state slots.',lifetime='C100..C200 is source CPU stack that is never read by the relocated component; actual hardware stack remains0100. C235..C360 is original OAM unreachable by recovered source instructions. Both source CPU fixtures and runtime use the native renderer packet at C200..C235, separately. Stage/decode first, zero all source state, then load these code slots and initialize before publishing owner authentication.'),scope='Actual original full coordinate/context/row/column roots, with destructive-query geometry captured in owned fields. No host material/align/control update ABI or native admission is claimed.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(W.__file__),O/'world-coordinates-v7.bin',O/'contact-core.bin']})
 (O/'world-coordinate-CPU-v7.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['finite_reader_closure','bindings']}))


if __name__=='__main__':main()
