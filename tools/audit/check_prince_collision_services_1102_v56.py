"""Private proposed native box/query/item semantics, no audio lifetime admission."""
from collections import Counter
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_sunny_rebase_1102_v54 as M
import check_prince_native_link_1102_v43 as V
import prince_original_cpu_1101_v1 as P
H,O,N=V.H,V.O,V.N
address,location=H.W.address,H.W.location


def host(base):
 h=H.host(base);h.m.ram[3][:0x1fdf]=(O/'native-runtime-v49.bin').read_bytes();meta=(O/'native-metadata-v49.bin').read_bytes();h.s[0x800:0x800+len(meta)]=meta
 audio=(O/'native-audio-v49.bin').read_bytes();h.s[0x780:0x800]=audio+bytes(128-len(audio));h.lab.update(json.loads((O/'native-labels-v49.json').read_text()));h.source('PpNativeInit');assert not h.callbacks
 return h


def invoke(h,name,args=(83,0,109,0x21),interrupt=None):
 h.map();m=h.m;m.controller_pad=N.get(m,'SavedJoypad1Bits');c=N.NesMPU(memory=m,pc=h.lab[name]if isinstance(name,str)else name);c.a,c.x,c.y,c.p=args;c.sp=224;c.stPushWord(0x5aff);low=c.sp;cuts=set();injected=False;calls=Counter()
 native={}
 for n in ['EraseEnemyObject','SetupFloateyNumber','MarioSourcePowerupCollision']:
  pc=address(h.b,n);native[pc,((location(h.b,n)-16)//8192)|128]=n
 for _ in range(200000):
  if c.pc==0x5b00:break
  low=min(low,c.sp);cut=(c.pc,c.sp,m.rawtags[1]);tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
  if 0xd8f1<=c.pc<0xdfce or 0xbd22<=c.pc<0xbd4b or 0xc780<=c.pc<0xc800 or 0x15a<=c.pc<0x17b:cuts.add(cut)
  if(c.pc,tag)in native:calls[native[c.pc,tag]]+=1
  if interrupt is not None and not injected and cut==interrupt[1]:
   injected=True;regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);maps=m.rawtags[:];state=[bytes(x)for x in m.ram];scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);wr=len(m.ram_writes);assert not c.p&4
   c.irq()if interrupt[0]=='IRQ'else c.nmi()
   for _ in range(200000):
    low=min(low,c.sp)
    if(c.pc,c.sp)==(regs[5],regs[4]):break
    assert m[c.pc]!=0,('Proposed collision ISR BRK',interrupt,hex(c.pc));c.step()
   else:raise AssertionError(('Proposed collision ISR bound',interrupt))
   assert regs[:3]==(c.a,c.x,c.y)and regs[3]&0xef==c.p&0xef and regs[4:]==(c.sp,c.pc)
   assert state==[bytes(x)for x in m.ram]and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b])and not m.ram_writes[wr:]
   if maps!=m.rawtags:
    ins=bytes(m[c.pc:c.pc+3]);assert ins in [bytes.fromhex('8d1551'),bytes.fromhex('8d1651'),bytes.fromhex('8e1651')]
    window=1 if ins[1]==0x15 else 2;shadow=N.get(m,'CurrentBank'if window==1 else'CurrentBankC');assert m.rawtags[window]==shadow and all(maps[k]==m.rawtags[k]for k in range(4)if k!=window)
  assert m[c.pc]!=0,('Proposed collision BRK',name,hex(c.pc));c.step()
 else:raise AssertionError(('Proposed collision bound',name,hex(c.pc)))
 assert c.sp==224 and(interrupt is None or injected)
 return dict(regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,minSP=low,cuts=cuts,calls=dict(calls))


def snapshot(h):
 for name in ['writes','ram_writes','ppu_log','blocked']:setattr(h.m,name,[])
 return N.fork(h.m)


def restore(h,seed):h.m=N.fork(seed);h.s=h.m.ram[2]


def view(h):return([bytes(x)for x in h.m.ram],bytes(h.m[:0x100]),bytes(h.m[0x200:0x800]),bytes(h.m[0x15a:0x17b]),h.m.rawtags[:])


def owned_view(h):
 fields=['PowerUpType','Enemy_Flag','Enemy_State','FloateyNum_Control','StarInvincibleTimer','NumberofLives','GameEngineSubroutine','PlayerStatus','Player_Y_Speed']
 return([bytes(x)for x in h.m.ram],bytes(h.m[3:11]),bytes(h.m[0x15a:0x17b]),h.m.rawtags[:],{n:bytes(h.m[address(h.b,n):address(h.b,n)+(6 if n in fields[:4]else 1)])for n in fields})


