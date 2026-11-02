"""Execute proposed resident routes only in an exact current CPU cartridge bus."""
import json,sys
from pathlib import Path
import prepare_bubble_bobble_common_cold_1102_v4 as P
import check_bubble_bobble_common_cold_1102_v4 as C
import check_hogan_current_bounded_v1 as N
from check_tmnt_render_oa import address,location
from check_excitebike_router_1101_v1 import endpoint,comparable
O=P.O


def bundle():
 old=P.scoped_load(P.ROM);assert P.sha(old['raw'])==P.PIN
 owner=P.P.labels(O/'common-owner.lbl');route=P.P.labels(O/'common-routes.lbl')
 parts=[(123,0xaf40,'common-split.bin'),(123,0xb9d6,'common-split-map.bin'),(65,0xae00,'common-owner.bin'),(65,0xa740,'common-routes.bin'),(65,0xb013,'common-route-scene-gate.bin'),(65,0xb026,'common-route-retire-stub.bin'),(65,0xb031,'common-route-foreign.bin'),(65,0xb062,'common-route-scene-own.bin')]
 b=C.patched(old,[(bank,pc,(O/name).read_bytes())for bank,pc,name in parts]);raw=bytearray(b['raw'])
 reset=16+65*8192+0x1100;assert raw[reset:reset+5]==bytes.fromhex('2034ae3860')
 raw[reset+1:reset+3]=owner['CoRetire'].to_bytes(2,'little')
 # Actual InitScreen farcall operand, still inside its original instruction span.
 at=location(old,'InitScreen')+8
 expected=bytes.fromhex('8d6a01a9e98d6c01a9a78d6d01a9c1205a01');assert raw[at:at+len(expected)]==expected
 raw[at+4]=route['CoSceneGate']&255;raw[at+9]=route['CoSceneGate']>>8
 image=(O/'native-private.bin').read_bytes()
 for i,page in enumerate([301,305,337,362,363,440,819,666]):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
 raw[1048592+441*1024:1048592+442*1024]=(O/'native-helper.chr').read_bytes()
 b['raw']=bytes(raw);b['syms']=dict(old['syms']);b['segs']=dict(old['segs'])
 b['segs']['bub_routes_resident']={'start':str(0xa000),'ooffs':str(16+65*8192)}
 for name,pc in {**owner,**route,'CoOldScene':0xa7e9}.items():b['syms'][name]={'val':str(pc),'seg':'bub_routes_resident'}
 for row in range(37):b['syms'][f'CoService{row}']={'val':str(0xb08c+3*row),'seg':'bub_routes_resident'}
 return old,b,owner,route


def actor_ready(b,identity=0):
 m=C.ready(b);N.put(m,SelectedCharacter=39,FmGroups=identity<<7,OperMode_Task=3,GameEngineSubroutine=8,GamePauseStatus=0,NumberofLives=2,FrameCounter=0,SavedJoypadBits=0,Player_X_Position=64,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,CurrentOAMOffset=24,GuestOamRotationActive=0,VRAM_Buffer1_Offset=0)
 for name in['Block_Buffer_1','Block_Buffer_2']:
  for row in range(13):
   for col in range(16):m[address(b,name)+16*row+col]=0x54 if row>=11 else 0
 for name in['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_Y_HighPos']:
  for i in range(6):m[address(b,name)+i]=0
 return m


