"""Accept identical anonymous JMP-table PCs by exact physical opcode proof.

Retain v1's false diagnostic at unchanged FF service15 B42D; reuse its
completed16,384 strict NrMovement pairs on these exact same cart hashes.
"""
from pathlib import Path
import json
p=Path(__file__).with_name('functional_roster_smb2_dispatch_v1.py');s=p.read_text()
s=s.replace("B.O/'dispatch-controls'","B.O/'dispatch-controls-v2'")
old="assert matched,('genuine callback identity',case,x,y,names)"
new="""if not matched and (x['dest'],x['bank'])==(y['dest'],y['bank']):
  at=x['dest']&8191;bank=x['bank']&127
  assert a.ROM_banks[bank][at:at+8]==b.ROM_banks[bank][at:at+8],('unchanged anonymous table opcode',case)
  matched=['same-physical-JMP-table-slot']
 assert matched,('genuine callback identity',case,x,y,names)"""
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("for name in['NrMovement','GmFreshGate']:","for name in['GmFreshGate']:")
anchor="try:\n  aa,bb=[T.bus(x)for x in[P,N]]"
new="""try:
  prior=json.loads((B.O/'dispatch-controls/result.json').read_text())
  for path,digest in prior['bindings'].items():assert B.sha(path)==digest,path
  counts.update(prior['partial_checks'])
  assert counts['NrMovement']['cases']==16384
  aa,bb=[T.bus(x)for x in[P,N]]"""
assert s.count(anchor)==1;s=s.replace(anchor,new)
s=s.replace("B.O/'source-stage.json']","B.O/'source-stage.json',B.O/'dispatch-controls/result.json',Path(__file__).with_name('functional_roster_smb2_dispatch_v1.py')]")
exec(compile(s,__file__,'exec'),globals())
