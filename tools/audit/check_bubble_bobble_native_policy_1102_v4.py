"""Actual native body/hazard/pickup ingress in a private CPU cartridge fixture."""
import json
from pathlib import Path
import check_bubble_bobble_common_routes_1102_v5 as Q
P=Q.P;C=Q.C;N=Q.N;O=P.O;R=P.R;address=Q.address


def bundle():
 old,b,owner,route=Q.bundle();raw=bytearray(b['raw']);image=(O/'native-policy.bin').read_bytes()
 for i,page in enumerate([301,305,337,362,363,440,819,666]):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
 raw[1048592+441*1024:1048592+442*1024]=(O/'native-policy-helper.chr').read_bytes()
 own=(O/'native-policy-owner.bin').read_bytes();raw[16+65*8192+0xe00:16+65*8192+0xe00+len(own)]=own
 b['raw']=bytes(raw);prior=dict(b)
 b=C.patched(b,[(74,0xbf03,(O/'native-contact-gate.bin').read_bytes())])
 q=json.loads((O/'native-policy-layout.json').read_text());return b,q,route,prior


def fresh(b,route,identity=0):
 m=Q.actor_ready(b,identity);assert C.call(m,route['CoSceneGate'])['P']&1
 N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=1,AreaType=1,InjuryTimer=0,ObjectOffset=0)
 return m


def enemy(m,x=64,y=184,ident=6,slot=0):
 for n,v in[('Enemy_Flag',1),('Enemy_ID',ident),('Enemy_State',0),('Enemy_PageLoc',x>>8),('Enemy_X_Position',x&255),('Enemy_Y_Position',y),('Enemy_Y_HighPos',1),('Enemy_X_Speed',8),('Enemy_Y_Speed',0),('Enemy_MovingDir',1)]:m[address(m.bundle,n)+slot]=v


