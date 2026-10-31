"""Rebind established whole BW/CF scene+native-name checks to actual JMP rows."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import cf_preload_name_caller_controls_v2 as A
A.P=R/'build/bt-current-cf-component-v2/joint'
A.J=R/'build/bt-jmp-row-cold-source-v1/joint'
A.O=R/'build/bt-jmp-row-scene-controls-v1'
if __name__=='__main__':
 A.main()
 p=A.O/'controls.json';q=json.loads(p.read_text());q['scope']='Actual223B JMP-row experiment7247 vs211B parent8961: wholeBW/CF cold+warm native caller outputs and privateCfLoadIfCold15→realB020; genuine invalid31/33 native name18. All readiness stayspending. Established source fixtures, no native.'
 q['bindings'][str(Path(__file__).resolve())]=A.sha(__file__)
 for root in[A.P,A.J]:q['bindings'][str((root/'source-stage.json').resolve())]=A.sha(root/'source-stage.json')
 p.write_text(json.dumps(q,indent=2)+'\n')
