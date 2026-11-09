import sys,json
from pathlib import Path
sys.path.insert(0,'tools/audit')
import check_mini_movement_vectors_1110_v1 as V
import check_mini_shared_offscreen_irq_1110_v1 as O
base=Path('build/mini-box-terrain-visible-1110/candidate.nes');candidate=Path('build/mini-move-offscreen-native-1110/candidate.nes')
images=[V.M.P.bundle(p.read_bytes()) for p in (base,candidate)]
out=Path('build/mini-move-offscreen-vectors-1110');out.mkdir(exist_ok=True)
result=dict(passed=True,base_SHA256=V.M.P.sha(base.read_bytes()),candidate_SHA256=V.M.P.sha(candidate.read_bytes()),movement=V.audit(images),offscreen=O.vectors(images))
(out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k not in ('movement','offscreen')})
