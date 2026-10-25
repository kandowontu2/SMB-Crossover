"""Execute the unchanged baseline's real column parser for audit-only static maps.

Seeded CPU calls here are explicitly map decoding, not gameplay/clear evidence.
"""
from pathlib import Path
import hashlib, importlib.util, json, sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/level-layout-audit-agent'
sys.path.insert(0,str(R/'build/verification/specialist-mario-easy-hard-source-a/deps'))
from py65.devices.mpu6502 import MPU
sp=importlib.util.spec_from_file_location('map_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
class Bus(list):
 def __init__(self,image):super().__init__([0]*65536);self.image=image;self.selector=0
 def __setitem__(self,k,v):
  if isinstance(k,int)and k==0x8000:self.selector=v;return
  if isinstance(k,int)and k==0x8001:
   assert self.selector==0x47,('unexpected mapper switch',self.selector)
   list.__setitem__(self,slice(0xa000,0xc000),self.image.raw[16+8192*v:16+8192*(v+1)]);return
  super().__setitem__(k,v)
class Decode:
 def __init__(self):
  self.i=im.Image(R/'build/smb-crossover-mmc3-baseline.nes');self.mem=Bus(self.i)
  for name in ('CODE','LOWCODE','COLLISION','LEVEL','FIXED'):
   seg=next(v for v in self.i.segs.values()if v['name']==name)
   self.mem[seg['start']:seg['start']+seg['size']]=self.i.raw[seg['ooffs']:seg['ooffs']+seg['size']]
  self.cpu=MPU(memory=self.mem);self.cpu.p=0x24
 def set(self,n,v):self.mem[self.i.ram[n]]=v
 def get(self,n):return self.mem[self.i.ram[n]]
 def call(self,n):
  c=self.cpu;c.pc=self.i.hook(n)['address'];c.sp=0xfd;self.mem[0x1fe]=0xfe;self.mem[0x1ff]=0x5f
  steps=0
  while c.pc!=0x5fff:
   c.step();steps+=1
   assert steps<50000,(n,hex(c.pc))
  return steps
 def area(self,pointer,width,world=0):
  self.mem[:0x800]=[0]*0x800
  self.mem[0x8000]=0x47;self.mem[0x8001]=2;self.set('CurrentBank',2)
  seg=next(v for v in self.i.segs.values()if v['name']=='SMCCODE')
  self.mem[seg['start']:seg['start']+seg['size']]=self.i.raw[seg['ooffs']:seg['ooffs']+seg['size']]
  self.set('AreaPointer',pointer);self.set('WorldNumber',world)
  self.set('Hidden1UpFlag',1)
  self.call('GetAreaDataAddrs')
  for n in range(3):self.mem[self.i.ram['AreaObjectLength']+n]=255
  rows=[[]for _ in range(13)];steps=0
  for x in range(width):
   steps+=self.call('AreaParserCore')
   for y in range(13):rows[y].append(self.mem[self.i.ram['MetatileBuffer']+y])
   self.call('IncrementColumnPos')
  return dict(pointer=pointer,width=width,steps=steps,rows=rows)
def main():
 d=Decode();areas={}
 for kind,typ,count in [('Water',0,3),('Ground',1,22),('Underground',2,3),('Castle',3,6)]:
  for n in range(count):
   key=f'{kind}{n+1}';print('Decoding',key,flush=True);areas[key]=d.area((typ<<5)|n,400,7 if key=='Water3'else 0)
 result=dict(scope='Static parser execution only; not an emulator/controller proof.',ROM_sha256=hashlib.sha256(d.i.raw).hexdigest(),areas=areas)
 (O/'nes-column-inventory.json').write_text(json.dumps(result)+'\n')
 print(dict(areas=len(areas),columns=sum(z['width']for z in areas.values())))
if __name__=='__main__':main()
