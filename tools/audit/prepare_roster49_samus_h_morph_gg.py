"""Retain the actual source Easy Morph entry displacement during the safe wait."""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[2];src=R/'tools/audit/run_roster49_samus_h_crouch_gf.py';out=R/'tools/audit/run_roster49_samus_h_morph_gg.py';assert not out.exists()
t=src.read_text(encoding='utf-8').replace('root49-samus-h-crouch-gf','root49-samus-h-morph-gg').replace('root49-h-samus-crouch-gf','root49-h-samus-morph-gg').replace('crouch-gf.csv','morph-gg.csv')
a="assert(c.grounded and c.x>=2755 and c.x<2760 and c.y==112 and(l~=0 or r~=0),'Actual144-top bank wait')"
b="assert(c.x>=2755 and c.x<2760 and ((c.grounded and c.y==112 and(l~=0 or r~=0))or(c.r('SmBall')~=0 and c.y>=107 and c.y<=112)),'Actual bank or source Easy Morph entry displacement')"
assert t.count(a)==1;t=t.replace(a,b)
t=t.replace('Hold actual Down crouch on the real bank while owner2 passes32px behind/dead/inactive, then release normally before approaching2816 staircase. No assumed standing clearance.', 'Actual Easy Down enters intrinsic Morph Ball; its documented SamusMorphEnter->Exit lifts five NESpx and briefly clears grounded without SmSourceJumped. Retain this real transition, keepX fixed, wait for actual owner2 pass/death, then ordinary A unmorph/jump edges. GF host ground assertion is retained as observer negative, not a runtime failure.')
t=t.replace('Crouch under the actual highfish on the supported late bank.', 'Use the actual intrinsic Easy Morph Ball below the highfish.')
out.write_text(t,encoding='utf-8');print(out,hashlib.sha256(out.read_bytes()).hexdigest())
