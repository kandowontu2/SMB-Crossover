"""Actual source-earned strike and interrupt proof after final130 full cold."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_deferred_strike_1102_v117 as U
import check_prince_strike_lifetime_1102_v125 as H
import check_prince_strike_cold_1103_v131 as C
N,O=C.N,C.O


def bind():
 # Only test plumbing changes: all live source/native instructions come from
 # real final130 full cold, never an injected private-code overlay.
 def loaded():
  b,m,lab=C.loaded();N.put(m,NmiDisable=255);return b,m,lab
 U.C.loaded=loaded;U.C.C.C.image=C.image
 original=U.C.V.normalized_state
 def normalize(m):
  out=list(original(m));native=bytearray(out[4]);native[0x7d8-0x200]=0;out[4]=bytes(native);return tuple(out)
 U.C.V.normalized_state=normalize


def environment():
 bind();return H.helpers()['environment']()[0]


def episode(e):
 b,m,lab=U.C.loaded();U.T.terrain(m,lambda x,y:0x54 if y>=208 else 0);m.ram[2][0x6ee]=2
 for name,value in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_BoundBoxCtrl=3,Enemy_X_Position=80,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=2).items():m[C.I.address(b,name)]=value
 for i,value in enumerate([4,0,0]):m[C.I.address(b,'GameTimerDisplay')+i]=value
 points={}
 for name in ['EnemiesAndLoopsCore','PlayerGfxHandler']:
  points[C.I.address(b,name),((U.C.V.S.location(b,name)-16)//8192)|128]=name
 points[0x9af8,254]='NativeDefeat';points[0xb0f2,193]='PublishedRow34';points[lab['PpNativeProxyOut'],2]='ProxyOut'
 actual=N.NesMPU;events=[]
 class Trace(actual):
  def step(self):
   tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
   if(self.pc,tag)in points:events.append(points[self.pc,tag])
   return super().step()
 found=None;total=0;rows=[]
 try:
  N.NesMPU=Trace
  for epoch in range(360):
   pad=128 if epoch>=40 else 0;m.controller_pad=pad;N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
   seed=N.fork(m);events.clear();out=e['run'](m,'GameLoop',lab);count=out['native_calls'].get('ShellOrBlockDefeat',0);total+=count
   if count:
    assert found is None and count==1 and events.count('NativeDefeat')==1
    assert events.index('PublishedRow34')<events.index('ProxyOut')<events.index('NativeDefeat')<events.index('EnemiesAndLoopsCore')<events.index('PlayerGfxHandler'),events
    found=(seed,out,lab,epoch);order=events[:];print('Actual final130 full-cold source-earned defeat',epoch,out['minSP'],flush=True)
   if epoch%8==0:rows.append(dict(epoch=epoch,source_HP=m.ram[2][0x6cf],guardHP=m.ram[2][0x6d0],guardDead=m.ram[2][0x6de],guardUID=m.ram[2][0x61c],nativeEnemyState=N.get(m,'Enemy_State')))
   if found and epoch>=found[3]+16:break
 finally:N.NesMPU=actual
 assert found and total==1 and N.get(m,'NumberofLives')==2
 assert found[3]==json.loads((O/'deferred-strike-CPU-v123.json').read_text())['actual_earned_defeat_epoch']==58
 return found,m,rows,order


def main():
 e=environment();(seed,ref,lab,epoch),final,rows,order=episode(e);reference=N.fork(seed);e['run'](reference,'GameLoop',lab);want=U.C.V.normalized_state(reference);counts={};minimum=224;cuts=U.V.fold(ref['cuts'])
 for kind in ['IRQ','lagNMI']:
  for cut in cuts:
   if kind=='IRQ'and cut[3]:continue
   m=N.fork(seed);got=e['run'](m,'GameLoop',lab,(kind,cut));assert got['regs']==ref['regs']and U.C.V.normalized_state(m)==want,(kind,cut);minimum=min(minimum,got['minSP']);counts[kind]=counts.get(kind,0)+1
  print('Final130 actual source strike cuts',kind,counts,minimum,flush=True)
 _,manifest=C.image();q=dict(passed=True,CPU_only=True,ROM_written=False,source_code_injected=False,qualified_current_shared_cold=True,memory_only_SHA256=manifest['expected_memory_only_SHA256'],actual_earned_defeat_epoch=epoch,native_defeats=1,following_updates_without_duplicate=16,lives=[2,N.get(final,'NumberofLives')],actual_order=order,real_IRQ_actual_FF_lagNMI=counts,all_actual_FF_I1_cuts=sum(bool(c[3])for c in cuts),foreground_minimum_SP=ref['minSP'],minimum_SP=minimum,trace=rows,scope='Exact final130 source-backed image loaded through complete currentcf7 shared cold and both headers. Native enemy/world/sword-mode are explicit CPU fixture inputs; genuine original A attack earns terminal guard and native defeat once at epoch58, then16updates with no duplicate/life loss. Real row34/ProxyOut/nativeSuffix precede enemy AI/playerdraw in sameMain. No source-code injection or native hit/life/death outcome seeds. All private/R0..7/SMC/maps/AXYP/SP and native state exact under IRQ/actual FF-lag except source-tracked nativeAudioUpdate07D8/07DA; actual lag branch/INC and no regular branch asserted. Native emulator/menu/fullstage remain pending.',bindings={p.relative_to(R).as_posix():C.M.M.sha(p.read_bytes())for p in [Path(__file__),Path(U.__file__),Path(H.__file__),Path(C.__file__),O/'strike-manifest-v130.json',O/'current-shared-cold-CPU-v131.json',O/'deferred-strike-CPU-v123.json',O/'strike-lifetime-CPU-v126.json',R/'src/game.s',R/'src/object.s',R/'src/music_drivers/vanilla_sfx.s']})
 (O/'actual-strike-CPU-v134.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','trace']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'actual-strike-negative-v134.json').write_text(json.dumps(dict(passed=False,CPU_only=True,source_code_injected=False,exception=repr(error)),indent=2)+'\n');raise
