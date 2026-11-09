"""Qualify real vectors in the exact sweep/seam successor."""
import json
from pathlib import Path
import check_mini_sweep_center_irq_1110 as S
import check_mini_goomba_page_seam_1110_v1 as G

before=Path('build/mini-combined-camera-native-1110/candidate.nes').read_bytes()
after=Path('build/mini-sweep-seam-native-1110/candidate.nes').read_bytes()
assert G.P.sha(before)=='56c4135e3edd7421c207fd4cd623ad8f58cd263353342d0af54202cd790cbcbc'
assert G.P.sha(after)=='ddd6e71b42aaed99645a54b64b766b4fb3a32aee5c3b55bfe9b7c552000c94b3'
out=Path('build/mini-sweep-seam-vectors-1110');out.mkdir(exist_ok=True)
q=dict(passed=True,parent_SHA256=G.P.sha(before),candidate_SHA256=G.P.sha(after),
       sweep=S.qualify(after),seam=G.vectors([G.P.bundle(x) for x in (before,after)]))
(out/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
print(dict(passed=True,candidate_SHA256=q['candidate_SHA256']))
