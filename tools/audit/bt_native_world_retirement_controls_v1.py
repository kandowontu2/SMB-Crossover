"""Rebind exact early-retirement/actual BT loader checks to the new cookie."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bt_jmp_cold_retirement_controls_v3 as A
A.J=R/'build/bt-native-world-source-v2/joint';A.O=R/'build/bt-native-world-retirement-controls-v1'
if __name__=='__main__':
 A.main();p=A.O/'controls.json';q=json.loads(p.read_text());q['bindings'][str(Path(__file__).resolve())]=A.V.sha(__file__);p.write_text(json.dumps(q,indent=2)+'\n')
