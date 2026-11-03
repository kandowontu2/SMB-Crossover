"""Native HUD IRQ inside genuine FF-lag audio after the owned strike repair."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_lifetime_1102_v125 as H
import check_prince_lag_nested_irq_1102_v92 as OLD
import check_prince_current_nested_irq_1102_v104 as IRQ
import check_prince_deferred_strike_1102_v117 as U
O=U.O


def main():
 h=H.helpers();e,_=h['environment']();old_inject=U.inject;old_normalize=U.C.V.normalized_state
 def normalize(m):
  out=list(old_normalize(m));native=bytearray(out[4]);native[0x7d8-0x200]=0;out[4]=bytes(native);return tuple(out)
 U.inject=h['inject'];U.C.V.normalized_state=normalize
 try:
  (seed,ref,lab,epoch),_,_=U.episode(e)
  source=Path(OLD.__file__);text=source.read_text().replace('v92','v127')
  start=text.index(' e=environment();b,m,lab=V.loaded()');end=text.index(' actual=N.NesMPU;',start)
  text=text[:start]+" e=FINAL_ENV;lab=FINAL_LAB;scenarios=[('genuine-source-strike',FINAL_SEED,'GameLoop')]\n"+text[end:]
  text=text.replace('key=(cut[0],cut[2],cut[3])','key=cut[0]').replace("cuts=V.fold_cuts(ref['cuts'])","cuts=FINAL_FOLD(ref['cuts'])")
  text=text.replace("counts['lag_NMI_gather']==1846","counts['lag_NMI_gather']==sum(len(FINAL_FOLD(row[0]['cuts']))for row in references)")
  text=text.replace('audio=m[0x7da];wr=', 'audio=m[0x7da];smack=m[0x7d8];wr=').replace("and audio==m[0x7da]and", "and audio==m[0x7da]and smack==m[0x7d8]and")
  env=dict(__file__=str(Path(__file__)),__name__='prince_strike_nested_v127',FINAL_ENV=e,FINAL_LAB=lab,FINAL_SEED=seed,FINAL_FOLD=U.V.fold);exec(compile(text,str(source),'exec'),env);env['main']()
 finally:U.inject=old_inject;U.C.V.normalized_state=old_normalize
 p=O/'post-return-nested-IRQ-CPU-v127.json';q=json.loads(p.read_text());q.update(source_code_injected=True,qualified_cold=False,new_lifetimes_ungranted=False,source_prototype='Final122 owned no-drop acknowledgement and existing row34 delivery.',finite_fixed_IRQ_closure=IRQ.irq_closure(),nested_domain='Every reached FF-lag handlerPC at its lowest realSP over every recorded final122 earned-strike foreground cut. Exact fixed68B branchless/call-free IRQ has no A/C-window reads or mapping effects, so folding only by handlerPC preserves the deepest stack and full state proof.',scope='Source-only prototype after97 authenticated full cold; genuine original strike and exact native suffix9AF8. Native IRQ only at real handlerI0, including FF-lag CLI.07D8/07DA are traced native AudioUpdate lengths; IRQ preserves both and all private/R0..7/SMC/maps/AXYP/SP. Changed backing/cookie/cold and native emulator remain pending.')
 q['bindings'].update({p.relative_to(U.R).as_posix():U.C.C.C.M.sha(p.read_bytes())for p in [Path(__file__),Path(H.__file__),Path(U.__file__),O/'deferred-strike-measurement-v122.json',O/'native-drop-policy-CPU-v119.json',O/'strike-lifetime-CPU-v126.json']});p.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'strike-nested-IRQ-negative-v127.json').write_text(json.dumps(dict(passed=False,CPU_only=True,source_injected=True,exception=repr(error)),indent=2)+'\n');raise
