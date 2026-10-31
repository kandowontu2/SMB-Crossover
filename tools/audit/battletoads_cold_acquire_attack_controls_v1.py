"""Exact-v4 genuine E2/native enemy bridge rebind."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_native_attack_controls_v1 as M
M.O=R/'build/battletoads-cold-acquire-v4';M.J=M.O/'joint'
if __name__=='__main__':
 M.main()
 p=M.O/'attack-controls.json';q=json.loads(p.read_text());q['bindings'][str(Path(__file__).resolve())]=M.T.L.sha(Path(__file__));p.write_text(json.dumps(q,indent=2)+'\n')
