from pathlib import Path
import json,sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-ship-lives-v25';O=V/'sophia-stall-v1';sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,location
b=load(V/'candidate.nes');raw=(O/'observed-ram.bin').read_bytes();m=MPU();m.memory[:2048]=raw[:2048];m.memory[0x6000:0x8000]=raw[2048:]
for window,bank in enumerate([254,69,36,255]):m.memory[0x8000+window*8192:0xa000+window*8192]=b['raw'][16+bank*8192:16+(bank+1)*8192]
d=Disassembler(m);print('Runtime SMC and neighbouring stack bytes:')
at=0x155
while at<0x19c:
 size,text=d.instruction_at(at);print('%04x %s %s'%(at,bytes(m.memory[at:at+size]).hex(),text));at+=size
print('Stack above SP96:',bytes(m.memory[0x197:0x1d8]).hex(' '))
for bank in [69,93,36]:
 rows=[]
 for n,s in b['syms'].items():
  if 'seg'not in s:continue
  g=b['segs'][s['seg']]
  if 'ooffs'not in g:continue
  pos=location(b,n);address=int(s['val'],0)
  if (pos-16)//8192==bank and 0x8000<=address<0x10000:rows.append((address,n))
 print('Bank',bank,'near A430:',[(hex(a),n)for a,n in sorted(rows)if 0xa300<=a<=0xa500][:20])
print('Zero-page stack caller snapshots:',bytes(m.memory[0x120:0x155]).hex(' '))
