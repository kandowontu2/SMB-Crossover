"""Private Bub/Bob adapter model using exactv30 bus/native CPU services.

This is executable host-adapter logic, not installed6502 routing. Source actor
opcodes execute from the independent A3 image. Import callbacks are explicit
model boundaries. Native enemy admission/draw/credit run only through this
private model, so no rejected public row is represented as functional.
"""
import collections,json
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_bubble_bobble_component_1101_v2 as P
import check_hogan_current_bounded_v1 as N
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load

PIN='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
BASE=R/'build/excitebike-pose-1101-v3/current4.nes';O=P.O


class Host:
 def __init__(self,identity=0,bundle=None,leaves=True,frame=True):
  self.b=bundle or scoped_load(BASE);assert P.B.sha(self.b['raw'])==PIN
  self.m=N.fresh(self.b);self.s=self.m.ram[2];self.lab=P.labels(O/'component.lbl')
  self.leaves=leaves;self.frame=frame
  self.m.ram[3][:]=(O/('native-private.bin'if leaves else'component.bin')).read_bytes();self.s[:1024]=bytes(1024)
  if leaves:self.s[0x1000:0x1400]=(O/'native-helper.chr').read_bytes()
  if leaves:self.lab.update(P.labels(O/'native-leaves.lbl'))
  self.bound_imports=set(json.loads((O/'native-leaves-layout.json').read_text())['actual_6502_import_bindings'])if leaves else set()
  self.end=max(self.lab['BbCodeEnd'],self.lab.get('BbNativeEnd',0));self.minimum_SP=224
  self.imports={r['vector']:r['name']for r in json.loads((O/'component-layout.json').read_text())['imports']}
  self.tilemap={r['oam_tile']:i*2+1 for i,r in enumerate(json.loads((O/'chr-closure.json').read_text())['tiles'])}
  self.attr=self.b['raw'][location(self.b,'MTileAttribute'):location(self.b,'MTileAttribute')+256]
  self.events=[];self.calls=collections.Counter();self.source_cycles=0;self.native_cycles=0;self.tokens=[None]*6;self.generation=[0]*6;self.observed=[None]*6
  self.identity=identity;self.actor=0x42 if identity else 0x2e;self.oy=8 if identity else 0
  self.map();self.put(OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,NumberofLives=2,Player_X_Position=64,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,DisableScreenFlag=0,Mirror_PPUMASK=30)
  self.construct()

 def get(self,name,i=0):return N.get(self.m,name,i)
 def put(self,**fields):N.put(self.m,**fields)
 def at(self,name):return address(self.b,name)
 def worldx(self):return self.get('Player_X_Position')+256*self.get('Player_PageLoc')
 def worldy(self):return self.get('Player_Y_Position')+256*self.get('Player_Y_HighPos')
 def camera(self):return self.get('ScreenLeft_X_Pos')+256*self.get('ScreenLeft_PageLoc')
 def setx(self,v):self.put(Player_X_Position=v&255,Player_PageLoc=(v>>8)&255)
 def sety(self,v):self.put(Player_Y_Position=v&255,Player_Y_HighPos=(v>>8)&255)
 def original(self,a):return self.s[P.ram(a)-P.STATE]
 def setoriginal(self,a,v):self.s[P.ram(a)-P.STATE]=v&255
 def map(self):
  self.m.raw_page(1,3);self.m.raw_page(2,2);self.m[self.at('CurrentBank')]=3;self.m[self.at('CurrentBankC')]=2

 def native(self,name,**regs):
  # Serialized model callback: protect the interrupted source call's live
  # stack/SMC and foreground scratch from the standalone native test harness.
  stack=bytes(self.m[0x100:0x200]);zp=bytes(self.m[3:11]);maps=list(self.m.rawtags)
  r=N.invoke(self.m,name,**regs);self.native_cycles+=r['CPU'];self.calls['native:'+name]+=1
  self.m[0x100:0x200]=stack;self.m[3:11]=zp
  assert self.m.rawtags==maps,(name,self.m.rawtags,maps)
  return r

 def source(self,name,*,x=0,y=0,a=0,p=0x30):
  self.map();pc=self.lab[name]if isinstance(name,str)else name;c=N.NesMPU(memory=self.m,pc=pc)
  c.a=a;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
  for _ in range(30000):
   if c.pc==0x5b00:break
   self.minimum_SP=min(self.minimum_SP,c.sp)
   if self.m.rawtags[1]==3 and c.pc in self.imports and self.imports[c.pc]in self.bound_imports:
    # Observation only: the compiled vector and its complete6502 body execute.
    # These events let the unchanged oracle assert source score/sound timing.
    imported=self.imports[c.pc];self.calls['compiled-import:'+imported]+=1
    if imported=='Score':self.events.append(('source-score',c.x,c.a))
    elif imported=='LivesUI':self.events.append(('source-lives',self.original(self.actor)))
    elif imported=='Sound':self.events.append(('source-sound',c.a))
   if self.m.rawtags[1]==3 and c.pc in self.imports and self.imports[c.pc]not in self.bound_imports:
    self.callback(self.imports[c.pc],c);c.pc=(c.stPopWord()+1)&65535;continue
   if c.pc==self.at('MetaspriteRenderLoop')and self.m.rawtags[1]&128:self.calls['native-direct:MetaspriteRenderLoop']+=1
   for service in['KillPlayer','ShellOrBlockDefeat']:
    if c.pc==self.at(service)and self.m.rawtags[(c.pc-0x8000)//8192]&128:
     assert self.m.rawtags[1]==128|((location(self.b,service)-16)//8192),(service,self.m.rawtags)
     self.calls['native:'+service]+=1
   assert (0xa000<=c.pc<self.end and self.m.rawtags[1]==3)or(0xd320<=c.pc<0xd400 and self.m.rawtags[2]==2)or(0x15a<=c.pc<0x17b)or(c.pc>=0x8000 and self.m.rawtags[(c.pc-0x8000)//8192]&128),('source outside',hex(c.pc),self.m.rawtags)
   assert self.m[c.pc]!=0
   c.step()
  else:raise AssertionError(('bounded source call',name,hex(c.pc)))
  assert c.sp==224;self.source_cycles+=c.processorCycles;self.calls['source:'+str(name)]+=1
  return c

 def callback(self,name,c):
  self.calls['import:'+name]+=1
  if name in ['Tile23','Tile84']:
   cursor=0x23 if name=='Tile23'else 0x84;ptr=self.original(cursor)+256*self.original(cursor+1)
   row,col=divmod(ptr-0x500,32);solid=self.query(self.camera()+col*8-16,row*8+32)
   c.a=0 if solid else 1;c.p=(c.p&~0x82)|(2 if c.a==0 else 0)
  elif name=='Sound':
   self.setoriginal(0x0f,c.a);self.events.append(('source-sound',c.a))
   # Actual FA81 returns restored Y in A and C0 after the five-bit bank write.
   c.a=c.y;c.p=(c.p&~0x83)|(c.a&128)|(2 if not c.a else 0)
  elif name=='Score':self.events.append(('source-score',c.x,c.a))
  elif name=='LivesUI':self.events.append(('source-lives',self.original(self.actor)))
  elif name=='EnemyDraw':
   # Keep the native victim's own art and surround it with the genuine grown
   # source bubble pair. No original enemy pixels are substituted for SMB art.
   if 0x68<=c.x<0x84 and self.original(c.x+2)&16:
    palette=3 if self.original(c.x+2)&1 else 0
    for off,val in[(1,0x26),(5,0x28),(2,palette),(6,palette)]:self.setoriginal(0x200+c.y+off,val)
  elif name in ['EnemyRelease','StageBubbles']:pass
  else:raise AssertionError(('unimplemented optional import',name))

 def construct(self,new_life=False):
  if self.leaves:
   self.source('BbNativeInit',a=self.identity,x=int(new_life))
   self.tokens=[None]*6;self.generation=[0]*6;self.observed=[None]*6;return
  self.s[:1024]=bytes(1024);self.s[0x300]=self.identity;self.s[0x304]=0xa7
  self.setoriginal(self.actor,self.get('NumberofLives')+1)
  self.setoriginal(0x461,1) # Private normalized input supplied by native adapter.
  self.setoriginal(0x454,255) # Original CPU free-running main counter saturatesFF.
  self.setoriginal(0x45d,2) # Original round1 metadata03 selects EC19[3]=2.
  rank=4+self.original(0x2e)+self.original(0x42);self.setoriginal(0x408,rank)
  self.setoriginal(0x492,40);self.setoriginal(0x40a,max(2,40-(rank-7)))
  self.source('BbSourceInit');self.source('BbSourceSprites');self.transport_in()
  pal=0 if self.identity else 3;facing=64 if self.get('PlayerFacingDir')==1 else 0
  self.setoriginal(0x202+self.oy,pal|facing);self.setoriginal(0x206+self.oy,pal|facing)
  self.s[0x308]=self.original(self.actor);self.s[0x305:0x307]=self.camera().to_bytes(2,'little')
  self.tokens=[None]*6;self.observed=[None]*6
  if new_life:self.setoriginal(self.actor+17,200)

 def sync_tokens(self):
  for i,t in enumerate(self.tokens):
   self.s[0x310+i*2:0x312+i*2]=(self.generation[i]&65535).to_bytes(2,'little')
   row=[0]*16
   if t:row=[1,t['id'],t['flag'],t['generation']&255,t['generation']>>8]+[t['saved'][n]for n in['Enemy_State','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer']]+[0]*6
   self.s[0x320+i*16:0x330+i*16]=bytes(row)

 def restore_proxy(self,i,t):
  if self.leaves:assert self.source('BbNativeProxyRestore',x=i).p&1
  else:
   for n,v in t['saved'].items():self.m[self.at(n)+i]=v

 def retire(self):
  self.observe()
  if self.leaves:
   self.source('BbNativeRetire');self.tokens=[None]*6;self.sync_tokens();self.events.append(('retired',));return
  for i,t in enumerate(self.tokens):
   if t:
    self.restore_proxy(i,t)
    self.tokens[i]=None
  self.sync_tokens();self.s[0x304]=0;self.s[0x303]=0;self.events.append(('retired',))

 def new_life(self):
  self.retire();self.construct(new_life=True)
  self.events.append(('source-newlife-grace',200))

 def terrain(self,fn,pages=(0,1)):
  for page,name in zip(pages,['Block_Buffer_1','Block_Buffer_2']):
   at=self.at(name)
   for row in range(13):
    for col in range(16):self.m[at+row*16+col]=fn(page*256+col*16,row*16+32)

 def query(self,x,y):
  if not 32<=y<240 or x<0:return False
  at=self.at('Block_Buffer_2'if (x>>8)&1 else'Block_Buffer_1')+((y-32)//16)*16+((x&255)//16)
  return self.attr[self.m[at]]&3==1

 def transport_in(self):
  if self.leaves:self.source('BbNativeIn');return
  sx=(self.worldx()-self.camera()+16)&255;sy=(self.worldy()-256+16)&255
  self.setoriginal(0x200+self.oy,sy);self.setoriginal(0x204+self.oy,sy)
  self.setoriginal(0x203+self.oy,sx);self.setoriginal(0x207+self.oy,sx+8)

 def source_bodies(self):
  return [dict(index=self.actor,y=self.original(0x200+self.oy),x=self.original(0x203+self.oy),kind='player')]+[dict(index=x,y=self.original(0x200+y),x=self.original(0x203+y),kind='bubble')for x,y in zip(range(0x88,0xc4,4),range(0x88,0x100,8))if self.original(x)]

 def shift_camera(self):
  self.observe()
  old=int.from_bytes(self.s[0x305:0x307],'little');delta=self.camera()-old
  if delta:
   for x,y in list(zip(range(0x88,0xc4,4),range(0x88,0x100,8)))+[(0x68+4*i,0x10+8*i)for i in range(6)if self.tokens[i]and self.original(0x6a+4*i)&16]:
    if not self.original(x):continue
    px=self.original(0x203+y)-delta
    if not 0<=px<=239 and x>=0x88:
     self.source('BbOriginal_DAB2',x=x,y=y);self.events.append(('offscreen-bubble-retire',x))
    elif not 0<=px<=239:
     i=(x-0x68)//4;t=self.tokens[i]
     if t:self.restore_proxy(i,t)
     self.tokens[i]=None;self.setoriginal(x,0);self.events.append(('offscreen-proxy-release',i))
    else:self.setoriginal(0x203+y,px);self.setoriginal(0x207+y,px+8)
  self.s[0x305:0x307]=self.camera().to_bytes(2,'little')

 def observe(self):
  invalid=[]
  for i in range(6):
   sig=(self.get('Enemy_Flag',i),self.get('Enemy_ID',i))
   if self.observed[i]!=sig:self.generation[i]=(self.generation[i]+1)&65535;self.observed[i]=sig
   old=self.tokens[i]
   invalid.append(bool(old and (not sig[0]or sig[0]&128 or sig[1]!=old['id']or old['generation']!=self.generation[i]or self.get('Enemy_State',i)&32)))
  self.sync_tokens()
  if self.leaves:self.source('BbNativeObserve')
  for i,old in enumerate(self.tokens):
   if self.leaves and old:assert (self.s[0x320+i*16]==0)==invalid[i]
   if invalid[i]:
    self.events.append(('proxy-invalidated',i));self.tokens[i]=None;self.setoriginal(0x68+4*i,0)
  self.sync_tokens()

 def actor_birth(self,i):
  """Explicit model ingress; native CheckpointEnemyID is not patched."""
  if self.leaves:
   assert self.source('BbNativeActorBirth',x=i).p&1
   self.generation[i]=int.from_bytes(self.s[0x310+i*2:0x312+i*2],'little')
  else:
   self.generation[i]=(self.generation[i]+1)&65535;self.setoriginal(0x68+4*i,0);self.setoriginal(0x6a+4*i,0)
  self.tokens[i]=None;self.observed[i]=(self.get('Enemy_Flag',i),self.get('Enemy_ID',i));self.sync_tokens()
  self.events.append(('actor-birth',i,self.generation[i]))

 def proxies_in(self):
  self.observe()
  if self.leaves:self.source('BbNativeProxiesIn');return
  for i in range(6):
   x=0x68+4*i;y=0x10+8*i;flag=self.get('Enemy_Flag',i);ident=self.get('Enemy_ID',i)
   eligible=0<flag<128 and ident<0x15 and ident not in[0x0c,0x14]and self.get('Enemy_Y_HighPos',i)==1 and not self.get('Enemy_State',i)&32
   if not eligible:self.setoriginal(x,0);continue
   if self.tokens[i]and self.original(x+2)&16:continue
   sx=self.get('Enemy_X_Position',i)+256*self.get('Enemy_PageLoc',i)-self.camera()+16;sy=self.get('Enemy_Y_Position',i)+8
   if not 0<=sx<240 or not 0<=sy<224:self.setoriginal(x,0);continue
   for off,val in enumerate([1,0,0,0]):self.setoriginal(x+off,val)
   for off,val in enumerate([sy,0,0,sx,sy,0,0,sx+8]):self.setoriginal(0x200+y+off,val)

 def proxies_out(self):
  if self.leaves:
   old=list(self.tokens);flags=[self.original(0x6a+4*i)for i in range(6)];self.source('BbNativeProxiesOut')
   for i,t in enumerate(old):
    r=self.s[0x320+i*16:0x330+i*16]
    if r[0]:
     self.tokens[i]=dict(id=r[1],flag=r[2],generation=int.from_bytes(r[3:5],'little'),saved=dict(zip(['Enemy_State','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer'],r[5:10])))
     if t is None:self.events.append(('trap',i,self.original(0x413+4*i)))
    else:
     self.tokens[i]=None
     if t:self.events.append(('native-defeat-credit'if flags[i]&8 else'release',i))
   self.sync_tokens();return
  for i in range(6):
   x=0x68+4*i;y=0x10+8*i;flags=self.original(x+2);token=self.tokens[i]
   if not self.original(x):continue
   if flags&16 and token is None:
    saved_names=['Enemy_State','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer']
    if self.leaves:
     assert self.source('BbNativeProxyCapture',x=i).p&1;r=self.s[0x320+i*16:0x330+i*16]
     token=dict(id=r[1],flag=r[2],generation=int.from_bytes(r[3:5],'little'),saved=dict(zip(saved_names,r[5:10])))
    else:token=dict(id=self.get('Enemy_ID',i),flag=self.get('Enemy_Flag',i),generation=self.generation[i],saved={n:self.get(n,i)for n in saved_names})
    self.tokens[i]=token;self.sync_tokens();self.events.append(('trap',i,self.original(0x3ab+x)))
   if token is None:continue
   if self.leaves:assert self.source('BbNativeProxyPosition',x=i).p&1
   else:
    wx=self.camera()+self.original(0x203+y)-16;ny=self.original(0x200+y)-8
    for name,val in [('Enemy_X_Position',wx&255),('Enemy_PageLoc',(wx>>8)&255),('Enemy_Y_Position',ny&255),('Enemy_Y_HighPos',1),('Enemy_X_Speed',0),('Enemy_Y_Speed',0)]:self.m[self.at(name)+i]=val
   if flags&8:
    self.put(ObjectOffset=i);self.m[self.at('R1')]=i;self.native('ShellOrBlockDefeat',x=i)
    self.events.append(('native-defeat-credit',i));self.tokens[i]=None;self.setoriginal(x,0)
   elif not flags&16:
    self.restore_proxy(i,token)
    self.events.append(('release',i));self.tokens[i]=None;self.setoriginal(x,0)
  self.sync_tokens()

 def enemy_step(self,i):
  """Required owner-specific admission seam; native routing is not patched."""
  self.observe()
  trapped=bool(self.tokens[i]and self.original(0x6a+4*i)&16)
  if self.leaves:assert bool(self.source('BbNativeEnemyAdmission',x=i).p&1)==trapped
  if trapped:self.calls['enemy-admission-suppressed']+=1;return False
  if self.get('Enemy_Flag',i):self.put(ObjectOffset=i);self.native('EnemiesAndLoopsCore',x=i)
  return True

 def hurt(self):
  if self.original(self.actor+17)or self.original(self.actor+3)&128:return False
  self.source('BbHurtBob'if self.identity else'BbHurtBub');self.events.append(('source-injury',));return True

 def contacts(self):
  if self.original(self.actor+3)&128 or self.original(self.actor+17):return
  if self.leaves:
   before=self.original(self.actor+3);self.source('BbNativeContacts')
   if not before&128 and self.original(self.actor+3)&128:self.events.append(('source-injury',))
   return
  for i in range(6):
   x=0x68+4*i;y=0x10+8*i
   if self.original(x)and not self.original(x+2)&24:
    self.setoriginal(0x21,self.original(0x200+self.oy));self.setoriginal(0x22,self.original(0x203+self.oy))
    c=self.source('BbOriginal_C43E',y=y,a=9)
    if not c.p&1:self.hurt();break

 def native_contact(self,first,second,distance=9):
  """Source anchor frame; inclusive native boxes reproduce distance<N."""
  base=self.at('BoundingBox_UL_Corner');saved=bytes(self.m[base+28:base+36])
  for offset,(x,y)in[(28,first),(32,second)]:self.m[base+offset:base+offset+4]=[x,y,x+distance-1,y+distance-1]
  try:r=self.native('SprObjectCollisionCore',x=28,y=32);return bool(r['P']&1)
  finally:self.m[base+28:base+36]=saved

 def kill(self,reason):
  if self.s[0x307]:return
  self.s[0x307]=1;self.native('KillPlayer',x=0);self.events.append(('native-death',reason))

 def ceiling(self,oldx,oldy,newx,newy):
  if self.leaves:
   c=self.source('BbNativeCeiling')
   if c.p&1:self.events.append(('solid-ceiling',self.s[0x3c8]))
   return self.worldy()-256
  if newy>=oldy:return newy
  for top in range(oldy+15,newy+15,-1):
   if any(self.query(q,top)for q in[newx+1,newx+14]):
    self.setoriginal(self.actor+3,2);self.setoriginal(self.actor+4,0)
    self.events.append(('solid-ceiling',top));return ((top//16)+1)*16-16
  return newy

 def step(self,keys,epoch=None,scroll=False):
  epoch=self.get('FrameCounter')if epoch is None else epoch&255;self.put(FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12)
  if self.s[0x304]!=0xa7 or self.get('OperMode')!=1 or self.get('GameEngineSubroutine')!=8 or self.get('GamePauseStatus')&1 or self.s[0x307]:return False
  if self.leaves and self.frame:
   self.observe();old=list(self.tokens);before=self.original(self.actor);pending=self.s[0x307]
   if not self.source('BbNativeUpdate').p&1:return False
   for i,t in enumerate(old):
    row=self.s[0x320+16*i:0x330+16*i];flags=self.original(0x6a+4*i)
    if row[0]:
     self.tokens[i]=dict(id=row[1],flag=row[2],generation=int.from_bytes(row[3:5],'little'),saved=dict(zip(['Enemy_State','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer'],row[5:10])))
     if t is None:self.events.append(('trap',i,self.original(0x413+4*i)))
    else:
     self.tokens[i]=None
     if t:self.events.append(('native-defeat-credit'if flags&8 else'offscreen-proxy-release'if flags&16 else'release',i))
   if self.s[0x3ef]:self.events.append(('solid-ceiling',self.s[0x3c8]))
   if not pending and self.s[0x307]:self.events.append(('native-death','source-injury-animation-finished'if before>self.original(self.actor)else'native-pit'))
   self.sync_tokens()
   if scroll and not self.s[0x307]:self.native('ScrollHandler')
   return True
  if self.leaves:
   if not self.source('BbNativeInput').p&1:return False
  else:
   if self.s[0x303]and epoch==self.s[0x302]:return False
   self.s[0x303]=1;self.s[0x302]=epoch;fresh=keys&~self.s[0x301];self.s[0x301]=keys
   controller=0xf6 if self.identity else 0xf5;self.setoriginal(controller,fresh);self.setoriginal(controller+2,keys)
   self.source('BbInput',x=self.actor,y=controller)
  self.shift_camera();oldx=self.worldx();oldy=self.worldy()-256;self.transport_in()
  self.proxies_in();before=self.original(self.actor)
  self.source('BbPlayerStep',x=self.actor,y=self.oy)
  if self.leaves:
   self.source('BbNativeOut');nx=self.worldx();ny=self.worldy()-256
  else:
   nx=self.camera()+self.original(0x203+self.oy)-16;sy=self.original(0x200+self.oy);ny=oldy+((sy-((oldy+16)&255)+128)%256-128)
  ny=self.ceiling(oldx,oldy,nx,ny)
  self.setx(max(self.camera(),nx));self.sety(256+ny);self.transport_in()
  self.source('BbBubbleStep')
  for i in range(6):
   x=0x68+4*i
   if self.original(x)and self.original(x+2)&16:
    self.setoriginal(0x26,x);self.source('BbTrappedEnemyStep',x=x,y=0x10+8*i)
  self.proxies_out();self.contacts();self.source('BbSourceClock')
  self.put(Player_X_Scroll=(self.worldx()-oldx)&255,Player_X_Speed=((self.worldx()-oldx)*16)&255,Player_Y_Speed=(ny-oldy)&255,Player_State=0 if self.original(self.actor+3)==0 else 1,Player_Pos_ForScroll=(self.worldx()-self.camera())&255,PlayerFacingDir=1 if self.original(0x202+self.oy)&64 else 2)
  if self.leaves:
   if self.source('BbNativeDeath').p&1:self.events.append(('native-death','source-injury-animation-finished'if before>self.original(self.actor)else'native-pit'))
  else:
   if before>self.original(self.actor):self.kill('source-injury-animation-finished')
   if self.worldy()>=256+240:self.kill('native-pit')
  if scroll and not self.s[0x307]:self.native('ScrollHandler')
  return True

 def bounds(self):
  x=self.worldx()-self.camera();y=self.worldy()-256
  if self.leaves:
   self.source('BbNativeContactBox');assert list(self.s[0x3b0:0x3b8])==[(x)&255,(y+16)&255,(x+15)&255,(y+31)&255,x&255,(y+16)&255,(x+8)&255,(y+24)&255]
   assert bytes(self.m[self.at('BoundingBox_UL_Corner'):self.at('BoundingBox_UL_Corner')+4])==bytes(self.s[0x3b4:0x3b8])
  return dict(terrain_visible=[x,y+16,x+15,y+31],source_hurt_anchor_box=[x,y+16,x+8,y+24],trap_distance=12,pop_chain_distance=15,bubble_contact_distance=16)

 def draw(self):
  if self.get('CurrentOAMOffset')&3:return dict(rejected='misaligned cursor',sprites=0)
  if self.get('GuestOamRotationActive')and self.get('RgOamRotation')&3:return dict(rejected='misaligned rotation',sprites=0)
  before=self.get('CurrentOAMOffset');bodies=[(self.oy,self.original(self.actor)>0)]+[(y,self.original(x)>0)for x,y in zip(range(0x88,0xc4,4),range(0x88,0x100,8))]
  for i,token in enumerate(self.tokens):
   if token:
    self.put(ObjectOffset=i);self.native('EnemyGraphicsEngine',x=i);self.native('DrawMetasprite',x=self.get('EnemyMetasprite',i),y=i+1)
    bodies.append((0x10+8*i,True))
  if self.leaves:
   self.source('BbNativeDraw')
   for i,t in enumerate(self.tokens):
    if t and not self.s[0x320+16*i]:self.tokens[i]=None;self.events.append(('offscreen-proxy-release',i))
   bodies=[]                 # Compiled draw includes all six trap circles.
  for y,active in bodies:
   if not active:continue
   rows=[[self.original(0x200+y+j+k)for k in range(4)]for j in[0,4]]
   if rows[0][0]>=240 or any(r[1]not in self.tilemap for r in rows):continue
   packet=[8]
   for yy,t,attr,x in reversed(rows):packet.extend([self.tilemap[t],attr,(yy-rows[0][0])&255,(x-rows[0][3])&255])
   self.s[0x3e0:0x3e9]=bytes(packet);sx=rows[0][3]-16
   for n,v in [('R0',0xe0),('R1',0xc3),('R3',0),('R4',sx&255),('R5',255 if sx<0 else 0),('R6',rows[0][0]),('R7',1)]:self.m[self.at(n)]=v
   self.native('MetaspriteRenderLoop')
  self.m[self.at('ObjectMetasprite')]=0;self.m[self.at('SmPosePtr')]=self.at('ObjectMetasprite')&255;self.m[self.at('SmPosePtr')+1]=self.at('ObjectMetasprite')>>8
  after=self.get('CurrentOAMOffset');assert after&3==0
  return dict(before=before,after=after,sprites=(after-before)//4)
