"""Static exact-span provenance for completed earlier source-only campaigns."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'build/rogue-dawn-host-pipeline-v2'
def bind(p):
 p=Path(p);v=p.read_bytes();return dict(path=str(p),bytes=len(v),sha256=hashlib.sha256(v).hexdigest())
def main():
 p=R/'build/rogue-dawn-host-deferred-v1/candidate.nes';q=O/'candidate.nes';a=p.read_bytes();b=q.read_bytes();rows=[]
 for bank,pc,n,role in [(124,0xb000,4090,'entire frozen literal CORE'),(124,0xae00,508,'entire frozen literal AUX'),(94,0xdf50,175,'entire genuine C94 callback bridge'),(95,0xa600,3560,'entire prior deferred services/selector/native transaction prefix'),(128+680//8,0,16384,'entire reserved Rogue CHR')]:
  at=16+1048576+680*1024 if role.endswith('CHR') else 16+bank*8192+(pc&8191)
  assert a[at:at+n]==b[at:at+n],role
  rows.append(dict(role=role,offset=at,bytes=n,sha256=hashlib.sha256(b[at:at+n]).hexdigest()))
 out=O/'span-reuse.json';assert not out.exists()
 proof=dict(passed=True,native_run=False,classification='Static byte-equivalence only. Earlier18,432 action/input/gear/facing cells completed before preserved standalone flush failure; neither old aggregate nor native scope is retagged.',spans=rows,bindings=[bind(v)for v in[Path(__file__),p,q,R/'build/rogue-dawn-host-deferred-v1/control-SP192-deferred-negative.json',O/'handoff.json']])
 out.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(bind(out)))
if __name__=='__main__':main()
