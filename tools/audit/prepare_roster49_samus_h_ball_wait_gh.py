"""Wait in intrinsic Morph without firing bombs that lift the player."""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[2];src=R/'tools/audit/run_roster49_samus_h_morph_gg.py';out=R/'tools/audit/run_roster49_samus_h_ball_wait_gh.py';assert not out.exists()
t=src.read_text(encoding='utf-8').replace('root49-samus-h-morph-gg','root49-samus-h-ball-wait-gh').replace('root49-h-samus-morph-gg','root49-h-samus-ball-wait-gh').replace('morph-gg.csv','ball-wait-gh.csv')
a='local b={b=c.poll%8<4,down=phase==0}';assert t.count(a)==1;t=t.replace(a,'local b={b=phase~=0 and c.poll%8<4,down=phase==0}')
t=t.replace('KeepX fixed, wait', 'KeepX fixed, wait')
a='Retain this real transition, keepX fixed, wait for actual owner2 pass/death, then ordinary A unmorph/jump edges.'
b='Retain this real transition, keepX fixed and suppress B bombs during the ball wait so no bomb-induced lift changes the waiting bank. After actual owner2 pass/death, use ordinary A unmorph/jump edges.'
assert t.count(a)==1;t=t.replace(a,b)
t=t.replace('Use the actual intrinsic Easy Morph Ball below the highfish.', 'Wait below the highfish in actual Morph Ball without bomb input.')
out.write_text(t,encoding='utf-8');print(out,hashlib.sha256(out.read_bytes()).hexdigest())
