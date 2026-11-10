"""Run actual FF/IRQ cuts without renaming nested generated function strings."""
import inspect,json
from pathlib import Path
import check_manual_wide_horizontal_qualification_1110 as Q


def vectors(bundle,labels,axis,pc):
 source=inspect.getsource(Q.D.vectors).replace('def vectors(','def local_vectors(',1)
 needle='if not (inside or hot) or key in seen:'
 assert source.count(needle)==1
 source=source.replace(needle,
  f'if not (inside or hot or tag == 154 and {pc} <= pc < {pc+256}) or key in seen:',1)
 env=dict(Q.D.__dict__);exec(source,env)
 return env['local_vectors'](bundle,labels,axis)


def main():
 old,new,q=Q.images();before,after=Q.P.bundles(old,new)
 results={}
 for axis in (0x28,0x24):
  results[axis]=vectors(after,q['labels'],axis,q['format']['table_pc'])
  print('Actual owned vectors',axis,results[axis],flush=True)
 receipt=dict(passed=True,preliminary_proof_SHA256=Q.sha(Q.PROOF),
  expected_memory_only_SHA256=q['expected_memory_only_SHA256'],owned=results,
  bindings={p.relative_to(Q.R).as_posix():Q.sha(p) for p in (Path(__file__).resolve(),Path(Q.__file__).resolve())})
 (Q.OUT/'irq.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
