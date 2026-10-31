"""Correct only the inherited receipt path after v1's binding I/O failure.

All menu/cold/selector assertions are unchanged. V1's failed receipt is kept.
"""
from pathlib import Path
p=Path(__file__).with_name('functional_roster_ready54_controls_v1.py');s=p.read_text()
assert s.count("O=B.O/'controls'")==1;s=s.replace("O=B.O/'controls'","O=B.O/'controls-v2'")
anchor="exec(compile(s,str(source),'exec'),dict(__name__='__main__',__file__=str(source)))"
assert s.count(anchor)==1
s=s.replace(anchor,"s=s.replace(\"A.O/'proposal.json'\",\"R/'build/arthur-quick-functional-admission-v1/proposal.json'\")\n  "+anchor)
exec(compile(s,__file__,'exec'),globals())
