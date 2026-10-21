"""Use actual crouch head clearance for the observed high-fish edge."""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[2];src=R/'tools/audit/run_roster49_samus_h_wait_gc.py';out=R/'tools/audit/run_roster49_samus_h_crouch_gf.py';assert not out.exists()
t=src.read_text(encoding='utf-8')
t=t.replace('root49-samus-h-wait-gc','root49-samus-h-crouch-gf').replace('root49-h-samus-wait-gc','root49-h-samus-crouch-gf').replace('wait-gc.csv','crouch-gf.csv')
a='local b={b=c.poll%8<4}';assert t.count(a)==1;t=t.replace(a,'local b={b=c.poll%8<4,down=phase==0}')
a='local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.right and 1 or 0)';assert t.count(a)==1;t=t.replace(a,a+'+(b.down and 4 or 0)')
a='The current highfish2 passes over the standing bank safely; wait until actual owner is32px behind/dead/inactive before approaching2816 staircase.'
b='Native GC standing topY113 touches highfish bottom113 at30479. Hold actual Down crouch on the real bank while owner2 passes32px behind/dead/inactive, then release normally before approaching2816 staircase. No assumed standing clearance.'
assert t.count(a)==1;t=t.replace(a,b)
t=t.replace('Wait for actual highfish pass before the final supported water steps.', 'Crouch under the actual highfish on the supported late bank.')
out.write_text(t,encoding='utf-8');print(out,hashlib.sha256(out.read_bytes()).hexdigest())
