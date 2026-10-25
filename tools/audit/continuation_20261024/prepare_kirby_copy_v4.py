from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'kirby-copy-core-v3.lua').read_text()
t=t.replace('local guardProtected=false','local guardProtected=false;local hovering=false')
t=t.replace('guardProtected=false;startY=176','guardProtected=false;hovering=false;startY=176')
t=t.replace("if phase=='inhale'then b.b=tick>=8","if phase=='inhale'then b.b=tick>=1")
old="if c.power==10 and tick>=8 and tick<30 then minY=math.min(minY,r('Player_Y_Position'));maxY=math.max(maxY,r('Player_Y_Position'));assert(maxY-minY<=3,'Cloud hover limits vertical drift while B is held')end"
new="if c.power==10 and tick>=8 and tick<30 then if not hovering then hovering=true;minY=r('Player_Y_Position');maxY=minY end;minY=math.min(minY,r('Player_Y_Position'));maxY=math.max(maxY,r('Player_Y_Position'));assert(maxY-minY<=3,'Cloud hover limits vertical drift while B is held')end"
assert t.count(old)==1;t=t.replace(old,new)
(D/'kirby-copy-core-v4.lua').write_text(t)
t=(D/'run_kirby_copies_wave_v2.py').read_text().replace('kirby-copy-core-v3.lua','kirby-copy-core-v4.lua').replace('kirby-copies-wave-v2','kirby-copies-wave-v3')
(D/'run_kirby_copies_wave_v3.py').write_text(t)
