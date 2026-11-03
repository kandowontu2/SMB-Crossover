"""Replay exact frozen frontend proposal against final130 cf7 component."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_frontend_proposal_1102_v109 as V
import check_prince_strike_cold_1103_v131 as C
O=C.O


def main():
 source=Path(V.__file__);text=inspect.getsource(V.main).replace('v109','v137').replace('post-return-manifest-v97.json','strike-manifest-v130.json')
 env=dict(V.__dict__,__file__=str(Path(__file__)),C=C);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'frontend-proposal-v137.json';q=json.loads(path.read_text());old=json.loads((O/'frontend-proposal-v109.json').read_text())
 assert len(q['patches'])==9 and q['total_changed_bytes']==26
 for a,z in zip(old['patches'],q['patches']):
  assert all(a[k]==z[k]for k in ['physical_PRG','CPU_half_open','file_offset','old_hex','new_hex'])
 q.update(exact_frozen109_nine_spans_rebound=True,current_component_memory_SHA256=C.image()[1]['expected_memory_only_SHA256'],source_assembly_verification='frontend-source-CPU-v113.json unchanged exact21B resolver and74B masks; all nine current preimages verified and actual entire menu replayed.')
 q['bindings'].update({p.relative_to(R).as_posix():C.M.M.sha(p.read_bytes())for p in [Path(__file__),source,Path(C.__file__),O/'frontend-proposal-v109.json',O/'frontend-source-CPU-v113.json',O/'strike-manifest-v130.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
