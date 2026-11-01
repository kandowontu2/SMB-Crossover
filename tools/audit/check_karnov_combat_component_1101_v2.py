"""Actual native target execution for the proposed selected-C2 combat worker.

Only this test explicitly loads the new component into RAM. No loader, ROM
carrier, menu/native playthrough or installation claim is made.
"""
from pathlib import Path
import hashlib,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from verify_native_relocation import NesMPU
from check_karnov_actor_1101_v1 import Memory
from recover_karnov_actor_1101_v1 import ROM
from check_tmnt_render_oa import address,location
O=R/'build/karnov-combat-component-1101-v2';P=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 debug='--debug-isr'in sys.argv
 q=dict(passed=False,source_CPU=True,native=False,installed=False,explicit_new_component_RAM_fixture=True)
 try:
  stage=json.loads((O/'assembly-stage.json').read_text());assert stage['passed']
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  b=H.C.qualified(P/'candidate.nes')
  native_names=[('GetBlockBufferAddr','native_block_queries'),('NativeRarePlayerHeadCollisionCore','native_head_effects'),('HandleEnemyFBallCol','native_enemy_damage'),('GetEnemyBoundBox','native_bounds')]
  native_points={(address(b,n),((location(b,n)-16)//8192)|128):key for n,key in native_names}
  for line in(O/'component.lbl').read_text().splitlines():
   a=line.split()
   if len(a)==3:b['syms'][a[2].lstrip('.')]=dict(val='0x'+a[1])
  pc=lambda n:address(b,n)
  def put(m,**kw):
   for n,v in kw.items():
    if n.startswith('Kr')and 0xc000<=pc(n)<0xe000:m.ram[2][pc(n)-0xc000]=v
    else:m[pc(n)]=v
  counters=dict(calls=0,native_block_queries=0,native_head_effects=0,native_enemy_damage=0,native_bounds=0)
  mins=[];cycles=[];digest=hashlib.sha256()
  def call(m,row=4,**kw):
   observer=kw.pop('observer',None)
   c=H.start(m,'KrServiceVeneers',**kw);at=pc('KrServiceVeneers')+row*3
   m[pc('FarcallJmpTarget_SMC')+1]=at&255;m[pc('FarcallJmpTarget_SMC')+2]=at>>8
   prior=bytes(m[3:11]);regs=(kw.get('a',85),kw.get('x',7),kw.get('y',91));obj=H.get(m,'ObjectOffset');tags=m.rawtags[:]
   def hook(mem,c,i):
    if observer:observer(mem,c,i)
    if c.pc>=0x8000:
     key=native_points.get((c.pc,mem.rawtags[(c.pc-0x8000)//8192]))
     if key:counters[key]+=1
   c,low=H.finish(m,c,hook)
   if row!=35:assert(c.a,c.x,c.y)==regs and c.p&1
   assert bytes(m[3:11])==prior and H.get(m,'ObjectOffset')==obj
   assert m.rawtags==tags and c.sp==kw.get('sp',224)
   counters['calls']+=1;mins.append(low);cycles.append(c.processorCycles)
   digest.update(bytes(m.ram[2][0x65:0x89]));return c
  def make():
   m=L.make(b);put(m,SelectedCharacter=34,FmAlts=1,FrameCounter=19,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,Player_X_Position=120,Player_PageLoc=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0)
   c,_=L.call(m,'KrLoad');assert c.p&1
   c=H.start(m,'KrServiceVeneers');at=pc('KrServiceVeneers')+45
   m[pc('FarcallJmpTarget_SMC')+1]=at&255;m[pc('FarcallJmpTarget_SMC')+2]=at>>8;H.finish(m,c)
   # Explicit new-code fixture; the existing real loader/cookie is tested by
   # the parent. This does not assert that the parent loads these new bytes.
   lo=stage['kernel_lease'][0]-0xa000;m.ram[3][lo:lo+stage['kernel_bytes']]=(O/'kernel.bin').read_bytes()
   lo=stage['proposed_C2_code_lease'][0]-0xc000;m.ram[2][lo:lo+stage['resident_bytes']]=(O/'resident.bin').read_bytes()
   for row,n in [(4,'KrCombat'),(34,'KrCombat'),(35,'KrCombatReset')]:
    at=pc('KrCacheServices')-0xa000+3*row;v=pc(n);m.ram[3][at:at+3]=bytes([76,v&255,v>>8])
   for n,count in [('Block_Buffer_1',208),('Block_Buffer_2',208),('MmSolidTerrain',416),('Enemy_Flag',6),('Enemy_State',6),('Block_State',2),('Block_RepFlag',2)]:
    at=pc(n)
    for i in range(count):m[at+i]=0
   put(m,KrHaveEpoch=1,KrLastEpoch=19,KrCameraLo=0,KrCameraHi=0,ObjectOffset=3,Square1SoundQueue=0,Square2SoundQueue=0,MmBlockAttack=0)
   call(m,35);return m
  seed=make()
  def shot(m,slot=0,flag=0x84,x=100,y=110,weapon=0):
   m.ram[2][0x65]=weapon
   for i in range(27):m.ram[2][0x6e+i]=0
   m.ram[2][0x6e+slot]=flag;m.ram[2][0x6f+slot]=x;m.ram[2][0x70+slot]=y
  def enemy(m,slot=0,ident=6,x=96,y=96,page=0,state=0,flag=1):
   for n,v in [('Enemy_Flag',flag),('Enemy_ID',ident),('Enemy_X_Position',x),('Enemy_PageLoc',page),('Enemy_Y_Position',y),('Enemy_Y_HighPos',1),('Enemy_State',state),('Enemy_BoundBoxCtrl',3)]:m[pc(n)+slot]=v
  def epoch(m,tick):put(m,FrameCounter=tick,KrLastEpoch=tick)
  def cell(m,x=100,y=110,page=0,tile=0x51,solid=0):
   cx=(x+4)&255;cp=(page+int(x+4>255))&255;row=((y+4)&240)-32
   at=pc('Block_Buffer_1')+(cp&1)*208+(cx>>4)+row
   m[at]=tile;m[at+pc('MmSolidTerrain')-pc('Block_Buffer_1')]=solid;return at
  # Every native enemy slot and all nine original shot records.
  hits=0
  for s,side,e in itertools.product(range(0,27,3),[0x84,0xc4],range(6)):
   if debug and(s,side,e)!=(0,0x84,0):continue
   m=L.fork(seed);shot(m,s,side,weapon=2);enemy(m,e);call(m)
   assert m.ram[2][0x6e+s]==(side&0xc0)|0x18,(s,side,e,m.ram[2][0x6e+s],counters,bytes(m.ram[2][0x840:0x860]).hex(),bytes(m[pc('BoundingBox_UL_Corner'):pc('BoundingBox_UL_Corner')+32]).hex())
   assert m[pc('Enemy_State')+e]&32,(s,side,e,'not defeated')
   assert H.get(m,'Square1SoundQueue')!=0
   assert m[pc('FloateyNum_X_Pos')+e]==96,(s,side,e,'score popup world origin')
   hits+=1
  # Reused damage owners retain native immunity/HP/alias/scoring semantics.
  kinds=[]
  for ident,expected in [(0,True),(1,True),(2,False),(6,True),(8,False),(12,False),(13,True),(14,True),(18,True),(36,False),(37,False)]:
   m=L.fork(seed);shot(m);enemy(m,ident=ident);call(m)
   defeated=bool(m[pc('Enemy_State')]&32);assert defeated==expected,(ident,defeated)
   kinds.append([ident,defeated,m.ram[2][0x6e]])
  m=L.fork(seed);shot(m);enemy(m,ident=45);put(m,BowserHitPoints=5);call(m);assert H.get(m,'BowserHitPoints')==4
  # Service4/34 are one contact epoch; impact phase cannot hit twice.
  enemycalls=counters['native_enemy_damage'];call(m,34);assert H.get(m,'BowserHitPoints')==4 and counters['native_enemy_damage']==enemycalls
  epoch(m,20);call(m);assert H.get(m,'BowserHitPoints')==4
  m=L.fork(seed);shot(m,weapon=8);enemy(m,ident=45);put(m,BowserHitPoints=5);call(m);assert H.get(m,'BowserHitPoints')==4 and m.ram[2][0x6e]==0x84
  for t in range(20,27):epoch(m,t);call(m)
  assert H.get(m,'BowserHitPoints')==4
  # Canonical Bowser rear and head share one victim bit.
  m=L.fork(seed);shot(m,weapon=8);enemy(m,0,45);enemy(m,1,45,flag=0x80);put(m,BowserHitPoints=5);call(m);assert H.get(m,'BowserHitPoints')==4
  # Ground/pipe cells never enter native destructive block dispatcher.
  safe=[]
  for tile,solid in [(0,0),(0x23,0),(0x26,0),(0x54,0),(0x52,1),(0x61,0),(0x62,0),(0x5f,0),(0x60,0)]:
   m=L.fork(seed);shot(m);at=cell(m,tile=tile,solid=solid);n=counters['native_head_effects'];call(m)
   assert m[at]==tile and counters['native_head_effects']==n,(tile,solid,'terrain destroyed');safe.append([tile,solid,m.ram[2][0x6e]])
  blocks=[]
  saved=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','PlayerSize','CrouchingFlag','Player_Y_Speed','MmBlockAttack']
  for tile,page,x,y in itertools.product([0x51,0x52,0x55,0xc1],[0,1,2],[40,100,252],[64,110,174]):
   if debug and(tile,page,x,y)!=(0x51,0,40,64):continue
   m=L.fork(seed);shot(m,x=x,y=y);put(m,KrCameraHi=page,ScreenLeft_PageLoc=page,MmBlockAttack=37,PlayerSize=1,CrouchingFlag=1,Player_Y_Speed=253)
   at=cell(m,x=x,y=y,page=page,tile=tile);prior=[H.get(m,n)for n in saved];before=counters['native_head_effects'];call(m)
   assert counters['native_head_effects']==before+1,(tile,page,x,y,'head not called',counters,m.ram[2][0x6e],bytes(m.ram[2][0x840:0x860]).hex())
   assert[H.get(m,n)for n in saved]==prior,(tile,page,x,y,'player proxy leaked')
   assert any(m[pc('Block_State')+i]for i in range(2)),(tile,page,x,y,'no native block animation')
   j=next(i for i in range(2)if m[pc('Block_State')+i])
   assert m[pc('Block_X_Position')+j]==((x+4)&240)and m[pc('Block_PageLoc')+j]==page+int(x+4>255)and m[pc('Block_Y_Position')+j]==((y+4)&240),(tile,page,x,y,'native block origin')
   blocks.append([tile,page,x,y,m.ram[2][0x6e]])
  m=L.fork(seed);shot(m);at=cell(m,tile=0x55)
  for i in range(2):m[pc('Block_State')+i]=1
  n=counters['native_head_effects'];call(m);assert m[at]==0x55 and counters['native_head_effects']==n
  # Guard failures never invoke native effects or alter shot records.
  negatives=[]
  for n,v in [('SelectedCharacter',7),('KrReady',0),('OperMode',0),('GameEngineSubroutine',7),('GamePauseStatus',1),('KrHaveEpoch',0),('KrLastEpoch',18)]:
   m=L.fork(seed);shot(m);enemy(m);put(m,**{n:v});old=bytes(m.ram[2][0x65:0x89]);countersold=counters.copy();call(m)
   assert bytes(m.ram[2][0x65:0x89])==old
   assert all(counters[k]==countersold[k]for k in counters if k!='calls');negatives.append(n)
  # New worker never advances original projectile timers. The original
  # executable and the already-linked original update own impact decay.
  donor=ROM.read_bytes();decay_cases=0;decay_updates=0
  for slot,side,weapon in itertools.product(range(0,27,3),[0x84,0xc4],[0,1,2]):
   if debug:break
   if(slot%9)//3>weapon:continue
   m=L.fork(seed);shot(m,slot,side,weapon=weapon);enemy(m);oldclock=m.ram[2][0xe8];call(m)
   assert m.ram[2][0xe8]==oldclock
   v=pc('KrSourceWeapons');m.ram[3][105:108]=bytes([76,v&255,v>>8])
   n=Memory();n[:2048]=m.ram[2][:2048];n[0xa000:0xc000]=donor[16+11*8192:16+12*8192];n[0xc000:]=donor[16+14*8192:16+16*8192]
   for tick in range(12):
    nc=NesMPU(memory=n,pc=0xaab2);nc.a=85;nc.x=7;nc.y=91;nc.p=0x71;nc.sp=224;nc.stPushWord(0x5aff)
    for step in range(12000):
     if nc.pc==0x5b00:break
     if nc.pc in [0xc81d,0xc3d8]:
      if nc.pc==0xc3d8:nc.a=0;nc.FlagsNZ(0)
      nc.pc=(nc.stPopWord()+1)&65535;continue
     assert n[nc.pc]!=0;nc.step()
    else:raise AssertionError('Original impact update bound')
    call(m,35)
    assert bytes(m.ram[2][0x6e:0x89])==bytes(n[0x6e:0x89]),(slot,side,weapon,tick,'original impact lifetime')
    decay_updates+=1
   assert m.ram[2][0x6e+slot]==0,(slot,side,weapon,'impact did not expire');decay_cases+=1
  # Genuine native IRQ/NMI cuts around callbacks and each mapper-publication
  # seam. New component injection is explicit; interrupt code is unchanged.
  previous=V.pending_store
  def pending(mem,c,slot,op):
   if previous(mem,c,slot,op):return True
   reg=0x5115 if slot==1 else 0x5116;value={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(mem[c.pc])
   return value is not None and bytes(mem[c.pc+1:c.pc+3])==reg.to_bytes(2,'little')and value==H.get(mem,'CurrentBank'if slot==1 else'CurrentBankC')
  V.pending_store=pending
  cuts=0;minimum_ISR=255;isr_summaries=[]
  def foreground(m):
   # Native NMI legitimately consumes the queued SFX; it is not foreground
   # corruption. The effect producer's queue is checked before these cuts.
   return [bytes(z)for z in m.ram],bytes(m[3:11]),bytes(m[0x200:0x300]),bytes(m[0x15a:0x17b]),m.rawtags[:],[(n,H.get(m,n))for n in saved+['BowserHitPoints']]
  for case in ['goomba','brick','mushroom']:
   initial=L.fork(seed);shot(initial)
   if case=='goomba':enemy(initial)
   else:cell(initial,tile=0x51 if case=='brick'else 0x55)
   trace=[];baseline=L.fork(initial);base=call(baseline,observer=lambda mem,c,i:trace.append((c.pc,c.sp,mem.rawtags[:])))
   low=min(z[1]for z in trace);positions={0,len(trace)-2,next(i for i,z in enumerate(trace)if z[1]==low)}
   for i,(at,sp,tags)in enumerate(trace):
    if(at,tags[(at-0x8000)//8192]if at>=0x8000 else None)in native_points:positions.add(i)
    if i and tags!=trace[i-1][2]:positions.update([i-1,i])
   events=[]
   for cut,kind in itertools.product(sorted(positions),['IRQ','NMI']):
    m=L.fork(initial);one=[]
    def interrupt(mem,c,i):
     if i==cut:
      savedSMC=bytes(mem[0x15a:0x17b])
      try:one.append(V.interrupt(mem,c,kind))
      except Exception as e:raise AssertionError((case,cut,kind,trace[cut],repr(e),[(hex(j+0x15a),a,z)for j,(a,z)in enumerate(zip(savedSMC,mem[0x15a:0x17b]))if a!=z],min(z[1]for z in trace)))from e
    c=call(m,observer=interrupt)
    assert len(one)==1 and(c.a,c.x,c.y,c.p,c.sp)==(base.a,base.x,base.y,base.p,base.sp)
    fa,fb=foreground(m),foreground(baseline)
    if fa!=fb:
     delta=[]
     for ii,(a,z)in enumerate(zip(fa,fb)):
      if a!=z:
       if ii==0:delta.append(('RAM',[(j,[(hex(k),av,zv)for k,(av,zv)in enumerate(zip(aa,zz))if av!=zv][:8])for j,(aa,zz)in enumerate(zip(a,z))if aa!=zz]))
       elif isinstance(a,bytes):delta.append((ii,[(hex(k),av,zv)for k,(av,zv)in enumerate(zip(a,z))if av!=zv][:8]))
       else:delta.append((ii,a,z))
     raise AssertionError((case,cut,kind,'foreground resume',trace[cut],delta))
    minimum_ISR=min(minimum_ISR,one[0]['minimum_SP']);events.append(one[0]['minimum_SP']);cuts+=1
   isr_summaries.append(dict(case=case,foreground_minimum_SP=low,cuts=len(events),ISR_minimum_SP=min(events)))
  assert minimum_ISR-0x7b>=12,('Service ISR reserve',minimum_ISR,isr_summaries)
  assert not debug,'Debug ISR run cannot qualify full component'
  q.update(passed=True,parent_ROM_sha256=stage['parent_ROM_sha256'],runtime_ID=34,legacy_raw7_effects_rejected=True,counters=counters,nine_shot_six_enemy_direction_cases=hits,native_enemy_classes=kinds,terrain_safety=safe,block_proxy_cases=len(blocks),block_and_score_origins_exact=True,negative_guards=negatives,original_impact_decay_cases=decay_cases,original_impact_decay_updates=decay_updates,real_ISR_cuts=cuts,service_ISR_summaries=isr_summaries,minimum_service_ISR_SP=minimum_ISR,service_ISR_bytes_above_SMC=minimum_ISR-0x7b,minimum_service_SP=min(mins),maximum_service_cycles=max(cycles),trace_sha256=digest.hexdigest(),scope='Actual native GetBlockBufferAddr, GuestClaimBlockSlot, NativeRarePlayerHeadCollisionCore, real enemy box producer, SprObjectCollisionCore and HandleEnemyFBallCol through authenticated parent service ingress; exact original impact decay. Proposed C2/code loaded explicitly. Real service-level IRQ/NMI cuts preserve live state and12 B SMC reserve; actual Main entry depth, carrier/loader and native playthrough remain root integration gates.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'assembly-stage.json',O/'kernel.bin',O/'resident.bin',P/'candidate.nes',P/'candidate.dbg']}
 (O/'combat-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('traceback')

if __name__=='__main__':main()
