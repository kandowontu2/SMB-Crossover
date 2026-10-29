"""Finite compiled original-v-port and actual parent helper/IRQ controls.

CPU+mapper only. No PPU scheduler, native route or audio integration claim.
"""
import json,re,sys,statistics,inspect
from pathlib import Path
from py65.devices.mpu6502 import MPU
import prepare_smb2_roster_native_v1 as D
import prepare_smb2_roster_component_v1 as B
sys.path.insert(0,str(D.ROOT/'tools/audit'))
from verify_native_relocation import NesMPU


class Memory:
 base=None;smc=None
 def __init__(self,s):
  if Memory.base is None:
   Memory.base=(D.OUT/'candidate.nes').read_bytes()
   for line in B.HOST.with_suffix('.dbg').open():
    if line.startswith('seg\t')and'name="SMCCODE"'in line:
     d=dict(re.findall(r'(\w+)=("[^"]*"|[^,\r\n]+)',line));Memory.smc=tuple(int(d[k],0)for k in ['start','ooffs','size']);break
  self.rom=Memory.base;self.ram=bytearray(32768);self.bank=[126,118,80,127];self.log=[];self.executions=[]
  p,o,n=Memory.smc;self.ram[p:p+n]=self.rom[o:o+n]
  self.ram[s['CurrentBank']]=0xf6
  self.ram[s['CurrentBankC']]=0xd0
  self.symbols=s
  self.ram[0x5204]=128
 def __getitem__(self,p):
  if isinstance(p,slice):return bytes(self[i]for i in range(*p.indices(65536)))
  p&=65535
  return self.ram[p]if p<32768 else self.rom[16+self.bank[(p-32768)//8192]*8192+(p&8191)]
 def __setitem__(self,p,v):
  if isinstance(p,slice):
   ids=list(range(*p.indices(65536)));assert len(ids)==len(v)
   for i,q in zip(ids,v):self[i]=q
   return
  p&=65535;v&=255
  if p<32768:self.ram[p]=v
  if 0x5114<=p<=0x5117:self.bank[p-0x5114]=v&127
  if p>=0x4000:self.log.append((p,v))


def execute(m,pc,inject=None,limit=60000,stop=0x600,**kw):
 c=NesMPU(memory=m,pc=pc);c.a=kw.get('a',0);c.x=kw.get('x',0);c.y=kw.get('y',0);c.p=kw.get('p',0x24);c.sp=253
 m[0x1fe]=(stop-1)&255;m[0x1ff]=(stop-1)>>8;trace=[];irq=None;low=c.sp
 for i in range(limit):
  low=min(low,c.sp)
  if c.pc==stop:c.lowest_sp=low;return c,trace,irq
  hit=(c.pc==inject)if isinstance(inject,int)else(bool(inject)and c.pc==inject[0]and m.bank[1]==inject[1])
  if hit and irq is None:
   before=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,list(m.bank));p,o,n=Memory.smc;smc=bytes(m.ram[p:p+n]);c.irq()
   for _ in range(3000):
    c.step()
    if c.pc==before[0]:break
   after=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,list(m.bank))
   assert before==after,('IRQCPU',before,after)
   assert smc==bytes(m.ram[p:p+n]),'IRQSMC'
   irq=before[0]
  trace.append(c.pc)
  if isinstance(m,Memory):m.executions.append((c.pc,m.bank[(c.pc-32768)//8192]if c.pc>=32768 else None))
  assert m[c.pc]!=0,('BRK',hex(c.pc),trace[-12:]);c.step()
 raise AssertionError(('noReturn',hex(pc),hex(c.pc)))


def original_call(m,pair,pc,**kw):
 # Pair1 for carry/objects, pair0 for player; genuine fixed E/F retained.
 return execute(m,pc,**kw)[0]


def mapped(s):
 report=json.loads((D.OUT/'native-projection.json').read_text())
 # $0544 is an operand-base expression Stats-2, NOT a copied field.
 # Genuine lifting indexes2..7 read original Stats0..5. Never compare the
 # nonexistent base as though it were extra owned RAM aliased over Fresh.
 return {int(r['original'],16):int(r['host'],16)for r in report['RAM']if r['alias']!='S2Stats-2'}


def init(s,variant=0,mode=1,y=176,x=100):
 m=Memory(s)
 for n,v in dict(SelectedCharacter=25,S2Variant=variant,NumberofLives=2,OperMode=1,
  GameEngineSubroutine=8,AreaType=1,Player_X_Position=x,Player_Y_Position=y,
  Player_Y_HighPos=1,Player_Rel_XPos=x,PlayerFacingDir=1,CrossoverBehaviorVersion=mode).items():m[s[n]]=v
 execute(m,s['S2ColdInit']);return m


def sync_from_original(a,m,ram):
 for p,q in ram.items():m[q]=a[p]


def assert_ram(a,m,ram,context,exclude=()):
 wrong=[(hex(p),hex(q),a[p],m[q])for p,q in ram.items()if p not in exclude and a[p]!=m[q]]
 assert not wrong,(context,wrong[:15])


def source_primitives(s,ram):
 cases=[]
 l=D.labels();stats=json.loads((D.ROOT/'build/smb2-roster-source-v1/audit.json').read_text())['character_stats']
 for char in range(4):
  for bits in range(8):
   for hold in [1,120]:
    a=D.original();m=init(s)
    a[l['CharacterStatsRAM']:l['CharacterStatsRAM']+23]=bytes(stats[char]['bytes'])
    for n,v in dict(CurrentCharacter=char,PlayerYLo=176,PlayerXVelocity=8 if bits&4 else 0,
     HoldingItem=bits&1,CrouchJumpTimer=60 if bits&2 else 0,Player1JoypadHeld=128).items():a[l[n]]=v
    sync_from_original(a,m,ram)
    ca=original_call(a,0,l['PlayerStartJump']);cb,_,_=execute(m,s['S2N8C99'])
    assert_ram(a,m,ram,['jump',char,bits,hold])
    assert(ca.a,ca.x,ca.y,ca.p&0xcf,ca.sp)==(cb.a,cb.x,cb.y,cb.p&0xcf,cb.sp)
    for tick in range(90):
     a[l['Player1JoypadHeld']]=128 if tick<hold else 0;a[0x10]=tick
     m[s['S2Held']]=a[l['Player1JoypadHeld']];m[s['S2Clock']]=tick
     ca=original_call(a,0,l['PlayerGravity']);cb,_,_=execute(m,s['S2N8CD9'])
     assert_ram(a,m,ram,['gravity',char,bits,hold,tick])
     ca=original_call(a,0,l['ApplyPlayerPhysicsY']);cb,_,_=execute(m,s['S2N8EA4'])
     assert_ram(a,m,ram,['integrateY',char,bits,hold,tick])
     assert(ca.a,ca.x,ca.y,ca.p&0xcf)==(cb.a,cb.x,cb.y,cb.p&0xcf)
    cases.append([char,bits,hold,90])
 return cases


def source_objects(s,ram):
 l=D.labels();cases=0;carry=0
 for axis in ['X','Y']:
  for speed in [0,1,7,15,16,24,48,62,127,128,208,232,240,248,255]:
   for frac in [0,1,127,128,255]:
    for slot in range(3):
     a=D.original(1);m=init(s);p=l['ObjectXVelocity']+(10 if axis=='Y'else 0)+slot
     a[p]=speed;a[l['ObjectXSubpixel']+(10 if axis=='Y'else 0)+slot]=frac
     a[l['ObjectXLo']+slot]=250;a[l['ObjectYLo']+slot]=170;a[0x12]=slot;a[l['IsHorizontalLevel']]=1
     sync_from_original(a,m,ram);m[s['S2ObjectLift']+slot]=0
     ca=original_call(a,1,l['ApplyObjectPhysics'+axis],x=slot);cb,_,_=execute(m,s['S2O9E50']if axis=='X'else s['S2O9E4B'],x=slot)
     assert_ram(a,m,ram,['object',axis,speed,frac,slot])
     assert a[2]==m[s['S2Math2']]
     assert(ca.a,ca.x,ca.y,ca.p&0xcf)==(cb.a,cb.x,cb.y,cb.p&0xcf)
     cases+=1
 for char in range(4):
  for size in range(2):
   for anim in [0,4,8]:
    for timer in range(1,8):
     for hitbox in [0,2,3]:
      a=D.original(1);m=init(s)
      for n,v in dict(CurrentCharacter=char,PlayerCurrentSize=size,PlayerDirection=1,
       PlayerXLo=120,PlayerXHi=1,PlayerYLo=80,PlayerYHi=0,PlayerAnimationFrame=anim,
       ObjectBeingCarriedTimer=timer,ObjectHitbox=hitbox,byte_RAM_12=0).items():a[l[n]]=v
      a[0x7f00:0x7f1c]=a[l['ItemCarryYOffsets']:l['ItemCarryYOffsets']+28]
      for off,n in [(0,'CarryYOffsetBigLo'),(7,'CarryYOffsetSmallLo'),(14,'CarryYOffsetBigHi'),(21,'CarryYOffsetSmallHi')]:a[0x7f00+off]=a[l[n]+char]
      sync_from_original(a,m,ram)
      ca=original_call(a,1,l['CarryObject'],stop=0x966e)
      cb,_,_=execute(m,s['S2O960F'])
      # Original stop is before its render continuation, so its caller return
      # is still on stack; all real arithmetic outputs and physical flags exact.
      assert_ram(a,m,ram,['carry',char,size,anim,timer,hitbox])
      assert a[l['EnemyMovementDirection']]==m[s['S2ObjectFacing0']]
      assert(ca.a,ca.x,ca.y,ca.p&0xcf)==(cb.a,cb.x,cb.y,cb.p&0xcf)
      carry+=1
 return cases,carry


def normal_campaigns(s,ram):
 l=D.labels();stats=json.loads((D.ROOT/'build/smb2-roster-source-v1/audit.json').read_text())['character_stats']
 solid=next(v for v in range(256)if Memory.base[16+127*8192+(s['MTileAttribute']-0xe000)+v]&s['MTILE_SOLID']and v not in [0x23,0x26,0xc2,0xc3,0x51,0x52,0x5f,0x60])
 rows=[];costs=[];scratch_sites=set()
 for char in range(4):
  for policy in ['idle','right','left','holdJump','releaseJump','reverseJump','crouchCharge','ceiling','wall','ledge']:
   a=D.original();m=init(s,variant=[0,3,2,1].index(char))
   a[l['CharacterStatsRAM']:l['CharacterStatsRAM']+23]=bytes(stats[char]['bytes'])
   for n,v in dict(CurrentCharacter=char,PlayerXLo=100,PlayerXHi=1,PlayerYLo=176,PlayerScreenX=100,PlayerDirection=1,IsHorizontalLevel=1).items():a[l[n]]=v
   # Same finite authored solid/empty arena in both engines; source consumes
   # genuine decoded tiles, port consumes genuine SMB block-buffer helper.
   for page in range(11):
    for ty in range(15):
     for tx in range(16):
      on=ty>=13
      if policy=='ceiling'and ty==7:on=True
      if policy=='wall'and tx==10 and ty>=9:on=True
      if policy=='ledge'and tx>=8:on=False
      a[0x6000+page*240+ty*16+tx]=255 if on else 0
      if ty>=2 and page<2:m[s['Block_Buffer_1']+page*208+(ty-2)*16+tx]=solid if on else 0
   sync_from_original(a,m,ram)
   for tick in range(85):
    held=0;fresh=0
    if policy in ['right','wall','ledge']:held=1
    if policy=='left':held=2
    if policy in ['holdJump','releaseJump','reverseJump','ceiling']:
     held=128 if policy!='releaseJump'or tick<3 else 0
     if policy=='reverseJump':held|=1 if tick<20 else 2
     if tick==0:fresh=128
    if policy=='crouchCharge':
     if tick<61:held=4
     elif tick==61:held=128;fresh=128
    a[l['Player1JoypadHeld']]=held;a[l['Player1JoypadPress']]=fresh;a[0x10]=tick
    m[s['S2Held']]=held;m[s['S2Fresh']]=fresh;m[s['S2Clock']]=tick
    # Camera boundary follows this world point in the controlled two-page
    # scene; no fake scroll/clamp is disabled inside either native routine.
    a[l['PlayerScreenX']]=100;m[s['S2ScreenX']]=100
    ca,ta,_=execute(a,l['HandlePlayerState_Normal']);cb,tb,_=execute(m,s['S2N8A41'])
    assert_ram(a,m,ram,[char,policy,tick],exclude=[1])
    assert(ca.a,ca.x,ca.y,ca.p&0xcf)==(cb.a,cb.x,cb.y,cb.p&0xcf),(char,policy,tick,'AXYP')
    costs.append(cb.processorCycles-ca.processorCycles)
    for p in ta:
     op,mode=MPU.disassemble[a[p]]
     if mode in ['zpg','zpx','zpy']and a[p+1]==1:scratch_sites.add((p,op,mode))
   rows.append([char,policy,85])
 # Native RAM1 is the translated terrain pointer scratch; outside the real
 # source query it is defined by STA8E53 before throw's ROL/LDA. No gameplay
 # consumer requires preserving a pointer into the original decoded map.
 return dict(campaigns=rows,full_Normal_updates=len(costs),actual_parent_solid=solid,
  whole_Normal_cycle_delta=[min(costs),max(costs)],terrain_pointer_scratch_exclusion='Only original RAM1 after genuine tile query; real host pointer is R6/R7, not original decoded-map pointer. All other mapped fields and final AXYP/SP strict.',
  observed_RAM1_instruction_sites=[[hex(p),op,mode]for p,op,mode in sorted(scratch_sites)])


def pixels(raw,m,oam,port=False):
 out={};l=D.labels()
 for y,t,attr,x in reversed(oam):
  at=(t&1)*4096+(t&254)*16
  if port:
   win=at//1024;page=m[m.symbols['CurrentCHRBank']+win]+((m[m.symbols['X5ChrMode']+win]&3)<<8)
   off=16+1048576+page*1024+(at&1023)
  else:
   if at<4096:page=m[l['SpriteCHR1']+at//1024]
   else:page=(m[l['BackgroundCHR1']+(at-4096)//2048]&254)+(at%2048)//1024
   off=16+131072+page*1024+(at&1023)
  pair=raw[off:off+32]
  for yy in range(16):
   for xx in range(8):
    sy=15-yy if attr&128 else yy;sx=7-xx if attr&64 else xx;a=sy//8*16+sy%8
    v=(pair[a]>>(7-sx)&1)|((pair[a+8]>>(7-sx)&1)<<1)
    if v:out[x+xx,y+1+yy]=(v,attr&3)
 return out


def render_controls(s):
 source=json.loads((D.OUT/'art-source.json').read_text())['cases'];renders=[];raw=D.ROM.read_bytes()
 for case in source:
  if 'native_character'not in case:continue
  char=case['native_character'];size=case['size'];anim=case['animation'];held=case['held'];face=case['face']
  m=init(s,variant=[0,3,2,1].index(char),y=80,x=80)
  for n,v in dict(S2Size=size,S2Animation=anim,S2Holding=held,S2Face=face).items():m[s[n]]=v
  m[0x200:0x300]=bytes([248])*256
  c,_,_=execute(m,s['S2DrawBody'])
  n=m[s['CurrentOAMOffset']];oam=[list(m[p:p+4])for p in range(0x200,0x200+n,4)]
  assert len(oam)==5
  # Authentic physical publication is returned to root X5 sprite-latch RAM;
  # source bytes in our sparse ROM are decoded with that actual page.
  page=796+char*2+size
  assert m[s['CurrentCHRBank']]+((m[s['X5ChrMode']]&3)<<8)==page
  a=D.original();l=D.labels()
  for name,v in dict(CurrentCharacter=char,PlayerCurrentSize=size,PlayerAnimationFrame=anim,HoldingItem=held,PlayerDirection=face,PlayerScreenX=80,PlayerScreenYLo=80).items():a[l[name]]=v
  original_call(a,0,l['LoadWorldCHRBanks'])
  expected=pixels(raw,a,case['source_OAM'])
  actual=pixels(m.rom,m,oam,True)
  assert expected==actual,('bodyPixels',char,size,anim,held,face,len(expected),len(actual))
  assert m.bank==[126,118,80,127]
  renders.append(c.processorCycles)
 objects=[]
 for case in source:
  if 'native_object'not in case:continue
  m=init(s,y=80,x=80);kind=case['native_object'];face=case['face'];frame=case['frame']
  for n,v in dict(S2ObjectState=1,S2ObjectType=kind,S2Clock=frame,S2ObjectFacing0=face).items():m[s[n]]=v
  m[s['S2X']+1]=80;m[s['S2Y']+1]=80
  m[0x200:0x300]=bytes([248])*256
  execute(m,s['S2DrawBody'])
  body_pages=[m[s['CurrentCHRBank']+i]+((m[s['X5ChrMode']+i]&3)<<8)for i in range(8)]
  if frame==0:
   c,_,_=execute(m,s['S2DrawObjects'])
  else:
   # Frame8 is an authenticated optional atlas record, not the initial
   # vegetable's nonexistent clock animation. Execute the actual generic
   # host renderer on that record and genuine independently published page.
   execute(m,s['S2DrawObjects'])
   m[s['CurrentOAMOffset']]=20
   execute(m,s['S2SetRecord'],a=case['record'])
   for name,v in dict(R0=m[s['SmPosePtr']],R1=m[s['SmPosePtr']+1],R3=0,R4=80,R5=0,R6=80,R7=1).items():m[s[name]]=v
   c,_,_=execute(m,s['S2Render'])
  assert m[s['CurrentOAMOffset']]==28 # 5 body +2 authentic vegetable parts.
  assert m[s['CurrentCHRBank']]+((m[s['X5ChrMode']]&3)<<8)==body_pages[0]
  assert m[s['CurrentCHRBank']+6]+((m[s['X5ChrMode']+6]&3)<<8)==804
  oam=[list(m[p:p+4])for p in range(0x214,0x21c,4)]
  a=D.original(1);l=D.labels();original_call(a,1,l['LoadWorldCHRBanks'])
  assert pixels(raw,a,case['source_OAM'])==pixels(m.rom,m,oam,True),('vegetablePixels',kind,frame,face)
  objects.append(c.processorCycles)
 return renders,objects


def adapter_controls(s,ram):
 l=D.labels();cases=0;transform=[];costs=[]
 for variant in range(4):
  for mode in range(2):
   m=init(s,variant,mode)
   assert m[s['S2NativeCharacter']]==[0,3,2,1][variant]
   # Actual collector API consumes a real input item type and preserves X.
   for k in range(5):
    m[s['PowerUpType']+3]=0;c,_,_=execute(m,s['S2Pickup'],x=3)
    assert c.x==3 and c.p&1 and m[s['S2MaxHealth']]==min(k+1,2)
    assert m[s['S2Health']]==[0x1f,0x2f,0x3f][min(k+1,2)]
   for k in range(5):
    m[s['PowerUpType']+4]=1;c,_,_=execute(m,s['S2Pickup'],x=4)
    assert c.x==4 and c.p&1 and m[s['S2Vegetables']]==min((k+1)*3,9)
   # Real nonfatal source DamagePlayer exact HP/knockback/SFX fields.
   for hp in [0x10,0x1f,0x20,0x2f,0x30,0x3f]:
    for contact_x in [80,100,120]:
     a=D.original(1);n=init(s,variant,mode)
     a[l['PlayerHealth']]=hp;a[l['PlayerScreenX']]=100;a[l['SpriteTempScreenX']]=contact_x
     n[s['S2Health']]=hp
     original_call(a,1,l['DamagePlayer']);execute(n,s['S2InjuryStart'],a=contact_x)
     for native,host in [('PlayerHealth','S2Health'),('DamageInvulnTime','S2Hurt'),('PlayerXVelocity','S2VX'),('PlayerYVelocity','S2VY'),('DPCMQueue','S2DpcmRequest')]:assert a[l[native]]==n[s[host]],(variant,mode,hp,contact_x,native)
     cases+=1
   # True source keyframe sequence and native30-update timer order. A fresh
   # Mushroom follows a real injury down to one heart, not an art-size seed.
   n=init(s,variant,mode)
   execute(n,s['S2InjuryStart'],a=120)
   assert n[s['S2Health']]==0x0f
   a=D.original();a[l['CurrentCharacter']]=[0,3,2,1][variant]
   a[l['PlayerHealth']]=0x0f;a[l['PlayerCurrentSize']]=0;a[l['DamageInvulnTime']]=127
   a[l['PlayerState']]=0;a[l['PlayerYLo']]=176
   # Isolate actual HandleState dispatch prefix+changing handler; normal
   # and carry terrain paths were already compared separately above.
   seq=[]
   for phase in ['shrink','grow']:
    if phase=='grow':
     execute(n,s['S2GiveItem'],a=0);a[l['PlayerHealth']]=n[s['S2Health']]
    for tick in range(32):
     if tick==31:break # next normal movement belongs to full terrain campaign.
     # The genuine original state machine requires a table-jump helper;
     # use the actual8A02 call until it returns through native handlers.
     ca,_,_=execute(a,l['HandlePlayerState']);cb,_,_=execute(n,s['S2HandlePlayerState'])
     for native,host in [('PlayerState','S2State'),('PlayerStateTimer','S2Timer'),('PlayerCurrentSize','S2Size'),('DamageInvulnTime','S2Hurt'),('SoundEffectQueue2','S2Sfx2')]:assert a[l[native]]==n[s[host]],(phase,tick,native,a[l[native]],n[s[host]])
     seq.append([phase,tick,n[s['S2Size']],n[s['S2Timer']]])
     execute(a,l['DecrementPlayerStateTimers_Loop'],x=3);execute(n,s['S2EndFrame'])
    assert n[s['S2State']]==0
   transform.append([variant,mode,seq])
   # Genuine ordinary INC gains, wrap and scene reset retain earned fields.
   before=[m[s[n]]for n in ['S2Health','S2MaxHealth','S2Vegetables']]
   for life in [3,5,255,0]:
    # Reachable ordinary gain sequence cannot jump5->255. Stage the prior
    # owned life byte only for finite arithmetic saturation/wrap unit scope.
    if life==255:m[s['S2Life']]=254
    m[s['NumberofLives']]=life;execute(m,s['S2Ensure'])
    assert [m[s[n]]for n in ['S2Health','S2MaxHealth','S2Vegetables']]==before
   m[s['AreaAddrsLOffset']]=1;execute(m,s['S2Ensure'])
   assert [m[s[n]]for n in ['S2Health','S2MaxHealth','S2Vegetables']]==before
   m[s['NumberofLives']]=255;execute(m,s['S2Ensure'])
   assert [m[s[n]]for n in ['S2Health','S2MaxHealth','S2Vegetables']]==[31,0,0]
   n=init(s,variant,mode);execute(n,s['S2GiveItem'],a=1)
   n[s['S2Fresh']]=64;execute(n,s['S2GroundInteraction'])
   n[s['S2Previous']]=64;n[s['S2Clock']]=77;n[s['AreaAddrsLOffset']]=1
   execute(n,s['S2Ensure'])
   assert [n[s[v]]for v in ['S2Holding','S2ObjectType','S2ObjectLift','S2Vegetables','S2Previous','S2Clock']]==[1,50,1,2,64,77]
   n[s['NumberofLives']]=1;execute(n,s['S2Ensure'])
   assert n[s['S2Clock']]==77 and n[s['S2Holding']]==0 and n[s['S2Vegetables']]==0
 return dict(nonfatal_original_injuries=cases,source_size_sequences=transform,item_and_life_modes=8)


def lift_throw_controls(s,ram):
 l=D.labels();rows=[]
 for variant in range(4):
  char=[0,3,2,1][variant]
  for mode in range(2):
   m=init(s,variant,mode);execute(m,s['S2GiveItem'],a=1)
   assert m[s['S2Vegetables']]==3
   # This source callback is reachable only after authentic downward support.
   # It grants no object without Down+freshB, stock and a free owned record.
   for held,fresh,duck in [(0,0,0),(4,64,1),(64,64,1)]:
    m[s['S2Held']]=held;m[s['S2Fresh']]=fresh;m[s['S2Duck']]=duck;execute(m,s['S2GroundInteraction'])
    assert not m[s['S2Holding']]and m[s['S2Vegetables']]==3
   m[s['S2Held']]=64;m[s['S2Fresh']]=64;m[s['S2Duck']]=0;execute(m,s['S2GroundInteraction'])
   assert m[s['S2Holding']]==1 and m[s['S2Vegetables']]==2 and m[s['S2ObjectHitbox']]==2
   a=D.original();sync={p:m[q]for p,q in ram.items()}
   for p,v in sync.items():a[p]=v
   ticks=0
   while m[s['S2State']]==2:
    ca,_,_=execute(a,l['HandlePlayerState_Lifting']);cb,_,_=execute(m,s['S2N8A87'])
    assert_ram(a,m,ram,['lifting',variant,mode,ticks])
    execute(a,l['DecrementPlayerStateTimers_Loop'],x=3);execute(m,s['S2EndFrame'])
    ticks+=1;assert ticks<200
   assert m[s['S2Holding']]==1 and m[s['S2ObjectLift']]==1
   # Native throw helper uses its original control bits, stand/run velocities
   # and fractions. No stock/carry state is charged before the actual throw.
   for face in range(2):
    for vx in [0,7,8,24,232,248]:
     n=init(s,variant,mode);aa=D.original()
     for name,v in dict(S2Holding=1,S2HeldIndex=0,S2ObjectType=50,S2ObjectState=1,S2ObjectLift=1,S2Face=face,
      S2Fresh=64,S2Held=64,S2VX=vx,S2X=100,S2Y=176).items():n[s[name]]=v
     for p,q in ram.items():aa[p]=n[q]
     ca,_,_=execute(aa,l['sub_BANK0_8DC0']);cb,_,_=execute(n,s['S2N8DC0'])
     assert_ram(aa,n,ram,['throw',char,mode,face,vx])
     assert(ca.a,ca.x,ca.y,ca.p&0xcf,ca.sp)==(cb.a,cb.x,cb.y,cb.p&0xcf,cb.sp)
     assert n[s['S2ObjectProjectile']]==1 and n[s['S2ObjectLift']]==0 and n[s['S2Holding']]==0
   # One held+two throws are the explicit host pool limit. Refused allocation
   # or third throw must neither spend reserve nor erase/replace live records.
   for i in range(3):m[s['S2ObjectState']+i]=1
   m[s['S2Holding']]=0;before=m[s['S2Vegetables']];execute(m,s['S2GroundInteraction'])
   assert m[s['S2Vegetables']]==before and m[s['S2Holding']]==0
   m[s['S2Holding']]=1;m[s['S2HeldIndex']]=0;m[s['S2Fresh']]=64
   m[s['S2ObjectProjectile']+1]=1;m[s['S2ObjectProjectile']+2]=1
   execute(m,s['S2LimitThrowPool']);assert m[s['S2Fresh']]==0 and m[s['S2Holding']]==1
   # Actual root lifecycle authority invalidates a referenced SMB slot;
   # an unrelated spawn/erase never invalidates the held actor.
   n=init(s,variant,mode)
   for name,v in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,S2Fresh=64,S2Held=64).items():n[s[name]]=v
   c,_,_=execute(n,s['S2TryLiftEnemy'],x=0)
   assert bool(c.p&1)==bool(mode)
   if mode:
    assert c.x==0 and c.y==0 and n[s['S2Holding']]==1
    execute(n,s['S2ActorEpochChanged'],x=1);assert n[s['S2Holding']]==1
    execute(n,s['S2ActorEpochChanged'],x=255);assert n[s['S2Holding']]==1
    execute(n,s['S2ActorEpochChanged'],x=0);assert n[s['S2Holding']]==0
   rows.append([variant,mode,ticks,'nativeLiftingAnd12ThrowCases/sourceItems/pool/realEpoch'])
 return rows


def ownership_and_irq(s):
 public=['S2ColdInit','S2NewLife','S2Ensure','S2Movement','S2EndFrame','S2NmiClock','S2GiveItem','S2Pickup','S2FullPower',
  'S2InjuryStart','S2InjuryStatus','S2DeathStart','S2DeathUpdate','S2StompPolicy','S2Box','S2HeadContact',
  'S2ActorEpochChanged','S2TryLiftEnemy','S2StandOnActor','S2CollisionBounds','S2EnemyControl','S2ObjectHit','S2Graphics','S2GraphicsBank','S2DrawBody','S2DrawObjects','S2PalettePointer']
 foreign=0
 for char in range(256):
  if char==25:continue
  for name in public:
   m=init(s);m[s['SelectedCharacter']]=char;before=bytes(m.ram)
   execute(m,s[name],a=1,x=0,y=173)
   assert m.ram[:0x100]==before[:0x100]and m.ram[0x200:]==before[0x200:],('foreign',char,name)
   assert m.bank==[126,118,80,127]
   foreign+=1
 clocks=0
 for value in range(256):
  for p in [0,1,4,8,0x40,0x80,0xcf]:
   m=init(s);m[s['S2Clock']]=value;m[s['S2Ready']]=0x72
   c,_,_=execute(m,s['S2NmiClock'],a=197,x=211,y=219,p=p)
   assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(197,211,219,p&0xcf,255)
   assert m[s['S2Clock']]==(value+1)&255 and m[s['S2Ready']]==0x72
   clocks+=1
 # Actual parentIRQ at every distinct component instruction reached by body
 # rendering, movement and an active lifting wrapper. All live CPU/SMC/banks
 # strict; no native NMI/PPU timing is being simulated.
 def irq_setup(scenario):
  m=init(s);m[s['SavedJoypadBits']]=129
  if scenario in ['lift','drawHeld']:
   execute(m,s['S2GiveItem'],a=1);m[s['S2Fresh']]=64;execute(m,s['S2GroundInteraction'])
   m[s['SavedJoypadBits']]=0
  if scenario=='throw':
   m[s['S2Holding']]=1;m[s['S2ObjectState']]=1;m[s['S2ObjectType']]=50;m[s['S2ObjectLift']]=1
   m[s['S2HeldIndex']]=0;m[s['SavedJoypadBits']]=64
  if scenario=='head':
   m[s['Player_Y_Position']]=80;m[s['S2Y']]=80;m[s['S2Air']]=1;m[s['S2VY']]=192
   m[s['S2Previous']]=128;m[s['SavedJoypadBits']]=128
   for i in range(416):m[s['Block_Buffer_1']+i]=16
  return m
 irqs=[]
 for name,scenario in [('S2DrawBody','body'),('S2DrawObjects','drawHeld'),('S2Movement','jump'),('S2Movement','lift'),('S2Movement','throw'),('S2Movement','head'),('S2NmiClock','clock')]:
  baseline=irq_setup(scenario)
  baseline.executions=[]
  end,trace,_=execute(baseline,s[name])
  points=sorted(set(p for p,b in baseline.executions if b==118 and 0xa640<=p<0xc000))
  for p in points:
   m=irq_setup(scenario)
   c,_,q=execute(m,s[name],inject=(p,118),p=0x20)
   # Baseline should use same I flag for actualirq eligibility.
   compare=irq_setup(scenario);ce,_,_=execute(compare,s[name],p=0x20)
   assert q is not None
   assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(ce.a,ce.x,ce.y,ce.p&0xcf,ce.sp)
   assert m.ram[0x5c00:0x5c80]==compare.ram[0x5c00:0x5c80]
   assert m.ram[0x5f98:0x5fa0]==compare.ram[0x5f98:0x5fa0]
   irqs.append([name,scenario,hex(p)])
 return dict(foreign_no_state_write_cases=foreign,NMI_clock_AXYP_SP_cases=clocks,actual_parent_IRQ_boundaries=irqs)


def phase_and_full_wrapper(s,ram):
 l=D.labels();lift=[];costs=[]
 for variant in range(4):
  for mode in range(2):
   for kind in [1,50,51]:
    m=init(s,variant,mode);m[s['S2ObjectType']]=kind;execute(m,s['S2BeginLift'])
    a=D.original()
    for p,q in ram.items():a[p]=m[q]
    ticks=0
    while m[s['S2State']]==2:
     execute(a,l['HandlePlayerState_Lifting']);execute(m,s['S2N8A87'])
     assert_ram(a,m,ram,['allClassLift',variant,mode,kind,ticks])
     execute(a,l['DecrementPlayerStateTimers_Loop'],x=3);execute(m,s['S2EndFrame'])
     ticks+=1;assert ticks<200
    lift.append([variant,mode,kind,ticks])
   # All256 masks at actual wrapper input, fresh/previous source bitmap.
   # No controller-bit reversal or inferred serial-input format is permitted.
   for mask in range(256):
    m=init(s,variant,mode);m[s['SavedJoypadBits']]=mask
    execute(m,s['S2Movement'])
    assert m[s['S2Previous']]==mask and m[s['S2Held']]==mask
   for action,mask in [('idle',0),('walk',1),('run',65),('jump',129),('release',1),('reverse',130)]:
    m=init(s,variant,mode);m[s['SavedJoypadBits']]=mask
    if action in ['release','reverse']:
     m[s['S2Air']]=1;m[s['S2VY']]=216;m[s['S2Previous']]=129
    c,_,_=execute(m,s['S2Movement']);e,_,_=execute(m,s['S2EndFrame'])
    costs.append([variant,mode,action,c.processorCycles,e.processorCycles,c.lowest_sp])
 # Scene reset can be interrupted by the private endpoint without losing the
 # NMI phase. This is endpoint interleaving, NOT an actual shared-NMI proof.
 baseline=init(s);baseline[s['S2Clock']]=7;baseline[s['AreaAddrsLOffset']]=1
 _,trace,_=execute(baseline,s['S2Ensure']);nsteps=len(trace)
 for index in range(nsteps):
  m=init(s);m[s['S2Clock']]=7;m[s['AreaAddrsLOffset']]=1
  c=NesMPU(memory=m,pc=s['S2Ensure']);c.sp=253;m[0x1fe]=255;m[0x1ff]=5
  for step in range(10000):
   if step==index:
    before=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,list(m.bank));resume=c.pc
    c.stPush((resume-1)>>8);c.stPush((resume-1)&255);c.pc=s['S2NmiClock']
    for _ in range(30):
     c.step()
     if c.pc==resume:break
    assert(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,list(m.bank))==before
   if c.pc==0x600:break
   c.step()
  assert m[s['S2Clock']]==8,(index,'lostNmiPhase')
  expected=bytearray(baseline.ram[0x5c00:0x5c80]);expected[s['S2Clock']-0x5c00]=8
  assert m.ram[0x5c00:0x5c80]==expected
 # Exact one-byte source hitbox fields, including original small-size rule.
 boxes=[]
 for size in range(2):
  for duck in range(2):
   m=init(s);m[s['S2Size']]=size;m[s['S2Duck']]=duck;execute(m,s['S2CollisionBounds'])
   a=D.original();left=a[l['ObjectCollisionHitboxLeft']+duck];top=a[l['ObjectCollisionHitboxTop']+duck]
   expected=[left,top,left+a[l['ObjectCollisionHitboxWidth']+duck],top+a[l['ObjectCollisionHitboxHeight']+duck]]
   assert [m[s['R0']+i]for i in range(4)]==expected
   boxes.append([size,duck,expected])
 # Source alive prefix ages the throw before object physics, including its
 # birth update. Original ages33..255 remain unchanged, not silently clamped.
 for value in range(256):
  a=D.original(1);a[l['ObjectProjectileTimer']]=value
  start=l['HandleEnemyState_Alive']+5
  assert a[start]==0xbc and a[start+4]==0xc0 # LDY abs,X; DEY; CPY1F
  execute(a,start,stop=l['loc_BANK2_89C9'])
  m=init(s);m[s['S2ObjectProjectile']]=value;execute(m,s['S2AdvanceProjectileAge'])
  assert m[s['S2ObjectProjectile']]==a[l['ObjectProjectileTimer']]
 return dict(all_class_small_large_vegetable_and_enemy_lift_campaigns=lift,actual_full_Movement_EndFrame_costs=costs,
  actual_wrapper_input_mask_cases=2048,scene_reset_NmiClock_endpoint_interleavings=nsteps,original_enemy_hitbox_cases=boxes,
  actual_source_projectile_age_cases=256,vegetable_animation='Actual native initialization0 remains0 through supported carry/throw; frame8 atlas is reference-only, no invented NMI animation.',
  contract='No full host NMI/PPU/IRQ scheduling implied by endpoint interleaving; real host IRQ is separately exercised. EndFrame AFTER action/render, Clock only NMI. Cold ownership excludesNMI before marker publish; scene/newlife never rewrite Clock.')


def main():
 s=B.overlay();s.update({n:v for n,v in B.labels(B.HOST.with_suffix('.lbl')).items()if n not in s})
 r=mapped(s)
 jumps=source_primitives(s,r);objects,carry=source_objects(s,r);normal=normal_campaigns(s,r);renders,veg=render_controls(s)
 adapters=adapter_controls(s,r);lift=lift_throw_controls(s,r);ownership=ownership_and_irq(s);phase=phase_and_full_wrapper(s,r)
 result=dict(status='PASS_FINITE_SOURCE_CPU_COMPONENT_CONTROLS_NO_NATIVE',source=D.binding(D.ROM),parent=D.binding(B.HOST.with_suffix('.nes')),
  candidate=D.binding(D.OUT/'candidate.nes'),jump_campaigns=jumps,object_integrator_cases=objects,carry_geometry_cases=carry,
  body_render_cases=len(renders),body_render_cycle_range=[min(renders),max(renders)],full_native_Normal=normal,
  simultaneous_body_vegetable_render_cases=len(veg),adapter_controls=adapters,ownership_IRQ=ownership,
  lift_throw_item_pool_controls=lift,
  complete_wrapper_phase_cost_controls=phase,
  limitations=['No shared hook/lifecycle/whole Main or NMI scheduling integration','No authentic audio yet','No all-area RGB qualification; original roles require root palette composition'])
 q=D.OUT/'component-controls.json';q.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(D.binding(q),indent=2))
 freeze(result)


def freeze(result):
 owned=sorted((D.ROOT/'src').glob('smb2_roster*'))+[
  D.ROOT/'chr/characters/smb2-roster.chr',D.ROOT/'docs/qa/smb2-roster-component-2026-10-28.txt']
 owned += [D.ROOT/'tools'/n for n in ['prepare_smb2_roster_native_v1.py','prepare_smb2_roster_objects_v1.py',
  'prepare_smb2_roster_art_v1.py','prepare_smb2_roster_component_v1.py','smb2_roster_component_controls_v1.py']]
 deps=[D.ROM]+[B.HOST.with_suffix('.'+ext)for ext in ['nes','dbg','lbl']]
 deps += sorted((D.REF/'bin').glob('native.nes.*.nl'))
 deps += [D.REF/p for p in ['src/prg-0-1.asm','src/prg-2-3.asm','src/prg-e-f.asm','src/prg-a-b.asm','src/ram.asm','src/defs.asm']]
 deps += [D.ROOT/'build/smb2-roster-source-v1/handoff.json',D.ROOT/'build/smb2-roster-source-v1/audit.json',
  D.ROOT/'build/smb2-roster-allocator-v1-handoff.json',D.ROOT/'build/smb2-roster-allocator-v1.json',
  Path(inspect.getfile(MPU)),Path(inspect.getfile(NesMPU)),Path(sys.executable)]
 deps += [D.ROOT/'tools/Windows/cc65/bin'/n for n in ['ca65.exe','ld65.exe']]
 outputs=[D.OUT/n for n in ['candidate.nes','component.bin','art.bin','chr.bin','component.dbg','component.lbl',
  'component.s','component.cfg','asset.s','native-projection.json','object-projection.json','art-source.json',
  'layout-controls.json','component-controls.json','parent-rebase.json','first-RAM-fit-negative.txt','first-build-failure.txt','first-source-control-negative.txt']]
 layout=json.loads((D.OUT/'layout-controls.json').read_text())
 summary=dict(jump_campaigns=len(result['jump_campaigns']),full_Normal_updates=result['full_native_Normal']['full_Normal_updates'],
  object_integrator_cases=result['object_integrator_cases'],carry_geometry_cases=result['carry_geometry_cases'],
  body_render_cases=result['body_render_cases'],vegetable_atlas_cases=result['simultaneous_body_vegetable_render_cases'],
  foreign_cases=result['ownership_IRQ']['foreign_no_state_write_cases'],Clock_context_cases=result['ownership_IRQ']['NMI_clock_AXYP_SP_cases'],
  actual_parent_IRQ_boundaries=len(result['ownership_IRQ']['actual_parent_IRQ_boundaries']),
  scene_clock_interleavings=result['complete_wrapper_phase_cost_controls']['scene_reset_NmiClock_endpoint_interleavings'],
  whole_Movement_cycle_range=[min(v[3]for v in result['complete_wrapper_phase_cost_controls']['actual_full_Movement_EndFrame_costs']),max(v[3]for v in result['complete_wrapper_phase_cost_controls']['actual_full_Movement_EndFrame_costs'])],
  no_native=True,no_audio_integration=True)
 manifest=dict(status='FROZEN_PRIVATE_SMB2_SOURCE_CPU_COMPONENT_READY_FOR_ROOT_SHARED_INTEGRATION_REVIEW_NOT_PLAYABLE_OR_NATIVE',
  parent=layout['parent'],candidate=layout['candidate'],raw_ID=25,menu_slot=24,variant_UI_to_source=[0,3,2,1],
  extent={k:layout[k]for k in ['core_start','core_end','core_bytes','art_start','art_end','art_bytes']},CHR_pages=[796,807],
  summary=summary,owned_files=[D.binding(p)for p in owned],input_bindings=[D.binding(p)for p in deps],
  output_bindings=[D.binding(p)for p in outputs],
  reference='Source vs authored host adapters, exact caller/clock/lifecycle/actor/palette contracts and remaining audio prerequisite are in the bound source/control note.',
  remaining=['ROOT raw25/menu/cold owner/scene/physics/collision/real actor lifecycle/HUD/palette hooks',
   'Actual current shared-caller composition+native strict gameplay/render/cadence proof','Authentic SMB2 audio/Roll relocation/E119-120 clone/sample ownership separate prerequisite'],
  freeze_rule='Do not mutate bound sources/tools/reports. These development commands write this output directory; independent reproduction must preserve the frozen packet or use a separately named small output build, never a source/runtime clone.')
 all_records=manifest['owned_files']+manifest['input_bindings']+manifest['output_bindings']
 manifest['distinct_bound_files']=len({p['path'].lower()for p in all_records})
 p=D.OUT/'handoff.json';p.write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(handoff=D.binding(p),summary=summary,owned=len(owned),bindings=manifest['distinct_bound_files']),indent=2))


if __name__=='__main__':main()
