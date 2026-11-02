"""Actual v6 public backdrop/status/menu ABI and new-code IRQ continuations."""
import itertools,json
from pathlib import Path
import check_bubble_bobble_native_proxy_1102_v5 as Q
P=Q.P;C=Q.C;N=Q.N;R=Q.R;O=Q.O;address=Q.address


def bundle():
 b,prior,route=Q.bundle();q=json.loads((O/'native-visible-layout.json').read_text());raw=bytearray(b['raw']);image=(O/'native-visible.bin').read_bytes()
 for i,page in enumerate([301,305,337,362,363,440,819,666]):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
 raw[1048592+441*1024:1048592+442*1024]=(O/'native-visible-helper.chr').read_bytes();owner=(O/'native-visible-owner.bin').read_bytes();raw[16+65*8192+0xe00:16+65*8192+0xe00+len(owner)]=owner
 b['raw']=bytes(raw);return b,q,route


def main():
 b,q,route=bundle();old,_,_=Q.bundle();checks={};seeds=[Q.fresh(b,route,i)for i in[0,1]];oldseeds=[Q.fresh(old,route,i)for i in[0,1]]
 # Exact native top-status input, including attribute2 header, labels/coin and
 # terminator. The original callback edits an existing message, not a queue.
 loc=Q.Q.Q.location(b,'TopStatusBarLine');data=b['raw'][loc:loc+120];native=data[:data.index(255)]+bytes([0]);assert native[:4]==bytes.fromhex('23c07faa')and len(native)<=84
 status=0;messages=0
 for identity,offset,msg,flags in itertools.product([0,1],[0,1,16,40,44,77],[0,1,2,4,255],[0x30,0xf1]):
  pair=[]
  for seed in[oldseeds[identity],seeds[identity]]:
   m=N.fork(seed);N.put(m,VRAM_Buffer1_Offset=offset,OperMode=1)
   for i in range(84):m[address(b,'VRAM_Buffer1')+i]=(i*13+17)&255
   m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+len(native)]=native;before=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84]);scratch=bytes(m[3:11]);z=N.invoke(m,'CrossoverPatchStatusName',a=msg,x=7,y=73,p=flags);pair.append((m,z,before,scratch))
  a,az,_,_=pair[0];m,z,before,scratch=pair[1]
  assert[z[k]for k in['A','X','Y','P']]==[az[k]for k in['A','X','Y','P']],('Status AXYP',identity,offset,msg,flags,z,az)
  expected=bytearray(before)
  if msg==0:expected[11:18]=bytes([11,24 if identity else 30,11,36,36,36,36]);status+=1
  else:messages+=1
  assert bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84])==expected and N.get(m,'VRAM_Buffer1_Offset')==offset and bytes(m[3:11])==scratch,(identity,offset,msg,flags)
 checks['actual_status_native_header_attributes_labels_terminator_preserved']=dict(A0_name7_only_cases=status,other_message_noop_cases=messages,nonzero_buffer_offsets=[1,16,40,44,77],native_message=list(native))
 # Actual whole WriteGameText confirms native copy -> callback -> final text,
 # with no hand-created status message used to stand in for that ingress.
 actual=0
 for identity,m in enumerate(seeds):
  m=N.fork(m);N.put(m,NumberOfPlayers=0);N.invoke(m,'WriteGameText',a=0,x=0,y=0)
  expected=bytearray(native);expected[11:18]=bytes([11,24 if identity else 30,11,36,36,36,36])
  assert bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+len(native)])==expected
  actual+=1
 checks['actual_native_WriteGameText_top_message_ingress']=actual
 menu=0
 for identity,offset,flags in itertools.product([0,1],[0,16,24,44,45,77],[0x30,0xf1]):
  pair=[]
  for seed in[oldseeds[identity],seeds[identity]]:
   m=N.fork(seed);N.put(m,OperMode=0,VRAM_Buffer1_Offset=offset);m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84]=bytes([0xa5])*84
   z=C.call(m,0xb08c+18*3,flags=flags);pair.append((m,z))
  a,az=pair[0];m,z=pair[1]
  assert[z[k]for k in['A','X','Y','P']]==[az[k]for k in['A','X','Y','P']]and bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84])==bytes(a[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84])and N.get(m,'VRAM_Buffer1_Offset')==N.get(a,'VRAM_Buffer1_Offset')and bytes(m[3:11])==bytes(a[3:11]);menu+=1
 checks['legacy_encoded_Menu18_exact_public_ABI_buffer_differentials']=menu
 color_ABI={}
 for identity,flags in itertools.product([0,1],[0x30,0xf1]):
  m=N.fork(oldseeds[identity]);N.put(m,VRAM_Buffer1_Offset=0);z=N.invoke(m,'GetPlayerColors',a=0xa5,x=7,y=73,p=flags)
  color_ABI[identity,flags]=([z[k]for k in['A','X','Y','P']],bytes(m[0x15a:0x17b]))
 colors=0;native_colors=[0x22,0x22,0x0f,0x0f,0x0f,0x22,0x0f,0x0f]
 for identity,area,bg,offset,flags in itertools.product([0,1],range(4),range(8),[0,16,40,44,45,83,255],[0x30,0xf1]):
  m=N.fork(seeds[identity]);N.put(m,AreaType=area,BackgroundColorCtrl=bg,VRAM_Buffer1_Offset=offset);m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84]=bytes([0xa5])*84
  m[3:11]=list(range(0xa1,0xa9));scratch=bytes(m[3:11]);start=len(m.writes);z=N.invoke(m,'GetPlayerColors',a=0xa5,x=7,y=73,p=flags)
  expected=bytearray([0xa5]*84);rgb=[44,35,48]if identity else[42,38,48];own=[63,17 if identity else 29,3,*rgb]
  if offset<=40:packet=[63,16,1,native_colors[bg if bg else area],*own,0];new_offset=offset+10
  elif offset<45:packet=[*own,0];new_offset=offset+6
  else:packet=[];new_offset=offset
  if packet:expected[offset:offset+len(packet)]=bytes(packet)
  assert bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84])==expected and N.get(m,'VRAM_Buffer1_Offset')==new_offset and bytes(m[3:11])==scratch,(identity,area,bg,offset,flags,z)
  assert([z[k]for k in['A','X','Y','P']],bytes(m[0x15a:0x17b]))==color_ABI[identity,flags],('Colors AXYP/SMC',identity,area,bg,offset,flags,z)
  # Every new write in the native buffer's enclosing memory interval remains
  # within the exact84-byte native queue. Busy inputs cannot cross into OAM.
  writes=[at for at,value in m.writes[start:]if address(b,'VRAM_Buffer1')<=at<address(b,'VRAM_Buffer1')+256]
  assert all(at<address(b,'VRAM_Buffer1')+84 for at in writes),(offset,writes)
  colors+=1
 checks['actual_all4areas_8background_controls_native_backdrop_safe_RGB']=dict(cases=colors,offsets=[0,16,40,44,45,83,255],universal_only_native_BackgroundColors=True,source_opaque_RGB_only_3F11_or3F1D=True,busy41_44_retains_original_opaque_only=True)
 # Main transport remains exact; only immutable source pointers/code image
 # changed. The original actor and native coordinates compare each update.
 motion=0
 for identity in[0,1]:
  pair=[N.fork(oldseeds[identity]),N.fork(seeds[identity])]
  for m in pair:
   N.put(m,CurrentPlayer=0,AreaParserTaskNum=7,TimerControl=0,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0)
   for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v
  for frame in range(40):
   for m in pair:N.put(m,FrameCounter=frame,SavedJoypadBits=1|(128 if frame==10 else 0),SavedJoypad1Bits=1|(128 if frame==10 else 0),VRAM_Buffer1_Offset=0);N.invoke(m,'GameCoreRoutine',x=0,y=0)
   a,m=pair;assert a.ram[2][:0x320]==m.ram[2][:0x320]and[(N.get(a,n),N.get(m,n))for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]==[(N.get(a,n),N.get(a,n))for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']];motion+=1
 checks['actual_Main_original_actor_world_state_v5_v6_differentials']=motion
 # Each reached new helper/shim/reclaimed-tail instruction, physical mapping
 # and SP, survives actual IRQ and lagNMI; full continuations remain exact.
 native=N.NesMPU;cuts_total={};low=255
 for service in['GetPlayerColors','CrossoverPatchStatusName']:
  m=N.fork(seeds[1]);N.put(m,NmiDisable=1,VRAM_Buffer1_Offset=0,BackgroundColorCtrl=0,AreaType=1);cuts=set()
  class Trace(native):
   def step(self):
    mem=self.memory;tag=mem.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else 0
    if(tag==2 and 0xd320<=self.pc<0xd400)or(tag==3 and(self.pc>=0xbfd1 or 0xa074<=self.pc<0xa080 or 0xa0e2<=self.pc<0xa0ef)):cuts.add((tag,self.pc,self.sp))
    return native.step(self)
  N.NesMPU=Trace;ref=N.fork(m)
  try:expected=N.invoke(ref,service,a=0,x=7,y=73,p=0x30)
  finally:N.NesMPU=native
  for kind in['IRQ','lagNMI']:
   for cut in sorted(cuts):
    n=N.fork(m);injected=False
    class Interrupt(native):
     def step(self):
      nonlocal injected,low
      mem=self.memory;tag=mem.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else 0
      if not injected and(tag,self.pc,self.sp)==cut:
       injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(mem.rawtags);private=[bytes(x)for x in mem.ram];scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b]);assert not self.p&4
       self.irq()if kind=='IRQ'else self.nmi()
       for _ in range(200000):
        low=min(low,self.sp)
        if self.pc==regs[5]and self.sp==regs[4]:break
        assert mem[self.pc]!=0;native.step(self)
       else:raise AssertionError(('ISR return',service,kind,cut))
       assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc)and maps==mem.rawtags and private==[bytes(x)for x in mem.ram]and scratch==bytes(mem[3:11])and smc==bytes(mem[0x15a:0x17b]),(service,kind,cut)
      return native.step(self)
    N.NesMPU=Interrupt
    try:z=N.invoke(n,service,a=0,x=7,y=73,p=0x30)
    finally:N.NesMPU=native
    assert injected and[z[k]for k in['A','X','Y','P']]==[expected[k]for k in['A','X','Y','P']]and n.ram==ref.ram and n.rawtags==ref.rawtags and bytes(n[3:11])==bytes(ref[3:11])and bytes(n[0x15a:0x17b])==bytes(ref[0x15a:0x17b]),('Final IRQ continuation',service,kind,cut)
    cuts_total[kind]=cuts_total.get(kind,0)+1
 checks['actual_new_helper_shims_IRQ_lagNMI']=dict(cuts=cuts_total,minimum_ISR_SP=low)
 poison=0
 for bank in[2,3]:
  for i in range(16):
   m=N.fork(seeds[0]);m.ram[bank][0x1fe0+i]^=1;before=[bytes(x)for x in m.ram];z=C.call(m,0xb08c+26*3);assert not z['P']&1 and before==[bytes(x)for x in m.ram];poison+=1
 checks['both_complete_headers_authenticate_v6_payload_helper']=poison
 out=dict(passed=True,ROM_written=False,admitted=False,base_ROM_SHA256='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60',checks=checks,scope='Final v6 public native callbacks, wholeWriteGameText and typedMenu18, allarea/backdrop selectors and boundedqueue states, originalMain/world state and actualISR instruction cuts. Exactsourcebody preserved. RealBub/Bobnativecold/gameplay remainsroot qualification.',bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/prepare_bubble_bobble_native_visible_1102_v6.py',O/'native-visible.bin',O/'native-visible-helper.chr',O/'native-visible-owner.bin',O/'native-visible-layout.json']})
 (O/'native-visible-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks)))


if __name__=='__main__':main()
