"""Deepest native IRQ inside genuine FF audio on actual source-backed130."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_actual_1103_v134 as A
import check_prince_lag_nested_irq_1102_v92 as OLD
import check_prince_current_nested_irq_1102_v104 as IRQ
O=A.O


def main():
 e=A.environment();(seed,ref,lab,epoch),_,_,_=A.episode(e)
 source=Path(OLD.__file__);text=source.read_text().replace('v92','v136')
 start=text.index(' e=environment();b,m,lab=V.loaded()');end=text.index(' actual=N.NesMPU;',start)
 text=text[:start]+" e=FINAL_ENV;lab=FINAL_LAB;scenarios=[('actual130-source-strike',FINAL_SEED,'GameLoop')]\n"+text[end:]
 text=text.replace('key=(cut[0],cut[2],cut[3])','key=cut[0]').replace("cuts=V.fold_cuts(ref['cuts'])","cuts=FINAL_FOLD(ref['cuts'])")
 text=text.replace("counts['lag_NMI_gather']==1846","counts['lag_NMI_gather']==sum(len(FINAL_FOLD(row[0]['cuts']))for row in references)")
 text=text.replace('audio=m[0x7da];wr=', 'audio=m[0x7da];smack=m[0x7d8];wr=').replace("and audio==m[0x7da]and", "and audio==m[0x7da]and smack==m[0x7d8]and")
 env=dict(__file__=str(Path(__file__)),__name__='prince_actual_strike_nested_v136',FINAL_ENV=e,FINAL_LAB=lab,FINAL_SEED=seed,FINAL_FOLD=A.U.V.fold);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'post-return-nested-IRQ-CPU-v136.json';q=json.loads(path.read_text());q.update(source_code_injected=False,qualified_cold=True,new_lifetimes_ungranted=False,memory_only_SHA256=A.C.image()[1]['expected_memory_only_SHA256'],finite_fixed_IRQ_closure=IRQ.irq_closure(),nested_domain='Every reached genuine FF-lag handlerPC at its lowest realSP across all actual130 earned-strike foreground cuts (I0andI1eligible). Native IRQ replay only at reached handlerI0. Fixed68B branchless/call-free IRQ has no A/C-window data/mapper effects; folding byhandlerPC preserves deepest stack/fullstate. All source and native code came from full current130 sharedcold.',scope='Actual cf7+Prince130 backing/header/constructor, real original earned strike and unchanged native9AF8 suffix. Full outer state/SMC/maps/AXYP/SP and nested private/scratch exact; IRQ preserves07D8/DA, genuine lagAudioUpdate owns their only async changes. No source-code injection, ROM/menu/emulator/fullstage claim.')
 q['bindings'].update({p.relative_to(R).as_posix():A.C.M.M.sha(p.read_bytes())for p in [Path(__file__),Path(A.__file__),source,O/'strike-manifest-v130.json',O/'current-shared-cold-CPU-v131.json',O/'actual-strike-CPU-v134.json',O/'post-return-nested-IRQ-CPU-v128.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'actual-strike-nested-negative-v136.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
