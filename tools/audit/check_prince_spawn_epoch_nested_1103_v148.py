"""Deepest native IRQ inside real lag audio during first8 ReadyA7 resync."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_spawn_epoch_isr_1103_v147 as A
import check_prince_lag_nested_irq_1102_v92 as OLD
import check_prince_current_nested_irq_1102_v104 as IRQ
O=A.O


def main():
 e,seed,lab=A.prepared();source=Path(OLD.__file__);text=source.read_text().replace('v92','v148')
 start=text.index(' e=environment();b,m,lab=V.loaded()');end=text.index(' actual=N.NesMPU;',start)
 text=text[:start]+" e=FINAL_ENV;lab=FINAL_LAB;scenarios=[('first8-ReadyA7-resync',FINAL_SEED,'GameLoop')]\n"+text[end:]
 text=text.replace('key=(cut[0],cut[2],cut[3])','key=cut[0]').replace("cuts=V.fold_cuts(ref['cuts'])","cuts=FINAL_FOLD(ref['cuts'])")
 text=text.replace("counts['lag_NMI_gather']==1846","counts['lag_NMI_gather']==sum(len(FINAL_FOLD(row[0]['cuts']))for row in references)")
 text=text.replace('audio=m[0x7da];wr=', 'audio=m[0x7da];smack=m[0x7d8];wr=').replace("and audio==m[0x7da]and", "and audio==m[0x7da]and smack==m[0x7d8]and")
 env=dict(__file__=str(Path(__file__)),__name__='prince_first8_nested_v148',FINAL_ENV=e,FINAL_LAB=lab,FINAL_SEED=seed,FINAL_FOLD=A.A.U.V.fold);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'post-return-nested-IRQ-CPU-v148.json';q=json.loads(path.read_text());q.update(source_code_injected=True,qualified_cold=False,new_lifetimes_ungranted=False,source_runtime_version=145,finite_fixed_IRQ_closure=IRQ.irq_closure(),nested_domain='Every reached real FF-lag handlerPC at minimumactualSP across all first8 ReadyA7/EpochValid0 foreground cuts, including everyI1eligible foreground PC; nativeIRQ only at actual handlerI0. Fixed68B branchless/callfree IRQ has no A/C-window or mapper data effects.',scope='Prototype source145 first8 fullGameLoop/original constructor resync, sourceHeaderReady remains A7 while original geometry is rebuilt from actual native entrance. NativeAudioUpdate may only change traced07D8/DA, IRQ preserves both; all private/scratch/SMC/maps/AXYP/SP and outerforeground state exact. No new resources/physicalcold/cookie/native/Mesen claim.')
 q['bindings'].update({p.relative_to(R).as_posix():A.P.C.M.M.sha(p.read_bytes())for p in [Path(__file__),Path(A.__file__),O/'spawn-epoch-CPU-v146.json',O/'deferred-strike-measurement-v145.json',O/'native-metadata-v145.bin']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'spawn-epoch-nested-negative-v148.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
