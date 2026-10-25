from pathlib import Path
D=Path(__file__).resolve().parent
t=(D/'kirby-copy-core-v2.lua').read_text();old="  if tick>=85 then\n   assert(attackSeen,'Actual B invokes copied ability')";assert t.count(old)==1
t=t.replace(old,"  assert(tick<400,'Copied movement must return to the arena floor after release')\n  if tick>=85 and r('Player_State')==0 then\n   assert(attackSeen,'Actual B invokes copied ability')")
(D/'kirby-copy-core-v3.lua').write_text(t)
t=(D/'run_kirby_copies_wave_v1.py').read_text().replace('kirby-copy-core-v2.lua','kirby-copy-core-v3.lua').replace('kirby-copies-wave-v1','kirby-copies-wave-v2')
(D/'run_kirby_copies_wave_v2.py').write_text(t)
