"""Inject native HUD IRQ inside real lag-NMI audio at deepest reached stacks."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_actual_lag_post_return_1102_v89 as V
O=V.O;N=V.S.N;address=V.S.address


def environment():
 source=Path(V.__file__);text=source.read_text();old="try:env['main']()"
 assert text.count(old)==1;text=text[:text.index('\n '+old)]+"\n CAPTURE['env']=env;return\n"
 capture={};env=dict(__file__=str(source),__name__='prince_nested_irq_harness_v92',CAPTURE=capture)
 exec(compile(text,str(source),'exec'),env);env['main']();return capture['env']


def main():
 e=environment();b,m,lab=V.loaded();fresh=N.fork(m);V.S.fatal(m,b)
 for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v
 scenarios=[]
 for epoch in range(22):
  N.put(m,FrameCounter=epoch,SavedJoypad1Bits=0,SavedJoypadBits=0)
  if epoch in [20,21]:scenarios.append(('fatal-kill'if epoch==20 else'death-row8',N.fork(m),'GameCoreRoutine'))
  e['run'](m,'GameCoreRoutine',lab)
 for kind in [2,3]:
  m=N.fork(fresh);N.put(m,ObjectOffset=5);m[address(b,'PowerUpType')+5]=kind;m[address(b,'Enemy_State')+5]=128;m[address(b,'Enemy_Flag')+5]=1
  scenarios.append((f'native-item-{kind}',m,'HuPickup'))
 actual=N.NesMPU;winners={};context=None;mode='gather';nested_target=None;counts=Counter();minimum=224
 class Trace(actual):
  def nmi(self):
   self.lag_return=(self.pc,self.sp);return super().nmi()
  def step(self):
   nonlocal minimum
   ret=getattr(self,'lag_return',None)
   if ret is not None and(self.pc,self.sp)==ret:self.lag_return=None;ret=None
   if ret is not None and not self.p&4:
    m=self.memory;cut=(self.pc,self.sp,m.rawtags[1],m.rawtags[2]);key=(cut[0],cut[2],cut[3])
    if mode=='gather':
     if key not in winners or self.sp<winners[key][0][1]:winners[key]=(cut,context)
    elif cut==nested_target and not getattr(self,'nested_done',False):
     self.nested_done=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=m.rawtags[:];private=[bytes(z)for z in m.ram];scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);audio=m[0x7da];wr=len(m.ram_writes)
     self.irq()
     for _ in range(20000):
      minimum=min(minimum,self.sp)
      if(self.pc,self.sp)==(regs[5],regs[4]):break
      assert m[self.pc]!=0,('Nested native IRQ BRK',context,cut,hex(self.pc));super().step()
     else:raise AssertionError(('Nested native IRQ bound',context,cut))
     assert(self.a,self.x,self.y,self.p&0xef,self.sp,self.pc)==(*regs[:3],regs[3]&0xef,*regs[4:])
     assert maps==m.rawtags and private==[bytes(z)for z in m.ram]and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b])and audio==m[0x7da]and not m.ram_writes[wr:]
     counts['nested_IRQ']+=1
   return super().step()
 N.NesMPU=Trace
 try:
  references=[]
  for index,(name,seed,target)in enumerate(scenarios):
   z=N.fork(seed);ref=e['run'](z,target,lab);references.append((ref,V.normalized_state(z)))
   cuts=V.fold_cuts(ref['cuts']);print('Gather real lag audio IRQ domain',name,len(cuts),flush=True)
   for fore in cuts:
    context=(index,fore);z=N.fork(seed);out=e['run'](z,target,lab,('lagNMI',fore))
    assert out['regs']==ref['regs']and V.normalized_state(z)==references[-1][1];counts['lag_NMI_gather']+=1
  mode='replay';print('Replay deepest actual lag-audio IRQ pairs',len(winners),flush=True)
  for cut,(index,fore)in winners.values():
   name,seed,target=scenarios[index];context=(index,fore);nested_target=cut;before=counts['nested_IRQ'];z=N.fork(seed);out=e['run'](z,target,lab,('lagNMI',fore));ref,want=references[index]
   assert counts['nested_IRQ']==before+1,(name,fore,cut)
   assert out['regs']==ref['regs']and V.normalized_state(z)==want,(name,fore,cut)
 finally:N.NesMPU=actual
 assert counts['nested_IRQ']==len(winners)>0 and counts['lag_NMI_gather']==1846
 files=[Path(__file__),Path(V.__file__),R/'src/reset.s',O/'native-stack-CPU-v89.json',O/'post-return-cold-CPU-v90.json']
 q=dict(passed=True,CPU_only=True,source_code_injected=True,qualified_cold=False,ROM_written=False,counts=dict(counts),minimum_nested_IRQ_SP=minimum,nested_domain='Each actual NMI instruction/A-bank/C-bank pair at its deepest reached SP across every1846 genuine lag foreground cut; only actual I=0 instructions can receive native HUD IRQ. References cover actual GameCore earnedKill, row8 death, native star and1up.',all_native_IRQ_AXYP_SP_private_scratch_SMC_mapper_exact=True,all_outer_foreground_returns_and_state_exact_except_tracked_async_SFX=True,normal_NMI_not_substituted=True,new_lifetimes_ungranted=True,bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in files})
 (O/'post-return-nested-IRQ-CPU-v92.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'post-return-nested-IRQ-negative-v92.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
