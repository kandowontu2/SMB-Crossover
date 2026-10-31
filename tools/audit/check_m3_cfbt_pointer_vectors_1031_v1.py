"""Actual final-shared NMI/IRQ at M3 low/high pointer and helper cuts."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_low_table_consumer_controls_1031_v1 as T
O=R/'build/m3-cfbt-source-join-v1';J=O/'joint'
def main():
 out=O/'pointer-vectors-v1.json';assert not out.exists()
 stage=json.loads(T.B.read(O/'source-stage.json'));T.B.bound(stage)
 T.O=O;T.J=J
 q=T.vectors();q.update(candidate=stage['candidate'],native=False,source_CPU=True,
  bindings={str(p.resolve()):T.B.sha(p)for p in[Path(__file__),Path(T.__file__),O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg']})
 T.B.write(out,json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],real_vectors=q['real_vectors'],candidate=q['candidate'])))
if __name__=='__main__':main()
