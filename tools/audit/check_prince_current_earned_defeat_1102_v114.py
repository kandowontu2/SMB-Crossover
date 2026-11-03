"""Current GameLoop earns an original strike and native enemy defeat."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_game_loop_isr_1102_v102 as C
import check_prince_player_pipeline_1102_v67 as T
N,O=C.N,C.O


def main():
 e=C.environment();b,m,lab=C.loaded();T.terrain(m,lambda x,y:0x54 if y>=208 else 0)
 m.ram[2][0x6ee]=2
 for name,value in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_BoundBoxCtrl=3,Enemy_X_Position=80,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=2).items():m[C.address(b,name)]=value
 for i,v in enumerate([4,0,0]):m[C.address(b,'GameTimerDisplay')+i]=v
 rows=[];found=None;events=0
 for epoch in range(360):
  pad=128 if epoch>=40 else 0;m.controller_pad=pad;N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
  before=N.fork(m);out=e['run'](m,'GameLoop',lab);events+=out['native_calls'].get('ShellOrBlockDefeat',0)
  if epoch%8==0:rows.append(dict(epoch=epoch,nativeX=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),nativeEnemyX=N.get(m,'Enemy_X_Position'),source_action=m.ram[2][0x616],source_HP=m.ram[2][0x6cf],guardHP=m.ram[2][0x6d0],guardDead=m.ram[2][0x6de],nativeState=N.get(m,'Enemy_State'),nativeEngine=N.get(m,'GameEngineSubroutine')))
  if out['native_calls'].get('ShellOrBlockDefeat'):found=(before,out);break
  if N.get(m,'NumberofLives')!=2:break
 assert events==1 and found and N.get(m,'Enemy_State')&32 and N.get(m,'NumberofLives')==2,(events,rows[-8:])
 seed,ref=found;want=C.V.normalized_state(m);cuts=C.V.fold_cuts(ref['cuts']);count={};minimum=224
 for kind in ['IRQ','lagNMI']:
  for cut in cuts:
   z=N.fork(seed);got=e['run'](z,'GameLoop',lab,(kind,cut));assert got['regs']==ref['regs']and C.V.normalized_state(z)==want,(kind,cut);minimum=min(minimum,got['minSP']);count[kind]=count.get(kind,0)+1
 q=dict(passed=True,CPU_only=True,ROM_written=False,memory_only_SHA256=C.C.C.image()[1]['expected_memory_only_SHA256'],actual_GameLoop_updates=epoch+1,native_ShellOrBlockDefeat_calls=events,source_guard_HP=m.ram[2][0x6d0],source_guard_dead=m.ram[2][0x6de],source_player_HP=m.ram[2][0x6cf],final_native_enemy_state=N.get(m,'Enemy_State'),lives=N.get(m,'NumberofLives'),foreground_minimum_SP=ref['minSP'],real_IRQ_FF_lagNMI_cuts=count,minimum_SP=minimum,trace=rows,source_injected=False,scope='Actual full97 shared cold/Fresh and complete GameLoop. Explicit initial CPU terrain/enemy and already-acquired sword2 are preconditions; A input triggers the original source attack. No attack/contact/hit/death outcome is written. Original guardHP/dead transition alone invokes the genuine native defeat once; actual draw and private/native/SMC/mapper/AXYP/SP survive every recorded IRQ/FF-lag cut. Does not prove natural sword acquisition, native emulator or1-1.',bindings={p.relative_to(R).as_posix():C.C.C.M.sha(p.read_bytes())for p in [Path(__file__),Path(C.__file__),O/'post-return-manifest-v97.json',O/'current-shared-cold-CPU-v99.json']})
 (O/'current-earned-defeat-CPU-v114.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','trace']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'current-earned-defeat-negative-v114.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
