"""Execute compiled score calls with mapper-aware CPU memory and real selectors.

Native gameplay checks are separate. This supplement covers foreign selector
inputs without using debugger writes to NES ROM/register addresses.
"""
from pathlib import Path
import json,itertools,hashlib
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];O=R/'build/verification/score-abi-at';assert not O.exists();O.mkdir()
def labels(p):
 out={}
 for line in p.read_text().splitlines():
  if line.startswith('al '):
   _,v,n=line.split();out[n[1:]]=int(v,16)
 return out
def segment(p,name):
 for line in p.read_text().splitlines():
  if line.startswith('seg\t'):
   z=dict(t.split('=',1)for t in line[4:].split(','))
   if z['name'].strip('"')==name:return {k:(int(v,0)if k in('start','size','ooffs')else v)for k,v in z.items()}
 raise KeyError(name)
class Bus:
 def __init__(self,raw,L,smc,mapper,selector):
  self.raw=raw;self.L=L;self.mapper=mapper;self.ram=bytearray(10240);self.a=7;self.c=21;self.selector=selector;self.ports=[]
  self.ram[smc['start']:smc['start']+smc['size']]=raw[smc['ooffs']:smc['ooffs']+smc['size']]
  self.put('CurrentBank',7|(128 if mapper=='mmc5'else 0));self.put('CurrentBankC',21|(128 if mapper=='mmc5'else 0))
  if mapper=='mmc3':self.put('BankShadow',selector)
 def offset(self,a):
  if a<0x2000:return a&2047
  if 0x6000<=a<0x8000:return 2048+a-0x6000
  raise AssertionError(('Unexpected mapped access',hex(a)))
 def __getitem__(self,a):
  if a>=0x8000:
   bank=62 if a<0xa000 else self.a if a<0xc000 else self.c if a<0xe000 else 63
   return self.raw[16+bank*8192+(a&8191)]
  return self.ram[self.offset(a)]
 def __setitem__(self,a,v):
  v&=255
  if self.mapper=='mmc3'and a in(0x8000,0x8001):
   self.ports.append((a,v))
   if a==0x8000:self.selector=v
   else:
    assert(self.selector&7)==7,'Score code only changes the A bank'
    self.a=v&63
  elif self.mapper=='mmc5'and a==0x5115:self.ports.append((a,v));self.a=v&127
  else:self.ram[self.offset(a)]=v
 def put(self,n,v,i=0):self.ram[self.offset(self.L[n]+i)]=v&255
 def get(self,n,i=0):return self.ram[self.offset(self.L[n]+i)]
def run(raw,L,smc,mapper,selector,slot,pair,p,control):
 world,camera=pair;mem=Bus(raw,L,smc,mapper,selector);mem.put('Enemy_X_Position',world,slot);mem.put('Enemy_Y_Position',80+slot*7,slot);mem.put('ScreenLeft_X_Pos',camera)
 wanted=(world-camera)&255;mem.put('Enemy_Rel_XPos',(wanted+128)&255)
 cpu=MPU(memory=mem,pc=L['SetupFloateyNumber']);cpu.a=control;cpu.x=slot;cpu.y=0xa5;cpu.p=p;cpu.sp=0xe0
 stop=0x5d00;mem.ram[0x1e1]=(stop-1)&255;mem.ram[0x1e2]=(stop-1)>>8
 scratch=bytes(mem.ram[:8]);steps=0
 while cpu.pc!=stop:
  cpu.step();steps+=1;assert steps<256
 nz=(2 if wanted==0 else 0)|(128 if wanted&128 else 0)
 errors=[]
 if mem.get('FloateyNum_X_Pos',slot)!=wanted:errors.append('anchor')
 if mem.get('FloateyNum_Y_Pos',slot)!=80+slot*7 or mem.get('FloateyNum_Control',slot)!=control or mem.get('FloateyNum_Timer',slot)!=48:errors.append('other-score-fields')
 if(cpu.a,cpu.x,cpu.y,cpu.sp)!=(wanted,slot,0xa5,0xe2)or(cpu.p&0x4d)!=(p&0x4d)or(cpu.p&0x82)!=nz:errors.append('registers-flags-stack')
 if mem.a!=7 or mem.c!=21:errors.append('mapper-windows')
 if mapper=='mmc3'and(mem.selector!=selector or mem.get('BankShadow')!=selector):errors.append('selector')
 if bytes(mem.ram[:8])!=scratch:errors.append('scratch')
 return errors,steps
results=[]
for mapper in('mmc3','mmc5'):
 stem=R/'build'/f'smb-crossover-{mapper}';raw=stem.with_suffix('.nes').read_bytes();L=labels(stem.with_suffix('.lbl'));smc=segment(stem.with_suffix('.dbg'),'SMCCODE')
 selectors=range(0x40,0x48)if mapper=='mmc3'else[0]
 total=0;maxsteps=0
 for sel,slot,pair,p,control in itertools.product(selectors,range(7),[(0,0),(255,0),(2,240),(0,255),(248,192),(128,64)],[0,1,0x40,0x41,0x44,0x45,0xc0,0xc1],[1,6,11]):
  errors,steps=run(raw,L,smc,mapper,sel,slot,pair,p,control);assert not errors,(mapper,sel,slot,pair,p,control,errors);total+=1;maxsteps=max(maxsteps,steps)
 results.append(dict(mapper=mapper,ROM_sha256=hashlib.sha256(raw).hexdigest(),cases=total,max_instructions=maxsteps,all_registers_flags_stack_mapper_and_anchors=True,scope='D is0 as in the actual NES game; no interrupt injection or cycle claim.'))
 print('SCORE_ABI',mapper,total,flush=True)
# The discarded standard-call prototype changes the foreign selector to7.
proto=(R/'build/verification/score-anchor-standard-call-al/build/smb-crossover-mmc3.nes').read_bytes()
base=R/'build/checkpoints/terrain-publication-af/build/smb-crossover-mmc3';L=labels(base.with_suffix('.lbl'));smc=segment(base.with_suffix('.dbg'),'SMCCODE')
errors,steps=run(proto,L,smc,'mmc3',0x40,0,(112,0),1,1);assert errors==['selector'],errors
report=dict(passed=True,results=results,standard_prototype_negative=errors,goal_complete=False)
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCORE_ABI_PASS',sum(z['cases']for z in results))
