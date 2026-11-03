"""Real RAM2/3 successor policies, earned native defeat and actual ISR cuts."""
from collections import Counter
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_successor_manifest_1102_v26 as M
import check_prince_native_proxy_1102_v41 as V
H,O,N,Q=V.H,V.O,V.N,V.Q


class ControllerBus(N.Bus):
 def __getitem__(self,i):
  if isinstance(i,int)and i in [0x4016,0x4017]:
   index=getattr(self,'serial_index',[0,0]);port=i-0x4016;bit=(getattr(self,'controller_pad',0)>>(7-min(index[port],7)))&1 if port==0 and index[port]<8 else 0;index[port]+=1;self.serial_index=index;return bit
  return super().__getitem__(i)
 def __setitem__(self,i,value):
  if isinstance(i,int)and i==0x4016 and value&1:self.serial_index=[0,0]
  return super().__setitem__(i,value)


def host(base):
 h=H.host(base);h.m.ram[3][:0x1fdf]=(O/'native-runtime-v42.bin').read_bytes();meta=(O/'native-metadata-v42.bin').read_bytes();h.s[0x800:0x800+len(meta)]=meta;h.lab.update(json.loads((O/'native-labels-v42.json').read_text()));h.source('PpNativeInit');assert not h.callbacks
 return h


def invoke(h,name,args=(83,71,109,0x21),interrupt=None):
 h.map();m=h.m;m.controller_pad=N.get(m,'SavedJoypad1Bits');c=N.NesMPU(memory=m,pc=h.lab[name]);c.a,c.x,c.y,c.p=args;c.sp=224;c.stPushWord(0x5aff);low=c.sp;cuts=set();injected=False;calls=Counter()
 native={}
 for n in ['ShellOrBlockDefeat','KillPlayer']:
  pc=H.W.address(h.b,n);native[pc,((H.W.location(h.b,n)-16)//8192)|128]=n
 for _ in range(150000):
  if c.pc==0x5b00:break
  low=min(low,c.sp);cut=(c.pc,c.sp,m.rawtags[1]);tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
  if 0xd8f1<=c.pc<0xdfa2 or 0xbd22<=c.pc<0xbd3e or 0x15a<=c.pc<0x17b:cuts.add(cut)
  if(c.pc,tag)in native:calls[native[c.pc,tag]]+=1
  if interrupt is not None and not injected and cut==interrupt[1]:
   injected=True;registers=(c.a,c.x,c.y,c.p,c.sp,c.pc);maps=m.rawtags[:];state=[bytes(m.ram[k])for k in [2,3]];scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);writes=len(m.ram_writes);assert not c.p&4
   c.irq()if interrupt[0]=='IRQ'else c.nmi()
   for _ in range(200000):
    low=min(low,c.sp)
    if(c.pc,c.sp)==(registers[5],registers[4]):break
    assert m[c.pc]!=0,('Placed ISR BRK',interrupt,hex(c.pc));c.step()
   else:raise AssertionError(('Placed ISR bound',interrupt))
   assert not any(bank in [2,3]for bank,at,value in m.ram_writes[writes:])
   assert registers[:3]==(c.a,c.x,c.y)and registers[3]&0xef==c.p&0xef and registers[4:]==(c.sp,c.pc)
   assert state==[bytes(m.ram[k])for k in [2,3]]and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b])
   if maps!=m.rawtags:
    op=bytes(m[c.pc:c.pc+3]);assert op==bytes.fromhex('8d1551')and m.rawtags[1]==N.get(m,'CurrentBank')and all(maps[k]==m.rawtags[k]for k in [0,2,3])
  assert m[c.pc]!=0,('Placed private BRK',name,hex(c.pc));c.step()
 else:raise AssertionError(('Placed private bound',name,hex(c.pc)))
 assert c.sp==224 and(interrupt is None or injected)
 return dict(regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,minSP=low,cuts=cuts,calls=dict(calls))


def snapshot(h):
 for name in ['writes','ram_writes','ppu_log','blocked']:setattr(h.m,name,[])
 return N.fork(h.m)


