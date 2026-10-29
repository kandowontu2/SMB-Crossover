"""Finite real-ROM callback/mapper/IRQ controls, not native PPU/Main admission."""
from pathlib import Path
import itertools,json,sys
import gimmick_host_controls_v2 as H
K=H.K;G=H.G;B=H.B;O=H.O;R=H.R;A=H.A
from check_tmnt_render_oa import address,Memory
from verify_native_relocation import NesMPU
SMC=['NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC']
SMCADDR=[A('NextBank_SMC')+1,A('SafecallA_SMC')+1,A('FarcallJmpTarget_SMC')+1,A('FarcallJmpTarget_SMC')+2,A('SafereturnA_SMC')+1]
def setv(m,**kw):H.setv(m,**kw)
def setup(name):
 bank=int(B['segs'][B['syms'][name]['seg']]['ooffs'])//8192
 m=H.mem(bank)
 if name!='GmNewGame':
  m.page(1,75);setv(m,CurrentBank=203);H.call(m,'GmNewGame');m.page(1,bank);setv(m,CurrentBank=bank|128)
 setv(m,GameEngineSubroutine=8,Player_X_Position=88,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,PlayerFacingDir=1,Player_State=0)
 return m
def execute(m,name,inject=None,far=False,**kw):
 pc=A(name);bank=int(B['segs'][B['syms'][name]['seg']]['ooffs'])//8192
 if far:
  m.page(1,8);setv(m,CurrentBank=136)
  m[SMCADDR[1]]=kw.get('a',0x55);m[SMCADDR[2]]=pc&255;m[SMCADDR[3]]=pc>>8
  pc=A('FarCallCommon')
 c=NesMPU(memory=m,pc=pc);c.a=bank|128 if far else kw.get('a',0x55);c.x=kw.get('x',3);c.y=kw.get('y',6);c.p=kw.get('p',0x31);c.sp=0xfd;c.stPushWord(0x5aff)
 trace=[];low=255;hit=False;irqlow=255;m.writes=[];m.deepest=None
 for _ in range(30000):
  if c.pc==0x5b00:return c,trace,low,hit,irqlow
  phys=m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
  if inject==(phys,c.pc)and not hit:
   before=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,m.banks[:]);zp=bytes(m[:256]);state=bytes(m[0x5c00:0x5c80]);smc=bytes(m[0x15a:0x17b]);m[0x5204]=128
   assert not c.p&4
   c.irq()
   for __ in range(1000):
    irqlow=min(irqlow,c.sp);c.step()
    if (c.pc,c.sp)==(before[0],before[5]):break
   else:raise AssertionError('actual IRQ did not return')
   assert (c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,m.banks)==before
   assert bytes(m[:256])==zp and bytes(m[0x5c00:0x5c80])==state and bytes(m[0x15a:0x17b])==smc
   assert irqlow>=0x7b,('IRQ/page1 overlaps real farcall code',irqlow)
   hit=True
  trace.append((phys,c.pc))
  if c.sp<low:low=c.sp;m.deepest=(phys,c.pc)
  assert m[c.pc]!=0,('BRK',name,hex(c.pc));c.step()
 raise AssertionError(('callback bound',name,hex(c.pc)))
def geometry():
 count=0
 for xp,x,y,probe in itertools.product([0,1,2,7],[0,7,15,248,255],[16,32,112,176,207],range(7)):
  m=setup('GmBodyProbe');setv(m,Player_PageLoc=xp,Player_X_Position=x,Player_Y_Position=y,R0=0xa6,R1=0x39)
  base1=A('Block_Buffer_1');base2=address(B,'Block_Buffer_2')
  for n in range(208):m[base1+n]=(n*3+7)&255;m[base2+n]=(n*5+11)&255
  dx=[8,5,11,5,5,11,11][probe];dy=[18,32,32,22,30,22,30][probe]
  xx=x+xp*256+dx;row=(((y+dy)&255)&0xf0)-32;row&=255
  base=base2 if xx//256&1 else base1;ptr=base+(xx%256)//16;expected=m[(ptr+row)&65535]
  c,_,_,_,_=execute(m,'GmBodyProbe',a=1 if probe>=3 else 0,y=probe)
  assert c.a==expected and c.y==probe and c.x==0 and m[A('R0')]==0xa6 and m[A('R1')]==0x39,('probe caller',xp,x,y,probe)
  assert m[A('R2')]==row and m[A('R3')]==expected and m[A('R6')]+256*m[A('R7')]==ptr
  assert m[A('R4')]==(x if probe>=3 else y)&15
  count+=1
 return dict(cases=count,scope='All7 source terrain geometry points, real current block-buffer layout/pages/column carry and native returned pointer/tile/row/fraction/Y/R0/R1. Typed block scene only, not native block gameplay or full BG caller.')
