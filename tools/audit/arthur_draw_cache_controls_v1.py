"""Execute abstract loader/emitter and compare to frozen real Arthur OAM."""
from pathlib import Path
import argparse,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];O=R/'build/arthur-draw-cache-v1';P=R/'build/arthur-host-integration-v2'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import arthur_actual_host_controls_v1 as A
import arthur_draw_cache_plan_v1 as D
from py65.devices.mpu6502 import MPU

def symbols():
 return{line.split()[2].lstrip('.'):int(line.split()[1],16)for line in(O/'cache-arena.lbl').read_text().splitlines()if line.startswith('al ')}
class Mem(list):
 def __init__(self):
  super().__init__([0]*65536);self.input=(O/'canonical-input.bin').read_bytes();self.addr=0;self.toggle=0;self.buffer=0;self.ppu_reads=0;self.ppu_writes=0
  self[0xa000:0xc000]=(O/'cache-arena.bin').read_bytes()
 def __getitem__(self,i):
  if i==0x2002:self.toggle=0;return 0
  if i==0x2007:
   self.ppu_reads+=1;v=self.buffer;self.buffer=self.input[self.addr]if self.addr<len(self.input)else 0;self.addr=(self.addr+1)&16383;return v
  return super().__getitem__(i)
 def __setitem__(self,i,v):
  if i==0x2006:
   self.ppu_writes+=1
   if self.toggle:self.addr=(self.addr&0x3f00)|v
   else:self.addr=(v&63)<<8
   self.toggle^=1
  super().__setitem__(i,v)

def invoke(m,L,name,limit=1000000):
 c=MPU(memory=m,pc=L[name]);c.sp=253;c.stPushWord(0x5aff)
 for _ in range(limit):
  if c.pc==0x5b00:return c
  assert m[c.pc]!=0,('unexpected BRK',name,hex(c.pc));c.step()
 raise AssertionError(('abstract CPU bound',name,c.pc))

def expected_cache(b):
 rows=[];ptr=[];offset=444
 for mode in range(3):
  for key in range(74):
   data=D.expand(b,mode,key)
   if data is None:ptr.extend([0,0]);continue
   pc=0xc000+offset;ptr.extend([pc&255,pc>>8]);offset+=len(data);rows.append(data)
 return bytes(ptr)+b''.join(rows)

def compare(b,m,L,mode,key,x,y,high,prefix,rotation):
 sourcepose=key if key<54 else D.byte(b,'ArPalShotPose',key-54);slot=0 if key<54 else 1
 q=A.setup(b);q.put(ArHostOldPage=mode,OperMode=1,GameEngineSubroutine=8,CurrentOAMOffset=prefix,GuestOamRotationActive=int(rotation!=0),RgOamRotation=rotation)
 for i in range(4):q.set('ArR_04F0',128 if i==slot else 0,i)
 for n,v in [('ArR_0522',sourcepose),('ArR_05AF',x),('ArR_0583',(1+high)&255),('ArR_0599',y),('ArR_056D',0)]:q.set(n,v,slot)
 q.put(ArR_0064=0,ArR_0065=1)
 initial=[248,0,0,0]*64;q.m[512:768]=initial;old,tr,mn=A.owned(q,'ArHostDraw')
 for name,value in [('Mode',mode),('Key',key),('DrawX',x),('DrawXHigh',high&255),('DrawY',y),('OamOffset',prefix),('RotationActive',int(rotation!=0)),('Rotation',rotation),('BodyPage',255)]:m[L[name]]=value
 m[512:768]=initial;c=invoke(m,L,'CacheEmit')
 assert list(m[512:768])==list(q.m[512:768]),('raw ordered OAM',mode,key,x,y,high,prefix,rotation)
 assert m[L['OamOffset']]==q.get('CurrentOAMOffset'),('source OAM capacity/order',mode,key,prefix)
 if slot==0:assert m[L['BodyPage']]==q.get('SmChrBank'),('actual later native page ABI',mode,key)
 return dict(mode=mode,key=key,X=x,Y=y,high=high,prefix=prefix,rotation=rotation,new_leaf_cycles=c.processorCycles,frozen_complete_Draw_with_mapper_and_slot_wrapper_cycles=old.processorCycles,parts_emitted=((m[L['OamOffset']]-prefix)&255)//4)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists();d=dict(passed=False,native=False,physical_lease_granted=False)
 try:
  b=A.scoped_load(P/'candidate.nes');L=symbols();m=Mem();c=invoke(m,L,'CacheLoad');expected=expected_cache(b);size=m[L['OutputPtr']]+256*m[L['OutputPtr']+1]-0xc000
  assert size==len(expected)==6130
  assert bytes(m[0xc000:0xc000+size])==expected,'Real buffered-read loader differs from all201expanded source views'
  d['loader']=dict(actual_6502_cycles=c.processorCycles,output_bytes=size,PPU_buffered_reads=m.ppu_reads,PPU_address_writes=m.ppu_writes,all_cache_bytes_exact=True,scope='Abstract forced-blank PPU buffered-read model, no hardware deadline or host mapping claim.')
  rows=[]
  keys=[i for i in range(74)if D.expand(b,0,i)is not None]
  for mode in range(3):
   for key in keys:rows.append(compare(b,m,L,mode,key,104,200,0,0,0))
  d['all_source_pose_mode_cases']=len(rows)
  edges=[(0,0,0,0,0),(0,16,0,240,4),(255,239,0,248,252),(255,208,-1,4,4),(0,208,1,0,0),(7,1,0,252,0),(248,200,0,244,252),(104,200,0,255,4)]
  for mode in range(3):
   for key in[0,1,16,32,53,54,58,63,73]:
    for x,y,high,prefix,rotation in edges:rows.append(compare(b,m,L,mode,key,x,y,high,prefix,rotation))
  d.update(passed=True,raw_ordered_OAM_clipping_priority_capacity_rotation_cases=len(rows),rows=rows,arena_code_bytes=L['CacheEnd']-L['CacheLoad'],loader_bytes=L['CacheEmit']-L['CacheLoad'],emitter_bytes=L['CacheEnd']-L['CacheEmit'],cycle_scope='New emitter includes an abstract10cycle body-publication stub; old comparison includes complete real mapper/slot/common-page wrapper. This is not a net host or native performance qualification.',limits=['No header, shared source, physical PRG/RAM lease or native run changed.','Input2326B fits unused grantedCHR881..883; sequential cache6130B would require an explicitly approved extra WRAM bank.','Actual shared FarCall, normal/lag NMI and loading-phase PPU/CHR restoration integration remain unimplemented.'])
 except Exception as e:d.update(failure=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):A.sha(p)for p in[Path(__file__),Path(D.__file__),P/'candidate.nes',P/'candidate.dbg',O/'cache-arena.s',O/'cache-arena.bin',O/'canonical-input.bin']}
 a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in['rows','bindings','traceback','limits']}));assert d['passed']
if __name__=='__main__':main()
