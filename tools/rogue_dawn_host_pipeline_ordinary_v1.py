"""Actual ordinary mapper builds of the private expanded-only sparse hooks."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import rogue_dawn_host_transactions_build_controls_v1 as original
import rogue_dawn_map_v1 as ref

def main():
 original.O=R/'build/rogue-dawn-host-pipeline-v2';original.main()
 p=original.O/'ordinary-controls.json';d=json.loads(p.read_text())
 d['bindings'].append(ref.binding(Path(__file__)));p.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
