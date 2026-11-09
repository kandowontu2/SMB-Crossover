import sys
sys.path.insert(0,'tools/audit')
from compose_mini_frame_budget_1108 import compose,load,digest
from pathlib import Path
import json,shutil,argparse
ap=argparse.ArgumentParser()
ap.add_argument('--proof',type=Path,default=Path('build/mini-camera-lifts-1110/proof.json'))
ap.add_argument('--output',type=Path,default=Path('build/mini-camera-native-1110'))
ap.add_argument('--kernel',type=Path,default=Path('build/mini-kernel-transport-1109/v2/kernel.bin'))
args=ap.parse_args()
base=Path('build/mini-box-terrain-visible-1110/candidate.nes'); raw=base.read_bytes();new=bytearray(raw)
proof=args.proof;compose(raw,new,load(proof),parent=digest(raw))
out=args.output;out.mkdir(exist_ok=True);rom=out/'candidate.nes';rom.write_bytes(new)
for ext in ('.dbg','.lbl'):shutil.copyfile(base.with_suffix(ext),rom.with_suffix(ext))
meta=load(base.with_suffix('.json'));meta.update(parent_SHA256=digest(raw),candidate_SHA256=digest(new),camera_lift_proof=str(proof));rom.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
from qualify_mini_busy_1109 import run_suite,ROOT
run_suite(out/'native',rom,args.kernel.resolve(),('route',))
