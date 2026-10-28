"""Real menu/lives PPU capture + ordinary controller1-1; no native launch."""
from pathlib import Path
import argparse,json
import current_roster_compact_11_v1 as base
from roster_expansion_native_prepare_v2 import navigation
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--identity',choices=['alex','ryan','celeste'],required=True)
 p.add_argument('--mode',choices=['easy','hard'],default='easy');p.add_argument('--frames',type=int,default=6500)
 p.add_argument('--policy',type=Path,required=True);p.add_argument('--replay',type=Path)
 a=p.parse_args()
 base.BASE.update(alex=(20,21,'RcVariant',0),ryan=(20,21,'RcVariant',1),celeste=(0,0,'MarioVariant',4))
 base.navigation=navigation;base.SCRIPT=Path(__file__).with_name('roster_expansion_cold_capture_v3.lua')
 base.prepare(a);ready=a.output.resolve()/'ready.json';d=json.loads(ready.read_text())
 for dep in [Path(__file__).resolve(),Path(__file__).with_name('roster_expansion_native_prepare_v2.py')]:d['bindings'][str(dep)]=base.sha(dep)
 d['controller_scope']='Real cold menu/Select/lives and controller1-1; native cold PPU added, total <=8selected whole frames, zero memory writes/cheats'
 ready.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(ready=str(ready),sha256=base.sha(ready))))
if __name__=='__main__':main()
