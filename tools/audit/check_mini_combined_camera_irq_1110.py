"""Rebind all changed interrupt contexts to the exact combined cartridge."""
import json
from pathlib import Path
import check_mini_movement_vectors_1110_v1 as V
import check_mini_shared_offscreen_irq_1110_v1 as O
import check_mini_side_pair_1110 as S
import check_mini_lift_retention_vectors_1110_v1 as L
from check_mini_funded_actor_1108_v3 import install

base=Path('build/mini-box-terrain-visible-1110/candidate.nes').read_bytes()
candidate=Path('build/mini-combined-camera-native-1110/candidate.nes').read_bytes()
camera=json.loads(Path('build/mini-camera-lifts-v2-1110/proof.json').read_text())
retained=json.loads(Path('build/mini-lift-retention-1110/proof-v2.json').read_text())
images=[V.M.P.bundle(q) for q in (base,candidate)]
out=Path('build/mini-combined-camera-vectors-1110');out.mkdir(exist_ok=True)
result=dict(passed=True,parent_SHA256=V.M.P.sha(base),candidate_SHA256=V.M.P.sha(candidate),
            movement=V.audit(images),offscreen=O.vectors(images),side=S.interrupts(candidate),
            lifts=L.qualify(install(base,camera['patches']),candidate,retained['labels']))
(out/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k.endswith('SHA256') or k=='passed'})
