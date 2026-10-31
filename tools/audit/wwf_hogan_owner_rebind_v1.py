"""Existing finite physical-owner API suite on the final private host source."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_first_hogan_owner_controls_v1 as T
J=R/'build/wwf-hogan-natural-source-v15/joint';O=R/'build/wwf-hogan-owner-rebind-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 T.J=J;T.S=J.parent/'source-stage.json';T.O=O;T.main()
 p=O/'controls.json';q=json.loads(p.read_text());q.pop('no_host_hooks',None)
 q['scope']='Physical owner API rebind only. The final private source also contains explicitly funded menu/scene/Main hooks, qualified in separate bound receipts. No native/install.'
 q['checks']['retirement_allflags_foreign_exact'].pop('physical_hooks_installed',None)
 q['bindings'][str(Path(__file__).resolve())]=sha(__file__);p.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