def movement():
 rows=[]
 for mask in [0,1,2,0x80,0x81,0x82,0x40]:
  m=setup('GmMovement');setv(m,GmRam036E=128,GmRam035A=2,SavedJoypadBits=mask,GmFresh=mask)
  scratch=[(i*29+13)&255 for i in range(8)]
  for i,v in enumerate(scratch):m[A('R'+str(i))]=v
  smc=[m[n]for n in SMCADDR];banks=m.banks[:]
  c,tr,low,_,_=execute(m,'GmMovement',a=0xa5,x=0x37,y=0x68,p=0xb1)
  assert(c.a,c.x,c.y,c.p,c.sp)==(0xa5,0x37,0x68,0xb1,0xfd)
  assert [m[n]for n in SMCADDR]==smc and m.banks==banks and [m[A('R'+str(i))]for i in range(8)]==scratch
  assert m[A('GmClock')]==0,'No fake Main-owned NMI clock'
  rows.append([mask,c.processorCycles,low,m[A('Player_X_Position')],m[A('Player_Y_Position')],m[A('GmRam00CC')],m[A('GmRam00C2')]])
 return dict(cases=len(rows),rows=rows,scope='Actual owned movement callback once, genuine native source integrator and all farcalls; no root shared BG/platform/camera bridge yet.')
def weapons_case(kind,enemy=True):
 m=setup('GmWeapons')
 setv(m,GmRam0091=1,GmRam0351=kind,GmRam00AF=0,GmRam00B9=6,GmRam009B=0,GmRam00A5=10,GmRam0329=0x80,GmRam0333=0,GmRam0315=0x80,GmRam031F=0)
 if enemy:
  for n,v in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_X_Position',88),('Enemy_PageLoc',0),('Enemy_Y_Position',144),('Enemy_Y_HighPos',1)]:m[A(n)]=v
 return m
def weapons():
 rows=[]
 for kind,enemy in itertools.product(range(3),[False,True]):
  m=weapons_case(kind,enemy);oldbank=m.banks[:];smc=[m[n]for n in SMCADDR];bb=bytes(m[A('BoundingBox_UL_Corner')+28:A('BoundingBox_UL_Corner')+36]);borrowed=[A(n)for n in ['MmSlot','MmEnemySlot','SmSlot','SmBombHits','MmBulletType','ObjectOffset']];old=[m[n]for n in borrowed]
  c,tr,low,_,_=execute(m,'GmWeapons',a=0xa5,x=0x37,y=0x68,p=0x31)
  assert(c.a,c.x,c.y,c.p,c.sp)==(0xa5,0x37,0x68,0x31,0xfd)
  assert m.banks==oldbank and [m[n]for n in SMCADDR]==smc and [m[n]for n in borrowed]==old
  assert bytes(m[A('BoundingBox_UL_Corner')+28:A('BoundingBox_UL_Corner')+36])==bb
  if enemy:assert m[A('Enemy_State')]&0x20 and m[A('GmRam0091')]==(0xd0 if kind==2 else 1),('actual native NPC contact',kind,m[A('Enemy_State')],m[A('GmRam0091')])
  else:assert m[A('GmRam0091')]==1
  rows.append([kind,enemy,c.processorCycles,low,m[A('Enemy_State')]])
 return dict(cases=len(rows),rows=rows,scope='Actual parent NPC collision/immunity/100-host-damage mapping for ordinary Goomba, sourceType2 first accepted contact->D0, live borrowed fields restored. This is an explicit native-enemy normalization, not original Gimmick enemy AI or all bosses.')
