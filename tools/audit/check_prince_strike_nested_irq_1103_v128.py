"""Rebind the final strike interrupt proof to its immutable Bub66 input."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_nested_irq_1102_v127 as V
import prepare_prince_current_post_return_1102_v97 as M
O=V.O
PARENT=R/'build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes'


def main():
 assert M.sha(PARENT.read_bytes())==M.PARENT
 M.NIGHTLY=PARENT
 source=Path(V.__file__);text=source.read_text().replace('v127','v128')
 env=dict(__file__=str(Path(__file__)),__name__='prince_strike_nested_v128');exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'post-return-nested-IRQ-CPU-v128.json';q=json.loads(path.read_text());assert q['passed']
 q.update(immutable_parent_input=PARENT.relative_to(R).as_posix(),immutable_parent_SHA256=M.PARENT,supersedes_footer_baseline_pin_failure='v127 completed all932 nested cuts before its footer reread the changed Downloads image. This distinct complete rerun pins the exact original Bub66 input; it does not qualify cf7.')
 q['bindings'].update({p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),source]});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'strike-nested-IRQ-negative-v128.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
