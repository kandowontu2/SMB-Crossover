from pathlib import Path
import json,hashlib
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
p=D/'ryu-head-packet-v5/packet.json';q=json.loads(p.read_text());print(list(q))
for key in ('source_files','source_hashes','files'):
 if key in q:
  x=q[key];print(key,type(x).__name__,len(x));print(str(next(iter(x.items()))if isinstance(x,dict)else x[0])[:260])