def isrs():
 rows=[]
 for name in ['GmNewGame','GmMovement','GmAfterTerrain','GmGraphics','GmDraw','GmWeapons','GmPickup','GmScene','GmBodyProbe']:
  m=weapons_case(2)if name=='GmWeapons'else setup(name)
  if name=='GmDraw':setv(m,GmVisible=1,GmRam0300=8,GmRam0091=1,GmRam0301=15,GmRam00A5=6,GmRam00B9=6)
  snapshot=(bytes(m),m.banks[:]);c,tr,low,_,_=execute(m,name,a=1,y=0)
  sites=sorted(set((bk,pc)for bk,pc in tr if bk in [24,75,122]or 0x15a<=pc<0x17b))
  sites=sorted(set(sites+[m.deepest])) # include actual deepest native caller too.
  minimum=255
  for site in sites:
   q=Memory(B);list.__setitem__(q,slice(None),snapshot[0]);q.banks=snapshot[1][:]
   d,_,_,hit,lo=execute(q,name,a=1,y=0,inject=site);assert hit
   minimum=min(minimum,lo)
  rows.append([name,len(sites),minimum,c.processorCycles,low])
 return dict(rows=rows,seams=sum(x[1]for x in rows),minimum_SP=min(x[2]for x in rows),scope='Actual parent physical IRQ at every unique reached owned/helper/SMC PC in nine real compiled paths, plus deepest real native callee; complete interrupted AXYP/SP/banks/ZP/private128B/33SMC exact. Not a normal/lag NMI clock/mixer or PPU timing qualification.')
def incoming():
 rows=[]
 for name,p,a in itertools.product(['GmMovement','GmAfterTerrain','GmGraphics','GmDraw','GmWeapons'],[0x30,0x79],[0,0x55,0xa5]):
  m=setup(name);bank=int(B['segs'][B['syms'][name]['seg']]['ooffs'])//8192
  c,tr,low,_,_=execute(m,name,far=True,a=a,x=0x37,y=0x68,p=p)
  expectedP=(p&0x7d)|(0x80 if a&128 else 0)|(2 if not a else 0)
  assert (c.a,c.x,c.y,c.p,c.sp)==(a,0x37,0x68,expectedP,0xfd),('incoming real farcall',name,p,a,(c.a,c.x,c.y,c.p,c.sp))
  assert m.banks[1]==8 and m[A('CurrentBank')]==136 and m.banks[2]==73 and m[A('CurrentBankC')]==201
  assert [m[n]for n in SMCADDR]==[bank|128,a,A(name)&255,A(name)>>8,a]
  rows.append([name,p,a,c.processorCycles,low])
 return dict(cases=len(rows),rows=rows,scope='Genuine incoming FarCallCommon from physicalA8 and real saved return, complete AXYP/SP and exact documented native NZ-of-returnA contract; all5 final SMC operands/true hardware+shadow banks checked, no fake target aliases.')
def clock():
 count=0
 for prev,held,clock,p in itertools.product([0,1,2,3,0x40,0x80,0x81,0xff],[0,1,2,3,0x40,0x80,0x81,0xff],[0,255],[0x30,0x79]):
  m=setup('GmNmiClock');setv(m,GmPrevious=prev,SavedJoypadBits=held,GmClock=clock)
  c,_,_,_,_=execute(m,'GmNmiClock',a=0x95,x=0x37,y=0x68,p=p)
  assert(c.a,c.x,c.y,c.p,c.sp)==(0x95,0x37,0x68,p,0xfd)
  assert m[A('GmFresh')]==held&(~prev&255) and m[A('GmPrevious')]==held and m[A('GmClock')]==(clock+1)&255
  count+=1
 m=setup('GmNmiClock');setv(m,GmReady=0,GmClock=51,GmPrevious=6,GmFresh=9);execute(m,'GmNmiClock');assert [m[A(n)]for n in ['GmClock','GmPrevious','GmFresh']]==[51,6,9]
 return dict(cases=count+1,scope='Real compiled endpoint byte/clock-wrap/edge and constructor-not-ready decline; source original ED increment is NMI-owned. Endpoint calls are a CPU model only. No installed common NMI origin/scheduling or host lag-controller sampling equivalence claim.')
