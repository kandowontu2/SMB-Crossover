"""Dedicated native contact row37, legacy Ex ABI and real ISR continuations."""
import json
from pathlib import Path
import check_bubble_bobble_native_proxy_1102_v5 as Q
P=Q.P;C=Q.C;N=Q.N;R=Q.R;O=Q.O;address=Q.address


def same_application(a,b):
 return (list.__getitem__(a,slice(0,256))==list.__getitem__(b,slice(0,256))
         and list.__getitem__(a,slice(512,32768))==list.__getitem__(b,slice(512,32768))
         and bytes(a[0x15a:0x17b])==bytes(b[0x15a:0x17b])and a.ram==b.ram
         and a.rawtags==b.rawtags and a.vram==b.vram)


def main():
 b,q,route=Q.bundle();old=P.scoped_load(P.ROM);checks={}
 assert P.sha(old['raw'])==P.PIN
 at=16+65*8192+0x10fb
 assert b['raw'][at:at+5]==old['raw'][at:at+5],"Real ExMenuDone/Reset entry must be untouched"
 assert old['raw'][16+65*8192+0x1026:16+65*8192+0x1031]==bytes.fromhex('2034ae4c49a8')+bytes([255])*5
 # Only old RetireBoth's B026 entry is retained. B029 was its JMP operand
 # stream, not an independent callable entry. Scan all linked bank65 absolute
 # operands, then classify the sole old JMP A849 by its instruction boundary.
 incoming=[]
 for i in range(8190):
  if old['raw'][16+65*8192+i]in[0x20,0x4c]:
   target=int.from_bytes(old['raw'][16+65*8192+i+1:16+65*8192+i+3],'little')
   if 0xb026<=target<0xb031:incoming.append([0xa000+i,target])
 assert all(t==0xb026 for _,t in incoming),incoming
 absolute=bytes.fromhex('0d0e191d1e202c2d2e393d3e4c4d4e595d5e6c6d6e797d7e8c8d8e999dacadaeb9bcbdbecccdced9dddeecedeef9fdfe')
 reader_candidates=[];bank65=old['raw'][16+65*8192:16+66*8192]
 for i in range(8190):
  if bank65[i]in absolute and 0xb029<=int.from_bytes(bank65[i+1:i+3],'little')<0xb031:reader_candidates.append([0xa000+i,bank65[i],int.from_bytes(bank65[i+1:i+3],'little')])
 assert not reader_candidates,reader_candidates
 checks['typed_row_source_lease']=dict(old_RetireBoth_half_open=[0xb026,0xb031],retained_entry=0xb026,new_stub_bytes=3,reclaimed_contact_bytes=8,old_absolute_entries=incoming,all_bank65_absolute_operand_reader_candidates=reader_candidates,real_ExMenuDone_unchanged=True)
 # Every old Ex row executes against identical source code/meta initialized
 # by its genuine scene ingress, with public input state and flags compared.
 seeds=[]
 for bb in[old,b]:
  m=C.ready(bb);z=C.call(m,0xa7e9 if bb is old else q['route_labels']['CoSceneGate']);assert z['P']&1
  seeds.append(m)
 assert seeds[0].ram[2:4]==seeds[1].ram[2:4]
 legacy=0
 for row in range(37):
  for flags in[0x30,0x71,0xb0,0xf1]:
   pair=[]
   for seed in seeds:
    m=N.fork(seed);z=C.call(m,0xb08c+3*row,flags=flags);pair.append((m,z))
   a,az=pair[0];d,dz=pair[1]
   assert[az[k]for k in['A','X','Y','P']]==[dz[k]for k in['A','X','Y','P']],('Legacy Ex AXYP',row,flags,az,dz)
   assert same_application(a,d),('Legacy Ex complete state',row,flags)
   legacy+=1
 checks['actual_all_37_Ex_row_full_state_ABI_differentials']=legacy
 # Typed37 on raw37 must use its existing final A56F reject and must never
 # execute real ExMenuDone at B0FB. The virtual offset is only a transport ID.
 native=N.NesMPU;visited=set()
 class Trace(native):
  def step(self):
   if self.pc>=0x8000:visited.add((self.memory.rawtags[(self.pc-0x8000)//8192],self.pc))
   return native.step(self)
 N.NesMPU=Trace
 try:
  m=N.fork(seeds[1]);before=[bytes(x)for x in m.ram];z=C.call(m,0xb029,flags=0x71)
 finally:N.NesMPU=native
 assert not z['P']&1 and(z['A'],z['X'],z['Y'])==(83,71,109)and[bytes(x)for x in m.ram]==before,(z,[(k,i,a,d)for k,(a0,d0)in enumerate(zip(before,m.ram))for i,(a,d)in enumerate(zip(a0,d0))if a!=d][:12],sorted((t,p)for t,p in visited if t==3))
 assert(3,0xa56f)in visited and(193,0xb0fb)not in visited
 checks['typed37_existing_Ex_A56F_reject_no_real_B0FB_execution']=True
 # All non-owning raw values, including FF and currently unused IDs, reject
 # before private execution. No table index or application/cache write.
 invalid=0
 for char in range(256):
  if char in[37,39]:continue
  for flags in[0x30,0xf1]:
   m=N.fork(seeds[1]);N.put(m,SelectedCharacter=char);before=[bytes(x)for x in m.ram];before_state=bytes(m[3:11]);z=C.call(m,0xb029,flags=flags)
   assert not z['P']&1 and(z['A'],z['X'],z['Y'])==(83,71,109)and[bytes(x)for x in m.ram]==before and bytes(m[3:11])==before_state,(char,flags,z)
   invalid+=1
 checks['typed37_invalid_foreign_raw_no_private_execution_cases']=invalid
 actors=[Q.fresh(b,route,i)for i in[0,1]]
 # Row11 remains a profile reject even if a valid nearby enemy happens to
 # occupy ObjectOffset. Contact requires the distinct real bridge -> row37.
 body_profiles=0
 for identity,seed in enumerate(actors):
  for slot in range(6):
   m=N.fork(seed);Q.Q.enemy(m,slot=slot);N.put(m,ObjectOffset=slot);before=[bytes(x)for x in m.ram];z=N.invoke(m,'HuBody',x=slot)
   assert not z['P']&1 and[bytes(x)for x in m.ram]==before
   body_profiles+=1
 checks['HuBody11_profile_does_not_contact_ObjectOffset_enemy']=body_profiles
 contacts=0
 for identity,seed in enumerate(actors):
  for dx in range(-10,11):
   for dy in range(-10,11):
    m=N.fork(seed);Q.Q.enemy(m,x=64+dx,y=184+dy)
    z=N.invoke(m,'GuestBodyContactBridge',a=85,x=0,y=91,p=0x31)
    actor=0x42 if identity else 0x2e;hit=abs(dx)<9 and abs(dy)<9
    assert z['P']&1 and bool(m.ram[2][actor+3]&128)==hit and m.ram[2][actor+17]==(200 if hit else 0),(identity,dx,dy,z)
    contacts+=1
 checks['actual_fixed_bridge_dedicated37_original_9px_contacts']=contacts
 poison=0
 for bank in[2,3]:
  for i in range(16):
   m=N.fork(actors[0]);m.ram[bank][0x1fe0+i]^=1;Q.Q.enemy(m);before=[bytes(x)for x in m.ram];z=C.call(m,0xb029)
   assert not z['P']&1 and[bytes(x)for x in m.ram]==before;poison+=1
 checks['typed37_both_complete_header_corruption_rejections']=poison
 # Foreign fixed contact continuation is byte/state identical to the
 # unmodified current gate, not only a direct public-row fixture.
 foreign=0
 prior=C.patched(b,[(74,0xbf03,old['raw'][16+74*8192+0x1f03:16+74*8192+0x1f34])])
 for char in range(39):
  for flags in[0x20,0x31,0x61,0xa9]:
   pair=[]
   for bb in[prior,b]:
    m=N.fork(actors[0]);m.bundle=bb;N.put(m,SelectedCharacter=char,CrossoverBehaviorVersion=1);Q.Q.enemy(m)
    z=N.invoke(m,'GuestBodyContactBridge',a=85,x=0,y=91,p=flags);pair.append((m,z))
   a,az=pair[0];d,dz=pair[1]
   assert[az[k]for k in['A','X','Y','P']]==[dz[k]for k in['A','X','Y','P']]and same_application(a,d),('Foreign native contact',char,flags)
   foreign+=1
 checks['actual_fixed_bridge_foreign_complete_state_ABI_cases']=foreign
 # Every new body-gate/typed/dispatch/auth reached instruction survives real
 # IRQ and Main-busy lagNMI with source state, SMC, maps and final result exact.
 cuts=set();m=actors[1];Q.Q.enemy(m);N.put(m,NmiDisable=1,VRAM_Buffer1_Offset=0)
 class Cuts(native):
  def step(self):
   tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else 0
   if(tag==193 and(0xa740<=self.pc<0xa800 or 0xae00<=self.pc<0xb031))or(tag==202 and 0xbf00<=self.pc<0xbf34):cuts.add((tag,self.pc,self.sp))
   return native.step(self)
 N.NesMPU=Cuts;ref=N.fork(m)
 try:expected=N.invoke(ref,'GuestBodyContactBridge',a=85,x=0,y=91,p=0x30)
 finally:N.NesMPU=native
 counts={};low=255;windows=0
 for kind in['IRQ','lagNMI']:
  for cut in sorted(cuts):
   n=N.fork(m);injected=False
   class Interrupt(native):
    def step(self):
     nonlocal injected,low,windows
     mem=self.memory;tag=mem.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else 0
     if not injected and(tag,self.pc,self.sp)==cut:
      injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(mem.rawtags);private=[bytes(mem.ram[k])for k in[2,3]];scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b])
      assert not self.p&4
      self.irq()if kind=='IRQ'else self.nmi()
      for _ in range(200000):
       low=min(low,self.sp)
       if self.pc==regs[5]and self.sp==regs[4]:break
       assert mem[self.pc]!=0,(kind,cut,hex(self.pc));native.step(self)
      else:raise AssertionError(('ISR return bound',kind,cut))
      map_ok=maps==mem.rawtags
      if not map_ok:
       instruction=bytes(mem[self.pc:self.pc+3]);previous=bytes(mem[self.pc-3:self.pc])
       assert kind=='lagNMI'and instruction[0]in[0x8d,0x8e]and instruction[1:]==bytes.fromhex('1651')and previous==bytes([instruction[0]])+address(b,'CurrentBankC').to_bytes(2,'little')and maps[:2]+maps[3:]==mem.rawtags[:2]+mem.rawtags[3:]and mem.rawtags[2]==mem[address(b,'CurrentBankC')],('Mapper publish window',kind,cut,maps,mem.rawtags)
       map_ok=True;windows+=1
      assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc)and map_ok and private==[bytes(mem.ram[k])for k in[2,3]]and scratch==bytes(mem[3:11])and smc==bytes(mem[0x15a:0x17b]),('ISR preservation',kind,cut)
     return native.step(self)
   N.NesMPU=Interrupt
   try:z=N.invoke(n,'GuestBodyContactBridge',a=85,x=0,y=91,p=0x30)
   finally:N.NesMPU=native
   assert injected and[z[k]for k in['A','X','Y','P']]==[expected[k]for k in['A','X','Y','P']]and n.ram==ref.ram and n.rawtags==ref.rawtags and bytes(n[3:11])==bytes(ref[3:11])and bytes(n[0x15a:0x17b])==bytes(ref[0x15a:0x17b]),('ISR final continuation',kind,cut)
   counts[kind]=counts.get(kind,0)+1
 checks['actual_typed_contact_auth_IRQ_lagNMI']=dict(cuts=counts,minimum_ISR_SP=low,pending_Cbank_publication_windows=windows,final_continuation_exact=True)
 for name in['qualified-native-proofs-1102-v1.json','native-ingress-qualified-1102-v4.json']:
  freeze=json.loads((O/name).read_text())
  for rel,item in freeze['files'].items():assert P.sha((R/rel).read_bytes())==item['SHA256'],rel
 out=dict(passed=True,ROM_written=False,admitted=False,checks=checks,base_ROM_SHA256=P.PIN,scope='In-memory proposed source-funded typed contact37 and shared routes only. Real fixed body bridge, every legacy Ex row, invalid IDs, both complete headers and IRQ/lagNMI execute. No native Mesen/gamepad/stage-clear/install claim.',bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/prepare_bubble_bobble_native_proxy_1102_v5.py',O/'native-proxy.bin',O/'native-proxy-helper.chr',O/'native-proxy-owner.bin',O/'native-proxy-routes.bin',O/'native-proxy-typed-contact.bin',O/'native-proxy-contact-gate.bin']})
 (O/'native-proxy-typed-contact-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks)))


if __name__=='__main__':main()