def main():
 base,_,_,_=M.bundle();H.W.PIN=M.A.PIN;N.Bus=ControllerBus;proof=json.loads((O/'native-link-measurement-v42.json').read_text());assert proof['measured']and proof['remaining_before_shared_clock']==46
 for path,digest in proof['bindings'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
 counts=Counter();cost=[];minimum=224;episodes=[];scenarios=[]
 # No terrain phase is pre-run here. Correct NativeInit's floor reference
 # prevents the retained v41 first-control128->176 discontinuity.
 for sword in [0,1,2]:
  h=host(base);h.s[0x6ee]=sword;V.enemy(h,0);rows=[];defeats=0;last=None
  for frame in range(360):
   N.put(h.m,FrameCounter=frame&255,SavedJoypad1Bits=128 if frame>=40 else 0)
   before=snapshot(h);got=invoke(h,'PpNativeTick');defeats+=got['calls'].get('ShellOrBlockDefeat',0);minimum=min(minimum,got['minSP']);cost.append(got['CPU'])
   if frame%4==0:rows.append(dict(Main=frame,X=h.x(),Y=h.s[0x611],action=h.s[0x616],pose=h.s[0x617],sword=h.s[0x6ee],HP=h.s[0x6cf],guardHP=h.s[0x6d0],guardDead=h.s[0x6de],nativeState=V.native(h,'Enemy_State')))
   assert h.s[0x611]==128 or not sword,('First controls vertical discontinuity',sword,rows)
   if got['calls'].get('ShellOrBlockDefeat'):
    last=before;break
  assert bool(defeats)==bool(sword)and defeats in [0,1]and N.get(h.m,'NumberofLives')==2
  if sword==1:scenarios.append(('earned-original-strike','PpNativeTick',h,last,(83,71,109,0x21)))
  episodes.append(dict(explicit_CPU_fixture_sword=sword,Main_updates=frame+1,real_native_defeats=defeats,trace=rows));counts['original_battle_episodes']+=1
 # Exact actual defender admission, HP/mode boundaries and caller ABI.
 for sword,hp,action,flags in itertools.product([0,1,2],range(6),[0,62,69,74],[0x20,0x61]):
  h=host(base);h.s[0x6ee]=sword;h.s[0x6cf]=hp;h.s[0x616]=action;h.s[0x617]=171;before=bytes(h.s);out=invoke(h,'PpNativeContact',(83,71,109,flags));minimum=min(minimum,out['minSP'])
  expect=hp if not hp or action in [62,69,74]else max(0,hp-(1 if sword==2 else 5))
  assert h.s[0x6cf]==expect,(sword,hp,action,h.s[0x6cf],expect)
  assert out['regs'][:3]==[83,71,109]and out['regs'][3]&0xef==(flags|1)&0xef and out['regs'][4]==224
  counts['original_incoming_ABI']+=1
 # Native ForceInjury actually consumes Z, so zero HP must still return
 # nonzero status until original contact/death has completed.
 h=host(base)
 for hp in range(6):
  h.s[0x6cf]=hp;out=invoke(h,'PpNativeHealthStatus');assert out['regs'][0]==1 and not out['regs'][3]&2 and out['regs'][3]&1;counts['injury_status']+=1
 # Player palette queue: all byte offsets, complete overflow rejection, no
 # universal-backdrop/native enemy-palette mutation, exact caller AXYP.
 at=H.W.address(base,'VRAM_Buffer1');off=H.W.address(base,'VRAM_Buffer1_Offset')
 for offset in range(256):
  h=host(base);h.m[at:at+256]=bytes([0x5a])*256;h.m[off]=offset;before=bytes(h.m[at:at+256]);out=invoke(h,'PpNativeColors');assert out['regs'][:3]==[83,71,109]and out['regs'][3]&0xef==0x21 and out['regs'][4]==224
  if offset<78:assert bytes(h.m[at+offset:at+offset+7])==bytes.fromhex('3f110327162000')and h.m[off]==offset+6
  else:assert bytes(h.m[at:at+256])==before and h.m[off]==offset
  counts['palette_queue_offsets']+=1
 # Actual source combat death animation must complete; environmental4CE2
 # is a separate genuine source terminal flag, never a host timer.
 h=host(base);h.s[0x6ee]=0;invoke(h,'PpNativeContact');assert h.s[0x6cf]==0 and h.s[0x616]==85;death=[];kills=0
 for frame in range(80):
  N.put(h.m,FrameCounter=frame&255,SavedJoypad1Bits=0);seed=snapshot(h);out=invoke(h,'PpNativeTick');kills+=out['calls'].get('KillPlayer',0)
  if frame%4==0:death.append(dict(Main=frame,pose=h.s[0x617],engine=N.get(h.m,'GameEngineSubroutine')))
  if kills:scenarios.append(('original-death-final-pose','PpNativeTick',h,seed,(83,71,109,0x21)));break
 assert kills==1 and h.s[0x617]==185 and N.get(h.m,'GameEngineSubroutine')==11
 h=host(base);h.s[0x6cf]=0;h.s[0x4ce]=2;out=invoke(h,'PpNativePitDeath');assert out['calls']=={'KillPlayer':1};counts['source_environmental_terminal']+=1
 h=host(base);h.s[0x6ee]=2;h.s[0x616]=62;scenarios.append(('original-parry','PpNativeContact',h,snapshot(h),(83,71,109,0x21)))
 cuts_count=Counter();scenario_rows=[]
 for scenario,name,h,seed,args in scenarios:
  h.m=N.fork(seed);h.s=h.m.ram[2];ref=invoke(h,name,args);final=[bytes(h.m.ram[k])for k in [2,3]];maps=h.m.rawtags[:];scratch=bytes(h.m[3:11]);smc=bytes(h.m[0x15a:0x17b]);cuts=sorted(ref['cuts']);scenario_rows.append(dict(name=scenario,cuts=len(cuts),actual_native_calls=ref['calls']))
  for kind in ['IRQ','lagNMI']:
   for cut in cuts:
    h.m=N.fork(seed);h.s=h.m.ram[2];out=invoke(h,name,args,(kind,cut));minimum=min(minimum,out['minSP'])
    regs=out['regs'];want=ref['regs'];equal=regs[:3]==want[:3]and regs[3]&0xef==want[3]&0xef and regs[4]==want[4]
    diff=[(k,hex(i),v,h.m.ram[k][i])for k,values in zip([2,3],final)for i,v in enumerate(values)if v!=h.m.ram[k][i]]
    assert equal and not diff and maps==h.m.rawtags and scratch==bytes(h.m[3:11])and smc==bytes(h.m[0x15a:0x17b]),(scenario,kind,cut,regs,want,diff[:15],maps,h.m.rawtags,scratch==bytes(h.m[3:11]),smc==bytes(h.m[0x15a:0x17b]))
    cuts_count[kind]+=1
 result=dict(passed=True,CPU_only=True,native_emulator=False,ROM_written=False,new_execution_scope_granted=False,base_SHA256=M.A.PIN,metadata_bytes=proof['metadata_bytes'],remaining_before_shared_clock=proof['remaining_before_shared_clock'],CPU_cases=dict(counts),original_battle_episodes=episodes,original_death_episode=death,native_CPU_range=[min(cost),max(cost)],minimum_SP=minimum,actual_ISR_cuts=dict(cuts_count),ISR_scenarios=scenario_rows,zero_ISR_private_writes_including_same_value=True,all_real_native_R0_R7_SMC_mapper_preserved=True,scope='Actual613b ROM plus proposed Prince code in real RAM2/3 mappings. Original armed/unarmed control, defender/parry/HP and completed death85/185 route genuine native defeat/KillPlayer; authentic source hues and source-floor constructor reference pass. This is CPU/ISR qualification; new executable-tail grant, compressed physical/backing/cold/reader closure, remaining native policies and emulator gameplay remain required.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-link-measurement-v42.json',O/'native-runtime-v42.bin',O/'native-metadata-v42.bin',O/'native-labels-v42.json',O/'native-contact-v42.bin',M.A.BASE]})
 (O/'native-link-CPU-v43.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','original_battle_episodes','original_death_episode']}))


if __name__=='__main__':main()