def support():
 count=0;accepted=0
 for width,dx,dy,vy,flags in itertools.product([0x30,0x80,0x1e0],[-1,0,1,2,3,4,5],[-1,0,1,63,127,128,129],[0,1,255],[0,64]):
  # dx selects actual asymmetric edge or interior fractional distance.
  half=width+0x30;distance=[-half-1,-half,-half+1,0,half-1,half,half+1][dx+1]
  src=G.Original(30);starx=1600;stary=2400;height=128;hero_y=stary-height+dy;vx=[0,1,255,24,232][count%5]
  for at,v in {0x33c:0x30,0xd7:flags,0x329:width&255,0x333:width>>8,0x315:height,0x31f:0,0xaf:starx&255,0xb9:starx>>8,0x9b:stary&255,0xa5:stary>>8,0xae:(starx+distance)&255,0xb8:((starx+distance)>>8)&255,0x9a:hero_y&255,0xa4:hero_y>>8,0xc2:vy,0xcc:vx}.items():src[at]=v
  m=K.port(src,bank=122)
  if vy<128:
   c=K.run(src,0xff13,y=1)
   if c.a:
    K.run(src,0x8364,0x8395,y=1);accepted+=1
  H.call(m,'GmRideStar')
  for at in [0x9a,0xa4,0xae,0xb8,0xcc,0xc2,0x36e]:assert src[at]==m[A(K.ALIASES[at])],('genuine support/noYsnap',width,distance,dy,vy,flags,hex(at))
  count+=1
 return dict(cases=count,accepted=accepted,scope='Actual originalFF13 geometry and8364 accepted reaction against compiled star support; ordinary host property projection only. Every original fractional edge is retained and Y is NOT snapped; original stand-mark0365 has no compiled star-reader and is not a host moving actor flag. No invented horizontal carry.')
def particles():
 rows=[]
 for phase in [0,1]:
  src=G.Original(16);list.__setitem__(src,slice(0xa000,0xc000),G.PRG[22*8192:23*8192]);entry=src[0xa028]+256*src[0xa029];assert entry==0xb3db
  for at,v in {0x92:1,0x352:0xb4,0x19:2,0x9c:0,0xa6:6,0xb0:0,0xba:6,0x3ac:255}.items():src[at]=v
  m=setup('GmEffectsTick');m[A('GmEffects'):A('GmEffects')+4]=[0,6,0,6];setv(m,GmSpawnIndex=0,GmClock=phase)
  for age in range(1,17):
   src[0xed]=phase;K.run(src,entry,0x8052,x=2);H.call(m,'GmEffectsTick')
   assert bool(src[0x92])==bool(m[A('GmEffects')+3]&0xf0),('actual B4 lifetime',age)
   if src[0x92]:assert src[0x302]==age//4 and (m[A('GmEffects')+3]>>4)==age
  rows.append(dict(NMI_parity=phase,updates=16,original_entry='22:B3DB from actual A028 table',source_velocity_zero=True))
 return dict(cases=32,rows=rows,scope='Genuine source general-object B4 lifetime/4pose clock plus zero-VX/Y integration/cull for interior source-spawned geometry; host viewport cull adaptation remains separately declared.')
def lifecycle():
 rows=[]
 for side,hp in itertools.product([0,1],[1,2,4]):
  src=G.Original(16);assert bytes(src[0x8c95:0x8c9b])==bytes.fromhex('8d0a03ce4603');src[0x346]=hp
  K.run(src,0x8c95,a=side)
  m=setup('GmInjury');setv(m,GmRam0346=hp);H.call(m,'GmInjury',a=side)
  for at in [0x346,0x30a,0x38c,0xcc,0xc2]:assert src[at]==m[A(K.ALIASES[at])],('actual injury side',side,hp,at)
  assert list(src[0x56:0x5a])==list(m[A('GmCues'):A('GmCues')+4])and src[0x5a]==m[A('GmCueCount')]
  rows.append([side,hp,m[A('GmRam0346')],m[A('GmRam00CC')]])
 for before,after,area,world in [(2,3,0,0),(2,4,0,0),(255,0,0,0),(2,1,0,0),(0,255,0,0),(2,3,1,0),(2,3,0,1)]:
  m=setup('GmEnsure');setv(m,NumberofLives=before);H.call(m,'GmEnsure');setv(m,GmRam0346=1,GmRam0036=2,GmRam0039=1,NumberofLives=after,AreaPointer=area,WorldNumber=world)
  H.call(m,'GmEnsure');assert m[A('GmRam0036')]==2 and m[A('GmRam0039')]==1
  assert m[A('GmRam0346')]==(2 if (after-before)&255>=128 else 1)
  assert m[A('GmArea')]==area and m[A('GmWorld')]==world and m[A('GmLife')]==after
 return dict(injury=rows,lifecycle_cases=7,scope='Actual accepted original damage body and queuedSound17, true side parameter. Typed real-writer life gain/loss/wrap scenarios; newgameHP2, scene/gain retains earned inventory, death refill. Native physical pickup/death/menu lifecycle still requires shared admission.')
