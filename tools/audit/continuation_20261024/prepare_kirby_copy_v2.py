from pathlib import Path
D=Path(__file__).resolve().parent
t=(D/'kirby-copy-core-v1.lua').read_text()
t=t.replace('local startY,minY,maxY=176,176,176','local guardProtected=false\nlocal startY,minY,maxY=176,176,176')
t=t.replace('spawned=false;recovered=false;startY=176','spawned=false;recovered=false;guardProtected=false;startY=176')
old="  if tick>=85 then\n   assert(attackSeen,'Actual B invokes copied ability')"
new="""  if c.power==4 and tick>=28 and not guardProtected then
   assert(guardContacts>0 and r('Enemy_Flag')~=0 and r('KbHealth')==6,'Held Beetle guard protects actual overlapping contact')
   guardProtected=true;pending=function()w('Enemy_Flag',0)end
  end
  if tick>=85 then
   assert(attackSeen,'Actual B invokes copied ability')"""
assert t.count(old)==1;t=t.replace(old,new)
old="assert(guardContacts>0 and r('Enemy_Flag')~=0,'Beetle guard protects real overlapping enemy contact')";assert t.count(old)==1
t=t.replace(old,"assert(guardProtected,'Beetle guard completed before its release')")
(D/'kirby-copy-core-v2.lua').write_text(t)
t=(D/'run_kirby_copies_v1.py').read_text().replace('kirby-copies-v1','kirby-copies-v2').replace('kirby-copy-core-v1.lua','kirby-copy-core-v2.lua')
(D/'run_kirby_copies_v2.py').write_text(t)
