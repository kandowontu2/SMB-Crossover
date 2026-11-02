"""Actual native event, ceiling recurrence, full foreign ABI and interrupt proof."""
import itertools,json
from pathlib import Path
import measure_bubble_native_bounce_gate_1102_v9 as G
import check_bubble_bobble_native_proxy_1102_v5 as Q
import check_bubble_bobble_native_stomp_1102_v7 as V7
P=G.P;R=G.R;O=G.O;N=G.N;C=Q.C;address=G.address


def bundle():
 old,b,patches=G.bundles();q=json.loads((O/'native-event-v9-layout.json').read_text());raw=bytearray(b['raw']);image=(O/'native-event-v9-image.bin').read_bytes()
 for i,page in enumerate([301,305,337,362,363,440,819,666]):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
 owner=(O/'native-event-v9-owner.bin').read_bytes();raw[16+65*8192+0xe00:16+65*8192+0xe00+len(owner)]=owner;b['raw']=bytes(raw)
 route=P.P.labels(O/'native-proxy-routes.lbl');return old,b,q,route


def main_fields(m):
 N.put(m,CurrentPlayer=0,AreaParserTaskNum=7,TimerControl=0,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0)
 for i,v in enumerate([4,0,0]):m[address(m.bundle,'GameTimerDisplay')+i]=v