def palette():
 rows=[]
 for ctrl,offset in itertools.product([0,1,6,8],[0,20,57,58,63]):
  m=setup('GmColors');setv(m,VRAM_Buffer_AddrCtrl=ctrl,VRAM_Buffer1_Offset=offset)
  before=bytes(m[A('VRAM_Buffer1'):A('VRAM_Buffer1')+64]);c=H.call(m,'GmColors');success=ctrl==0 and offset<=57
  assert bool(c.p&1)==success
  if success:assert bytes(m[A('VRAM_Buffer1')+offset:A('VRAM_Buffer1')+offset+7])==bytes.fromhex('3f11030b2a3000')
  else:assert bytes(m[A('VRAM_Buffer1'):A('VRAM_Buffer1')+64])==before
  rows.append([ctrl,offset,success])
 m=setup('GmColors');H.call(m,'GmColors');ptr=A('VRAM_Buffer1');setv(m,NmiR0=ptr&255,NmiR1=ptr>>8);K.run(m,A('SamusFreezeUpdateScreen'))
 assert [v for at,v in m.writes if at==0x2007]==[0x0b,0x2a,0x30],('genuine native UpdateScreen palette consumer',m.writes[-20:])
 return dict(cases=len(rows),actual_consumer_PPUDATA=[11,42,48],scope='Only3F11 visible-body triple; successful complete packet or strict busy/capacity decline, actual native UpdateScreen ordered writes. Never writes universal backdrop or world/enemy palettes. Source palette1->nativeP2 assumes genuine host worldP2[16,30,27] remains owned by its native publisher; one darkbrown07->16 adaptation, not full source color equality.')
def foreign():
 count=0
 for raw,name in itertools.product([*range(26),27,31],['GmMovement','GmAfterTerrain','GmGraphics','GmDraw','GmWeapons','GmPickup','GmEnsure','GmNewGame','GmScene','GmNmiClock','GmInjury','GmFullPower','GmBox','GmHealth','GmDeathStart','GmBodyProbe','GmPortrait']):
  m=setup(name);setv(m,SelectedCharacter=raw);before=bytes(m[:0x8000]);banks=m.banks[:]
  execute(m,name,a=1,y=0)
  # Only the actual private API's dead push area may differ. All ZP, live
  #100..159,33SMC, OAM, application/ExRAM/bank registers remain exact.
  assert bytes(m[:0x100])==before[:0x100]and bytes(m[0x100:0x15a])==before[0x100:0x15a]and bytes(m[0x15a:0x17b])==before[0x15a:0x17b]and bytes(m[0x200:0x8000])==before[0x200:]and m.banks==banks,('foreign API writes',raw,name)
  count+=1
 return dict(cases=count,scope='Foreign direct APIs leave complete application/ZP/OAM/livepage1/33SMC/banks unchanged; published output A/P/Y contracts differ by API, so this is not a blanket AXYP claim for helpers returning values.')
def main():
 assert not(O/'handoff.json').exists()
 proof=dict(status='CPU_CALLERS_PASS',candidate=G.bind(O/'candidate.nes'))
 try:
  proof.update(geometry=geometry(),movement=movement(),weapons=weapons(),support=support(),particles=particles(),lifecycle=lifecycle(),palette=palette(),foreign=foreign(),incoming_farcall=incoming(),clock=clock(),IRQ=isrs())
  (O/'caller-controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,default=str))
 except Exception as e:
  path=O/'caller-first-failure.json'
  if not path.exists():path.write_text(json.dumps(dict(status='FALSE',error=repr(e),candidate=G.bind(O/'candidate.nes')),indent=2)+'\n')
  raise
if __name__=='__main__':main()
