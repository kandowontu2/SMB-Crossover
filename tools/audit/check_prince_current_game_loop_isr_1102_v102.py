"""Current authenticated image, actual GameLoop FF interval and native gateways."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_actual_lag_post_return_1102_v89 as V
import check_prince_current_respawn_1102_v100 as C
O=V.O;N=V.S.N;address=V.S.address


def loaded():
 b,m,lab=C.loaded();N.put(m,NmiDisable=255);return b,m,lab


def environment():
 source=Path(V.__file__);text=source.read_text();assert text.count('A.loaded()')==1;text=text.replace('A.loaded()','CURRENT_LOADED()')
 marker=' env=dict(__file__=str(Path(__file__)),__name__=\'prince_actual_lag_v89\'';assert marker in text
 text=text.replace(marker," text=text.replace('cuts.add(cut)',\"if N.get(m,'NmiDisable')==255:cuts.add(cut)\")\n"+marker)
 old="try:env['main']()";assert text.count(old)==1;text=text[:text.index('\n '+old)]+"\n CAPTURE['env']=env;return\n"
 capture={};env=dict(__file__=str(source),__name__='prince_current_isr_builder_v102',CURRENT_LOADED=loaded,CAPTURE=capture);exec(compile(text,str(source),'exec'),env);env['main']();return capture['env']


def scenarios(e):
 b,m,lab=loaded();fresh=N.fork(m);V.S.fatal(m,b)
 for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v
 result=[]
 for epoch in range(30):
  before=N.fork(m);out=e['run'](m,'GameLoop',lab)
  if out['native_calls'].get('KillPlayer'):result.append(('actual-GameLoop-earned-Kill',before,'GameLoop'))
  if result and out['native_calls'].get('MegaManDeathUpdate'):result.append(('actual-GameLoop-death-row8',before,'GameLoop'));break
 assert len(result)==2
 for kind in [2,3]:
  m=N.fork(fresh);N.put(m,ObjectOffset=5);m[address(b,'PowerUpType')+5]=kind;m[address(b,'Enemy_State')+5]=128;m[address(b,'Enemy_Flag')+5]=1
  result.append((f'native-item-{kind}',m,'HuPickup'))
 return lab,result


def main():
 e=environment();lab,cases=scenarios(e);counts=Counter();rows=[];minimum=224
 for name,seed,target in cases:
  m=N.fork(seed);ref=e['run'](m,target,lab);want=V.normalized_state(m);cuts=V.fold_cuts(ref['cuts']);assert cuts
  print('Current actualFF GameLoop cuts',name,len(cuts),flush=True)
  assert ref['gateway_entries']==(0 if 'earned-Kill'in name else 1)
  for kind in ['IRQ','lagNMI']:
   for cut in cuts:
    z=N.fork(seed);out=e['run'](z,target,lab,(kind,cut));assert out['regs']==ref['regs']and V.normalized_state(z)==want,(name,kind,cut);counts[kind]+=1;minimum=min(minimum,out['minSP'])
  rows.append(dict(name=name,cuts=len(cuts),foreground_minimum_SP=ref['minSP'],actual_native_calls=ref['native_calls'],gateway_entries=ref['gateway_entries']))
  print('Completed current scenario',name,dict(counts),minimum,flush=True)
 assert dict(counts)==dict(e['COUNTS'])
 _,manifest=C.C.image();q=dict(passed=True,CPU_only=True,ROM_written=False,source_code_injected=False,qualified_current_shared_cold=True,memory_only_SHA256=manifest['expected_memory_only_SHA256'],real_IRQ_and_actual_FF_lagNMI=dict(counts),minimum_SP=minimum,scenarios=rows,actual_GameLoop_source_sets_FF=True,all_cuts_within_real_negative_flag_foreground_interval=True,actual_lag_branch_PC=e['nmi_path'](cases[0][1])[0],all_lag_branch_visits_exactly_once=True,regular_NMI_branch_never_reached=True,full_private_R0_R7_SMC_mapper_AXYP_SP_parity=True,native_0200_07FF_exact_except_tracked_audio_07DA=True,scope='Exact current authenticated97 image loaded by complete shared cold, no code injection. Actual GameLoop includes original FF store and complete native GameCore/owner/death/draw route; cut collection excludes the regular-publication interval afterPauseSkip. Native star/1up gateways also execute. Every reached shared/SMC/hook/router/gateway PC/A-bank at deepest actualSP runs real IRQ and actual FF lagNMI;07DA advances only via actual AudioUpdate and is preserved by resumed foreground. No ROM/menu/install/emulator claim; nested IRQ source-equivalence/actual current replay remains separate.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(V.__file__),Path(C.__file__),O/'post-return-manifest-v97.json',O/'current-shared-cold-CPU-v99.json',O/'post-return-respawn-CPU-v101.json',R/'src/game.s',R/'src/reset.s']})
 (O/'current-game-loop-ISR-CPU-v102.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'current-game-loop-ISR-negative-v102.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