def main():
 old,b,q,route=bundle();checks={};core=P.P.labels(O/'component.lbl');native=N.NesMPU;calls={}
 points={(3,q['labels']['BbNativeStomp']):'event',(3,core['BbOriginal_D36B']):'D36B',(3,q['labels']['BbNativeCeilingHit']):'ceiling'}
 for name in['EnemyStomped','MegaManBounceVelocity']:
  points[(((G.B.location(b,name)-16)//8192)|128,address(b,name))]=name
 class Trace(native):
  def step(self):
   if self.pc>=0x8000:
    name=points.get((self.memory.rawtags[(self.pc-0x8000)//8192],self.pc))
    if name:calls[name]=calls.get(name,0)+1
   return native.step(self)
 N.NesMPU=Trace
 try:
  seeds=[Q.fresh(b,route,i)for i in[0,1]]
  ordinary=0
  for identity,selector,velocity in itertools.product([0,1],[0,1,2,3,128],[0,1,252,253,255]):
   m=N.fork(seeds[identity]);actor=0x42 if identity else 0x2e;m.ram[2][actor+3]=selector;m.ram[2][actor+4]=7;N.put(m,Player_Y_Speed=velocity)
   before=dict(calls)
   for _ in range(3):N.invoke(m,'HuDraw',x=0,y=0)
   assert calls.get('event',0)==before.get('event',0)and calls.get('D36B',0)==before.get('D36B',0)
   assert m.ram[2][actor+3]==selector and m.ram[2][actor+4]==7;ordinary+=1
  checks['ordinary_zero_positive_negative_native_speed_never_infers_restart']=ordinary
  events=[]
  for identity,velocity,keys,flags in itertools.product([0,1],[0,252,253,255],[0,1,2,3],[0x30,0x71,0xfe]):
   m=N.fork(seeds[identity]);actor=0x42 if identity else 0x2e;oy=8 if identity else 0;m.ram[2][actor+3]=2;m.ram[2][actor+4]=7;m.ram[2][actor+1]=keys
   donor=N.fork(m);donor.ram[2][actor+3]=0;V7.target(donor,core['BbOriginal_D36B'],a=velocity,x=actor,y=oy,p=flags)
   N.put(m,Player_Y_Speed=velocity);before=dict(calls);coords=[N.get(m,n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']];scratch=bytes(m[3:11]);maps=list(m.rawtags)
   z=N.invoke(m,'MegaManBounceVelocity',a=velocity,x=3,y=199,p=flags)
   # FarCallCommon loads the saved A before entering fixed PHP, so that
   # wrapper preserves the actual loaded-A NZ flags rather than pre-call NZ.
   expected_p=((flags|0x30)&~0x82)|(2 if velocity==0 else velocity&128)
   assert[z[n]for n in['A','X','Y','P']]==[velocity,3,199,expected_p],(identity,velocity,keys,flags,z)
   assert bytes(m.ram[2][actor:actor+20])==bytes(donor.ram[2][actor:actor+20])and m.ram[2][15]==donor.ram[2][15]
   assert coords==[N.get(m,n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]and bytes(m[3:11])==scratch and m.rawtags==maps
   assert calls.get('event',0)==before.get('event',0)+1 and calls.get('D36B',0)==before.get('D36B',0)+1
   for _ in range(3):N.invoke(m,'HuDraw',x=0,y=0)
   assert calls['event']==before.get('event',0)+1 and calls['D36B']==before.get('D36B',0)+1
   events.append(dict(identity=identity,native_velocity=velocity,directional_latch=keys,flags=flags))
  checks['actual_event_ignores_velocity_equality_and_restarts_original_once']=len(events)
  stomps=[]
  for identity,enemy_id in itertools.product([0,1],[6,0]):
   m=N.fork(seeds[identity]);Q.Q.enemy(m,x=64,y=208);N.invoke(m,'InitGoomba',x=0)
   N.put(m,Enemy_ID=enemy_id,CrossoverBehaviorVersion=0,Player_Y_Speed=1,ObjectOffset=0,GuestBodyNoStomp=1,AreaType=1,InjuryTimer=0,Enemy_CollisionBits=0,EnemyOffscrBitsMasked=0)
   actor=0x42 if identity else 0x2e;m.ram[2][actor+3]=2;before=dict(calls);N.invoke(m,'HandlePECollisions',a=0,x=0,y=enemy_id,p=0x30)
   assert calls['EnemyStomped']==before.get('EnemyStomped',0)+1 and calls['event']==before.get('event',0)+1 and calls['D36B']==before.get('D36B',0)+1
   assert m.ram[2][actor+3]==1 and m.ram[2][actor+4]==28
   stomps.append(dict(identity=identity,enemy_ID=enemy_id,actual_native_stomp_event=True,original_jump_timer=28))
  checks['actual_Easy_HandlePECollisions_Goomba_Koopa']=stomps
  motion=[]
  # Compare source-native motion to the old visible6 behavior, with the v8
  # inferred ingress removed in memory. That is a motion baseline, not a new
  # claimed candidate. Overhead row8 is solid only in the ceiling fixtures.
  base=dict(old);rr=bytearray(old['raw']);pc=q['native_event']['old_inferred_ingress']
  pageindex=(pc-0xa000)//1024;at=1048592+[301,305,337,362,363,440,819,666][pageindex]*1024+(pc-0xa000)%1024;rr[at:at+3]=bytes([234])*3;base['raw']=bytes(rr)
  for identity,ceiling,keys in itertools.product([0,1],[False,True],[0,1,2]):
   pair=[Q.fresh(bb,route,identity)for bb in[base,b]];xs=[];ys=[];starts=calls.get('D36B',0);hits=calls.get('ceiling',0)
   for m in pair:
    main_fields(m)
    if ceiling:
     for name in['Block_Buffer_1','Block_Buffer_2']:
      for col in range(16):m[address(b,name)+8*16+col]=0x54
   for epoch in range(100):
    for m in pair:
     k=keys|(128 if epoch==1 else 0);N.put(m,FrameCounter=epoch,SavedJoypadBits=k,SavedJoypad1Bits=k,VRAM_Buffer1_Offset=0);N.invoke(m,'GameCoreRoutine',x=0,y=0)
    a,m=pair
    assert a.ram[2][:0x320]==m.ram[2][:0x320]and [N.get(a,n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]==[N.get(m,n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']],(identity,ceiling,keys,epoch)
    xs.append(N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'));ys.append(N.get(m,'Player_Y_Position'))
   assert calls.get('D36B',0)-starts==2,(identity,ceiling,keys,calls,starts)
   assert not ceiling or calls.get('ceiling',0)>hits,(identity,keys,'ceiling not exercised')
   assert ys[-1]==176 and N.get(m,'NumberofLives')==2
   motion.append(dict(identity=identity,ceiling=ceiling,direction=keys,updates=100,minY=min(ys),finalY=ys[-1],finalX=xs[-1],source_starts_per_variant=1,native_event_calls=0))
  checks['original_motion_directional_latch_and_repeated_Main_ceiling_differentials']=motion
  negatives=[]
  for identity in[0,1]:
   m=Q.fresh(old,route,identity);main_fields(m);before=calls.get('D36B',0);xs=[];ys=[]
   for name in['Block_Buffer_1','Block_Buffer_2']:
    for col in range(16):m[address(b,name)+8*16+col]=0x54
   for epoch in range(70):
    keys=1|(128 if epoch==1 else 0);N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0);N.invoke(m,'GameCoreRoutine',x=0,y=0);ys.append(N.get(m,'Player_Y_Position'))
   starts=calls.get('D36B',0)-before;assert starts>1,(identity,starts)
   negatives.append(dict(identity=identity,old_v8_false_source_starts=starts,updates=70,minY=min(ys),native_stomp_events=0))
  checks['old_v8_ceiling_false_restart_reproduced_without_native_event']=negatives
 finally:N.NesMPU=native
 cold=[];owner=P.P.labels(O/'native-event-v9-owner.lbl');image=(O/'native-event-v9-image.bin').read_bytes();art=(O/'native-cold-fix-helper.chr').read_bytes()
 for label,fault in[('cold',None),('code-readback',(3,2048)),('helper-readback',(2,0x1320)),('WRAM-protected','locked')]:
  m=C.ready(b);N.put(m,SelectedCharacter=39)
  if fault=='locked':m.protection=[0,0]
  elif fault:m.corrupt_at=fault
  scratch=bytes(m[3:11]);maps=list(m.rawtags);z=C.call(m,owner['CoCold']);assert bytes(m[3:11])==scratch and maps==m.rawtags and(z['A'],z['X'],z['Y'])==(83,71,109)
  if fault:assert not z['P']&1 and m.ram[2][0x1fe0]!=0xa7
  else:
   expected=bytearray(image);expected[0x1fe0:0x1ff0]=bytes.fromhex(q['BB_cookie']);assert m.ram[3]==expected and m.ram[2][:1024]==bytes(1024)and bytes(m.ram[2][4096:5120])==art and m.ppu_reads==18450
   assert m.ram_writes[-1]==(2,0x1fe0,0xa7);writes=len(m.ram_writes);reads=m.ppu_reads;assert C.call(m,owner['CoCold'])['P']&1 and len(m.ram_writes)==writes and m.ppu_reads==reads
  cold.append(dict(case=label,accepted=bool(z['P']&1)))
 checks['complete_nine_row_cold_verify_last_commit_and_warm']=cold
 retired=[]
 for identity in[0,1]:
  m,epoch,saved=Q.trap(b,route,identity);C.call(m,owner['CoRetire']);assert not m.ram[2][0x320]and N.get(m,'Enemy_Flag')==saved['Enemy_Flag']and not m.ram[2][0x1fe0]and not m.ram[3][0x1fe0];retired.append(dict(identity=identity,original_flag_restored=saved['Enemy_Flag']))
 checks['original_trapped_AI_retired_before_overlay']=retired
 poison=0
 for bank,i in itertools.product([2,3],range(16)):
  m=N.fork(seeds[0]);m.ram[bank][0x1fe0+i]^=1;before=[bytes(v)for v in m.ram];N.invoke(m,'MegaManBounceVelocity',a=253,x=3,y=91,p=0x30)
  assert before==[bytes(v)for v in m.ram];poison+=1
 checks['actual_event_requires_both_complete_headers']=poison
 # Actual IRQ and lag NMI at every reached owner gate/thunk/callback PC.
 seed=N.fork(seeds[0]);N.put(seed,NmiDisable=1,Player_Y_Speed=253);cuts=set()
 def selected(c):
  tag=c.memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else 0
  return(tag==252 and(0xa4b0<=c.pc<0xa4bb or 0xa0d6<=c.pc<0xa0e0))or(tag==3 and q['labels']['BbNativeStomp']<=c.pc<q['labels']['BbNativeStomp']+20)
 class CutTrace(native):
  def step(self):
   if selected(self):cuts.add((self.memory.rawtags[(self.pc-0x8000)//8192],self.pc,self.sp))
   return native.step(self)
 N.NesMPU=CutTrace;ref=N.fork(seed)
 try:expected=N.invoke(ref,'MegaManBounceVelocity',a=253,x=7,y=73,p=0x30)
 finally:N.NesMPU=native
 counts={};low=255
 for kind,cut in itertools.product(['IRQ','lagNMI'],sorted(cuts)):
  m=N.fork(seed);injected=False
  class Interrupt(native):
   def step(self):
    nonlocal injected,low
    mem=self.memory;tag=mem.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else 0
    if not injected and(tag,self.pc,self.sp)==cut:
     injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(mem.rawtags);private=[bytes(v)for v in mem.ram];scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b]);assert not self.p&4
     self.irq()if kind=='IRQ'else self.nmi()
     for _ in range(200000):
      low=min(low,self.sp)
      if self.pc==regs[5]and self.sp==regs[4]:break
      assert mem[self.pc]!=0;native.step(self)
     else:raise AssertionError('ISR return')
     assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc)and maps==mem.rawtags and private==[bytes(v)for v in mem.ram]and scratch==bytes(mem[3:11])and smc==bytes(mem[0x15a:0x17b])
    return native.step(self)
  N.NesMPU=Interrupt
  try:z=N.invoke(m,'MegaManBounceVelocity',a=253,x=7,y=73,p=0x30)
  finally:N.NesMPU=native
  assert injected and[z[n]for n in['A','X','Y','P']]==[expected[n]for n in['A','X','Y','P']]and m.ram==ref.ram and m.rawtags==ref.rawtags
  counts[kind]=counts.get(kind,0)+1
 checks['new_event_actual_IRQ_lagNMI']=dict(cuts=counts,minimum_ISR_SP=low)
 out=dict(passed=True,ROM_written=False,native=False,checks=checks,source_entry_counts=calls,BB_cookie=q['BB_cookie'],bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/prepare_bubble_native_event_1102_v9.py',R/'tools/audit/measure_bubble_native_bounce_gate_1102_v9.py',O/'native-event-v9-image.bin',O/'native-event-v9-owner.bin',O/'native-event-v9-layout.json']},scope='Actual CPU code in explicit legal flat-room/overhead-block fixtures; original source bytes retained. Native controller Easy/fullstage/performance remain root-owned and unqualified.')
 (O/'native-event-v9-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks)))


if __name__=='__main__':main()
