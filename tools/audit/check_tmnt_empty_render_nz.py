"""TMNT equipment CPU component checks. Seeded RAM is not natural collection."""
from pathlib import Path
import argparse,hashlib,json,gzip
from py65.devices.mpu6502 import MPU
P=argparse.ArgumentParser();P.add_argument('--rom',type=Path,required=True);P.add_argument('--baseline',type=Path,required=True);P.add_argument('--output',type=Path,required=True);A=P.parse_args();O=A.output;O.mkdir(parents=True,exist_ok=False);raw=A.rom.read_bytes();S={};G={}
f=A.rom.with_suffix('.dbg');txt=f.read_text()if f.exists()else gzip.decompress(A.rom.with_suffix('.dbg.gz').read_bytes()).decode()
for line in txt.splitlines():
 if not line.startswith(('sym\t','seg\t')):continue
 z=dict(x.split('=',1)for x in line[4:].split(',')if '='in x)
 if line.startswith('seg\t'):G[z['id']]=z
 elif 'val'in z:S[z['name'].strip('"')]=z

def addr(n):return int(S[n]['val'],0)
def bank(n):
 g=G[S[n]['seg']];return(int(g['ooffs'],0)+addr(n)-int(g['start'],0)-16)//8192
class Mem(list):
 def __init__(self):super().__init__([0]*65536);self.writes=[];self.banks=[126,87,88,127];self.banks[1]=87
 def page(self,w,b):
  self.banks[w]=b;list.__setitem__(self,slice(0x8000+w*8192,0xa000+w*8192),raw[16+b*8192:16+(b+1)*8192])
 def __setitem__(self,k,v):
  if isinstance(k,int):
   if k>=0x8000:raise AssertionError(('unexpected CPU ROM write',hex(k),v))
   self.writes.append((k,v));list.__setitem__(self,k,v)
   if 0x5114<=k<=0x5117:self.page(k-0x5114,v&127)
  else:list.__setitem__(self,k,v)
def setup(n):
 m=Mem()
 for i,b in enumerate([126,87,88,127]):m.page(i,b)
 for g in G.values():
  if g.get('name')=='"SMCCODE"':
   start,size,pos=(int(g[v],0)for v in ['start','size','ooffs']);m[start:start+size]=raw[pos:pos+size]
 seg=G[S[n]['seg']];window=(int(seg['start'],0)-0x8000)//8192;m.page(window,bank(n))
 for x,w in [('CurrentBank',1),('CurrentBankC',2)]:
  if x in S:m[addr(x)]=m.banks[w]|128
 def put(n,v,i=0):m[addr(n)+i]=v&255
 def get(n,i=0):return m[addr(n)+i]
 return m,put,get

def run(m,n,a=0,x=0,y=0,p=0x30):
 m[0x1fe]=0xef;m[0x1ff]=0xff;m.writes=[];c=MPU(memory=m,pc=addr(n));c.sp=0xfd;c.a=a;c.x=x;c.y=y;c.p=p
 for i in range(30000):
  if c.pc==0xfff0:return c
  c.step()
 raise AssertionError(('timeout',n,hex(c.pc),m.banks))

NEW=(raw,S,G)
path=A.baseline;raw=path.read_bytes();S={};G={}
for line in gzip.decompress(path.with_suffix('.dbg.gz').read_bytes()).decode().splitlines():
 if not line.startswith(('sym\t','seg\t')):continue
 z=dict(x.split('=',1)for x in line[4:].split(',')if '='in x)
 if line.startswith('seg\t'):G[z['id']]=z
 elif 'val'in z:S[z['name'].strip('"')]=z
OLD=(raw,S,G)
rows=[]
for scenario in ['empty','equipped','shot','drop','pickup']:
 for v in range(4):
  for offset in [0,16,124,232,240,252]:
   for rotation in [0,4,128,252]:
    for flags in [0x30,0x71]:
     results=[];counts=[]
     for bundle in [OLD,NEW]:
      raw,S,G=bundle;m,w,r=setup('TnDrawEquipment')
      for n,value in [('SelectedCharacter',19),('GameEngineSubroutine',8),('TnVariant',v),('CurrentOAMOffset',offset),('RgOamRotation',rotation),('GuestOamRotationActive',1),('Player_Y_HighPos',1),('R0',0xa0),('R1',0x5c),('R4',80),('R6',7),('R7',1)]:w(n,value)
      if scenario=='equipped':w('TnGearSelected',1);w('TnEquipment',3,v);w('TnAmmo',102,v)
      if scenario=='shot':w('TnShotKind',2);w('TnShotAnim',74);w('TnShotFace',2);w('TnShotX',100);w('TnShotY',150)
      if scenario=='drop':w('TnDropKind',3);w('TnDropX',255);w('TnDropY',200)
      if scenario=='pickup':
       for n,value in [('Enemy_Flag',1),('Enemy_ID',0x2e),('Enemy_State',128),('InvPickupOwner',19),('InvPickup',0xb4),('TnPickupStamp',4),('Enemy_X_Position',2),('Enemy_Y_Position',120),('Enemy_Y_HighPos',1)]:w(n,value,5)
      c=run(m,'TnDrawEquipment',a=0x55,x=3,y=0,p=flags)
      excluded=set(range(0x100,0x200))|set(range(0x5114,0x5118))
      for g in G.values():
       if g.get('name')=='"SMCCODE"':excluded.update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
      for n in ['safecall_a','SafecallA']:
       if n in S:excluded.add(addr(n))
      memory={at:m[at]for at,value in m.writes if at<0x8000 and at not in excluded}
      results.append(((c.a,c.x,c.y,c.p&0xcf),memory));counts.append(c.processorCycles)
     assert results[0]==results[1],(scenario,v,offset,rotation,flags,results[0][0],results[1][0],[(hex(at),results[0][1].get(at),results[1][1].get(at))for at in set(results[0][1])|set(results[1][1])if results[0][1].get(at)!=results[1][1].get(at)][:16])
     rows.append(dict(scenario=scenario,variant=v,offset=offset,rotation=rotation,flags=flags,old_cycles=counts[0],new_cycles=counts[1]))
proof=dict(passed=True,old_ROM_sha256=hashlib.sha256(OLD[0]).hexdigest(),new_ROM_sha256=hashlib.sha256(NEW[0]).hexdigest(),cases=len(rows),registers='A/X/Y and NV-DIZC meaningful flags',memory='All written application RAM and mapper publication shadows; stack, SMC operands, bank registers and safecall bookkeeping excluded',scope='Isolated actual6502 renderer differential; no native timing/whole-campaign claim.')
(O/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');(O/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(proof))
