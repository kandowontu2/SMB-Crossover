"""Corrected-v10 actual native kernel source pixels; preserves v9 negative."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_native_adapter_controls_v2 as M

def main():
    T=M.T
    M.O=R/'build/battletoads-cold-acquire-v4';M.J=M.O/'joint'
    T.O=M.O;T.J=M.J;T.palettes_render=M.render
    T.main()
    p=T.O/'boundary-controls.json';q=json.loads(p.read_text())
    q['bindings'].update({str(x.resolve()):T.L.sha(x)for x in[Path(__file__),Path(M.__file__)]})
    p.write_text(json.dumps(q,indent=2)+'\n')

if __name__=='__main__':main()
