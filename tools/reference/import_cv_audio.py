"""Relocate the local Castlevania sound bank using executed instruction/operand provenance.
All sound IDs are exercised. Only observed CPU operands and indirect pointer words
are relocated; byte patterns in note streams are never blindly replaced.
"""
from pathlib import Path
import json,hashlib
from py65.devices.mpu6502 import MPU
ROOT=Path(__file__).resolve().parents[2]
rom=Path('C:/NES/Castlevania (USA).nes').read_bytes()
data=rom[16:16+16384]
seen=set();words=set();calls=0
accesses={}
class Memory(list):
 def __init__(self):super().__init__([0]*65536)
mem=Memory();mem[0x8000:0xc000]=data
cpu=MPU(memory=mem)
origin={};reg={'a':None,'x':None,'y':None}
def effective(pc,mode):
 b=mem[pc+1];v=b+256*mem[pc+2]
 if mode=='zpg':return b
 if mode=='zpx':return (b+cpu.x)&255
 if mode=='zpy':return (b+cpu.y)&255
 if mode=='abs':return v
 if mode=='abx':return (v+cpu.x)&65535
 if mode=='aby':return (v+cpu.y)&65535
 if mode in ('iny','inx','ind'):
  ptr=(b+cpu.x)&255 if mode=='inx' else b if mode=='iny' else v
  nxt=(ptr+1)&255 if mode!='ind' else (ptr&0xff00)|((ptr+1)&255)
  o1,o2=origin.get(ptr),origin.get(nxt)
  val=mem[ptr]+256*mem[nxt]
  if o1 is not None and o2==o1+1 and 0x8000<=val<0xc000:words.add(o1-0x8000)
  return (val+(cpu.y if mode=='iny' else 0))&65535
 return None
def call(pc,a=None):
 global calls
 if a is not None:
  cpu.a=a;reg['a']=None;cpu.p=(cpu.p&0x7d)|(0x02 if a==0 else 0)|(a&0x80)
 cpu.sp=0xfd;mem[0x1fe]=0xff;mem[0x1ff]=1;cpu.pc=pc
 for count in range(30000):
  pc=cpu.pc
  if pc==0x200:return
  assert 0x8000<=pc<0xc000,hex(pc)
  seen.add(pc);op,mode=cpu.disassemble[mem[pc]];addr=effective(pc,mode)
  if addr is not None:accesses.setdefault(pc,set()).add(addr)
  if op in ('LDA','LDX','LDY'):
   reg[op[-1].lower()]=addr if addr is not None and addr>=0x8000 else origin.get(addr)
  elif op in ('STA','STX','STY'):origin[addr]=reg[op[-1].lower()]
  elif op in ('TAX','TAY','TXA','TYA'):reg[op[-1].lower()]=reg[op[1].lower()]
  elif op in ('ADC','SBC','AND','ORA','EOR','PLA','ASL','LSR','ROL','ROR'):reg['a']=None
  elif op in ('INX','DEX','TSX'):reg['x']=None
  elif op in ('INY','DEY'):reg['y']=None
  cpu.step();calls+=1
 raise RuntimeError('Unbounded audio routine '+hex(pc))
for sound in range(1,85):
 mem[:0x100]=[0]*256;origin.clear();reg={k:None for k in reg}
 mem[0x60]=sound;call(0x8187,sound)
 for frame in range(4000):call(0x838a)
patch={}
for pc in seen:
 op,mode=cpu.disassemble[mem[pc]]
 if mode in ('abs','abx','aby','ind'):
  target=mem[pc+1]+256*mem[pc+2]
  if 0x8000<=target<0xc000:patch[pc-0x8000+1]=target+0x2000
for pos in words:
 target=int.from_bytes(data[pos:pos+2],'little');patch[pos]=target+0x2000
(ROOT/'build/cv-audio-coverage.json').write_text(json.dumps({'instructions':sorted(seen),'words':sorted(words),'accesses':{str(k):sorted(v) for k,v in accesses.items()}}))
patch[0x185]=int.from_bytes(data[0x185:0x187],'little')+0x2000
out=ROOT/'src/audio/roster/castlevania.inc'
lines=['.segment "CV_AUDIO"','CastlevaniaNative:']
pos=0
while pos<len(data)-1024:
 if pos in patch:lines.append(f' .word ${patch[pos]:04x}');pos+=2
 else:
  end=min([pos+16,len(data)-1024]+[v for v in patch if pos<v<pos+16]);lines.append(' .byte '+','.join(f'${v:02x}' for v in data[pos:end]));pos=end
out.write_text('\n'.join(lines)+'\n')
meta={'rom_sha256':hashlib.sha256(rom).hexdigest(),'original_init':'8187','original_update':'838a','executed_instructions':len(seen),'relocated_operands':len(patch),'indirect_pointer_words':len(words),'emulated_instructions':calls,'tested_sound_ids':[1,84],'frames_per_sound':4000}
(ROOT/'docs/reference/castlevania-audio.json').write_text(json.dumps(meta,indent=2)+'\n')
print(meta)

# The relocated driver must produce the original APU writes for every exercised
# sound, including looping music. This catches missed pointer/code relocations.
rebased=bytearray(data)
for pos,target in patch.items():rebased[pos:pos+2]=target.to_bytes(2,'little')
(ROOT/'build/cv-audio-relocated.bin').write_bytes(rebased)
class Bus(list):
 def __init__(self,base,body):
  super().__init__([0]*65536);self[base:base+len(body)]=body;self.events=[]
 def __setitem__(self,k,v):
  if isinstance(k,int) and 0x4000<=k<=0x4017:self.events.append((k,v))
  super().__setitem__(k,v)
def execute(c,pc,a=None):
 if a is not None:c.a=a;c.p=(c.p&0x7d)|(2 if a==0 else 0)|(a&0x80)
 c.sp=0xfd;c.memory[0x1fe]=255;c.memory[0x1ff]=1;c.pc=pc
 for step in range(30000):
  if c.pc==0x200:return
  assert 0x8000<=c.pc<0xe000,hex(c.pc)
  c.step()
 raise RuntimeError('Audio call did not return')
for sound in range(1,85):
 original=MPU(memory=Bus(0x8000,data));moved=MPU(memory=Bus(0xa000,rebased))
 execute(original,0x8187,sound);execute(moved,0xa187,sound)
 for frame in range(4000):
  assert original.memory.events==moved.memory.events,(sound,frame,original.memory.events,moved.memory.events)
  original.memory.events.clear();moved.memory.events.clear()
  execute(original,0x838a);execute(moved,0xa38a)
print('PASS Castlevania original/relocated APU event equality, 84 sounds x 4000 frames')
