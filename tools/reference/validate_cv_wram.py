"""Compare the final assembled WRAM port with the original CV1 APU writes."""
from pathlib import Path
import re,json
from py65.devices.mpu6502 import MPU
ROOT=Path(__file__).resolve().parents[2]
original=Path('C:/NES/Castlevania (USA).nes').read_bytes()[16:16+16384]
rom=(ROOT/'build/smb-crossover-mmc3.nes').read_bytes();moved=rom[16+0x1b*8192:16+0x1d*8192]
labels={m[2]:int(m[1],16) for m in re.finditer(r'^al ([A-Fa-f0-9]+) \.([\w]+)$',(ROOT/'build/smb-crossover-mmc3.lbl').read_text(),re.M)}
class Bus(list):
 def __init__(self,base,body):super().__init__([0]*65536);self[base:base+len(body)]=body;self.events=[]
 def __setitem__(self,k,v):
  if isinstance(k,int) and 0x4000<=k<=0x4017:self.events.append((k,v))
  super().__setitem__(k,v)
def call(c,pc,a=None):
 if a is not None:c.a=a;c.p=(c.p&0x7d)|(2 if a==0 else 0)|(a&128)
 c.sp=0xfd;c.memory[0x1fe]=255;c.memory[0x1ff]=1;c.pc=pc
 for step in range(30000):
  if c.pc==0x200:return
  assert 0x8000<=c.pc<0xe000,hex(c.pc)
  c.step()
 raise RuntimeError('Audio call did not return')
for sound in range(1,85):
 a=MPU(memory=Bus(0x8000,original));b=MPU(memory=Bus(0xa000,moved))
 call(a,0x8187,sound);call(b,labels['Cv8187'],sound)
 for frame in range(4000):
  assert a.memory.events==b.memory.events,(sound,frame,a.memory.events,b.memory.events)
  a.memory.events.clear();b.memory.events.clear();call(a,0x838a);call(b,labels['Cv838a'])
 print('PASS final CV1 WRAM driver sound '+str(sound),flush=True)
(ROOT/'build/cv-wram-validation.json').write_text(json.dumps({'sound_ids':84,'frames_each':4000,'apu_events_identical':True})+'\n')

