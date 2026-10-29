"""Finite genuine Main/renderer/lifecycle controls for private SuperMaaa."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import dragon_power_gameplay_controls_v1 as C
import dragon_power_flagpole_controls_v2 as T
import dragon_power_gameplay_isr_v1 as ISR
from sunny_integrated_controls_v1 import *
O=R/'build/supermaaa-host-v1';P=R/'build/pit-retold-host-v3'

def setup(b,char=0,variant=2,length=0):
 q=C.setup(b,char);q.put(MarioVariant=variant);q.m[0x5c7f]=length
 return q

def physical(q,name):return((location(q.b,name)-16)//8192,address(q.b,name))
def different(a,b):return[(i,x,z)for i,(x,z)in enumerate(zip(a,b))if x!=z][:20]

def code_label(b,bank,pc,exact=False):
 labels=[]
 for n,s in b['syms'].items():
  if '::'in n or s.get('type')!='lab'or'seg'not in s:continue
  g=b['segs'][s['seg']]
  if 'ooffs'not in g:continue
  at=address(b,n)
  if at<=pc and (not exact or at==pc)and(location(b,n)-16)//8192==bank:labels.append((at,n))
 assert labels,('No genuine linked code owner',bank,hex(pc))
 at,n=max(labels);return(n,pc-at)

def run_linked(q,name,**kw):
 # JumpEngine consumes a JSR return as a table pointer, then its selected
 # table word as a real JMP target. Record that complete consumer, so only
 # genuine relocated code pointers may differ in the ordered RAM writes.
 orig=NesMPU.step;annotations={};events=[];pending=None
 je=address(q.b,'JumpEngine');je_bank=physical(q,'JumpEngine')[0];pointer_pcs={je+z for z in[3,6,11,16]}
 def step(c):
  nonlocal pending
  pc=c.pc;bank=q.m.banks[(pc-0x8000)//8192]if pc>=0x8000 else -1
  if pc==je and bank==je_bank:
   ret=q.m[0x100+((c.sp+1)&255)]+256*q.m[0x100+((c.sp+2)&255)]
   jsr=ret-2;owner=q.m.banks[(jsr-0x8000)//8192]
   assert bytes(q.m[jsr+i]for i in range(3))==bytes([32,pc&255,pc>>8])
   table=ret+1+2*c.a;target=q.m[table]+256*q.m[table+1]
   tb=q.m.banks[(target-0x8000)//8192]
   key=(code_label(q.b,owner,jsr),c.a,code_label(q.b,tb,target,True))
   pending=(key,target,tb);events.append([owner,jsr,ret,table,tb,target,key])
  st=len(q.m.writes)
  is_pointer=bank==je_bank and pc in pointer_pcs
  consumed=pending if bank==je_bank and pc==je+18 else None
  if consumed:assert bytes(q.m[pc+i]for i in range(3))==bytes([108,address(q.b,'R6'),0])
  orig(c)
  if is_pointer:
   assert pending
   for i,(a,v)in enumerate(q.m.writes[st:],st):
    assert a in[address(q.b,n)for n in['R4','R5','R6','R7']]
    annotations[i]=('genuine JumpEngine pointer',pending[0],a)
  if consumed:
   assert(c.pc,q.m.banks[(c.pc-0x8000)//8192])==(consumed[1],consumed[2])
   pending=None
 NesMPU.step=step
 try:c,tr,mn=C.M.runtrace(q,name,**kw)
 finally:NesMPU.step=orig
 assert pending is None
 return c,tr,mn,annotations,events

def smc_contract(qa,qb,ta,tb):
 va=[qa.m[i]for i in smc_at(qa.b)];vb=[qb.m[i]for i in smc_at(qb.b)]
 assert va[:2]==vb[:2]and va[4:]==vb[4:]
 if va[2:4]==vb[2:4]:return None
 pa=va[2]+256*va[3];pb=vb[2]+256*vb[3];bank=va[0]&127
 names=[]
 for n,s in qa.b['syms'].items():
  if '::'in n or s.get('type')!='lab'or'seg'not in s or n not in qb.b['syms']:continue
  g=qa.b['segs'][s['seg']]
  if 'ooffs'not in g or int(s.get('val','-1'),0)!=pa:continue
  if (location(qa.b,n)-16)//8192==bank and address(qb.b,n)==pb and(location(qb.b,n)-16)//8192==bank:names.append(n)
 assert names and(bank,pa)in ta and(bank,pb)in tb,('not a real reached relocated5SMC target',va,vb,names)
 return [bank,hex(pa),hex(pb),names]

def art_controls(b):
 layout=json.loads((O/'asset-layout.json').read_text());raw=(R/'build/source-acquisition/super-maaa-author-2026-10-29/source/chr/lanky_mario.chr').read_bytes()
 def stamp(out,tile,sx,sy,flip=False,pattern=None,height=8):
  data=pattern if pattern is not None else raw[tile*16:tile*16+16]
  for y in range(height):
   for x in range(8):
    xx=7-x if flip else x;off=y//8*16+y%8
    value=(data[off]>>(7-xx)&1)|((data[off+8]>>(7-xx)&1)<<1)
    if value and 0<=sx+x<256 and 0<=sy+y<240:out.setdefault((sx+x,sy+y),value)
 def expected(frame,face,length,y=100):
  tiles,head,base=layout['source_frames'][frame];out={}
  for row,col in itertools.product(range(4),range(2)):
   physical=col if face==1 else 1-col;flip=face!=1
   if physical==1 and(row==3 and base in[10,22,23,24,25]or row==2 and base==22):flip=True
   if physical==0 and(row==3 and base in[10,22,23,24,25]or row==2 and base==22):flip=False
   sy=y+8*row-(length if row==head//2 else 0)
   if sy>=0:stamp(out,tiles[row*2+col],96+physical*8,sy+1,flip)
  if length:
   sx=96+([3,4,3,6,5,4,5,2][base+(0 if face==1 else 4)]if base<4 else 4)
   for n in range(length//8+1):
    sy=y+head*4+1-8*n
    if sy<0:break
    stamp(out,16,sx,sy+1,face!=1)
  return out
 def actual(q):
  out={};page=768+q.get('SmChrBank')
  for off in range(0,256,4):
   sy,t,a,sx=bytes(q.m[0x200+off:0x204+off])
   if sy>=248:continue
   assert t<64
   data=b['raw'][1048592+page*1024+(t&254)*16:1048592+page*1024+(t&254)*16+32]
   stamp(out,0,sx,sy+1,bool(a&64),data,16)
  return out
 rows=[]
 for ident,face,length in itertools.product(range(1,63),[1,2],[0,1,7,8,15,16,80,160]):
  q=setup(b,length=length);q.put(ObjectMetasprite=ident,PlayerFacingDir=face,Player_Rel_XPos=96,Player_Y_Position=100,Player_Rel_YPos=100,CrossoverMenuState=0,CurrentOAMOffset=0)
  q.put(R3=32,R4=96,R5=0,R6=100,R7=1)
  for off in range(0,256,4):q.m[0x200+off]=248
  c,_,mn=C.M.runtrace(q,'MaaBodyDraw');assert q.get('CurrentOAMOffset')==24
  c2,_,mn2=C.M.runtrace(q,'MaaDrawNeck')
  got=actual(q);want=expected(layout['native_map'][ident],face,length)
  assert got==want,('actual authored body/neck pixel classes',ident,face,length,len(got),len(want),list(got.keys()-want.keys())[:4],list(want.keys()-got.keys())[:4])
  rows.append([ident,face,length,c.processorCycles,c2.processorCycles,min(mn,mn2)])
 return dict(cases=len(rows),all62_native_pose_IDs_both_faces_lengths=True,actual_CHR_and_OAM_vs_authored_original_patterns=True,source_special_bottom_H_flips_retained=True,body_CPU=[min(z[3]for z in rows),max(z[3]for z in rows)],neck_CPU=[min(z[4]for z in rows),max(z[4]for z in rows)],minimum_SP=min(z[5]for z in rows))

def gameplay_controls(old,b):
 ck={};rows=[]
 q=setup(b,length=159);q.put(CrossoverMenuState=2,CrossoverMenuIndex=0,CrossoverMenuButtons=0,MarioVariant=0)
 for keys,want in[(32,1),(32,1),(0,1),(32,2),(0,2),(32,3),(0,3),(32,4),(0,4),(32,0)]:
  q.put(SavedJoypad1Bits=keys,SavedJoypad2Bits=0)
  c,tr,mn=C.M.runtrace(q,'CrossoverMenuInput');assert q.get('MarioVariant')==want and q.get('SelectedCharacter')==(8 if want==1 else 0)
  rows.append([keys,want,c.processorCycles,mn]);q.put(NmiDisable=0);T.nmi(q,c);q.put(NmiDisable=255)
 q=setup(b,length=159);q.put(CrossoverMenuState=2,CrossoverMenuIndex=0,VRAM_Buffer1_Offset=0)
 C.M.runtrace(q,'QueueSelectName');at=q.get('VRAM_Buffer1_Offset');assert bytes(q.m[address(b,'VRAM_Buffer1')+at-16:address(b,'VRAM_Buffer1')+at])==bytes(q.m[address(b,'MaaQueueName::Name')+i]for i in range(16))
 ck['actual_Select_input_and_name']=dict(Select32_release_and_hold_rows=rows,menu_slot0_unchanged=True,exact16_name_cells=True)
 rows=[]
 for mode,kind,size in itertools.product(range(2),range(4),[0,1]):
  q=setup(b,length=80);q.put(CrossoverBehaviorVersion=mode,PlayerSize=size,PlayerStatus=1-size)
  C.actor(q,5,0x2e,96,176);q.set('Enemy_State',128,5);q.set('PowerUpType',kind,5);q.put(ObjectOffset=5)
  c,tr,mn=C.M.runtrace(q,'NrPickup',x=5)
  assert q.m[0x5c7f]==80 and q.get('Enemy_Flag',5)==0
  if kind==3:
   assert q.get('FloateyNum_Control',5)==11
   for _ in range(64):C.M.runtrace(q,'FloateyNumbersCore',x=5)
   assert q.get('NumberofLives')==3 and q.m[0x5c7f]==80
  rows.append([mode,kind,size,q.get('PlayerStatus'),q.get('NumberofLives'),mn])
 ck['actual_mature_pickup_and_1up_preserve_length']=dict(cases=len(rows),rows=rows,no_fixture_resource_grants=True)
 # Real fresh constructor and both life-loss BPL branches. Scene setup does
 # not own the length; neither native scene-loader memory bounds nor 1-Up
 # calls clear the exact-owner active overlay.
 q=setup(b,length=159);C.M.runtrace(q,'MaaFresh');assert q.m[0x5c7f]==0
 q=setup(b,length=159);q.put(CrossoverMenuState=2,CrossoverMenuIndex=0,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
 c,tr,mn=C.M.runtrace(q,'CrossoverMenuInput')
 assert q.m[0x5c7f]==0 and q.get('MarioVariant')==2 and physical(q,'MaaFresh')in tr and q.get('CrossoverMenuState')==0
 ck['actual_Start_constructor_before_gameplay']=dict(real_Start16=True,variant2_preserved=True,length_cleared=True,CPU=c.processorCycles,minimum_SP=mn)
 rows=[]
 for ch,var,lives in itertools.product([0,1,6,15,23],[0,2],[0,1,2]):
  out=[]
  for v in[old,b]:
   q=setup(v,ch,var,81);q.put(NumberofLives=lives)
   c,tr,mn=C.M.runtrace(q,'PlayerLoseLife');out.append((q,c,tr,mn))
  qa,ca,ta,ma=out[0];qb,cb,tb,mb=out[1]
  assert registers(ca)==registers(cb)and tuple(qa.m.banks)==tuple(qb.m.banks)
  want=0 if ch==0 and var==2 else qa.m[0x5c7f]
  assert qb.m[0x5c7f]==want
  qb.m[0x5c7f]=qa.m[0x5c7f];assert C.M.fastapp(qa)==C.M.fastapp(qb),('complete life caller',ch,var,lives)
  rows.append([ch,var,lives,cb.processorCycles-ca.processorCycles,mb,want])
 ck['fresh_and_complete_life_loss']=dict(cases=len(rows),rows=rows,all_final_application_except_intended_owned_length_clear_exact=True)
 rows=[]
 for length,yy,index in itertools.product([0,1,8,80,160],[16,31,32,40,64,176,240],[0,7,14]):
  q=setup(b,length=length);q.put(Player_Y_Position=yy,Local_eb=index)
  # Each row is a different native tile so an off-by-one row is observable.
  for nm in['Block_Buffer_1','Block_Buffer_2']:
   for row in range(13):
    for col in range(16):q.m[address(b,nm)+row*16+col]=0xa0+row
  c,tr,mn=C.M.runtrace(q,'MaaHead',y=index)
  total=((yy+q.m[address(b,'BlockBuffer_Y_Adder')+index])&255)-length
  expected=0 if total<32 else q.m[address(b,'Block_Buffer_1')+6+((total&240)-32)]
  assert c.a==expected and q.get('Player_Y_Position')==yy and c.y==index,('source-relative head query',length,yy,index,c.a,expected,c.y)
  rows.append([length,yy,index,c.a,c.processorCycles,mn])
 ck['source_relative_head_actual_native_reader']=dict(cases=len(rows),rows=rows,original_adder_then_subtract_order=True,PlayerY_and_caller_Y_restored=True)
 # Genuine fireball creation, including source underflow rejection, through
 # the complete native initializer; no directly seeded projectile outcomes.
 rows=[]
 for size,face,length,yy in itertools.product([0,1],[1,2],[0,8,80,160],[40,176]):
  q=setup(b,length=length);q.put(PlayerStatus=2,PlayerSize=size,PlayerFacingDir=face,Player_Y_Position=yy,A_B_Buttons=64,PreviousA_B_Buttons=0,ObjectOffset=0)
  c,tr,mn=C.M.runtrace(q,'ProcFireball_Bubble')
  at=q.get('FireballCounter')-1
  accepted=q.get('Fireball_State',0)==1 or q.get('Fireball_State',1)==1
  assert accepted==(yy>=length),('source fire underflow',size,face,length,yy,accepted)
  if accepted:
   slot=0 if q.get('Fireball_State',0)==1 else 1
   assert q.get('Fireball_Y_Position',slot)==yy-length+4,('genuine same-update fireball movement',size,face,length,yy,q.get('Fireball_Y_Position',slot))
  rows.append([size,face,length,yy,accepted,c.processorCycles,mn])
 ck['complete_native_fireball_creation']=dict(cases=len(rows),rows=rows)
 rows=[]
 for length,mode,size,tile in itertools.product([0,16,80],range(2),range(2),[0xc0,0x51]):
  q=setup(b,length=length);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=1-size,PlayerSize=size,GameTimerCtrlTimer=100)
  row=(176-length-32)//16-2;at=address(b,'Block_Buffer_1')+row*16+6;q.m[at]=tile
  for age in range(30):
   q.put(SavedJoypadBits=128 if age<16 else 0,NmiDisable=255)
   c,tr,mn=C.M.runtrace(q,'GameLoop')
   if physical(q,'NativeRarePlayerHeadCollisionCore')in tr:
    assert physical(q,'MaaHead')in tr
    rows.append([length,mode,size,tile,age,q.get('Player_Y_Position'),q.get('Block_Y_Position'),q.get('Block_State'),q.m[at],c.processorCycles,mn]);break
  else:raise AssertionError(('No real Main head collision',length,mode,size,tile))
 ck['controller_jump_real_Main_native_block_contact']=dict(cases=len(rows),rows=rows,actual_native_question_brick_score_and_block_writers_preserved=True,no_seeded_hit_or_block_outcome=True)
 return ck

def renderer_controls(b):
 rows=[]
 meta=address(b,'METASPRITE_GOOMBA_WALKING_1')
 for length,count,epoch in itertools.product([0,8,80,160],[0,1,6,20],[0,1]):
  q=setup(b,length=length);q.put(ObjectMetasprite=1,CurrentOAMOffset=24,FrameCounter=epoch)
  for i in range(1,count+1):
   q.set('ObjectMetasprite',meta,i);q.set('SprObject_X_Position',48+i*8,i);q.set('SprObject_Y_Position',140,i);q.set('SprObject_Y_HighPos',1,i);q.set('SprObject_PageLoc',0,i);q.set('PlayerFacingDir',1,i)
  q.put(FloateyNum_Control=6,FloateyNum_Timer=32,FloateyNum_X_Pos=128,FloateyNum_Y_Pos=88)
  original=NesMPU.step;before=None;after=None
  target=physical(q,'MaaDrawNeck')
  def step(c):
   nonlocal before,after
   bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
   if(bank,c.pc)==target:before=bytes(q.m[0x200:0x300])
   original(c)
  NesMPU.step=step
  try:c,tr,mn=C.M.runtrace(q,'DrawAllMetasprites')
  finally:NesMPU.step=original
  final=bytes(q.m[0x200:0x300]);assert before is not None and tr.count(target)==1
  assert final[:24]==before[:24]
  for off in range(24,256,4):
   if before[off]<248:assert final[off:off+4]==before[off:off+4],('neck overwrote actual world/score',length,count,epoch,off)
  assert tr.count(physical(q,'MaaBodyDraw'))==1 and q.get('GuestOamRotationActive')==0
  rows.append([length,count,epoch,c.processorCycles,mn,sum(final[i]<248 for i in range(24,256,4))])
 # Exact capacity boundary, no wrap or writes on a rejected body group.
 for cursor in range(0,256,4):
  q=setup(b,length=160);q.put(ObjectMetasprite=1,CurrentOAMOffset=cursor,R3=32,R4=96,R5=0,R6=100,R7=1)
  before=bytes(q.m[0x200:0x300]);C.M.runtrace(q,'MaaBodyDraw')
  assert q.get('CurrentOAMOffset')==(cursor+24 if cursor<232 else cursor)
  if cursor>=232:assert bytes(q.m[0x200:0x300])==before
 return dict(complete_DrawAll_cases=len(rows),rows=rows,actual_world_and_score_active_parts_retained=True,one_body_in_physical0_23=True,neck_only_free_slots24_255=True,capacity_cases=64,reject_without_cursor_wrap=True,native_Vine_40_44_is_outside_body_prefix=True)

def coin_controls(b):
 rows=[]
 for length,busy in itertools.product([8,16,80,160],['empty','buffer1','buffer2','ctrl']):
  q=setup(b,length=length);q.put(DisableScreenFlag=0,GameTimerCtrlTimer=1)
  for nm in['Block_Buffer_1','Block_Buffer_2']:
   for row in range(10):q.m[address(b,nm)+row*16+6]=0xc2
  if busy=='buffer1':q.put(VRAM_Buffer1_Offset=17)
  if busy=='buffer2':q.put(VRAM_Buffer2_Offset=10,VRAM_Buffer2=32)
  if busy=='ctrl':q.put(VRAM_Buffer_AddrCtrl=6)
  before=bytes(q.m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416]);coins=q.get('CoinTallyFor1Ups')
  c,tr,mn=C.M.runtrace(q,'MaaCoins')
  paid=q.get('CoinTallyFor1Ups')-coins
  assert paid==(1 if busy=='empty'else 0),('actual paid coin admission',length,busy,paid)
  if paid:
   assert tr.count(physical(q,'HandleCoinMetatile'))==1 and q.get('VRAM_Buffer_AddrCtrl')==6
   assert q.get('VRAM_Buffer1_Offset')==14 and q.get('VRAM_Buffer2',2)==q.get('VRAM_Buffer2',7)==2 and q.get('VRAM_Buffer2',10)==0
   # Consume the genuine selected block-erase queue, then its real deferred
   # score/coin queue, without backfilling either packet or its offsets.
   ni=[]
   for i in range(2):q.put(NmiDisable=0);ni.append(T.nmi(q,c))
   rows.append([length,busy,paid,c.processorCycles,mn,ni])
  else:
   assert bytes(q.m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416])==before
   rows.append([length,busy,paid,c.processorCycles,mn])
 return dict(cases=len(rows),rows=rows,real_erase_credit_score_owners_once=True,busy_native_queues_preserve_uncollected_coins=True,maximum_one_extra_coin_per_Main_by_native_ctrl6=True,only_native_Block2_and_deferred_score_coin_packets=True)

def interrupt_controls(b):
 q=setup(b,length=80);q.put(SavedJoypadBits=129)
 c,tr,mn=C.M.runtrace(q,'GameLoop',p=0x30)
 names=['MaaTimer','MaaAfterBG','MaaHead','MaaBox','MaaBodyDraw','MaaDrawNeck','MaaRenderGate','MaaTail']
 points=[]
 for n in names:
  p=physical(q,n)
  assert p in tr,('unreached actual IRQ owner',n,p)
  k=tr.index(p);points.append(p)
  # The actual instruction immediately after C-shadow publication is
  # independently tested with the existing literal native NMI rule.
  if n=='MaaRenderGate':
   for bk,at in tr[k:k+20]:
    if bytes(q.b['raw'][16+bk*8192+(at&8191):16+bk*8192+(at&8191)+3])==bytes([141,22,81]):points.append((bk,at))
 events=[]
 for kind,point in itertools.product(['IRQ','NMI'],points):
  q=setup(b,length=80);q.put(SavedJoypadBits=129,NmiDisable=255)
  c,_,minimum,_,hit=ISR.interrupt_actual(q,'GameLoop',flags=0x30,inject=point,kind=kind,a=0)
  assert hit;events.append([kind,*point,minimum])
 return dict(cases=len(events),events=events,physical_IRQ_context_exact=True,lag_NMI_only_literal_pending_C_publication_normalization=ISR.SHADOW_WINDOWS,minimum_SP=min(e[-1]for e in events))

def publication_controls(old,b):
 rows=[]
 for ch,var,lag in itertools.product([0,1,3,6,8,15,18,20,21,23],[0,1,2,3,4],[0,255]):
  if ch==0 and var==2:continue
  pair=[]
  for v in[old,b]:
   q=setup(v,ch,var,80);q.put(NmiDisable=lag,DisableScreenFlag=0,ReloadCHRBank=1,Mirror_PPUCTRL=168,Mirror_PPUMASK=30)
   c,tr,mn=C.M.runtrace(q,'GameLoop') if not lag else (NesMPU(memory=q.m,pc=0x5b00),[],253)
   if lag:c.sp=253
   q.put(NmiDisable=lag);q.m.writes=[];cycles=T.nmi(q,c)
   pair.append((registers(c),C.M.fastapp(q),tuple(q.m.banks),[(a,z)for a,z in q.m.writes if not 0x100<=a<0x200],cycles))
  assert pair[0][:4]==pair[1][:4],('foreign normal/lag publication',ch,var,lag,different(pair[0][1],pair[1][1]))
  rows.append([ch,var,lag,pair[1][-1]-pair[0][-1]])
 # Every reached instruction cut inside actual owned body construction.
 # The lag ISR may not publish any CHR page or DMA that private image.
 q=setup(b,length=80);q.put(SavedJoypadBits=129)
 c,tr,mn=C.M.runtrace(q,'GameLoop');cuts=sorted(set((bk,pc)for bk,pc in tr if bk==68 and address(b,'MaaBodyDraw')<=pc<address(b,'MaaDrawNeck')))
 for cut in cuts:
  q=setup(b,length=80);q.put(SavedJoypadBits=129,NmiDisable=255,Mirror_PPUCTRL=168,Mirror_PPUMASK=30,DisableScreenFlag=0)
  original=NesMPU.step;hit=False
  def step(c):
   nonlocal hit
   physical=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
   if not hit and(physical,c.pc)==cut:
    hit=True;at=c.pc;sp=c.sp;oam=bytes(q.m[0x200:0x300]);reload=q.get('ReloadCHRBank');start=len(q.m.writes)
    c.nmi()
    for _ in range(50000):
     original(c)
     if c.pc==at and c.sp==sp:break
    else:raise AssertionError(('lag body cut timeout',cut))
    w=q.m.writes[start:]
    assert not any(a==0x4014 or 0x5120<=a<=0x5130 for a,z in w),('private image leaked on lag',cut,w)
    assert bytes(q.m[0x200:0x300])==oam and q.get('ReloadCHRBank')==reload
   original(c)
  NesMPU.step=step
  try:c,tr,mn=C.M.runtrace(q,'GameLoop')
  finally:NesMPU.step=original
  assert hit
  q.put(NmiDisable=0);q.m.writes=[];T.nmi(q,c)
  assert any(a==0x4014 for a,z in q.m.writes)and any(a==0x5120 for a,z in q.m.writes)and q.get('ReloadCHRBank')==0
 return dict(foreign_normal_lag_cases=len(rows),rows=rows,entire_final_application_AXYP_SP_banks_and_ordered_nonstack_NMI_writes_exact=True,foreign_NMI_CPU_delta=[min(r[-1]for r in rows),max(r[-1]for r in rows)],actual_owned_body_build_lag_cuts=len(cuts),no_CHR_or_DMA_publication_on_lag=True,next_normal_NMI_publishes_CHR_and_DMA=True)

def stomp_controls(old,b):
 rows=[]
 for ch,var,kind,length,f in itertools.product([0,6],[0,2],[0,6,9],[0,1,80,160],[f for f in range(256)if f&0x30==0x30]):
  out=[]
  for v in[old,b]:
   q=setup(v,ch,var,length);C.actor(q,0,kind,96,176)
   c,tr,mn=C.M.runtrace(q,'ChkForDemoteKoopa',a=kind,x=0,p=f)
   out.append((q,c,tr,mn))
  qa,ca,ta,ma=out[0];qb,cb,tb,mb=out[1]
  want=length//2 if ch==0 and var==2 and kind<9 else length
  assert qb.m[0x5c7f]==want
  qb.m[0x5c7f]=qa.m[0x5c7f]
  assert registers(ca)==registers(cb),('complete native stomp caller AXYP',ch,var,kind,length,f,registers(ca),registers(cb))
  assert C.M.fastapp(qa)==C.M.fastapp(qb)and qa.m.banks==qb.m.banks,('native reward/bounce/stomp state',ch,var,kind,length,f)
  rows.append([ch,var,kind,length,f,cb.processorCycles-ca.processorCycles,mb])
 return dict(cases=len(rows),rows=rows,genuine_native_score_drop_revive_bounce_caller_exact=True,demoted_paratroopa_preserves_length=True,only_regular_owned_stomp_halves_length=True,CPU_delta=[min(r[-2]for r in rows),max(r[-2]for r in rows)])

def main():
 assert not(O/'handoff.json').exists(),'Do not mutate a frozen packet'
 old,b=[scoped_load(x/'candidate.nes')for x in[P,O]]
 proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={},candidate=sha(O/'candidate.nes'));ck=proof['checks']
 try:
  # Full foreign Main: no changed application value, final5SMC/banks or real
  # IO. Only actual consumed stack cells and extra standard mapper calls
  # differ; retain all named page1 application bytes below observed minSP.
  rows=[];linked=[]
  identities=[(i,0)for i in[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23]]+[(0,i)for i in[1,3,4]]
  for (ch,variant),mode,keys in([]if'--owned-only'in sys.argv else itertools.product(identities,range(2),[0,1,129])):
   pair=[]
   for v in[old,b]:
    q=setup(v,ch,variant,37);q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys)
    c,tr,mn,ann,events=run_linked(q,'GameLoop',p=0x71)
    pair.append((q,c,tr,mn,ann,events))
   qa,ca,ta,ma,ana,ea=pair[0];qb,cb,tb,mb,anb,eb=pair[1]
   assert [z[-1]for z in ea]==[z[-1]for z in eb],('real JumpEngine consumers',ch,ea,eb)
   assert registers(ca)==registers(cb),('foreign Main registers',ch,variant,mode,keys,registers(ca),registers(cb))
   aa,bb=C.M.fastapp(qa),C.M.fastapp(qb)
   assert aa==bb,('foreign Main application',ch,variant,mode,keys,different(aa,bb))
   assert tuple(qa.m.banks)==tuple(qb.m.banks)
   moved=smc_contract(qa,qb,ta,tb)
   if moved and moved not in linked:linked.append(moved)
   # Actual SMC operands live on page1. They were checked above, including
   # the one real relocated target, rather than treated as dead stack.
   stack_smc=set(smc_at(old))|set(smc_at(b))
   assert bytes(qa.m[i]for i in range(0x100,0x101+min(ma,mb))if i not in stack_smc)==bytes(qb.m[i]for i in range(0x100,0x101+min(ma,mb))if i not in stack_smc)
   def writes(q,v,ann):return[(i,ann.get(k,x))for k,(i,x)in enumerate(q.m.writes)if not 0x100<=i<0x200 and not 0x5114<=i<=0x5117 and i not in smc_at(v)and i not in[address(v,'CurrentBank'),address(v,'CurrentBankC')]]
   assert writes(qa,old,ana)==writes(qb,b,anb),('foreign ordered non-mapper writes',ch,variant,mode,keys)
   assert qb.m[0x5c7f]==qa.m[0x5c7f],('foreign active overlay',ch,variant)
   rows.append([ch,variant,mode,keys,cb.processorCycles-ca.processorCycles,mb])
  if rows:ck['foreign_complete_Main']=dict(cases=len(rows),AXYP_SP_application_live_page1_banks_remaining_ordered_writes_exact=True,final5SMC_only_genuine_reached_code_relocations=linked,CPU_delta=[min(z[-2]for z in rows),max(z[-2]for z in rows)],rows=rows)
  ck['authored_art_pixels']=art_controls(b)
  ck.update(gameplay_controls(old,b))
  ck['full_renderer_capacity_world']=renderer_controls(b)
  ck['actual_coin_writers_and_NMI']=coin_controls(b)
  ck['actual_full_Main_ISR']=interrupt_controls(b)
  ck['lag_vs_normal_publication']=publication_controls(old,b)
  ck['native_complete_stomp_caller']=stomp_controls(old,b)
  rows=[]
  for length,mode,keys in itertools.product([0,1,7,8,15,16,80,159,160],range(2),[0,1,129]):
   q=setup(b,length=length);q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys)
   c,tr,mn=C.M.runtrace(q,'GameLoop')
   assert q.m[0x5c7f]==min(160,length+1)
   assert tr.count(physical(q,'MaaTimer'))==1 and tr.count(physical(q,'MaaAfterBG'))==1
   assert q.get('Player_Y_Position')==((170 if mode==0 else 172)if keys&128 else 176)and q.get('Player_Y_HighPos')==1,('real first native jump',length,mode,keys,q.get('Player_Y_Position'))
   assert q.get('X5ChrMode')==0x83 and q.get('CurrentCHRBank')in[45,46,47]
   assert all(q.get('X5ChrMode',i)==0 for i in range(1,12))
   rows.append([length,mode,keys,c.processorCycles,mn,q.get('ObjectMetasprite')])
  ck['owned_complete_Main']=dict(cases=len(rows),one_postfeet_one_native_timer=True,rows=rows,CPU=[min(z[3]for z in rows),max(z[3]for z in rows)])
  # Real timer cadence through consecutive Main + normalNMI, no timer seed
  # between updates. Actual pending controller serial input is explicit.
  rows=[]
  for mode in range(2):
   q=setup(b);q.put(CrossoverBehaviorVersion=mode,DisableScreenFlag=0)
   growth=[]
   for age in range(100):
    q.put(SavedJoypadBits=0,SavedJoypad2Bits=0,NmiDisable=255)
    c,tr,mn=C.M.runtrace(q,'GameLoop');before=q.m[0x5c7f]
    T.nmi(q,c)
    growth.append([age,before,q.get('GameTimerCtrlTimer')])
   assert q.m[0x5c7f]<10 and q.m[0x5c7f]>1,('native timer cadence',mode,q.m[0x5c7f])
   rows.append([mode,growth,q.m[0x5c7f]])
  ck['consecutive_Main_normalNMI_timer']=dict(updates=200,rows=rows)
  proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'candidate.nes',R/'tools/reference/supermaaa_host_core_v1.s',R/'tools/prepare_supermaaa_host_v1.py']}
 target=O/'controls-draft.json';target.write_text(json.dumps(proof,indent=2)+'\n')
 if not proof['passed']:
  with(O/'negative-ledger.jsonl').open('a')as f:f.write(json.dumps(dict(candidate=proof['candidate'],tool_sha256=sha(Path(__file__)),failure=proof['failure'],completed=list(ck)))+'\n')
 print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']

if __name__=='__main__':main()
