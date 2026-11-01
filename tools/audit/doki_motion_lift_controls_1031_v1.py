"""Original held-B/clamp, reversal and timed-lift leaves, no native emulator."""
from pathlib import Path
import hashlib,json,re,sys,traceback
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import location,Memory as CartMemory
P=R/'build/doki-original-rebuild-1031-v1';H=R/'build/doki-original-physics-audit-1031-v2/audit.json';O=R/'build/doki-motion-lift-controls-1031-v1'
INST=R/'build/contra-force-world-chr-publisher-1031-v1/joint/candidate.nes';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,motion=[],lifts=[])
 try:
  q=json.loads(H.read_text());assert q['passed']
  for p,h in q['bindings'].items():assert sha(p)==h,p
  cfg=q['source_functions'];orig=(P/'original-files/main_pro.bin').read_bytes();temp=(P/'original-files/temp_prg.bin').read_bytes();us=Path('C:/NES/Super Mario Bros. 2 (USA).nes').read_bytes();b=qualified(INST)
  class Flat:
   def __init__(self,kind):
    self.m=bytearray(65536)
    if kind=='DDP':self.m[0x6000:0xe000]=orig;self.m[0x6000:0x65ff]=temp
    else:self.m[0x8000:0xc000]=us[16:16+16384];self.m[0xc000:]=us[16+7*16384:16+8*16384]
   def __getitem__(self,p):return self.m[p]
   def __setitem__(self,p,v):self.m[p]=v&255
  def make(kind,v):
   if kind=='S2':
    m=CartMemory(b);m.page((cfg[kind]['func']['jump']-0x8000)//8192,(location(b,'S2N8C99')-16)//8192)
   else:m=Flat(kind)
   for i,value in enumerate(q['stats'][v]['Doki'if kind=='DDP'else'USA']):m[cfg[kind]['fields']['stats']+i]=value
   return m
  def put(m,k,**fields):
   for n,v in fields.items():m[cfg[k]['fields'][n]]=v
  def get(m,k,n):return m[cfg[k]['fields'][n]]
  def call(m,k,n):
   c=MPU(memory=m,pc=cfg[k]['func'][n]);c.sp=253;c.p=0x24;m[0x1fe]=254;m[0x1ff]=127
   for _ in range(10000):
    if c.pc==0x7fff:return c
    assert m[c.pc]!=0,(k,n,hex(c.pc));c.step()
   raise AssertionError('CPU bound')
  signed=lambda x:x-256 if x&128 else x
  for v in range(4):
   for face,pad in [('right',1),('left',2)]:
    for run in[0,64]:
     for held in[0,1]:
      row=dict(character=q['stats'][v]['name'],facing=face,B_held=bool(run),heavy_actor_held=bool(held),engines={});traces={}
      for kind in cfg:
       m=make(kind,v);put(m,kind,x=128,xh=0,held=pad|run,fresh=0,holding=held,obj_type=0,obj_state=1,held_index=0);trace=[]
       for tick in range(100):
        current=pad|run if tick<60 else(0 if tick<76 else(3^pad)|run)
        put(m,kind,held=current,fresh=0,frame=tick&255);call(m,kind,'action');call(m,kind,'X')
        trace.append([get(m,kind,'x')+256*get(m,kind,'xh'),get(m,kind,'xf'),signed(get(m,kind,'vx'))])
       traces[kind]=trace;row['engines'][kind]=dict(speed_at60=trace[59][2],position_at60=trace[59][0],release_at76=trace[75],reverse_at100=trace[-1],trace_sha256=hashlib.sha256(json.dumps(trace).encode()).hexdigest())
      assert traces['USA']==traces['S2'],row
      if not run:assert traces['DDP']==traces['USA'],row
      d['motion'].append(row)
  for v in range(4):
   row=dict(character=q['stats'][v]['name'],engines={});traces={}
   for kind in cfg:
    m=make(kind,v);put(m,kind,state=2,timer=0,held_index=0,holding=1,obj_type=0,obj_state=1,lift_timer=7);trace=[]
    for tick in range(200):
     call(m,kind,'lift');trace.append([get(m,kind,n)for n in['state','timer','lift_timer','animation','air','duck']])
     if get(m,kind,'state')==0:break
     timer=get(m,kind,'timer')
     if timer:put(m,kind,timer=timer-1)
    else:raise AssertionError('Lift completion bound')
    traces[kind]=trace;row['engines'][kind]=dict(updates=len(trace),trace=trace)
   assert traces['DDP']==traces['USA']==traces['S2'],row;d['lifts'].append(row)
  d.update(passed=True,motion_cases=len(d['motion']),timed_lift_cases=len(d['lifts']),scope='Explicit original legal grounded/held-heavy-actor leaf fixtures, B already held/fresh0 so no throw is requested. Actual action+Q4 integration, release/reversal and original timed enemy-lift routine run. Frame-end state timer decrement is declared. No native/controller/terrain, pickup-admission or whole-room carry claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),H,P/'original-files/main_pro.bin',P/'original-files/temp_prg.bin',INST,INST.with_suffix('.dbg')];d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],error=d.get('error'))),flush=True)
if __name__=='__main__':main()
