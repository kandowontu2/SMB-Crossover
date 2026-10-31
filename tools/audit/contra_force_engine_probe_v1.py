"""Execute authentic original CF input/motion/pose/shot routines in a CPU arena.

World contacts are explicit flat-floor arena inputs. No host/native claim.
"""
from pathlib import Path
import hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from verify_native_relocation import NesMPU
P=R/'build/contra-force-reproduction-v2';O=R/'build/contra-force-engine-probe-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
RAW=(P/'candidate.nes').read_bytes();assert sha(P/'candidate.nes')=='ba5337367a2140c72ae40826ff4fb9b86a38798ed129edc9bd519aec8818abfa'
class Mem(list):
 def __init__(self):
  super().__init__([0]*65536);self.select=6;self.reg=[0]*8;self.reg[6:8]=[4,5];self.mapper=[];self.map()
 def map(self):
  for at,b in zip([0x8000,0xa000,0xc000,0xe000],[self.reg[6],self.reg[7],14,15]):
   list.__setitem__(self,slice(at,at+8192),RAW[16+b*8192:16+(b+1)*8192])
 def pair(self,lo):self.reg[6:8]=[lo,lo+1];self.map()
 def __setitem__(self,at,v):
  if isinstance(at,int)and at>=0x8000:
   if at==0x8000:self.select=v&7;assert not(v&0x40),'Arena expects source PRG mode0'
   elif at==0x8001:
    self.reg[self.select]=v
    if self.select>=6:self.map()
   elif at not in[0xa000,0xa001,0xc000,0xc001,0xe000,0xe001]:raise AssertionError(('unmodeled source ROM write',hex(at),v))
   self.mapper.append((at,v));return
  super().__setitem__(at,v)
def machine(var,gear=0):
 m=Mem();m[0xb1]=var;m[0x7f+var]=0x10|gear;m[0x782]=1;m[0x64e]=112;m[0x668]=168;m[0x682]=10;m[0x7d2]=1
 return NesMPU(memory=m)
def call(c,at,x=0,a=0,y=0):
 c.pc=at;c.x=x;c.a=a;c.y=y;c.p=0x24;c.sp=255;c.stPushWord(0x7ffe)
 start=c.processorCycles;trace=[]
 while c.pc!=0x7fff:
  assert len(trace)<30000,('source routine bound',hex(at),hex(c.pc))
  assert c.memory[c.pc]!=0,('source BRK',hex(at),hex(c.pc))
  trace.append((c.memory.reg[6],c.memory.reg[7],c.pc));c.step()
 return dict(CPU=c.processorCycles-start,instructions=len(trace),trace=trace)
def step(c,pad,ground=True):
 m=c.memory;m.pair(4);m[0x23]=(m[0x23]+1)&255;m[0x40]=pad&~m[0x42];m[0x42]=pad
 call(c,0xf640);m[0x7d2]=1 if ground else 0
 z=call(c,0xa2e7);z2=call(c,0xa538)
 d=[m[0x7e6]+256*m[0x7e8],m[0x7ea]+256*m[0x7ec]]
 # This is the genuine original final position integration boundary with
 # zero original camera delta, not a Python reproduction of its fractions.
 m.pair(0);z3=call(c,0xbce0);m.pair(4)
 return dict(x=m[0x64e],y=m[0x668],fractionX=m[0x6c8],fractionY=m[0x6de],dX=d[0]if d[0]<32768 else d[0]-65536,dY=d[1]if d[1]<32768 else d[1]-65536,input_state=m[0x7aa],air_age=m[0x7b4],animation=[m[0x634],m[0x61a]],source_CPU=z['CPU']+z2['CPU']+z3['CPU'],shot_count=m[0x83])
def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,original_source=True,host=False,arena_world='Explicit source07D2 flat-floor/air contacts; original query tables otherwise zero-camera source data.',checks={})
 try:
  rows=[]
  for var in range(4):
   c=machine(var);seq=[step(c,1)for _ in range(24)]
   expected=[312,304,288,319][var]
   assert all(z['dX']==expected and z['dY']==0 for z in seq),(var,seq)
   assert seq[-1]['x']>112
   rows.append(dict(variant=var,source_speed_8_8=expected,rows=seq))
  q['checks']['four_source_walks']=rows
  print('4 original source walks PASS',flush=True)
  rows=[]
  for var in range(4):
   c=machine(var);seq=[]
   for age in range(48):
    m=c.memory;ground=not(m[0x7aa]&64)
    z=step(c,0x80 if age==0 else 0,ground=ground);seq.append(z)
    if z['dY']>=0 and z['y']>=168 and age>1:
     # Host contact proposal is explicit; no original landing claim here.
     break
   assert min(z['y']for z in seq)<168 and any(z['dY']>0 for z in seq),(var,seq)
   rows.append(dict(variant=var,initial_source_velocity=-[960,896,832,928][var],apex=168-min(z['y']for z in seq),rows=seq))
  q['checks']['four_original_source_jump_arcs']=rows
  rows=[]
  for var in range(4):
   for gear in range(3):
    c=machine(var,gear);z=step(c,0x40)
    m=c.memory;slots=[dict(slot=i,kind=m[0x782+i],animation=[m[0x634+i],m[0x61a+i]],direction=m[0x6b2+i],state=m[0x682+i])for i in range(2,10)if m[0x782+i]]
    assert z['shot_count']>0 and slots,(var,gear,z,slots)
    rows.append(dict(variant=var,gear=gear,body=z,actual_spawned_slots=slots))
  q['checks']['twelve_actual_source_weapon_allocations']=rows
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files={Path(__file__),Path(sys.modules['verify_native_relocation'].__file__),P/'proof.json',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl'}
  q['bindings']={str(p.resolve()):sha(p)for p in sorted(files)}
  p=O/'controls.json';p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),path=str(p),sha256=sha(p))),flush=True)
if __name__=='__main__':main()