def main():
 base,_,_,_=M.bundle();H.W.PIN=M.PIN;N.Bus=V.ControllerBus
 proof=json.loads((O/'collision-services-measurement-v49.json').read_text());assert proof['measured']and not proof['qualified']and not proof['source_dead_audio_execution_granted']
 for path,digest in proof['bindings'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
 h=host(base);seed=snapshot(h);counts=Counter();scenarios=[];cost=[];minimum=224
 route=h.lab['PpNativeRoute'];assert h.m[route+16]==0x8d;vector_smc=int.from_bytes(bytes(h.m[route+17:route+19]),'little');assert vector_smc==route+21 and h.m[vector_smc-1]==0x4c
 # Actual sole PlayerSubs caller fixes nativeX=0. Relative coordinates wrap
 # as native8bit boxes do; rectangle matches the explicit source-world anchor.
 for x,y in itertools.product([0,1,15,16,127,239,240,255],[0,31,112,176,208,224,255]):
  restore(h,seed);N.put(h.m,Player_Rel_XPos=x,Player_Rel_YPos=y);h.s[0x9e]=48;before=bytes(h.s);out=invoke(h,'PpNativeRoute');box=address(base,'BoundingBox_UL_XPos')
  assert bytes(h.m[box:box+4])==bytes([x,y,(x+16)&255,(y+32)&255]);assert out['regs'][1:3]==[0,0]and out['regs'][3]&1
  assert all(a==z or i==vector_smc-0xc000 for i,(a,z)in enumerate(zip(before,h.s))),('Box changed source state',x,y);counts['full_box_player_X0']+=1
 # Typed maturity row only admits geometry; canonical collector still gates
 # every immature regular item and every dead source player.
 for a,x,y,flags in itertools.product([0,83,255],[0,5],[0,109],[0x20,0x61]):
  restore(h,seed);h.s[0x9e]=69;before=view(h);out=invoke(h,'PpNativeRoute',(a,x,y,flags));assert view(h)==before and out['regs'][:3]==[a,x,y]and out['regs'][3]&1;counts['maturity_pure_admission']+=1
 # Genuine fixed native head/side query owns its complete R0..R7/output ABI.
 # Compare the proposed typed leaf against that exact original native entry
 # across pages, corners, velocities and standing-probe indices.
 for tag,native,ys in [(30,'BlockBufferColli_Head',[6]),(42,'BlockBufferColli_Side',[9,10,11,12])]:
  for x,y,speed,probe in itertools.product([0,239,255,256,511],[31,112,176,223],[-4,0,4],ys):
   restore(h,seed);N.put(h.m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,Player_Y_Speed=speed&255);h.s[0x9e]=tag;case=snapshot(h)
   out=invoke(h,'PpNativeRoute',(83,0,probe,0x21));actual=view(h)
   restore(h,case);want=invoke(h,address(base,native),(83,0,probe,0x21));expected=view(h)
   # Public vector writes only its owned low-byte SMC operand. Compare every
   # native/private byte except that declared dispatcher instruction byte.
   r=[i for i,(a,z)in enumerate(zip(actual[0][2],expected[0][2]))if a!=z];assert all(i==vector_smc-0xc000 for i in r),(native,'Unexpected private diff',r)
   assert actual[1:]==expected[1:]and actual[0][:2]==expected[0][:2]and actual[0][3]==expected[0][3]
   assert out['regs']==want['regs'],(native,x,y,speed,probe,out['regs'],want['regs']);counts['exact_native_query_ABI']+=1
 # Native transport conveys the physical signed foot delta, never alters the
 # original actor/source trajectory. Source difference remains modulo8bits.
 for old,delta in itertools.product([0,127,255,256,511],[-32,-4,-1,0,1,4,32]):
  restore(h,seed);h.s[0x84:0x86]=((old+delta)&65535).to_bytes(2,'little');h.s[0x86:0x88]=old.to_bytes(2,'little');before=bytes(h.s);out=invoke(h,'PpNativeMotionExport');assert N.get(h.m,'Player_Y_Speed')==delta&255 and bytes(h.s)==before;counts['source_vertical_sign_transport']+=1
 # Explicit CPU item fixtures: neither native actor nor outcome is seeded in
 # an emulator. Every admitted item uses real Erase/score/nativecollector.
 for kind,state,hp,slot in itertools.product(range(4),[0,1,6,127,128,255],[0,1,4,5],[0,5]):
  restore(h,seed);h.s[0x6cf]=hp;N.put(h.m,ObjectOffset=slot);h.m[address(base,'PowerUpType')+slot]=kind;h.m[address(base,'Enemy_State')+slot]=state;h.m[address(base,'Enemy_Flag')+slot]=1;case=snapshot(h);before=bytes(h.s)
  out=invoke(h,'PpNativePickup',(83,slot,109,0x21));cost.append(out['CPU']);minimum=min(minimum,out['minSP']);admit=bool(hp and(kind>=2 or state&128))
  assert bool(out['calls'].get('EraseEnemyObject',0))==admit and bool(out['calls'].get('SetupFloateyNumber',0))==admit,(kind,state,hp,slot,out)
  assert out['calls'].get('MarioSourcePowerupCollision',0)==int(admit and kind>=2)
  assert N.get(h.m,'NumberofLives')==2 and N.get(h.m,'GameEngineSubroutine')==8
  if not admit:assert bytes(h.s)==before and h.m[address(base,'Enemy_Flag')+slot]==1
  elif kind==0:assert h.s[0x6cf]==min(5,hp+1)and h.s[0x6ee]==0
  elif kind==1:
   assert h.s[0x6cf]==hp and h.s[0x6ee]==1 and h.s[0x616]==91
   # Compare the genuine original sword-effect action entry, including its
   # script and Map5 bookkeeping, against this exact actor state.
   d=P.machine();d.memory.switch(7);list.__setitem__(d.memory,slice(0,2048),case.ram[2][:2048]);d.memory[0x6ee]=1;P.call(d,0xd6d8,a=91,x=slot,y=0,p=0x21)
   assert bytes(h.s[0x60e:0x61c])==bytes(d.memory[0x60e:0x61c])and h.s[0x6d1]==d.memory[0x6d1]
  elif kind==2:assert N.get(h.m,'StarInvincibleTimer')==35
  else:assert h.m[address(base,'FloateyNum_Control')+slot]==11
  if admit and state==128 and hp==4 and slot==5:scenarios.append((f'item-{kind}','PpNativePickup',case,(83,slot,109,0x21)))
  counts['native_item_boundaries']+=1
 restore(h,seed);h.s[0x9e]=48;scenarios.append(('box-vector','PpNativeRoute',snapshot(h),(83,0,109,0x21)))
 restore(h,seed);N.put(h.m,Player_Y_Speed=252);h.s[0x9e]=30;scenarios.append(('head-vector','PpNativeRoute',snapshot(h),(83,0,6,0x21)))
 irq=Counter();scenario_rows=[]
 for name,target,case,args in scenarios:
  restore(h,case);ref=invoke(h,target,args);expected=owned_view(h);cuts=sorted(ref['cuts']);scenario_rows.append(dict(name=name,cuts=len(cuts),actual_native_calls=ref['calls']))
  for kind in ['IRQ','lagNMI']:
   for cut in cuts:
    restore(h,case);got=invoke(h,target,args,(kind,cut));actual=owned_view(h);regs=got['regs'];want=ref['regs'];equal=regs[:3]==want[:3]and regs[3]&0xef==want[3]&0xef and regs[4]==want[4]
    assert equal and actual==expected,(name,kind,cut,regs,want,[(k,hex(i),a,z)for k in range(4)for i,(a,z)in enumerate(zip(expected[0][k],actual[0][k]))if a!=z][:10]);minimum=min(minimum,got['minSP']);irq[kind]+=1
 q=dict(passed=True,private_proposal_only=True,execution_granted=False,ROM_written=False,native_emulator=False,base_SHA256=M.PIN,CPU_cases=dict(counts),native_item_CPU_range=[min(cost),max(cost)],real_IRQ_lagNMI_cuts=dict(irq),ISR_scenarios=scenario_rows,minimum_SP=minimum,original_sword_effect_action91_differential=True,source_physics_unchanged=True,original_audio_events_pending_not_mixed=True,scope='Proposed v49 private direct typed leaves execute against actual current Sunny native routines in RAM2/3. Fullbox/native head-side ABI/source sign/regular maturity/HP and original sword action/star/1up CPU predicates qualify; real IRQ and lagNMI preserve live private state and native scratch/maps. Audio interval/staged prefix/extra13B renderer and metadata extension are ungranted. No current shared routing/auth rebind, cold/backing fit, menu, emulator or playable-stage claim.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),M.BASE,O/'collision-services-measurement-v49.json',O/'native-runtime-v49.bin',O/'native-metadata-v49.bin',O/'native-state-v49.bin',O/'native-labels-v49.json',O/'sunny-rebase-manifest-v54.json']})
 (O/'collision-services-CPU-v56.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
