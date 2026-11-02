"""CPU-only model successor; every world query executes compiled6502 leaves."""
import prince_host_world_1102_v6 as W
import json
from collections import Counter,deque
P,O=W.P,W.O


class World(W.World):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw)
  self.worldlab=P.T.labels(O/'host-world-v8.lbl');coords=P.T.labels(O/'world-coordinates-v7.lbl')
  self.worldlayout=json.loads((O/'host-world-layout-v8.json').read_text())
  code=(O/'world-coordinates-v7.bin').read_bytes();self.s[0x100:0x200]=code[:256];self.s[0x235:0x235+len(code)-256]=code[256:]
  self.loadcode(0xb310,(O/'contact-point.bin').read_bytes())
  code=(O/'host-world-v8.bin').read_bytes()
  for q in self.worldlayout['regions']:
   a,z=q['half_open'];self.loadcode(a,code[q['source_file_offset']:q['source_file_offset']+z-a])
  targets={**{n:a for n,a in coords.items()if n in self.recovery['declared_original_environment_boundaries']},**{n:a for n,a in self.worldlab.items()if n in self.recovery['declared_original_environment_boundaries']}}
  targets['PpWorldContext']=self.worldlab['PpWorldSourceContext'];targets['PpWorldColumn']=self.worldlab['PpWorldSourceColumn']
  for n in ['PpWorldGateState','PpWorldGateSupport','PpWorldGateHeight']:targets[n]=self.worldlab['PpWorldGateEmpty']
  for tag,v in self.recovery['instructions'].items():
   if v['mn']not in ['JSR','JMP']:continue
   bank,pc=tag.split(':');at=self.lab[f'PpN_{bank}_{pc}'];old=self.m[at+1]|self.m[at+2]<<8
   n=self.callbacks.get(old,(None,))[0]
   if n in targets:
    a=targets[n];self.m[at+1]=a&255;self.m[at+2]=a>>8
  self.callbacks={a:v for a,v in self.callbacks.items()if v[0]not in targets}
  self.field('PpWorldOrigin',self.ORIGIN);self.field('PpWorldOrigin',0,1)
  self.field('PpWorldLastY',self.s[0x611]);self.field('PpWorldDelta',3)
  self.field('PpWorldOldFoot',self.oldfoot&255);self.field('PpWorldOldFoot',self.oldfoot>>8,1)
 def loadcode(self,a,code):
  if 0xa000<=a<0xc000:self.m.ram[3][a-0xa000:a-0xa000+len(code)]=code
  else:assert 0xc000<=a<0xc800;self.s[a-0xc000:a-0xc000+len(code)]=code
 def field(self,n,value=None,delta=0):
  at=self.worldlab[n]-0xc000+delta
  if value is not None:self.s[at]=value&255
  return self.s[at]
 def leaf(self,n):
  self.map();c=W.N.NesMPU(memory=self.m,pc=self.worldlab[n]);c.a=0;c.x=0;c.y=0;c.p=0x21;c.sp=224;c.stPushWord(0x5aff)
  for _ in range(10000):
   if c.pc==0x5b00:break
   assert self.m[c.pc]!=0,(n,hex(c.pc));c.step()
  else:raise AssertionError(('World leaf bound',n,hex(c.pc)))
  assert c.sp==224;return c
 def geometry(self):
  super().geometry()
  self.field('PpWorldDelta',(self.s[0x6f1]-self.s[0x611])&255)
 def source(self,name):
  self.map();c=W.N.NesMPU(memory=self.m,pc=self.lab[name]);c.a=0;c.x=0;c.y=0;c.p=0x21;c.sp=224;c.stPushWord(0x5aff);pcs=Counter();last=deque(maxlen=20)
  pending=[]
  for _ in range(100000):
   if c.pc==0x5b00:break
   pcs[c.pc]+=1;last.append((hex(c.pc),c.a,c.x,c.y,c.p,c.sp))
   if getattr(self,'inspect_tiles',False):
    if pending and c.pc==pending[-1][0]and c.sp==pending[-1][1]:
     ret,sp,want,detail=pending.pop()
     assert c.a==want,('Tile differential',c.a,want,detail,list(self.s[0x78:0xa6]))
    if c.pc in [self.worldlab['PpWorldTile'],self.worldlab['PpWorldTileY']]:
     index=self.s[0x4b1]if c.pc==self.worldlab['PpWorldTile']else c.y
     raw=self.s[0x78]|self.s[0x79]<<8;self.realcol=(raw if raw<32768 else raw-65536)//32
     self.baseindex=self.s[0x7a]+10*self.currentrow();self.roomrows=self.field('PpWorldRoomRows');self.roomrows=self.roomrows if self.roomrows<128 else self.roomrows-256
     self.oldfoot=self.field('PpWorldOldFoot')|self.field('PpWorldOldFoot',delta=1)<<8
     want=W.World.tile(self,index);ret=(self.m[0x101+c.sp]|self.m[0x102+c.sp]<<8)+1
     pending.append((ret,c.sp+2,want,dict(index=index,raw=raw,base=self.baseindex,roomrows=self.roomrows,X=self.x(),Y=self.s[0x611],frame=self.s[0x617],foot=self.foot(),action=self.s[0x616],mode=self.s[0x618],surface=self.surface)))
   if c.pc in self.callbacks:
    n,bank,pc=self.callbacks[c.pc];self.callback(c,n,bank,pc);c.pc=(c.stPopWord()+1)&65535;continue
   assert self.m[c.pc]!=0,('Source BRK',name,hex(c.pc));c.step()
  else:raise AssertionError(('Compiled source adapter bound',name,hex(c.pc),pcs.most_common(10),list(last),list(self.s[0x78:0xa6])))
  assert c.sp==224;self.steps+=1;return c
 def step(self,pad):
  phase=self.phase;self.phase=(phase+1)%4
  if phase==0:
   self.s[0x2c]=0;self.s[0x69]=0;self.source('PpAdvanceActor');self.geometry()
  elif phase==2:
   self.s[0x2c]=3;self.s[0x40a]=pad;self.source('PpControls')
  elif phase==3:
   self.s[0x2c]=4;self.source('PpFall');self.source('PpTerrainContact');self.s[0x2c]=0
  self.leaf('PpWorldPhysicalFoot')
  physical=self.field('PpWorldFoot')|(self.field('PpWorldFoot',delta=1)<<8)
  if phase==3:
   self.field('PpWorldOldFoot',physical);self.field('PpWorldOldFoot',physical>>8,1)
  if self.x()>=32768:self.s[0x60f:0x611]=(8).to_bytes(2,'little')
  return dict(X=self.x(),Y=self.s[0x611],foot=physical,frame=self.s[0x617],action=self.s[0x616],mode=self.s[0x618],phase=phase)
