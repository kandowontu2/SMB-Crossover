"""Finite actual source/consumer closure and legal menu variants for v9 gate."""
import itertools,json,re
from pathlib import Path
import check_bubble_native_event_1102_v9 as E
import audit_bub_menu_frontend_1102_v1 as F
P=E.P;R=E.R;O=E.O;N=E.N;C=E.C;G=E.G;address=E.address


def main():
 old,new,q,route=E.bundle();raw=old['raw'];origin=16+124*8192;checks={}
 nav=R/'build/bub-menu-navigation-1102-v1';source=(nav/'navigation.s').read_text();labels=P.P.labels(nav/'navigation.lbl');body=(nav/'navigation.bin').read_bytes()
 assert labels['BubMenuUsedEnd']==0xa0d6 and '.res $e0-(*-BubMenuLeft),$ff'in source
 assert raw[origin:origin+224]==body and body[214:]==bytes([255])*10
 ranges=[]
 for n in['Left','Right','Up','Down','Characters','CursorLo']:
  pc=labels['BubMenu'+n];assert pc+33<=0xa0c6;ranges.append(dict(name=n,CPU_half_open=[pc,pc+33],legal_indices=[0,32]))
 assert labels['BubMenuCursorHi']==0xa0c6
 # The only source/table readers are each rebound to the compact ranges;
 # CursorHi is a computation ending RTS immediately before the lease.
 proposal=json.loads((nav/'proposal.json').read_text());readers=[]
 for z in proposal['patches']:
  at=z['offset'];post=bytes.fromhex(z['new']);assert raw[at:at+len(post)]==post,z
  readers.append(dict(function=z['function'],table=z['table'],file_offset=at,actual_hex=post.hex()))
 assert len(readers)==7 and body[213]==0x60
 # All words naming an interior tail address in bank124 are inspected as a
 # conservative operand/pointer census, not treated as executable proof.
 tail_words=[];stomp_interior_words=[];bank=raw[origin:origin+8192]
 for i in range(8191):
  word=int.from_bytes(bank[i:i+2],'little')
  if 0xa0d6<=word<0xa0e0:tail_words.append(dict(CPU=0xa000+i,word=word,preceding_opcode=bank[i-1]if i else None))
  if 0xa4b1<=word<0xa4bb:stomp_interior_words.append(dict(CPU=0xa000+i,word=word,preceding_opcode=bank[i-1]if i else None))
 assert not tail_words and not stomp_interior_words,(tail_words,stomp_interior_words)
 # Exact current source farcall targets, limited to physical PRG. Their
 # FarCallCommon protocol publishes A before the replaced redundant store.
 callers=[];prg=raw[16:1048592]
 for end in[bytes.fromhex('205a01'),bytes.fromhex('4c5a01')]:
  needle=bytes.fromhex('a9b08d6c01a9a48d6d01a9fc')+end
  start=0
  while(pos:=prg.find(needle,start))>=0:
   at=16+pos;callers.append(dict(physical_PRG=pos//8192,CPU=0xa000+pos%8192,file_offset=at,hex=needle.hex(),preceding_A_save=raw[at-3:at].hex()));start=pos+1
 assert {z['physical_PRG']for z in callers}=={119,120,125,127}and all(z['preceding_A_save']=='8d6a01'for z in callers),callers
 assert G.B.location(old,'MegaManBounceVelocity')+4==next(z['file_offset']for z in callers if z['physical_PRG']==127)
 # No source branch/direct entry targets the replaced thunk's interior;
 # typed service12 is the sole selected source stomp operation.
 assert bank[0x179:0x190]==bytes.fromhex('9818690f0a0a0a0a8d6c01a9b669008d6d01a9cf4c0da6')
 assert bank[0x22a:0x230]==bytes.fromhex('ad02604c90a1')
 checks['source_funding_and_actual_finite_readers']=dict(navigation_used=214,allocation=224,source_padding_half_open=[0xa0d6,0xa0e0],all_six_indexed_tables=ranges,actual_readers=readers,tail_word_candidates=tail_words,stomp_interior_word_candidates=stomp_interior_words,exact_PRG_farcall_callers=callers,indirect_contract='Original native FarCallCommon publishes SafecallA before loaded A; serviceY12 produces public27. Remaining indirect/table native service targets and original124 router are unchanged. No legal native path enters the11B thunk interior or navpadding.',foreign_structural_equivalence='Same saved callerP/Y/inputA at old124:A190; first CMP#10 resets classifier NZC. All original foreign dispatch leaves and SMC side effects execute byte-identically. Existing decimal/V/I bits are untouched by new CMP. New39 alone branchesA179.')
 # Resolve every real existing slot/alternate through the current resolver
 # and Select chain, then compare actual native bounce full-state behavior.
 seeds=[N.fresh(bb)for bb in[old,new]];profiles=[];cases=0
 for slot,count in enumerate(F.COUNTS):
  pair=[N.fork(m)for m in seeds]
  for m in pair:N.put(m,CrossoverMenuIndex=slot);F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
  for variant in range(count):
   if variant:
    for m in pair:N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput')
   assert N.get(pair[0],'SelectedCharacter')==N.get(pair[1],'SelectedCharacter')!=39
   profiles.append(dict(slot=slot,variant=variant,raw=N.get(pair[0],'SelectedCharacter'),FmAlts=N.get(pair[0],'FmAlts'),FmGroups=N.get(pair[0],'FmGroups')))
   for speed,flags in itertools.product([0,252,253],[0x30,0xf1]):
    results=[]
    for seed in pair:
     m=N.fork(seed);N.put(m,Player_Y_Speed=speed,OperMode=1,GameEngineSubroutine=8,NmiDisable=1);z=N.invoke(m,'MegaManBounceVelocity',a=speed,x=7,y=91,p=flags);results.append((m,z))
    diff=G.same(results[0][0],results[1][0],results[0][1],results[1][1]);assert not diff,(slot,variant,speed,flags,diff);cases+=1
 assert len(profiles)==91
 checks['actual91_resolved_native_menu_profiles_foreign_full_state']=dict(profiles=profiles,cases=cases,scope='Actual installed resolver and Select-derived native profile state. This is bounce ingress parity, not a full gameplay or stage test for each foreign character.')
 # Current authenticated Ex/Sh owners also take their exact original path.
 warm=[]
 for raw_owner in[37,38]:
  pair=[]
  for bb in[old,new]:
   m=C.ready(bb);N.put(m,SelectedCharacter=raw_owner,OperMode_Task=3,GameEngineSubroutine=8,NumberofLives=2,FmAlts=4,FmGroups=0)
   z=C.call(m,route['CoSceneGate']);assert z['P']&1,(raw_owner,z);pair.append(m)
  prior=G.same(pair[0],pair[1],dict(A=0,X=0,Y=0,P=0),dict(A=0,X=0,Y=0,P=0));assert not prior,(raw_owner,prior)
  for speed in[0,252,253]:
   results=[]
   for seed in pair:
    m=N.fork(seed);N.put(m,Player_Y_Speed=speed,NmiDisable=1);z=N.invoke(m,'MegaManBounceVelocity',a=speed,x=7,y=91,p=0x30);results.append((m,z))
   diff=G.same(results[0][0],results[1][0],results[0][1],results[1][1]);assert not diff,(raw_owner,speed,diff);warm.append(dict(raw=raw_owner,speed=speed,bounce_differences=[]))
 checks['current_authentic_Ex_Sh_scene_and_bounce_parity']=warm
 native=N.NesMPU;irq_counts={};minimum_sp=255
 for raw_owner in[0,22,26,37,38,255]:
  seed=N.fork(seeds[1]);N.put(seed,SelectedCharacter=raw_owner,OperMode=1,GameEngineSubroutine=8,NmiDisable=1,Player_Y_Speed=253);cuts=set()
  class CutTrace(native):
   def step(self):
    if self.pc>=0x8000 and self.memory.rawtags[(self.pc-0x8000)//8192]==252 and(0xa4b0<=self.pc<0xa4bb or 0xa0d6<=self.pc<0xa0e0):cuts.add((self.pc,self.sp))
    return native.step(self)
  N.NesMPU=CutTrace;ref=N.fork(seed)
  try:expected=N.invoke(ref,'MegaManBounceVelocity',a=253,x=7,y=91,p=0x30)
  finally:N.NesMPU=native
  for kind,cut in itertools.product(['IRQ','lagNMI'],sorted(cuts)):
   m=N.fork(seed);injected=False
   class Interrupt(native):
    def step(self):
     nonlocal injected,minimum_sp
     mem=self.memory
     if not injected and self.pc>=0x8000 and mem.rawtags[(self.pc-0x8000)//8192]==252 and(self.pc,self.sp)==cut:
      injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(mem.rawtags);private=[bytes(v)for v in mem.ram];scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b]);assert not self.p&4
      self.irq()if kind=='IRQ'else self.nmi()
      for _ in range(200000):
       minimum_sp=min(minimum_sp,self.sp)
       if self.pc==regs[5]and self.sp==regs[4]:break
       assert mem[self.pc]!=0;native.step(self)
      else:raise AssertionError('Foreign ISR return')
      assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc)and maps==mem.rawtags and private==[bytes(v)for v in mem.ram]and scratch==bytes(mem[3:11])and smc==bytes(mem[0x15a:0x17b])
     return native.step(self)
   N.NesMPU=Interrupt
   try:z=N.invoke(m,'MegaManBounceVelocity',a=253,x=7,y=91,p=0x30)
   finally:N.NesMPU=native
   assert injected and[z[n]for n in['A','X','Y','P']]==[expected[n]for n in['A','X','Y','P']]and m.ram==ref.ram and m.rawtags==ref.rawtags
   irq_counts[kind]=irq_counts.get(kind,0)+1
 checks['foreign_branch_actual_IRQ_lagNMI']=dict(raw_owners=[0,22,26,37,38,255],cuts=irq_counts,minimum_ISR_SP=minimum_sp)
 bindings=[Path(__file__),R/'tools/audit/measure_bubble_native_bounce_gate_1102_v9.py',R/'tools/audit/prepare_bub_menu_navigation_1102_v1.py',nav/'navigation.s',nav/'navigation.bin',nav/'navigation.lbl',nav/'proposal.json',R/'src/megaman_environment.s',R/'src/x5_bounce.s',R/'src/macros.inc']
 bindings=[p for p in bindings if p.is_file()]
 out=dict(passed=True,ROM_written=False,shared_mutation=False,base_ROM_SHA256=G.B.PIN,checks=checks,bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in bindings},scope='Exact finite source/readers and current legal foreign ABI closure for the proposed10B/11B event gate. No ROM composition, native qualification or production admission.')
 (O/'native-event-v9-closure.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,profiles=len(profiles),foreign_profile_cases=cases,authenticated_owner_cases=len(warm),tail_reader_candidates=0,stomp_interior_candidates=0,actual_farcall_callers=callers,foreign_IRQ_NMI=checks['foreign_branch_actual_IRQ_lagNMI'])))


if __name__=='__main__':main()
