"""Current159 deepest actual lag-NMI IRQ domain, including cold I1 seams."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_live_policy_current_1103_v168 as C
import check_prince_lag_nested_irq_1102_v92 as OLD
import check_prince_current_nested_irq_1102_v104 as IRQ
O=C.O


def main():
 e,lab,scenarios,fixture=C.scenarios();source=Path(OLD.__file__);text=source.read_text().replace('v92','v169')
 start=text.index(' e=environment();b,m,lab=V.loaded()');end=text.index(' actual=N.NesMPU;',start)
 text=text[:start]+' e=FINAL_ENV;lab=FINAL_LAB;scenarios=FINAL_CASES\n'+text[end:]
 text=text.replace('key=(cut[0],cut[2],cut[3])','key=cut[0]').replace("cuts=V.fold_cuts(ref['cuts'])","cuts=FINAL_FOLD(ref['cuts'])")
 text=text.replace("counts['lag_NMI_gather']==1846","counts['lag_NMI_gather']==sum(len(FINAL_FOLD(row[0]['cuts']))for row in references)")
 text=text.replace('audio=m[0x7da];wr=', 'audio=m[0x7da];smack=m[0x7d8];wr=').replace('and audio==m[0x7da]and','and audio==m[0x7da]and smack==m[0x7d8]and')
 env=dict(__file__=str(Path(__file__)),__name__='prince_live_nested_v169',FINAL_ENV=e,FINAL_LAB=lab,FINAL_CASES=scenarios,FINAL_FOLD=C.V.V.A.U.V.fold);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'post-return-nested-IRQ-CPU-v169.json';q=json.loads(path.read_text());q.update(source_code_injected=False,qualified_cold=True,new_lifetimes_ungranted=True,memory_SHA256=C.V.V.M.image()[1]['expected_memory_only_SHA256'],finite_fixed_IRQ_closure=IRQ.irq_closure(),source_fixture_SHA256=C.V.V.M.sha(fixture.encode()),scope='Current159 fullsourcebacked first8 originalconstructor/nativeGameLoop, actualGetPlayerColors/fullWriteGameText and onlynewcold finalizer/C2installer/residentthunk seams including everyactualI1 foreground PC in that newcold domain. EverygenuineFF cut contributes reachedlagNMIhandlerPC at lowestactualSP; realIRQ replays at all eligibleI0 handlers with byte-identical fixed68B branchless/callfree/noA/Cwindow IRQ. Tracks07D8/DA and preservesfullprivate/R0..7/SMC/maps/AXYP/SP/outerforeground state. No groundednativecollisionY fix/nativeemulator/menu/install admission inferred.')
 q['bindings'].update({p.relative_to(R).as_posix():C.V.V.M.sha(p.read_bytes())for p in [Path(__file__),Path(C.__file__),O/'backdrop-manifest-v159.json',O/'live-policy-ISR-v168.json',O/'walk-oam-CPU-v167.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'live-policy-nested-negative-v169.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
