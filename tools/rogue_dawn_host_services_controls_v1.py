"""Actual assembled A95/C94 services + immutable124 leaves in a CPU composition.

No emulator/native/PPU claim. World cells are actual SMB Block_Buffer bytes;
staged tests are explicit source controls, never acquisition/gameplay evidence.
"""
from pathlib import Path
import argparse,itertools,json,re,subprocess,sys
import prepare_rogue_dawn_host_services_v1 as build
import rogue_dawn_map_v1 as ref
import rogue_dawn_control_controls_v1 as original
ROOT=build.ROOT
sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU

def compose(out):
 code,s,b,raw=build.build(out)
 bridge=ROOT/'build/rogue-dawn-host-plan-v1'
 bs=build.labels(bridge/'bridge.lbl');bridgecode=(bridge/'bridge.bin').read_bytes()
 assert len(bridgecode)==175 and bs['RdHostBridgeStart']==0xdf50
 names=sorted(set(re.findall(r'RdHost\w+',(ROOT/'src/rogue_dawn_control.s').read_text())))
 callbacks={n:bs[n]for n in names}
 text='\n'.join(f'{n}=${v:04x}'for n,v in callbacks.items())+'\n'+(ROOT/'build/rogue-dawn-art-v1/render.s').read_text()+'.include "rogue_dawn_control.s"\n'
 (out/'linked-leaves.s').write_text(text,newline='\n')
 cfg='MEMORY { H:start=$AE00,size=$200,bank=124,file="'+str((out/'rogue-control-aux.bin').resolve()).replace('\\','/')+'"; K:start=$B000,size=$1000,bank=124,file=%O; A:start=$D300,size=$D00,bank=94,file="'+str((out/'linked-art.bin').resolve()).replace('\\','/')+'"; }\nSEGMENTS { ROGUE_DAWN_CORE:load=K,type=ro; ROGUE_DAWN_ART:load=A,type=ro; ROGUE_DAWN_CONTROL_AUX:load=H,type=ro; }\n'
 (out/'linked-leaves.cfg').write_text(cfg)
 cc=ROOT/'tools/Windows/cc65/bin'
 for cmd in [[str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(out/'linked-leaves.s'),'-o',str(out/'linked-leaves.o')],
  [str(cc/'ld65.exe'),'-C',str(out/'linked-leaves.cfg'),'-o',str(out/'linked-leaves.bin'),'-Ln',str(out/'linked-leaves.lbl'),'--dbgfile',str(out/'linked-leaves.dbg'),str(out/'linked-leaves.o')]]:
  z=subprocess.run(cmd,capture_output=True,text=True)
  assert z.returncode==0,z.stdout+z.stderr
 ls=build.labels(out/'linked-leaves.lbl')
 for macro,name in [('RD_LEAF_RENDER_PLAYER','RdRenderPlayer'),('RD_LEAF_ADD_MISSILE_TANK','RdAddMissileTank'),('RD_LEAF_DAMAGE_COMPLETE','RdControlDamageComplete')]:assert s[macro]==ls[name]
 image=bytearray(b['raw']);placements=[]
 for bank,pc,data,why in [(95,0xa600,code,'new services/frozen helpers'),(94,0xdf50,bridgecode,'frozen bridge'),(124,0xb000,(out/'linked-leaves.bin').read_bytes(),'frozen leaf source; real bridge relocations'),(124,0xae00,(out/'rogue-control-aux.bin').read_bytes(),'frozen AUX source; real bridge relocations'),(94,0xd300,(out/'linked-art.bin').read_bytes(),'frozen exact art')]:
  at=16+bank*8192+(pc&8191);assert image[at:at+len(data)]==b'\xff'*len(data),(bank,hex(pc))
  image[at:at+len(data)]=data;placements.append(dict(bank=bank,start=f'{pc:04X}',bytes=len(data),role=why,sha256=ref.digest(data)))
 assert (out/'linked-leaves.bin').read_bytes()[:2293]==(ROOT/'build/rogue-dawn-art-v1/render.bin').read_bytes()
 assert (out/'linked-art.bin').read_bytes()==(ROOT/'build/rogue-dawn-control-v1/art.bin').read_bytes()
 return dict(b,raw=bytes(image)),dict(s,**ls),callbacks,raw,placements

class TracedMemory(Memory):
 def __init__(self,b):super().__init__(b);self.reads=set()
 def __getitem__(self,k):
  if isinstance(k,int):self.reads.add(k)
  return super().__getitem__(k)

