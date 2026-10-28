"""Finite genuine public Movement/lifecycle controls; CPU+mapper model only.

Uses the immutable host's real block-address helper and source solid attributes.
The source side receives the matching actual original 16x16 collision map.
No PPU, native NMI scheduler, host enemy damage or full-route claim.
"""
import json
import dragon_power_host_controls_v1 as H
import dragon_power_port_v1 as P
import dragon_power_controls_v1 as C

def main():
 code,s=H.B.build();s.update({k:v for k,v in H.symbols().items()if k not in s})
 raw=H.B.HOST.with_suffix('.nes').read_bytes()
 solid=next(i for i in range(256)if raw[16+127*8192+s['MTileAttribute']-0xe000+i]&s['MTILE_SOLID']
  and i not in [0x23,0x26,0x51,0x52,0x5f,0x60,0xc2,0xc3])
 def floor(m):
  for idx in range(32):
   H.execute(m,s['GetBlockBufferAddr'],a=idx)
   ptr=m[s['R6']]|m[s['R7']]<<8
   for row in range(0,208,16):m[ptr+row]=solid if row>=144 else 0
 def new():
  m=H.Memory(code,s);floor(m)
  m[s['Player_Y_Position']]=144;m[s['Player_Rel_XPos']]=80;m[s['Player_X_Position']]=80
  m[s['DpPose']]=2;m[s['DpAction']]=1
  return m
 def cell(m,x,y,tile):
  H.execute(m,s['GetBlockBufferAddr'],a=((x>>8)&1)*16+((x&255)>>4))
  ptr=m[s['R6']]|m[s['R7']]<<8;m[ptr+(y&0xf0)-32]=tile
 def damage_live(m):return [m[s[n]]for n in ['DpHP','DpPole','DpWaves','DpPower']]
 campaigns=[];updates=0
 for camera in [0,256]:
  for policy in ['idle','walk','release','reverse','punch','pole','wave','crouch','camera','wall','ceiling','brick']:
   m=new();a=H.A.O.arena();prior=0
   m[s['ScreenLeft_PageLoc']]=camera>>8;m[s['Player_PageLoc']]=camera>>8
   a.ram[0x3b]=3;m[s['DpWaves']]=3
   if policy=='wall':
    for y in range(80,176,16):a.ram[0x300+y+7]=0x75;cell(m,camera+112,y,solid)
   if policy in ['ceiling','brick']:
    for x in range(64,160,16):
     a.ram[0x300+112+(x>>4)]=0x95 if policy=='brick'else 0x75
     cell(m,camera+x,112,0x51 if policy=='brick'else solid)
   if policy=='pole':a.ram[0x32]=1;m[s['DpPole']]=1
   for addr in P.RAM:
    if addr not in [0,1]:m[C.loc(s,addr)]=a.ram[addr]
   rows=[]
   for tick in range(90):
    held=0
    if policy in ['walk','camera','wall']:held=0x80
    elif policy in ['ceiling','brick']:held=1 if tick==0 else 0
    elif policy in ['release','reverse']:
     held=0x80 if tick<20 else (0x40 if policy=='reverse'else 0)
     if tick==0:held|=1
    elif policy in ['punch','pole','wave']:
     held=2
     if policy=='wave'and a.ram[0x2d]==8:held|=1
    elif policy=='crouch':held=32|(2 if tick>=10 else 0)
    cam=camera+(16 if policy=='camera'and tick>=30 else 0)
    world=m[s['Player_X_Position']]+256*m[s['Player_PageLoc']]
    rel=(world-cam)&255
    a.ram[0xf7]=rel;m[s['Player_Rel_XPos']]=rel
    m[s['ScreenLeft_X_Pos']]=cam&255;m[s['ScreenLeft_PageLoc']]=cam>>8
    fresh=(held^prior)&held;prior=held
    # SMB pad layout is the bit reverse of the original canonical byte.
    smb=int(f'{held:08b}'[::-1],2);m[s['SavedJoypadBits']]=smb
    a.ram[0xdf]=held;a.ram[0xe0]=fresh
    ca=C.invoke(a,0xe82e);C.invoke(a,0xec4d,a=ca.a,x=ca.x,y=ca.y,p=ca.p)
    a.ram[0x26]=(a.ram[0x26]+1)&255;a.ram[0x27]=(a.ram[0x27]+1)%60
    cb,_,_=H.execute(m,s['DpMovement'])
    for addr in P.RAM:
     if addr in [0,1]:continue
     assert m[C.loc(s,addr)]==a.ram[addr],('fullMovement',camera,policy,tick,hex(addr),P.RAM[addr],a.ram[addr],m[C.loc(s,addr)])
    assert m[s['Player_Y_Position']]==(a.ram[0xf8]-16)&255
    assert m[s['Player_X_Position']]+256*m[s['Player_PageLoc']]==cam+a.ram[0xf7]
    assert m[s['DpCueOverflow']]==0
    assert m.bank==[126,86,85,127]
    rows.append([tick+1,a.ram[0x2d],a.ram[0xf7],a.ram[0xf8],cb.processorCycles,cb.lowest_sp])
    updates+=1
   campaigns.append(dict(camera=camera,policy=policy,updates=90,min_y=min(r[3]for r in rows),final=rows[-1],
    min_cycles=min(r[4]for r in rows),max_cycles=max(r[4]for r in rows),min_SP=min(r[5]for r in rows)))
 # Ensure keeps acquired inventory on ordinary gains, including INC wrap;
 # actual losses reset. Arbitrary >=128 differences intentionally reset.
 life=[]
 for previous,now,reset in [(2,2,False),(2,3,False),(2,4,False),(255,0,False),(254,0,False),
                            (2,1,True),(0,255,True),(1,129,True)]:
  m=new();m[s['DpLife']]=previous;m[s['NumberofLives']]=now
  for n,v in dict(DpHP=147,DpPole=1,DpWaves=37,DpPower=2).items():m[s[n]]=v
  H.execute(m,s['DpEnsure'])
  assert damage_live(m)==([100,0,0,0]if reset else[147,1,37,2])
  life.append([previous,now,reset,damage_live(m)])
 # Area/world/type changes clear active state, preserve earned persistent data.
 scene=[]
 for field,value in [('AreaAddrsLOffset',1),('WorldNumber',1),('AreaType',2)]:
  m=new();m[s['DpAction']]=8;m[s['DpShotState']]=2;m[s[field]]=value
  m[s['DpWaves']]=25;H.execute(m,s['DpEnsure'])
  assert m[s['DpAction']]==1 and m[s['DpShotState']]==0 and m[s['DpWaves']]==25
  scene.append([field,value,m[s['DpArea']],m[s['DpWorld']]])
 # Pause, nonplay engine and freeze timer must not advance the active kernel.
 gates=[]
 for field,value in [('GamePauseStatus',1),('GameEngineSubroutine',7),('TimerControl',1)]:
  m=new();m[s[field]]=value;before=bytes(m.ram[0x5c00:0x5c80])
  H.execute(m,s['DpMovement']);assert bytes(m.ram[0x5c00:0x5c80])==before
  gates.append([field,value])
 cold=new();cold[s['DpReady']]=0;cold.ram[0x5c00:0x5c80]=bytes([0xa5])*128
 cold.ram[0x5fcf]=0x39;cold.ram[0x5fdc:0x5fe0]=bytes([0x52])*4
 H.execute(cold,s['DpEnsure'])
 assert damage_live(cold)==[100,0,0,0]and cold[s['DpAction']]==1
 assert cold.ram[0x5fcf]==0x39 and cold.ram[0x5fdc:0x5fe0]==bytes([0x52])*4
 assert all(cold[s[n]]==0 for n in ['DpShotState','DpProtection','DpCueCount','DpCueOverflow'])
 # Approved crossover reward, genuine original plain-kind refusal and cap.
 pickup=[]
 for item in [0,1,2,255]:
  for hp in [1,100,140,149,150]:
   for stock in [0,1,59,60,0x43,0x81]:
    for tier in [0,1,2]:
     m=new();m[s['DpHP']]=hp;m[s['DpWaves']]=stock;m[s['DpPower']]=tier
     c,_,_=H.execute(m,s['DpPickup'],a=item)
     if item==0:expect=[min(150,hp+20),1,stock,max(1,tier)]
     elif item==1:expect=[hp,0,stock if stock&0x3f and stock&0xc0 else min(60,(stock&63)+3),tier if stock&0x3f and stock&0xc0 else 2]
     else:expect=[hp,0,stock,tier]
     assert damage_live(m)==expect,('pickup',item,hp,stock,tier,damage_live(m),expect)
     assert c.p&1==(item<2)
     pickup.append([item,hp,stock,tier,damage_live(m)])
 sequence=new();sequence[s['DpHP']]=100
 for item in [0,1,0]:H.execute(sequence,s['DpPickup'],a=item)
 assert damage_live(sequence)==[140,1,3,2],'repeatedMushroomPreservesEarnedFlower'
 H.execute(sequence,s['DpInjuryStart'],a=5);H.execute(sequence,s['DpInjuryStart'],a=17)
 assert sequence[s['DpProtection']]==5 and sequence[s['DpHP']]==140,'nativeProtectionDoesNotOverwrite'
 # All owned renderer code paths retain hardware-relevant flags/stack/banks
 # and the entire real host SMC span when interrupted at every executed PC.
 m=new();end,trace,_=H.execute(m,s['DpMovement']);irqs=[]
 for pc in sorted(set(p for p in trace if 0xa800<=p<0xc000)):
  q=new();out,_,receipt=H.execute(q,s['DpMovement'],inject=pc)
  assert receipt and (out.a,out.x,out.y,out.p&0xcf,out.sp)==(end.a,end.x,end.y,end.p&0xcf,end.sp)
  assert q.ram[0x5c00:0x5c80]==m.ram[0x5c00:0x5c80]
  assert q.ram[0x5fd0:0x5fdc]==m.ram[0x5fd0:0x5fdc]
  irqs.append(receipt)
 proof=dict(status='PASS_FINITE_PUBLIC_HOST_CPU_CONTROLS',core=H.A.O.D.binding(H.B.OUT/'component.bin'),
  parent=H.A.O.D.binding(H.B.HOST.with_suffix('.nes')),movement_updates=updates,campaigns=campaigns,
  lifecycle_cases=life,scene_cases=scene,paused_gates=gates,pickup_cases=pickup,actual_IRQ_cases=irqs,
  cold_initialization='actual owned Ensure; exact128B clear; preserved adjacent Sunny/Parodius bytes',
  repeated_rewards_and_protected_contact=damage_live(sequence)+[sequence[s['DpProtection']]],
  limits=['No PPU/NMI scheduler/native gameplay/cadence or source-audio driver integration',
   'Caller must initialize identity-exclusive marker on genuine selection/new game; Parodius can overwrite overlay',
   'Floor arenas use actual native helper but do not establish all SMB terrain/contact/block-effect interactions',
   'Mushroom/Flower mapping is approved authored crossover behavior, not original Dragon Power collectible types'])
 p=H.B.OUT/'wrapper-controls.json';p.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(proof=H.A.O.D.binding(p),updates=updates,IRQ=len(irqs),pickups=len(pickup)),indent=2))
if __name__=='__main__':main()
