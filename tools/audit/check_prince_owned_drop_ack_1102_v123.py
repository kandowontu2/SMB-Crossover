"""Final validated-actor acknowledgement source prototype qualification."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_owned_drop_ack_1102_v121 as V
O=V.O


def main():
 source=Path(V.__file__);text=source.read_text().replace('v121','v123').replace('v120','v122')
 env=dict(__file__=str(Path(__file__)),__name__='prince_final_drop_ack_v123');exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'deferred-strike-CPU-v123.json';q=json.loads(path.read_text());assert q['passed']
 q['bindings'].update({source.relative_to(R).as_posix():V.C.C.C.M.sha(source.read_bytes())});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'deferred-strike-negative-v123.json').write_text(json.dumps(dict(passed=False,CPU_only=True,source_injected=True,exception=repr(error)),indent=2)+'\n');raise
