"""Final170 harness and current159 native lag-NMI nested IRQ closure."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_live_policy_nested_1103_v169 as V
import check_prince_live_policy_final_1103_v170 as C
import check_prince_backdrop_native_1103_v160 as HOST
O=C.O


def main():
 text=inspect.getsource(V.main).replace('v169','v171').replace('live-policy-ISR-v168','live-policy-ISR-v170').replace('C.V.V.','HOST.')
 env=dict(V.__dict__,C=C,HOST=HOST,__file__=str(Path(__file__)));exec(compile(text,str(Path(V.__file__)),'exec'),env);env['main']()
 annotate()


def annotate():
 path=O/'post-return-nested-IRQ-CPU-v171.json';q=json.loads(path.read_text())
 assert q['passed']and q['counts']==dict(lag_NMI_gather=1208,nested_IRQ=777)and q['minimum_nested_IRQ_SP']==125
 q['nested_domain']='All1208 actual current159 genuineFF foreground cuts:639first8GameLoop constructor,298nativeGetPlayerColors,240fullWriteGameText,31newcold staging/installer/thunk I1cuts. Each reachedlaghandlerPC is replayed at lowestactualSP,777eligibleIRQ locations; fixed68B IRQ has no A/C-window data or mapper effects. Historical1846/death/star wording from generic92 is superseded by this exact domain.'
 q['receipt_annotation_only']='Final annotation corrects inherited generic92 nested_domain description; actual1208gathers/777replays/minSP125 and all machine assertions were already complete. No tested code/oracle changed.'
 q['bindings'].update({p.relative_to(R).as_posix():HOST.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),Path(C.__file__)]});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:annotate()if '--annotate-only'in sys.argv else main()
 except Exception as error:
  (O/'live-policy-nested-negative-v171.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
