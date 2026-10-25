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
for proc in ['RlDropDispatch','VvPrepareDispatch','M3PrivatePickup','M3RisePickup','M3PickupCollision','LmWeaponsGate']:
 for identity in range(19):
  for slot in [0,5]:
   for state in [1,128]:
    results=[]
    for bundle in [OLD,NEW]:
     raw,S,G=bundle;m,w,r=setup(proc)
     for n,value in [('SelectedCharacter',identity),('GameEngineSubroutine',8),('Player_Y_HighPos',1),('Enemy_ID',0x2e),('Enemy_Flag',1),('Enemy_State',state),('PowerUpType',1),('NumberofLives',2)]:w(n,value,slot if n.startswith('Enemy_')or n=='PowerUpType'else 0)
     c=run(m,proc,a=0x56,x=slot,y=3,p=0x71)
     # Ignore stack residue, SMC operands, mapper latches and bank bookkeeping.
     memory={i:m[i]for i in [*range(0x20,0x100),*range(0x200,0x800),*range(0x5c00,0x6000)]}
     for n in ['CurrentBank','CurrentBankC','safecall_a']:
      if n in S:memory.pop(addr(n),None)
     results.append(((c.a,c.x,c.y,c.p&1),memory))
    assert results[0]==results[1],(proc,identity,slot,state,results[0][0],results[1][0],[(hex(a),results[0][1].get(a),results[1][1].get(a))for a in set(results[0][1])|set(results[1][1])if results[0][1].get(a)!=results[1][1].get(a)][:15])
    rows.append({'procedure':proc,'identity':identity,'slot':slot,'state':state})
(O/'proof.json').write_text(json.dumps({'passed':True,'old_ROM_sha256':hashlib.sha256(OLD[0]).hexdigest(),'new_ROM_sha256':hashlib.sha256(NEW[0]).hexdigest(),'cases':len(rows),'registers':'A/X/Y/carry','memory':'actor/persistent/overlay application RAM; stack/SMC/mapper bookkeeping excluded','scope':'Isolated CPU native shared hook differential; seeded incoming actor records, no campaign claim.'},indent=2)+'\n');print('PASS',len(rows))