def main():
 old,new,owner,route=bundle();checks={};seeds=[N.fresh(b)for b in[old,new]]
 # The actual already-installed PRG79 classifier routes odd raw39 to the
 # existing Ex veneers. No bank79 instruction or table needs changing.
 foreign=0;newroutes=0
 for row in range(36):
  for b in[old,new]:b['syms']['CoRouterProbe']=dict(b['syms']['HuMovement'],val=str(0xb600+16*row))
  for char in range(40):
   for flags in[0x30,0xf1]:
    pair=[]
    for seed in seeds:
     m=N.fork(seed);N.put(m,SelectedCharacter=char,RdVariant=0,FmAlts=0);pair.append(endpoint(m,'CoRouterProbe',p=flags))
    assert comparable(pair[0])==comparable(pair[1]),('Foreign endpoint ABI',char,row,flags,pair)
    if char==39:
     if row==32:assert pair[1]['stop_pc']==address(new,'HuNativeWorldPalette')
     else:assert pair[1]['target']==[193,0xb08c+3*row],(row,pair[1])
     newroutes+=1
    else:foreign+=1
 checks['unchanged_actual_PRG79_endpoints']=dict(foreign_cases=foreign,raw39_cases=newroutes,PRG79_bytes_changed=0)
 # Execute the proposed actual scene gate, full nine-row loader, dispatcher,
 # private row36 and original actor initialization. Both source identities.
 actors=[]
 for identity in[0,1]:
  m=actor_ready(new,identity);r=C.call(m,route['CoSceneGate']);assert r['P']&1
  assert m.ram[2][0x300]==identity and m.ram[2][0x304]==0xa7 and m.ppu_reads==18450
  assert m.ram[2][0x1fe0]==0xa7 and m.ram[3][0x1fe0]==0xa7
  actors.append(m)
 checks['actual_proposed_scene_cold_original_Fresh']=dict(identities=2,rows=9,code_bytes=8192,immutable_helper_bytes=1024,buffered_PPU_reads=18450)
 # A direct authenticated private vector and the genuine resident veneer
 # must return the same AXYP and produce identical private/native state.
 vectors=0
 for identity,m in enumerate(actors):
  for row in range(37):
   if row==19:continue # Genuine ROM-only invalidation deliberately bypasses private code.
   direct=N.fork(m);transport=N.fork(m)
   for n in[direct,transport]:n.raw_page(2,2);n[address(new,'CurrentBankC')]=2
   a=C.call(direct,0xa000+3*row,bank=3);b=C.call(transport,0xb08c+3*row)
   assert [a[k]for k in['A','X','Y','P']]==[b[k]for k in['A','X','Y','P']],('Vector ABI',identity,row,a,b)
   assert direct.ram[2:4]==transport.ram[2:4],('Vector private state',identity,row)
   assert bytes(direct[3:11])==bytes(transport[3:11])and direct.rawtags==transport.rawtags
   vectors+=1
 checks['actual_resident_to_private_vector_differentials']=vectors
 poison=0
 for bank in[2,3]:
  for i in range(16):
   n=N.fork(actors[0]);n.ram[bank][0x1fe0+i]^=1;before=[bytes(r)for r in n.ram]
   r=C.call(n,0xb08c);assert not r['P']&1 and(r['A'],r['X'],r['Y'])==(83,71,109)and before==[bytes(r)for r in n.ram];poison+=1
 checks['actual_dispatch_complete_header_rejections']=poison
 # Old raw37 scene remains state/ABI equivalent to the exact current scene.
 ex=[]
 for b in[old,new]:
  m=C.ready(b);r=C.call(m,0xa7e9 if b is old else route['CoSceneGate']);ex.append((m,r))
 assert ex[0][0].ram[2:4]==ex[1][0].ram[2:4]
 assert [ex[0][1][k]for k in['A','X','Y','P']]==[ex[1][1][k]for k in['A','X','Y','P']]
 checks['actual_existing_Ex_scene_exact_state_and_ABI']=True
 # IRQ and Main-busy NMI at each reached dispatcher/auth instruction/SP.
 # Use a real preserving Colors leaf; no fixture success leaf is installed.
 native=N.NesMPU;cuts=set();m=actors[1];N.put(m,NmiDisable=1,VRAM_Buffer1_Offset=0)
 class Trace(native):
  def step(self):
   if self.memory.rawtags[1]==193 and(0xa740<=self.pc<0xa7f2 or 0xae00<=self.pc<0xb013):cuts.add((self.pc,self.sp))
   return native.step(self)
 N.NesMPU=Trace
 reference=N.fork(m)
 try:expected=C.call(reference,0xb08c+26*3,flags=0x30)
 finally:N.NesMPU=native
 counts={};low=255;publish_windows=0
 for kind in['IRQ','lagNMI']:
  for cut in sorted(cuts):
   n=N.fork(m);injected=False
   class Interrupt(native):
    def step(self):
     nonlocal injected,low,publish_windows
     mem=self.memory
     if not injected and mem.rawtags[1]==193 and(self.pc,self.sp)==cut:
      injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(mem.rawtags);private=[bytes(mem.ram[k])for k in[2,3]];scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b])
      assert not self.p&4
      self.irq()if kind=='IRQ'else self.nmi()
      for _ in range(200000):
       low=min(low,self.sp)
       if self.pc==regs[5]and self.sp==regs[4]:break
       assert mem[self.pc]!=0,(kind,cut,hex(self.pc));native.step(self)
      else:raise AssertionError(('ISR return bound',kind,cut))
      after=(self.a,self.x,self.y,self.p,self.sp,self.pc)
      changed=[(k,i,a,z)for k,old in zip([2,3],private)for i,(a,z)in enumerate(zip(old,mem.ram[k]))if a!=z]
      # Native NMI restores the published CurrentBankC. At the precise
      # software-store/hardware-store boundary it can finish that pending
      # publication before the foreground STA$5116 repeats it. No C-bank
      # instruction/data read occurs between these adjacent instructions.
      map_ok=maps==mem.rawtags
      if not map_ok:
       instruction=bytes(mem[self.pc:self.pc+3]);prior=bytes(mem[self.pc-3:self.pc])
       assert kind=='lagNMI' and instruction[0]in[0x8d,0x8e]and instruction[1:]==bytes.fromhex('1651')and prior==bytes([instruction[0]])+address(new,'CurrentBankC').to_bytes(2,'little')and maps[0:2]+maps[3:]==mem.rawtags[0:2]+mem.rawtags[3:]and mem.rawtags[2]==mem[address(new,'CurrentBankC')],('Mapper publication window',kind,cut,maps,mem.rawtags)
       map_ok=True;publish_windows+=1
      assert regs==after and map_ok and not changed and scratch==bytes(mem[3:11])and smc==bytes(mem[0x15a:0x17b]),(kind,cut,regs,after,maps,mem.rawtags,changed[:8],scratch.hex(),bytes(mem[3:11]).hex(),smc.hex(),bytes(mem[0x15a:0x17b]).hex())
     return native.step(self)
   N.NesMPU=Interrupt
   try:r=C.call(n,0xb08c+26*3,flags=0x30)
   finally:N.NesMPU=native
   assert injected and[r[k]for k in['A','X','Y','P']]==[expected[k]for k in['A','X','Y','P']],(kind,cut,r,expected)
   assert n.ram[2:4]==reference.ram[2:4]and n.rawtags==reference.rawtags and bytes(n[3:11])==bytes(reference[3:11]),('Final ISR continuation',kind,cut)
   counts[kind]=counts.get(kind,0)+1
 checks['actual_dispatch_auth_IRQ_lagNMI']=dict(cuts=counts,minimum_ISR_SP=low,NMI_completes_pending_Cbank_publication_windows=publish_windows,final_continuation_exact=True)
 q=dict(passed=True,ROM_written=False,shared_source_written=False,admitted=False,base_ROM_SHA256=P.PIN,in_memory_candidate_SHA256=P.sha(new['raw']),checks=checks,scope='Actual current bank79 endpoints remain unchanged; proposed bank65 resident/auth/scene and real private vectors execute in a memory-only cartridge. Full loader and original Fresh run; IRQ/Main-busy NMI preserve reached dispatch/auth continuations. Actual game Main, contact/AI/birth/native body/terrain admission and full-stage emulator remain pending.',bindings={p.relative_to(P.R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),P.R/'tools/audit/prepare_bubble_bobble_common_routes_1102_v5.py',O/'common-routes.bin',O/'common-route-foreign.bin',O/'common-route-scene-gate.bin',O/'common-route-scene-own.bin',O/'common-route-retire-stub.bin',O/'common-owner.bin',O/'common-split.bin',O/'common-split-map.bin',O/'native-private.bin',O/'native-helper.chr']})
 (O/'common-routes-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks,ROM_written=False)))


if __name__=='__main__':main()
