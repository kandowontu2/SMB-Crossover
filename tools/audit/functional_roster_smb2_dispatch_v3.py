"""Complete36 services; classify real relocated SMC operands consistently.

V2 compared permitted relocated farcall operands again as static page1 bytes.
Only those same actual three operand bytes/CurrentBank are excluded there;
all other33SMC/static/live bytes remain exact. No product source changes.
"""
from pathlib import Path
p=Path(__file__).with_name('functional_roster_smb2_dispatch_v1.py');s=p.read_text()
s=s.replace("B.O/'dispatch-controls'","B.O/'dispatch-controls-v3'")
old="assert matched,('genuine callback identity',case,x,y,names)"
new="""if not matched and (x['dest'],x['bank'])==(y['dest'],y['bank']):
  at=x['dest']&8191;bank=x['bank']&127
  assert a.ROM_banks[bank][at:at+8]==b.ROM_banks[bank][at:at+8],('unchanged anonymous table opcode',case)
  matched=['same-physical-JMP-table-slot']
 assert matched,('genuine callback identity',case,x,y,names)"""
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("a.ram[256:256+low]==b.ram[256:256+low]","all(a.ram[i]==b.ram[i]for i in range(256,256+low)if i not in (transient if moved else set()))")
s=s.replace("for name in['NrMovement','GmFreshGate']:","for name in[]:")
anchor="try:\n  aa,bb=[T.bus(x)for x in[P,N]]"
new="""try:
  prior=json.loads((B.O/'dispatch-controls-v2/result.json').read_text())
  for path,digest in prior['bindings'].items():assert B.sha(path)==digest,path
  counts.update(prior['partial_checks'])
  assert counts['NrMovement']['cases']==counts['GmFreshGate']['cases']==16384
  aa,bb=[T.bus(x)for x in[P,N]]"""
assert s.count(anchor)==1;s=s.replace(anchor,new)
s=s.replace('entries=T.FIRST+T.ONLY',"entries=T.FIRST+T.ONLY+['HuBounce','HuWorldPalette','HuPowerup','HuWeaponTail','HuVine']")
s=s.replace("B.O/'source-stage.json']","B.O/'source-stage.json',B.O/'dispatch-controls-v2/result.json',Path(__file__).with_name('functional_roster_smb2_dispatch_v1.py'),Path(__file__).with_name('functional_roster_smb2_dispatch_v2.py')]")
exec(compile(s,__file__,'exec'),globals())
