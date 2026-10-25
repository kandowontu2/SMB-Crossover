from pathlib import Path
import hashlib
D=Path(__file__).resolve().parent
p=D/'capture_food_v3.py';t=p.read_text();old='def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()';new='''def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()'''
assert t.count(old)==1;t=t.replace(old,new)
(D/'capture_food_v4.py').write_text(t)
