"""Deep actual GameRoutines/native gateway IRQ and disposable-packet closure."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_native_lifecycle_1102_v71 as C
N,O=C.C.N,C.O
address,location=C.C.address,C.C.location


def run(m,target,lab,interrupt=None):
 b=m.bundle;pc=address(b,target)
 m[address(b,'SafecallA_SMC')+1]=83
 m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
 c=N.NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=((location(b,target)-16)//8192)|128;c.x=N.get(m,'ObjectOffset')if target=='HuPickup'else 0;c.y=0;c.p=0x21;c.sp=224;c.stPushWord(0x5aff)
 low=c.sp;cuts=set();injected=False;calls=Counter();gateway_return=None;gateway_entries=0
 native={}
 for name in ['KillPlayer','MegaManDeathUpdate','MarioSourcePowerupCollision','ShellOrBlockDefeat','MetaspriteRenderLoop']:
  native[address(b,name),((location(b,name)-16)//8192)|128]=name
 for _ in range(500000):
  if c.pc==0x5b00:break
  low=min(low,c.sp);bank=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
  if c.pc==gateway_return:gateway_return=None
  if bank==2 and c.pc==lab['PpNativeCall']:
   assert gateway_return is None,'NativeCall reentered its foreground packet'
   gateway_return=((m[0x101+c.sp]|m[0x102+c.sp]<<8)+1)&65535;gateway_entries+=1
  if gateway_return is not None:
   assert not(bank==3 and c.pc==lab['PpHostDraw']),'Draw consumed packet during NativeCall'
   assert native.get((c.pc,bank))!='MetaspriteRenderLoop','Native sprite reader consumed packet during NativeCall'
  name=native.get((c.pc,bank))
  if name:calls[name]+=1
  cut=(c.pc,c.sp,m.rawtags[1])
  if c.sp<=180 and (0x15a<=c.pc<0x17b or bank==2 and lab['PpNativeTick']<=c.pc<lab['PpNativeServicesEnd'] or bank==193 and(0xa740<=c.pc<0xa7dc or 0xaaf7<=c.pc<0xabd4 or 0xae00<=c.pc<0xb013)):
   cuts.add(cut)
  if interrupt is not None and not injected and cut==interrupt[1]:
   injected=True;regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);maps=m.rawtags[:];state=[bytes(z)for z in m.ram];scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);writes=len(m.ram_writes)
   assert not c.p&4
   c.irq()if interrupt[0]=='IRQ'else c.nmi()
   for _ in range(200000):
    low=min(low,c.sp)
    if(c.pc,c.sp)==(regs[5],regs[4]):break
    assert m[c.pc]!=0,('Stack ISR BRK',interrupt,hex(c.pc));c.step()
   else:raise AssertionError(('Stack ISR bound',interrupt))
   assert regs[:3]==(c.a,c.x,c.y)and regs[3]&0xef==c.p&0xef and regs[4:]==(c.sp,c.pc)
   same=state==[bytes(z)for z in m.ram]and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b])and not m.ram_writes[writes:]
   assert same,dict(interrupt=interrupt,ram_diff=[(k,hex(i),a,z)for k in range(4)for i,(a,z)in enumerate(zip(state[k],m.ram[k]))if a!=z][:12],scratch=[list(scratch),list(m[3:11])],smc=[list(smc),list(m[0x15a:0x17b])],writes=m.ram_writes[writes:][:8])
   if maps!=m.rawtags:
    ins=bytes(m[c.pc:c.pc+3]);assert ins in [bytes.fromhex('8d1551'),bytes.fromhex('8d1651'),bytes.fromhex('8e1651')]
    window=1 if ins[1]==0x15 else 2;shadow=N.get(m,'CurrentBank'if window==1 else'CurrentBankC');assert m.rawtags[window]==shadow and all(maps[k]==m.rawtags[k]for k in range(4)if k!=window)
  assert m[c.pc]!=0,('Stack foreground BRK',hex(c.pc),c.sp,m.rawtags);c.step()
 else:raise AssertionError(('Stack foreground bound',target,hex(c.pc)))
 assert c.sp==224 and gateway_return is None and(interrupt is None or injected)
 return dict(regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,minSP=low,cuts=cuts,gateway_entries=gateway_entries,native_calls=dict(calls))


def clear(m):
 for name in ['writes','ram_writes','ppu_log','blocked']:setattr(m,name,[])


def fatal(m,b):
 C.C.terrain(m,lambda x,y:0x54 if y>=208 else 0);N.invoke(m,'HuFullBox',a=83,x=0,y=0,p=0x21);N.put(m,ObjectOffset=0)
 for field,value in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=48,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=3,Enemy_MovingDir=2).items():m[address(b,field)]=value
 for native in ['RelativeEnemyPosition','GetEnemyOffscreenBits','GetEnemyBoundBox','PlayerEnemyCollision']:N.invoke(m,native,a=83,x=0,y=0,p=0x21)
 assert m.ram[2][0x6cf]==0 and m.ram[2][0x616]==85
 m[address(b,'Enemy_Flag')]=0


def state(m):return([bytes(z)for z in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],bytes(m[0x200:0x800]))


def main():
 b,m,lab=C.loaded();fatal(m,b);scenarios=[]
 for epoch in range(22):
  N.put(m,FrameCounter=epoch,SavedJoypad1Bits=0,SavedJoypadBits=0)
  if epoch in [20,21]:clear(m);scenarios.append(('fatal-kill'if epoch==20 else'death-row8',N.fork(m),'GameRoutines'))
  out=run(m,'GameRoutines',lab)
 assert N.get(m,'GameEngineSubroutine')==11
 # Real star/1up collectors are the other public item gateway clients.
 for kind in [2,3]:
  _,m,_=C.loaded();N.put(m,ObjectOffset=5);m[address(b,'PowerUpType')+5]=kind;m[address(b,'Enemy_State')+5]=128;m[address(b,'Enemy_Flag')+5]=1
  clear(m);scenarios.append((f'native-item-{kind}',N.fork(m),'HuPickup'))
 rows=[];counts=Counter();minimum=224
 for name,seed,target in scenarios:
  print('Checking '+name,flush=True)
  m=N.fork(seed);ref=run(m,target,lab);expected=state(m);cuts=sorted(ref['cuts']);minimum=min(minimum,ref['minSP'])
  assert ref['gateway_entries']==1,(name,ref)
  for kind in ['IRQ','lagNMI']:
   for cut in cuts:
    z=N.fork(seed);got=run(z,target,lab,(kind,cut));assert got['regs']==ref['regs']and state(z)==expected,(name,kind,cut)
    counts[kind]+=1;minimum=min(minimum,got['minSP'])
  rows.append(dict(name=name,actual_native_calls=ref['native_calls'],gateway_entries=ref['gateway_entries'],foreground_minimum_SP=ref['minSP'],cuts=len(cuts)))
 graph={}
 for stem in ['contact-recovery.json','world-coordinate-recovery-v7.json','combat-tail-recovery-v34.json']:graph.update(json.loads((O/stem).read_text())['instructions'])
 indirect=[];direct=0
 for key,r in graph.items():
  if r['mn']in ['JSR','JMP']and r['mode']!='ind':continue
  if r['mode']in ['iny','inx','ind']:indirect.append(key)
  if r['mode']not in ['abs','zpg','abx','aby','zpx','zpy']:continue
  lo=r['value'];hi=lo+(256 if r['mode']in ['abx','aby','zpx','zpy']else 1)
  assert not(lo<0x235 and hi>0x200),('Original packet consumer',key,r)
  direct+=1
 q=dict(passed=True,CPU_only=True,ROM_written=False,qualified_cold=False,packet_lifetime_amendment_ungranted=True,real_IRQ_lagNMI_cuts=dict(counts),minimum_SP=minimum,scenarios=rows,source_original_instruction_count=len(graph),direct_indexed_domains_checked=direct,indirect_sites=indirect,indirect_closure='Existing v62 exact immutable-script reader/15command closure is unchanged; no source indirect reader can reach C200..C235.',packet_lifetime='Original source graph has zero direct/indexed aliases even expanding every8bit index; immutable-script indirect domain unchanged. Actual gateway callee traces reject nested NativeCall, original Draw and native metasprite reader. Synchronous native gateway writes first13 packet bytes; no draw occurs until return. Next original Draw overwrites every consumed packet byte before MetaspriteRenderLoop. Real IRQ/lagNMI preserve full private RAM, packet, R0..7, five SMC bytes and mapper state at every reached deep gateway/transport instruction.',required='Source-backed Defeat gateway and final post-gateway draw comparisons; exact new cold/backing and cookie rebind; warm respawn; root packet/two-byte execution lifetime review.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(C.__file__),O/'native-lifecycle-measurement-v70.json',O/'native-lifecycle-CPU-v71.json',O/'native-services-v70.s',O/'native-audio-v70.s',O/'native-runtime-v70.bin',O/'native-metadata-v70.bin',R/'tools/reference/prince_host_render_1102_v1.s',R/'docs/qa/allocations/prince-collision-lifetime-1102-v62.json']})
 (O/'native-stack-CPU-v72.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','indirect_sites','packet_lifetime']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  q=dict(passed=False,CPU_only=True,ROM_written=False,qualified_cold=False,exception=repr(error),scope='Preserved actual deep GameRoutines/native gateway ISR negative. Foreground repair alone does not qualify full native interrupt preservation.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-lifecycle-measurement-v70.json',O/'native-lifecycle-CPU-v71.json']})
  (O/'native-stack-negative-v72.json').write_text(json.dumps(q,indent=2)+'\n')
  raise
