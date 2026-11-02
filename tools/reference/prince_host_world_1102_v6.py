"""Explicit native terrain oracle for the original Prince source component.

This Python boundary model measures the adaptation before its6502 binding.
Original movement/control/contacts execute from the recovered instructions.
No Mario motion, emulator, host ROM, public callback or new allocation is used.
"""
from collections import Counter
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import prince_original_cpu_1101_v1 as P
import check_hogan_current_bounded_v1 as N
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/prince-actor-1101-v1'
BASE=R/'build/metal-reservation-1102-v42/candidate.nes'
PIN='1cd8e192ee4bee33dfe0d9c737bec097e1cf2339e0b9f77353fd5194f2530f55'


class World:
 ORIGIN=77 # Native spawn176 -> foot208; original128 -> projected foot131.
 def __init__(self,b=None,x=48,y=176):
  self.b=b or scoped_load(BASE);assert P.hashlib.sha256(self.b['raw']).hexdigest()==PIN
  self.m=N.fresh(self.b);self.m.ram[2][:]=bytes(8192);self.s=self.m.ram[2]
  blob=(O/'contact-core.bin').read_bytes();self.m.ram[3][:len(blob)]=blob
  self.lab=P.T.labels(O/'contact-core.lbl');self.recovery=json.loads((O/'contact-recovery.json').read_text())
  self.callbacks={self.lab[n]:(n,k[0],int(k[1],16))for n,k in self.recovery['declared_original_environment_boundaries'].items()}
  self.art={q['source_frame']:q for q in json.loads((O/'source-art.json').read_text())['poses']if q['source_facing']==0}
  raw=P.donor();template=raw[16+2*16384+0x2bbf:16+2*16384+0x2bbf+14]
  assert template.hex()=='80a0008000db96ff000000000000'
  self.s[0x60e:0x61c]=template;self.s[0x60f:0x611]=(x+8).to_bytes(2,'little');self.s[0x611]=(y-48)&255
  self.s[0x6cf]=5;self.s[0x6d1]=5;self.phase=0;self.calls=Counter();self.events=[];self.native_queries=0;self.steps=0
  self.realcol=(x+8)//32;self.baseindex=0;self.roomrows=0;self.surface=None;self.surface_row=0;self.surface_col=self.realcol;self.aligns=[];self.contacts=[];self.oldfoot=y+32
  self.map();self.attr=self.b['raw'][location(self.b,'MTileAttribute'):location(self.b,'MTileAttribute')+256]
 def map(self):
  self.m.raw_page(1,3);self.m.raw_page(2,2);N.put(self.m,CurrentBank=3,CurrentBankC=2)
 def x(self):return self.s[0x60f]|self.s[0x610]<<8
 def foot(self):
  frame=self.s[0x617];delta=self.art.get(frame,self.art[15])['source_projection_geometry']['native_06F1_minus_anchor_y'];delta=delta if delta<128 else delta-256
  return self.s[0x611]+delta+self.ORIGIN
 def native(self,x,y):
  self.native_queries+=1
  if not(0<=x<=65535 and 32<=y<240):return 0
  at=address(self.b,'Block_Buffer_1'if x//256%2==0 else'Block_Buffer_2')+(x&255)//16+((y-32)//16)*16
  tile=self.m[at];return tile if self.attr[tile]&1 else 0
 def terrain(self,fn):
  for page in range(2):
   at=address(self.b,'Block_Buffer_1'if page==0 else'Block_Buffer_2')
   for row in range(13):
    for col in range(16):self.m[at+row*16+col]=fn(page*256+16*col,32+16*row)
 def nz(self,c,a):c.a=a&255;c.p=(c.p&~0x82)|(c.a&128)|(2 if not c.a else 0)
 def donor(self,c,pc,bank=5):
  d=P.machine();d.memory.switch(bank);list.__setitem__(d.memory,slice(0,2048),self.s[:2048])
  z=P.call(d,pc,a=c.a,x=c.x,y=c.y,p=c.p,limit=10000)
  self.s[:256]=d.memory[:256];self.s[512:2048]=d.memory[512:2048];c.a,c.x,c.y,c.p=z[:4]
 def setcol(self,raw):
  # Original A89A adds20 only for the declared alternate facing0 form.
  if self.s[0x4fe]and not self.s[0x615]:raw=(raw+20)&65535
  self.realcol=(raw if raw<32768 else raw-65536)//32;self.roomrows=0
 def currentrow(self):
  amount=36 if self.s[0x616]in [3,4,14]else 29
  return max(0,self.s[0x611]-amount)//64
 def indexgeometry(self,index):
  # Source index changes represent32px columns /64px rows; retain those
  # units and the visual+16 origin while translating the native cell access.
  diff=index-self.baseindex;dx=((diff+5)%10)-5;dy=(diff-dx)//10
  return self.realcol+dx,self.baseindex//10+dy+self.roomrows
 def tile(self,index):
  col,row=self.indexgeometry(index);qfoot=self.foot()+64*(row-self.currentrow());xs=[col*32+24,col*32+40]
  surface=[];wall=False;swept=[]
  for x in xs:
   if row==self.currentrow()and self.s[0x618]in [3,4]and self.oldfoot<=qfoot:
    for top in range(((self.oldfoot+15)//16)*16,qfoot+1,16):
     if self.native(x,top)and not self.native(x,top-1):swept.append(top);break
   wall|=bool(self.native(x,qfoot-24))
   ys=[qfoot]
   if row<self.currentrow():ys+=list(range(((qfoot//16)+1)*16,qfoot+64,16))
   for y in ys:
    if not self.native(x,y):continue
    top=(y//16)*16
    while top>32 and self.native(x,top-1):top-=16
    surface.append(top);break
  if swept:surface=swept
  material=1 if swept else(20 if wall else(1 if surface else 0))
  self.surface=(min(surface)if material==1 else self.s[0x611]+80+64*(row-self.currentrow()))
  self.surface_row=row;self.surface_col=col
  if 190<=self.x()<=210 and 80<=self.s[0x611]<=120 and len(self.contacts)<40:self.contacts.append(dict(X=self.x(),Y=self.s[0x611],frame=self.s[0x617],action=self.s[0x616],index=index,base=self.baseindex,col=col,row=row,currentrow=self.currentrow(),qfoot=qfoot,material=material,surface=self.surface))
  return material
 def align(self,c,dx,dy):
  before=(self.x(),self.s[0x611],self.s[0x616],self.s[0x617],self.s[0x4b1],self.baseindex,self.realcol,self.roomrows,self.surface,self.surface_row,self.surface_col,dx,dy)
  col,row=self.indexgeometry(self.s[0x4b1]);world=col*32+dx
  if self.s[0x4fe]and not self.s[0x615]:world=(world&~255)|((world-30)&255)
  if self.surface is None:logicalY=row*64
  else:logicalY=self.surface-self.ORIGIN-3+64*(row-self.surface_row-1)
  self.s[0x60f:0x611]=(world&65535).to_bytes(2,'little');self.s[0x611]=(logicalY+dy)&255
  if len(self.aligns)<16:self.aligns.append(dict(before=before,after=[self.x(),self.s[0x611]]))
  self.nz(c,self.s[0x611]);c.y=0;c.x=(3*(self.s[0x4b1]))&255;c.p&=~1
 def callback(self,c,n,bank,pc):
  self.calls[n]+=1;s=self.s
  if n in ['PpWorldTile','PpWorldTileY']:
   index=s[0x4b1]if n=='PpWorldTile'else c.y;c.y=index;self.nz(c,self.tile(index));return
  if n in ['PpWorldAlign','PpWorldPlaceAligned']:
   self.align(c,c.y if n=='PpWorldAlign'else c.a,64 if n=='PpWorldAlign'else c.x);return
  if n=='PpWorldLandingAlign':
   assert c.y==0,'Only the original player landing is bound in this model'
   if len(self.contacts)<40:self.contacts.append(dict(landing_from=s[0x611],surface=self.surface,frame=s[0x617],X=self.x()))
   if self.surface is not None:s[0x611]=(self.surface-self.ORIGIN-3)&255
   self.nz(c,s[0x611]);c.p&=~1;return
  if n=='PpWorldRoomAbove':self.roomrows-=3;self.nz(c,0);return
  if n in ['PpWorldGateState','PpWorldGateSupport','PpWorldGateHeight']:
   self.nz(c,0);return # No original gates are published by this native adapter.
  if n in ['PpNativeMusic','PpNativeSfx']:
   self.events.append((n,c.a,c.x));s[0x6d1]=6;return # Explicit audio boundary.
  if n in ['PpNativeEndScene','PpSourceTrapContact','PpSourceHazardContact','PpSourceSwordPickup','PpSourcePotionContact']:
   raise AssertionError(('Unbound original scene/material event',n,s[0x616],s[0x617]))
  raw=None
  if n=='PpWorldContext':self.roomrows=0
  if n=='PpWorldFeetContext':raw=(self.x()-(31 if not s[0x615]else 20))&65535
  if n=='PpWorldAheadContext':raw=(self.x()-(40 if not s[0x615]else 4))&65535
  if n in ['PpWorldOffsetContext','PpWorldOffsetX']:raw=(self.x()-c.x)&65535
  if n=='PpWorldSupportContext':
   if s[0x616]in [21,18,3,4]:off=40 if not s[0x615]else 8
   elif not s[0x615]:off=24 if s[0x4fe]or s[0x616]==32 else 34
   else:off=20
   raw=(self.x()-off)&65535
  if n=='PpWorldColumn':raw=s[0x17]|s[0x18]<<8
  if raw is not None:self.setcol(raw)
  # These boundaries execute the actual donor coordinate/room-pointer
  # instructions, never manufactured movement or returned terrain.
  self.donor(c,pc,bank if pc<0xc000 else s[0x6d1])
  if n in ['PpWorldFeetContext','PpWorldAheadContext','PpWorldOffsetContext','PpWorldSupportContext','PpWorldColumn','PpWorldOffsetX','PpWorldRow','PpWorldRowAdjusted']:self.baseindex=s[0x4b1]
 def source(self,name):
  self.map();c=N.NesMPU(memory=self.m,pc=self.lab[name]);c.a=0;c.x=0;c.y=0;c.p=0x21;c.sp=224;c.stPushWord(0x5aff)
  for _ in range(20000):
   if c.pc==0x5b00:break
   if c.pc in self.callbacks:
    n,bank,pc=self.callbacks[c.pc];self.callback(c,n,bank,pc);c.pc=(c.stPopWord()+1)&65535;continue
   assert self.m[c.pc]!=0,('Source BRK',name,hex(c.pc));c.step()
  else:raise AssertionError(('Source adapter bound',name,hex(c.pc)))
  assert c.sp==224;self.steps+=1;return c
 def geometry(self):
  frame=self.s[0x617]
  if frame not in self.art:return
  g=self.art[frame]['source_projection_geometry'];self.s[0x70f]=g['native_070F'];self.s[0x6f1]=(self.s[0x611]+g['native_06F1_minus_anchor_y'])&255;self.s[0x4bc]=(g['native_06F1_minus_anchor_y']-3)&255;self.s[0x4c3]=g['native_04C3']
 def step(self,pad):
  phase=self.phase;self.phase=(phase+1)%4
  if phase==0:
   self.s[0x2c]=0;self.s[0x69]=0;self.source('PpAdvanceActor');self.geometry()
  elif phase==2:
   self.s[0x2c]=3;self.s[0x40a]=pad;self.source('PpControls')
  elif phase==3:
   self.s[0x2c]=4;self.source('PpFall');self.source('PpTerrainContact');self.s[0x2c]=0;self.oldfoot=self.foot()
  # Source room-left sentinel is imported to the real native left edge.
  if self.x()>=32768:self.s[0x60f:0x611]=(8).to_bytes(2,'little')
  return dict(X=self.x(),Y=self.s[0x611],foot=self.foot(),frame=self.s[0x617],action=self.s[0x616],mode=self.s[0x618],phase=phase)