def arena(b,s):
 m=TracedMemory(b);m.page(1,95);m.page(2,94)
 for n,v in [('SelectedCharacter',2),('CurrentBank',223),('CurrentBankC',222),('Player_Y_HighPos',1),('ScreenLeft_PageLoc',0),('ScreenRight_PageLoc',1),('DisableScreenFlag',1),('OperMode',1),('GameEngineSubroutine',8),('Sprite0HitDetectFlag',0)]:m[address(b,n)]=v
 m[0x5fee]=1
 return m

def invoke(m,pc,a=0,x=0,y=0,p=0x71,sp=0xc0,seam=None):
 if seam:
  # REAL pinned driver initialization precedes the test caller. A zeroed
  # SmAudioBank falsely executes bank0 gameplay as an audio entrypoint.
  invoke(m,address(m.bundle,'AudioInit'),sp=0xf0)
  invoke(m,address(m.bundle,'SamusAudioInit'),sp=0xf0)
  m[address(m.bundle,'AreaMusicQueue')]=1
  m[address(m.bundle,'NmiDisable')]=0 if seam[2]=='NMI'else 255
 c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,sp;c.stPushWord(0x5aff)
 for i in range(sp+1,256):m[0x100+i]=(i*17+29)&255
 live=bytes(m[0x101+sp:0x200]);m.writes.clear();m.reads.clear();low=c.sp;trace=[];fired=False
 smc=[address(m.bundle,n)+k for n,k in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
 def snap():return(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(m.banks),m[address(m.bundle,'CurrentBank')],m[address(m.bundle,'CurrentBankC')],bytes(m[z]for z in smc),bytes(m[0x101+c.sp:0x200]),bytes(m[0x5c00:0x5c80]),bytes(m[0x5fb0:0x5fb8]))
 for _ in range(100000):
  if c.pc==0x5b00:break
  if seam and not fired and(c.pc,m.banks[1])==seam[:2]:
   fired=True;before=snap();kind=seam[2];want=list(m.banks)
   if kind!='IRQ'and m.banks[1]!=(m[address(m.bundle,'CurrentBank')]&127):
    assert bytes(m[c.pc:c.pc+3])==bytes.fromhex('8d1551');want[1]=m[address(m.bundle,'CurrentBank')]&127
   if kind=='IRQ':c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(m.bundle,'IrqScrollSplit')
   else:
    if kind=='lagNMI':m[address(m.bundle,'NmiDisable')]=255
    c.nmi()
   for _ in range(50000):
    low=min(low,c.sp);c.step()
    if c.pc==before[5]and c.sp==before[4]:break
   else:raise AssertionError(('ISR timeout',seam,hex(c.pc)))
   after=snap();assert after[:6]==before[:6]and after[6]==tuple(want)and after[7:]==before[7:],('ISR context',seam,before,after)
  trace.append((c.pc,m.banks[1]));assert m[c.pc]!=0,('BRK',hex(c.pc),m.banks)
  if hasattr(m,'morph_watch')and(c.pc,m.banks[1])==(m.morph_watch[0],124):m.morph_watch[1].append(dict(X=c.x,frame=m[0x5c03],facing=m[0x5c2c],action=m[0x5c00]))
  c.step();low=min(low,c.sp)
 else:raise AssertionError(('timeout',hex(c.pc),m.banks))
 assert c.sp==sp and bytes(m[0x101+sp:0x200])==live,('caller stack',c.sp,sp)
 assert low>=0x7b,('live SMCCODE stack collision',low)
 assert not seam or fired,('seam never reached',seam)
 return c,low,trace

def put(m,b,**kw):
 for n,v in kw.items():m[address(b,n)]=v
def read(m,b,n,i=0):return m[address(b,n)+i]
def call(m,s,name,**kw):return invoke(m,s[name],**kw)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/rogue-dawn-host-services-v1/controls.json');a=p.parse_args();b,s,cb,raw,placements=compose(a.output.parent)
 rows={};costs={};minimum=255
 # Every service foreign dispatch, no global overlay read/write. Exact-ID gate
 # must precede even service-ID read, not merely protect writes afterward.
 owned=set(range(0x5c00,0x5c80))|set(range(0x5fb0,0x5fb8));foreign=0
 publics=['RdHostDispatch','RdHsNewSession','RdHsNewLife','RdHsEnterScene','RdHsImportPosition','RdHsExportPosition','RdHsDamage','RdHsGrantType','RdHsRewardForRaw','RdHsPrepareActor','RdHsCollectActor','RdHsDropContact','RdHsActorEligible','RdHsActorContact','RdHsClockBefore','RdHsClockAfter']
 for char,var,name in itertools.product([0,1,2,3,20,21,23,255],[0,1,2,255],publics):
  if(char,var)==(2,1):continue
  m=arena(b,s);put(m,b,SelectedCharacter=char);m[0x5fee]=var
  c,low,_=call(m,s,name,a=0x5a,x=4,y=0xe0,p=0x71)
  assert not m.reads&owned and not any(k in owned for k,_ in m.writes),(char,var,name)
  assert not c.p&1;foreign+=1
 rows['foreign_no_overlay_read_write']=foreign
 # Source-derived BCD debit including suit rounding, nonlethal+death, complete
 # REAL post-debit continuation and its sound/action reset in frozen leaf124.
 damage=[]
 for hp,hi,amount,amount_hi,suit in itertools.product([0x01,0x50,0x99],[0,9,0x19],[0x01,0x10,0x99],[0,1],[0,32]):
  n=original.art.Memory(ref.cpu_image(raw,lower_bank=2));n[0x106],n[0x107],n[0x6e],n[0x6f],n[0x6878]=hp,hi,amount,amount_hi,suit;n[0x300]=0
  q=NesMPU(memory=n,pc=0xceac);q.sp=0xc0;q.stPushWord(0x5aff)
  for _ in range(10000):
   if q.pc==0x5b00:break
   assert n[q.pc]!=0,(hex(q.pc),hp,hi,amount)
   q.step()
  else:raise AssertionError('source damage timeout')
  m=arena(b,s);m[0x5fb0],m[0x5fb4],m[0x5fb5]=suit,hp,hi
  c,low,_=call(m,s,'RdHsDamage',a=amount,y=amount_hi);minimum=min(minimum,low)
  assert [m[0x5fb4],m[0x5fb5],m[0x5c00]]==[n[0x106],n[0x107],n[0x300]],('BCD',hp,hi,amount,amount_hi,suit,[m[0x5fb4],m[0x5fb5],m[0x5c00]],[n[0x106],n[0x107],n[0x300]])
  assert m[s['Rh6']]==m[s['Rh7']]==0 and c.p&1
  damage.append(c.processorCycles)
 rows['complete_source_BCD_damage']=len(damage);costs['damage_CPU']=[min(damage),max(damage)]
 # Complete typed native gear/tank commits versus REAL source61 item arithmetic.
 grants=0;selectors=0
 for gear,item in itertools.product(range(256),range(10)):
  m=arena(b,s);m[0x5fb0]=gear;m[0x5fb1]=253;m[0x5fb2]=254;m[0x5fb3]=2;m[0x5fb4]=0x23;m[0x5fb5]=0x10
  c,low,_=call(m,s,'RdHsGrantType',a=item);minimum=min(minimum,low)
  assert c.p&1
  assert m[0x5c24]==0x40 and m[0x5c23]==0,'Authentic CBF9/CBFF request channel4'
  expect=gear|(1<<item)if item<8 else gear
  assert m[0x5fb0]==expect and m[0x5fb6]==0
  if item==8:assert [m[0x5fb3],m[0x5fb4],m[0x5fb5]]==[3,0x99,0x39]
  if item==9:assert [m[0x5fb1],m[0x5fb2]]==[255,255]
  grants+=1
 for tanks,stock,maxstock,item in itertools.product(range(7),[0,1,250,255],[0,5,250,255],[8,9]):
  m=arena(b,s);m[0x5fb1:0x5fb6]=bytes([stock,maxstock,tanks,0x55,0])
  call(m,s,'RdHsGrantType',a=item)
  if item==8:assert [m[0x5fb3],m[0x5fb4],m[0x5fb5]]==[min(6,tanks+1),0x99,(min(6,tanks+1)<<4)|9]
  else:assert [m[0x5fb1],m[0x5fb2]]==[min(255,stock+5),min(255,maxstock+5)]
  grants+=1
 for gear,missiles,rawtype in itertools.product(range(256),[0,5],[0,1,2,255]):
  m=arena(b,s);m[0x5fb0]=gear;m[0x5fb2]=missiles;before=bytes(m[0x5fb0:0x5fb8]);c,_,_=call(m,s,'RdHsRewardForRaw',a=rawtype)
  assert bytes(m[0x5fb0:0x5fb8])==before
  if rawtype<2:
   expect=8 if rawtype==0 else 9 if missiles==0 else next((i for i in range(8)if not gear&(1<<i)),9)
   assert c.p&1 and c.a==expect,(gear,missiles,rawtype,c.a,expect)
  else:assert not c.p&1
  selectors+=1
 rows.update(typed_grants=grants,selectors_no_automatic_grant=selectors)
 # Indexed actual actor preparation/contact with nonuniform other-slot types.
 # No actor erasure is faked; the shared real contact caller retains that owner.
 actors=0
 for slot,state,owner,ident,flag in itertools.product(range(6),[1,16,0x80],[2,3],[0x2e,6],[1,0,0x81]):
  m=arena(b,s)
  for i in range(6):m[s['PowerUpType']+i]=i%2
  m[s['Enemy_ID']+slot]=0x2e
  c,_,_=call(m,s,'RdHsPrepareActor',x=slot);assert c.p&1
  assert m[s['InvPickup']+slot]==(0xd8 if slot%2==0 else 0xd9)
  m[s['Enemy_State']+slot]=state;m[s['InvPickupOwner']+slot]=owner;m[s['Enemy_ID']+slot]=ident;m[s['Enemy_Flag']+slot]=flag
  before=bytes(m[0x5fb0:0x5fb6]);c,_,_=call(m,s,'RdHsCollectActor',x=slot)
  ok=state==0x80 and owner==2 and ident==0x2e and flag==1
  assert bool(c.p&1)==ok
  if not ok:assert bytes(m[0x5fb0:0x5fb6])==before
  assert m[s['Enemy_Flag']+slot]==flag,'Grant cannot erase the actor early'
  actors+=1
 rows['real_slot_typed_actor_maturity_rejections']=actors
 drops=0
 for lo,hi,tanks,kind,stock,maxstock in itertools.product([0,0x50,0x99],[0,9,0x19],[0,2],[0,1],[0,250],[0,5,255]):
  m=arena(b,s);m[0x5fb4],m[0x5fb5],m[0x5fb3],m[0x5fb1],m[0x5fb2]=lo,hi,tanks,stock,maxstock
  c,_,_=call(m,s,'RdHsDropContact',a=kind);assert c.p&1
  if kind:
   assert m[0x5fb1]==min(maxstock,stock+5)
  else:
   n=original.art.Memory(ref.cpu_image(raw,lower_bank=2));n[0x106],n[0x107],n[0x6877],n[0x6e],n[0x6f]=lo,hi,tanks,0x50,0
   q=NesMPU(memory=n,pc=0xcef9);q.sp=0xc0;q.stPushWord(0x5aff)
   for _ in range(1000):
    if q.pc==0x5b00:break
    q.step()
   else:raise AssertionError('source AddHealth timeout')
   assert [m[0x5fb4],m[0x5fb5]]==[n[0x106],n[0x107]]
  drops+=1
 rows['typed_drop_resource_source_cells']=drops
 # All original page/Y anchor carry cases; import/export is once per player
 # phase. New-life refill is the explicitly approved SMB adaptation.
 lifecycle=0
 for page,x,y,high,tanks in itertools.product([0,1,15],[0,7,248,255],[0,16,239,240,255],[0,1,2],[0,3,6]):
  m=arena(b,s);put(m,b,Player_PageLoc=page,Player_X_Position=x,Player_Y_Position=y,Player_Y_HighPos=high)
  m[0x5fb6]=0xa5;m[0x5fb7]=0x5a;m[0x5fb0:0x5fb6]=bytes([0x95,7,25,tanks,1,0]);before=bytes(m[0x5fb0:0x5fb7])
  call(m,s,'RdHsImportPosition');call(m,s,'RdHsExportPosition')
  assert [read(m,b,n)for n in ['Player_PageLoc','Player_X_Position','Player_Y_Position','Player_Y_HighPos']]==[page,x,y,high]
  assert bytes(m[0x5fb0:0x5fb7])==before
  call(m,s,'RdHsNewLife')
  assert bytes(m[0x5fb0:0x5fb7])==bytes([0x95,7,25,tanks,0x99,(tanks<<4)|9,0xa5])
  lifecycle+=1
 rows['full_anchor_and_newlife_cells']=lifecycle
 actor_effects=0
 for slot,ident,state,flag,shot,action in itertools.product([0,4,5],[0,6,0x14,0x15,0x2e],[0,0x20],[0,1,0x81],[0xd0,0xe0,0xf0,0xcf],[0,1,2,3,4,9,10,11]):
  m=arena(b,s);m[s['Enemy_ID']+slot]=ident;m[s['Enemy_State']+slot]=state;m[s['Enemy_Flag']+slot]=flag;m[0x5b70+shot]=action
  enemy_before=bytes(m[s['Enemy_Flag']:s['Enemy_Flag']+6])+bytes(m[s['Enemy_State']:s['Enemy_State']+6]);c,_,_=call(m,s,'RdHsActorContact',x=slot,y=shot)
  yes=slot<5 and ident<0x15 and state!=0x20 and flag==1 and shot in[0xd0,0xe0,0xf0]and action in[1,2,3,10,11]
  assert bool(c.p&1)==yes
  if yes:assert c.a=={1:4,2:4,3:0x14,10:0x80,11:0x40}[action]
  assert bytes(m[s['Enemy_Flag']:s['Enemy_Flag']+6])+bytes(m[s['Enemy_State']:s['Enemy_State']+6])==enemy_before
  actor_effects+=1
 rows['actual_actor_eligibility_and_typed_effect_cells']=actor_effects
 # All true source frame/radius samples, floor/ceilings/pipe sides/page edges.
 attrs=b['raw'][location(b,'MTileAttribute'):location(b,'MTileAttribute')+256];solid=0x54
 assert attrs[solid]&s['MTILE_SOLID']and not attrs[solid]&s['MTILE_CLIMB']
 geometry=0;geomcost=[]
 def tileat(m,wx,y):
  if y<32 or y>=240:return 0
  pg,xx=divmod(wx,256)
  if pg<0 or pg>1:return solid
  return m[s['Block_Buffer_1'if not pg&1 else'Block_Buffer_2']+(y&240)-32+(xx>>4)]
 def blocked(m,wx,y):
  t=tileat(m,wx,y)
  return t not in [0x5f,0x60,0xc2,0xc3,0xc5]and bool(attrs[t]&s['MTILE_SOLID'])and not attrs[t]&s['MTILE_CLIMB']
 for wx,y,rx,ry,service,pflags in itertools.product([4,15,16,120,239,250,255,256,260],[48,64,95,112,160,192,224],[0,4,16],[0,8,15],[9,10,11,12,14,15,16,17],[0x30,0x71]):
  m=arena(b,s)
  # Actual two-page cell map: ground208, pipeX128..159/Y144..207,
  # ceilingY64/X0..511, blank elsewhere. No synthetic roomRAM.
  for pg in range(2):
   for ty in range(2,15):
    for tx in range(16):
     xx=pg*256+tx*16;yy=ty*16
     if yy==208 or yy==64 or 128<=xx<160 and 144<=yy<208:m[s['Block_Buffer_1'if pg==0 else'Block_Buffer_2']+(ty-2)*16+tx]=solid
  axis={9:1,10:2,11:3,12:0,14:1,15:2,16:3,17:0}[service]
  xx,yy=wx,y;xs,ys=([wx-rx,wx,wx+rx],[y-ry,y,y+ry])
  pts=[(q,y-ry-1 if axis==0 else y+ry+1)for q in xs]if axis<2 else[(wx-rx-1 if axis==2 else wx+rx+1,q)for q in ys]
  hit=any(blocked(m,*q)for q in pts)
  m[0x5c0c],m[0x5c0e],m[0x5c0d],m[0x5c02],m[0x5c01],m[0x5c79]=wx>>8,wx&255,y,rx,ry,service
  for n,v in zip(['R0','R1','R2','R3','R4','R5','R6','R7'],range(0x91,0x99)):m[s[n]]=v
  oldscratch=bytes(m[s['R0']:s['R7']+1]);c,low,_=call(m,s,'RdHostDispatch',a=0x5a,x=0x37,y=0x91,p=pflags);minimum=min(minimum,low)
  assert bool(c.p&1)==(not hit),(wx,y,rx,ry,service,pts,hit,c.p)
  if service<14 and not hit:xx+=(-1 if axis==2 else 1 if axis==3 else 0);yy+=(-1 if axis==0 else 1 if axis==1 else 0)
  assert [m[0x5c0c]*256+m[0x5c0e],m[0x5c0d]]==[xx,yy&255]
  assert(c.a,c.x,c.y,c.p&0xce)==(0x5a,0x37,0x91,pflags&0xce)
  assert bytes(m[s['R0']:s['R7']+1])==oldscratch
  geometry+=1;geomcost.append(c.processorCycles)
 rows['real_block_page_geometry_cells']=geometry;costs['geometry_with_dispatch_CPU']=[min(geomcost),max(geomcost)]
 classes=0
 for tile,axis in itertools.product(range(256),range(4)):
  m=arena(b,s);m[s['Rh2']],m[s['Rh3']],m[s['Rh4']],m[s['Rh5']]=0,96,64,axis
  m[s['Block_Buffer_1']+68]=tile
  c,_,_=call(m,s,'RdHsReadCell')
  expected=axis==0 if tile in[0x5f,0x60]else False if tile in[0xc2,0xc3,0xc5]else bool(attrs[tile]&s['MTILE_SOLID'])and not bool(attrs[tile]&s['MTILE_CLIMB'])
  assert bool(c.p&1)==expected,(tile,axis,c.p,expected)
  classes+=1
 rows['all_native_tile_axis_classifications']=classes
 poses=0
 for frame,face,alt in itertools.product(range(256),[0,1,2],[0,1]):
  m=arena(b,s);m[0x5c79]=3;m[0x5c03],m[0x5c2c],m[0x5c7d]=frame,face,alt
  c,low,_=call(m,s,'RdHostDispatch');minimum=min(minimum,low)
  # Compare against exact frozen own descriptor/table, NEVER host OAM cursor.
  real=not alt and face<2 and frame<106 and m[s['RdBodyIndex0'if face==0 else'RdBodyIndex1']+frame]!=255
  if real:
   index=m[s['RdBodyIndex0'if face==0 else'RdBodyIndex1']+frame]
   ptr=m[s['RdArtRecordLo']+index]+256*m[s['RdArtRecordHi']+index]
   assert m[s['SmPosePtr']]+256*m[s['SmPosePtr']+1]==ptr
   assert m[s['SmChrBank']]==(680+m[s['RdArtRecordPage']+index])&255
   assert m[0x5c01]==m[s['RdBodyRadiusY']+frame]and m[0x5c02]==m[s['RdBodyRadiusX']+frame]
   assert m[s['ObjectMetasprite']]==s['METASPRITE_SAMUS_BODY']
  else:assert m[s['ObjectMetasprite']]==0 and m[s['SmPosePtr']]+256*m[s['SmPosePtr']+1]==s['RdArtEmpty']
  assert not any(k in[s['R0'],s['R1']]for k,_ in m.writes),'No NMI-volatile live pointer'
  poses+=1
 rows['real_pose_facing_alt_admission_and_pointer_cells']=poses
 platforms=0
 for ident,ctrl,x,page,y,delta,dx,flag in itertools.product([0x24,0x2a,0x2b,6],[4,5,6],[248],[0,1],[112,208],[0,2],[-8,4,24,48],[1,0x81]):
  m=arena(b,s);slot=2
  for n,val in [('Enemy_ID',ident),('Enemy_BoundBoxCtrl',ctrl),('Enemy_X_Position',x),('Enemy_PageLoc',page),('Enemy_Y_Position',y),('Enemy_Y_HighPos',1),('Enemy_Flag',flag)]:m[s[n]+slot]=val
  left=m[s['BoundBoxCtrlData']+4*ctrl];right=m[s['BoundBoxCtrlData']+4*ctrl+2];top=m[s['BoundBoxCtrlData']+4*ctrl+1]
  wx=page*256+x+dx;m[0x5c0c]=wx>>8;m[0x5c0e]=wx&255;m[0x5c0d]=(y+top-16+delta)&255;m[0x5c01]=15;m[0x5c02]=4;m[0x5c79]=6
  c,_,_=call(m,s,'RdHostDispatch')
  expected=ident>=0x24 and flag==1 and delta==0 and dx+4>=left and dx-4<=right
  assert bool(c.p&1)==expected,(ident,ctrl,page,y,delta,dx,flag,c.p,expected)
  platforms+=1
 rows['native_primary_platform_bbox_support_cells']=platforms
 # Complete real bridge+source action+pixel callbacks, not mocked callbacks.
 # Explicit source scene at hostX96/Y176, current floor208; A-hold/release and
 # bothfacings run/jump/morph. ContextB remains a disclosed SMB adaptation.
 actions=[]
 for gear,pads in [(0,[0]*3+[129]*10+[1]*65+[0]*8),(4,[2]*12+[130]*10+[2]*55),(17,[4,0,128]+[0]*45+[8,0]+[0]*35),(8,[129]*14+[1]*60)]:
  m=arena(b,s);m[0x5fb0]=gear;m[0x5fb4]=0x99;m[0x5fb5]=9
  put(m,b,Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=176,SavedJoypadBits=0)
  for pg in range(2):
   for tx in range(16):m[s['Block_Buffer_1'if pg==0 else'Block_Buffer_2']+176+tx]=solid
  call(m,s,'RdHsEnterScene');seen=set();total=0;lowest=255
  for pad in pads:
   put(m,b,SavedJoypadBits=pad);call(m,s,'RdHsClockBefore')
   m.page(1,124);m[s['CurrentBank']]=252
   c,low,tr=call(m,s,'RdControlStep');lowest=min(lowest,low);seen.add(m[0x5c00]);total+=c.processorCycles
   assert m.banks[1:3]==[124,94]and m[s['CurrentBank']]==252
   # Nothing in ordinary Samus state is delegated to or aliased by services.
   m.page(1,95);m[s['CurrentBank']]=223;call(m,s,'RdHsClockAfter')
  assert m[0x5c0d]+m[0x5c01]<208,(gear,m[0x5c0d],m[0x5c01])
  actions.append(dict(gear=gear,updates=len(pads),source_actions=sorted(seen),final_center=[m[0x5c0c]*256+m[0x5c0e],m[0x5c0d]],real_bridge_and_callbacks=True,minimum_SP=lowest,total_CPU=total))
  minimum=min(minimum,lowest)
 rows['complete_action_campaigns']=actions
 morphs=[]
 for action,face,gear in itertools.product([0,1,2,4,6],[0,1],[0,16]):
  m=arena(b,s);m[0x5fb0]=gear;m[0x5fb4]=0x99;m[0x5fb5]=9
  put(m,b,Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=120,SavedJoypadBits=0)
  call(m,s,'RdHsEnterScene');m[0x5c00]=action;m[0x5c2c]=face;m[0x5c28]=4;m[0x5c29]=4;m[0x5c14]=24 if action in[1,2,6]else 0
  m.morph_watch=(s['RdC_D0CD'],[]);m.page(1,124);m[s['CurrentBank']]=252
  c,_,_=call(m,s,'RdControlStep')
  for hit in m.morph_watch[1]:
   expected=b['raw'][16+95*8192+(s['RdHostBodyOnlyReturnX']&8191)+hit['frame']]if hit['frame']<106 else 0
   assert hit['X']==expected,(action,face,gear,hit,expected)
  morphs.append(dict(start_action=action,facing=face,gear=gear,actual_D0CD_entries=m.morph_watch[1]))
 assert any(r['actual_D0CD_entries']for r in morphs)
 rows['complete_same_update_draw_to_morph_context_B']=morphs
 bridge_rows=[]
 for service,pflags,sp in itertools.product(range(22),[0x30,0x71],[160,192,240]):
  m=arena(b,s);m.page(1,124);m[s['CurrentBank']]=252
  m[0x5fb4]=0x99;m[0x5fb5]=9;m[0x5c0d]=160;m[0x5c0e]=100;m[0x5c01]=15;m[0x5c02]=4;m[0x5c03]=8
  name=sorted(cb)[service];c,low,_=invoke(m,cb[name],a=0,x=0,y=0xd0,p=pflags,sp=sp);minimum=min(minimum,low)
  assert m.banks[1:3]==[124,94]and m[s['CurrentBank']]==252 and m[s['CurrentBankC']]==222
  bridge_rows.append(dict(service=service,callback=name,entry_SP=sp,minimum_SP=low,CPU=c.processorCycles))
 rows['actual_bridge_real_service_returns']=bridge_rows
 # Actual NMI/IRQ seams inside geometry and the real C94 bridge; no fake return.
 m=arena(b,s);m[0x5c79]=12;m[0x5c0c]=0;m[0x5c0e]=100;m[0x5c0d]=160;m[0x5c01]=15;m[0x5c02]=4
 _,_,trace=call(m,s,'RdHostDispatch');seams=[]
 for name in ['RdHostDispatch','RdHsGeometry','RdHsReadCell','RdHsRestoreC']:
  for kind in ['IRQ','NMI','lagNMI']:
   m=arena(b,s);m[0x5c79]=12;m[0x5c0c]=0;m[0x5c0e]=100;m[0x5c0d]=160;m[0x5c01]=15;m[0x5c02]=4
   c,low,_=call(m,s,'RdHostDispatch',seam=(s[name],95,kind));minimum=min(minimum,low);seams.append(dict(entry=name,kind=kind,protocol='off-protocol regular-NMI stress'if kind=='NMI'else'active-Main IRQ/lag',minimum_SP=low,real_audio_initialized=True))
 rows['actual_ISR_seams']=seams
 # Whole source control call with ACTUAL service/bridge interruptions, including
 # a nested per-pixel support query. EntrySP>=192 is the admitted service-host
 # IRQ contract; exploratory132 noninterrupt calls atSP160 do NOT extend it.
 for name,bank in [('RdControlDispatch',124),('RdHostCall95',124),('RdHsGeometry',95),('RdHsReadCell',95),('RdHsDraw',95)]:
  for kind in ['IRQ','NMI','lagNMI']:
   m=arena(b,s);m[0x5fb4]=0x99;m[0x5fb5]=9
   put(m,b,Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=176,SavedJoypadBits=0)
   for tx in range(16):m[s['Block_Buffer_1']+176+tx]=solid
   call(m,s,'RdHsEnterScene');m[0x5c14]=0x1a;m[0x5c08]=1
   m.page(1,124);m[s['CurrentBank']]=252
   target=s[name]if name in s else build.labels(ROOT/'build/rogue-dawn-host-plan-v1/bridge.lbl')[name]
   c,low,_=call(m,s,'RdControlStep',seam=(target,bank,kind));minimum=min(minimum,low)
   seams.append(dict(complete_source_control=True,entry=name,kind=kind,entry_SP=192,minimum_SP=low,protocol='off-protocol regular-NMI stress'if kind=='NMI'else'active-Main IRQ/lag',real_audio_initialized=True))
 rows['admitted_IRQ_entry_SP_minimum']=192
 for name in ['RdHsStage','RdHsOffset','RdHsCommit']:
  for kind in ['IRQ','NMI','lagNMI']:
   m=arena(b,s);m[0x5fb4]=0x99;m[0x5fb5]=9
   put(m,b,Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=120,SavedJoypadBits=0)
   call(m,s,'RdHsEnterScene');m[0x5c00]=3;m[0x5c01]=8;m[0x5c03]=27;m[0x5c05]=22;m[0x5c06]=22;m[0x5c28]=8;m[0x5c29]=8
   m.page(1,124);m[s['CurrentBank']]=252
   c,low,_=call(m,s,'RdControlStep',seam=(s[name],95,kind));minimum=min(minimum,low)
   assert m[0x5c00]!=3 and m[0x5c0d]<136
   seams.append(dict(complete_unmorph_chain=True,entry=name,kind=kind,entry_SP=192,minimum_SP=low,real_audio_initialized=True,protocol='off-protocol regular-NMI stress'if kind=='NMI'else'active-Main IRQ/lag'))
 proof=dict(passed=True,native_run=False,scope=__doc__,host_ROM_SHA=build.HOST_SHA,host_services_bytes=len((a.output.parent/'services.bin').read_bytes()),minimum_SP=minimum,placements_in_memory_only=placements,counts=rows,owned_CPU_costs=costs,admitted_host_geometry='SMB16px cell/page semantics, source-center radii and pixel/no-displacement responses; not original Metroid roomRAM',open_obligations=['Shared exact-owner admission/hook transaction integration, real actor defeat/Ice and damage dictionary ownership.','Real block bump/coin/axe/pipe and platform carry/second-small-platform surface transactions.','Distinct original item objects/emergence/art/announcements; selectors/grants alone are not acquired native coverage.','Original sound driver/data/request processing including06C4 low-health counter; no authentic waveform claim.','Source scene actions5/9 remain explicit unsupported door/elevator boundaries, no ordinary walking fallback.','No native deadlines/cadence/full sprite output/CHR or full-world source pipeline claim.'],bindings=[ref.binding(q)for q in [Path(__file__),ROOT/'tools/prepare_rogue_dawn_host_services_v1.py',ROOT/'src/rogue_dawn_host_services.s',ROOT/'src/rogue_dawn_host_services_bcd.inc',ROOT/'src/rogue_dawn_host.s',ROOT/'src/rogue_dawn_host_bridge.s',ROOT/'src/rogue_dawn_host_context.inc',ROOT/'src/rogue_dawn_control.s',build.HOST,build.HOST.with_suffix('.dbg'),ref.ROM,a.output.parent/'services.bin',a.output.parent/'linked-leaves.bin',a.output.parent/'rogue-control-aux.bin',a.output.parent/'linked-art.bin',ROOT/'build/rogue-dawn-host-plan-v1/bridge.bin']])
 a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,foreign=foreign,BCD=len(damage),grants=grants,selectors=selectors,actors=actors,geometry=geometry,campaigns=len(actions),ISR=len(seams),minimum_SP=minimum)))
if __name__=='__main__':main()
