"""Actual GameLoop original-strike phase parity and real interrupt prototype."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_I1_lag_1102_v112 as V
import check_prince_player_pipeline_1102_v67 as T
C=V.C;N,O=C.N,C.O


def inject(m):
 m.ram[3][:8159]=(O/'native-runtime-v116.bin').read_bytes();m.ram[2][0x800:0x800+6095]=(O/'native-metadata-v116.bin').read_bytes();m.ram[2][0x766:0x800]=(O/'native-state-v116.bin').read_bytes()[-154:]
 return json.loads((O/'native-labels-v116.json').read_text())


def source_state(m):
 grants=json.loads((R/'docs/qa/allocations/prince-executable-state-1102-v15.json').read_text());excluded={i-0xc000 for a,z in grants['executable_code_half_open']for i in range(a,z)}|set(range(0x200,0x235))|set(range(0x766,0x800))
 return bytes(v for i,v in enumerate(m.ram[2][:0x800])if i not in excluded)


def state(m):return(source_state(m),bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x15a:0x17b]),m.rawtags[:])


def episode(e):
 b,old,oldlab=C.loaded();T.terrain(old,lambda x,y:0x54 if y>=208 else 0);old.ram[2][0x6ee]=2
 for name,value in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_BoundBoxCtrl=3,Enemy_X_Position=80,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=2).items():old[C.address(b,name)]=value
 for i,value in enumerate([4,0,0]):old[C.address(b,'GameTimerDisplay')+i]=value
 new=N.fork(old);lab=inject(new);totals=[0,0];found=None;rows=[]
 for epoch in range(360):
  pad=128 if epoch>=40 else 0
  for m in [old,new]:m.controller_pad=pad;N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
  before=N.fork(new);a=e['run'](old,'GameLoop',oldlab);z=e['run'](new,'GameLoop',lab)
  for i,out in enumerate([a,z]):totals[i]+=out['native_calls'].get('ShellOrBlockDefeat',0)
  assert a['regs']==z['regs']and state(old)==state(new),('Deferred completeGameLoop parity',epoch,a['regs'],z['regs'],[(hex(i),old[i],new[i])for i in range(0x800)if old[i]!=new[i]][:16])
  if z['native_calls'].get('ShellOrBlockDefeat'):
   assert found is None and a['native_calls'].get('ShellOrBlockDefeat')==1;found=(before,z,lab,epoch);print('Earned actual old/new nativeDefeat',epoch,'minSP',a['minSP'],z['minSP'],flush=True)
  if epoch%8==0:rows.append(dict(epoch=epoch,source_HP=new.ram[2][0x6cf],guardHP=new.ram[2][0x6d0],guardDead=new.ram[2][0x6de],guardUID=new.ram[2][0x61c],nativeEnemyState=N.get(new,'Enemy_State')))
  if found and epoch>=found[3]+16:break
 assert found and totals==[1,1]and N.get(new,'NumberofLives')==2,totals
 return found,new,rows


def main():
 e,_=V.environment();(seed,ref,lab,epoch),final,rows=episode(e);reference=N.fork(seed);e['run'](reference,'GameLoop',lab);want=C.V.normalized_state(reference);counts={};minimum=224;cuts=V.fold(ref['cuts'])
 for kind in ['IRQ','lagNMI']:
  for cut in cuts:
   if kind=='IRQ'and cut[3]:continue
   z=N.fork(seed);got=e['run'](z,'GameLoop',lab,(kind,cut));assert got['regs']==ref['regs']and C.V.normalized_state(z)==want,(kind,cut);minimum=min(minimum,got['minSP']);counts[kind]=counts.get(kind,0)+1
  print('Deferred strike interrupts',kind,counts,minimum,flush=True)
 q=dict(passed=True,CPU_only=True,ROM_written=False,source_code_injected=True,changed_full_cold_qualified=False,source_parent_memory_SHA256=C.C.C.image()[1]['expected_memory_only_SHA256'],actual_earned_defeat_epoch=epoch,actual_complete_GameLoop_old_new_finalstate_parity=True,original_source_live_fields_all_exact=True,native_ZP_0200_07FF_AXYP_SP_SMC_mapper_exact=True,original_native_defeats=1,deferred_native_defeats=1,following_updates_without_duplicate=16,real_IRQ_actual_FF_lagNMI=counts,foreground_minimum_SP=ref['minSP'],minimum_SP=minimum,trace=rows,scope='Source-only prototype overlays exact116 images after authenticated97 full cold. No native life/engine/hit outcomes seeded. Same genuine source attack, native enemy fixture and realGameLoop input earn the same native defeat in the sameMain, before enemyAI/draw, before any source-earned pending nativeKill. Old/new complete native and all original source-live fields match every epoch; native transportSMC/AXYP/SP match. Real lag branch and no regular branch asserted. New backing/cookie/fullcold/nestedIRQ still required; not native-ready.',bindings={p.relative_to(R).as_posix():C.C.C.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'deferred-strike-measurement-v116.json',*[O/f'native-{n}-v116.bin'for n in ['runtime','metadata','state']],O/'native-labels-v116.json',O/'current-earned-defeat-negative-v114.json']})
 (O/'deferred-strike-CPU-v117.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','trace']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'deferred-strike-negative-v117.json').write_text(json.dumps(dict(passed=False,CPU_only=True,source_code_injected=True,exception=repr(error)),indent=2)+'\n');raise