def main():
 b,layout,route,prior=bundle();checks={};seeds=[fresh(b,route,i)for i in[0,1]]
 foreign=0
 for char in range(39):
  for flags in[0x20,0x31,0x61,0xa9]:
   pair=[]
   for variant in[prior,b]:
    m=N.fork(seeds[0]);m.bundle=variant;N.put(m,SelectedCharacter=char,CrossoverBehaviorVersion=1);enemy(m)
    z=N.invoke(m,'GuestBodyContactBridge',a=85,x=0,y=91,p=flags);pair.append((m,z))
   a,za=pair[0];z,zz=pair[1]
   assert[za[n]for n in['A','X','Y','P']]==[zz[n]for n in['A','X','Y','P']],('Foreign body AXYP',char,flags,za,zz)
   assert list.__getitem__(a,slice(0,256))==list.__getitem__(z,slice(0,256))and list.__getitem__(a,slice(512,32768))==list.__getitem__(z,slice(512,32768))and bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b])and a.ram==z.ram and a.rawtags==z.rawtags and a.vram==z.vram,('Foreign body full state',char,flags)
   foreign+=1
 checks['actual_foreign_body_full_AXYP_application_SMC_maps_cases']=foreign
 cls=N.NesMPU;events={};points={(((Q.location(b,n)-16)//8192)|128,address(b,n)):n for n in['GuestBodyContactBridge','LmBodyGate','NrBody','JnBodyDispatch','HuBody','HuInjury','HuInjuryStatus','HuVisible','HuMature','HuWeaponTail']if n in b['syms']};far=[]
 for name in['BbNativeBodyContact','BbPolicyInjury','BbPolicyStatus']:
  pc=layout['labels'][name];points[(2 if pc>=0xc000 else 3,pc)]=name
 class Trace(cls):
  def step(self):
   key=(self.memory.rawtags[(self.pc-0x8000)//8192],self.pc)if self.pc>=0x8000 else(None,self.pc)
   if key in points:events[points[key]]=events.get(points[key],0)+1
   if self.pc==address(b,'FarCallCommon')+3 and len(far)<30:far.append([self.a,N.get(self.memory,'FarcallJmpTarget_SMC',1)+256*N.get(self.memory,'FarcallJmpTarget_SMC',2)])
   return cls.step(self)
 N.NesMPU=Trace
 try:
  cases=0
  for identity,seed in enumerate(seeds):
   actor=0x42 if identity else 0x2e
   for dx in range(-10,11):
    for dy in range(-10,11):
     m=N.fork(seed);enemy(m,x=64+dx,y=184+dy)
     r=N.invoke(m,'GuestBodyContactBridge',a=85,x=0,y=91,p=0x31)
     expected=abs(dx)<9 and abs(dy)<9
     assert bool(m.ram[2][actor+3]&128)==expected and r['P']&1,(identity,dx,dy,r,m.ram[2][actor+3],events,far)
     assert m.ram[2][actor+17]==(200 if expected else 0)and N.get(m,'GameEngineSubroutine')==8
     cases+=1
  checks['actual_GuestBodyContactBridge_original_9px_cases']=cases
  # PowerUpObject is the real$2E. It remains outside ordinary source hurt;
  # native flying Cheep-Cheep$14 is a genuine damageable/trappable enemy.
  actual_ids=0
  for identity,seed in enumerate(seeds):
   actor=0x42 if identity else 0x2e
   for ident,handled in[(0x2e,False),(0x14,True)]:
    m=N.fork(seed);enemy(m,ident=ident)
    r=N.invoke(m,'GuestBodyContactBridge',a=85,x=0,y=91,p=0x31)
    assert bool(r['P']&1)==handled and bool(m.ram[2][actor+3]&128)==handled
    actual_ids+=1
  checks['real_native_powerup46_and_FlyingCheep20_contact']=actual_ids
  hazards=0
  for identity,seed in enumerate(seeds):
   actor=0x42 if identity else 0x2e;m=N.fork(seed)
   for attempt in range(2):
    N.invoke(m,'InjurePlayer',a=85,x=0,y=91,p=0x31)
    assert m.ram[2][actor+3]==128 and m.ram[2][actor+17]==200 and N.get(m,'GameEngineSubroutine')==8 and N.get(m,'NumberofLives')==2
    hazards+=1
   # Genuine native visibility/geometry policies leave SMB power state alone.
   before=(N.get(m,'PlayerSize'),N.get(m,'PlayerStatus'))
   assert N.invoke(m,'GuestPlayerVisible')['P']&1
   for name,expected in[('MegaManCollisionAdder',2),('MegaManCollisionBox',1)]:
    z=N.invoke(m,name,a=39,x=0,y=0,p=0x31);assert z['Y']==expected,(name,z)
   assert before==(N.get(m,'PlayerSize'),N.get(m,'PlayerStatus'))
  checks['actual_native_InjurePlayer_source_hurt_and_repeat_grace']=hazards
  checks['actual_native_visible_adder_box_no_powerstate_change']=2
  maturity=0
  for state in[0,6,16,127,128,129,255]:
   for kind in range(4):
    for flags in[0x20,0x31,0x61,0xa9]:
     m=N.fork(seeds[0]);m[address(b,'Enemy_State')+5]=state;m[address(b,'PowerUpType')+5]=kind
     before=[bytes(m.ram[k])for k in[2,3]]
     assert N.invoke(m,'NrPickupCollision',a=85,x=5,y=73,p=flags)['P']&1
     assert before==[bytes(m.ram[k])for k in[2,3]];maturity+=1
  checks['actual_existing_NrPickupCollision_admission_cases']=maturity
 finally:N.NesMPU=cls
 assert events.get('BbNativeBodyContact')and events.get('HuInjury')and events.get('BbPolicyInjury')and events.get('BbPolicyStatus'),events
 checks['existing_NrPickupCollision_does_not_reach_HuMature39']=not bool(events.get('HuMature'))
 checks['actual_native_ingress_counts']=events
 # Every newly rewritten body-gate instruction under real native interrupts,
 # including the unchanged foreign and original SMB2 owner continuations.
 cuts_total={};low=255
 for char in[0,25,39]:
  m=N.fork(seeds[0]);N.put(m,SelectedCharacter=char,NmiDisable=1);enemy(m);cuts=set()
  class GateTrace(cls):
   def step(self):
    if self.memory.rawtags[1]==202 and 0xbf00<=self.pc<0xbf34:cuts.add((self.pc,self.sp))
    return cls.step(self)
  N.NesMPU=GateTrace;reference=N.fork(m)
  try:expected=N.invoke(reference,'GuestBodyContactBridge',a=85,x=0,y=91,p=0x30)
  finally:N.NesMPU=cls
  for kind in['IRQ','lagNMI']:
   for cut in sorted(cuts):
    n=N.fork(m);injected=False
    class Interrupt(cls):
     def step(self):
      nonlocal injected,low
      mem=self.memory
      if not injected and mem.rawtags[1]==202 and(self.pc,self.sp)==cut:
       injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(mem.rawtags);private=[bytes(mem.ram[k])for k in[2,3]];scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b])
       assert not self.p&4
       self.irq()if kind=='IRQ'else self.nmi()
       for _ in range(200000):
        low=min(low,self.sp)
        if self.pc==regs[5]and self.sp==regs[4]:break
        assert mem[self.pc]!=0,(kind,char,cut,hex(self.pc));cls.step(self)
       else:raise AssertionError(('Body gate ISR bound',char,kind,cut))
       assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc)and maps==mem.rawtags and private==[bytes(mem.ram[k])for k in[2,3]]and scratch==bytes(mem[3:11])and smc==bytes(mem[0x15a:0x17b]),(char,kind,cut)
      return cls.step(self)
    N.NesMPU=Interrupt
    try:z=N.invoke(n,'GuestBodyContactBridge',a=85,x=0,y=91,p=0x30)
    finally:N.NesMPU=cls
    assert injected and[z[k]for k in['A','X','Y','P']]==[expected[k]for k in['A','X','Y','P']]and n.ram==reference.ram and n.rawtags==reference.rawtags
    cuts_total[kind]=cuts_total.get(kind,0)+1
 checks['actual_new_body_gate_IRQ_lagNMI']=dict(cuts=cuts_total,minimum_ISR_SP=low)
 # The policy change must not silently mutate any frozen proof-bound input.
 freeze=json.loads((O/'qualified-native-proofs-1102-v1.json').read_text())
 for rel,item in freeze['files'].items():assert P.sha((R/rel).read_bytes())==item['SHA256'],rel
 q=dict(passed=True,ROM_written=False,shared_source_written=False,admitted=False,base_ROM_SHA256=P.PIN,in_memory_candidate_SHA256=P.sha(b['raw']),checks=checks,layout=layout,scope='Actual native GuestBodyContactBridge uses the proposed source-funded bank74 gate and authenticated resident row11; InjurePlayer, GuestPlayerVisible, MegaManCollisionAdder/Box reach real private policies through current shared routing. Existing native NrPickupCollision admits raw39 without reaching HuMature; its112 cases are existing fallback behavior, not new row23 wiring or mapped item effects. Legal isolated flat/enemy fixtures. No native Main, AI/birth hook, shot-bank/fullbox gate, terrain head/side, native emulator, item effects or fullstage claim.',bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/prepare_bubble_bobble_native_policy_1102_v4.py',R/'tools/audit/prepare_bubble_bobble_contact_gate_1102_v1.py',R/'tools/reference/bubble_bobble_contact_gate_1102_v1.inc',O/'native-contact-gate.bin',O/'native-contact-gate-layout.json',O/'native-policy.bin',O/'native-policy-helper.chr',O/'native-policy-owner.bin']})
 (O/'native-policy-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks,ROM_written=False)))


if __name__=='__main__':main()
