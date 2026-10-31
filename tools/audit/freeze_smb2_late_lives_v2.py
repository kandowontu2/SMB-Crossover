"""Bind the actual native WriteGameText retry supplement without changing firstfreeze."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];O=R/'build/smb2-late-lives-palette-v6';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();p=O/'handoff.json';h=json.loads(p.read_text());assert sha(p)=='d6d41dda82316035c1cb37154e565aa3b908b0863707af282e222454eae632d3'
for n,v in h['bindings'].items():assert sha(n)==v,n
q=R/'build/smb2-late-lives-retry-v1/controls.json';d=json.loads(q.read_text());assert d['passed']and d['cases']==8
for n,v in d['bindings'].items():assert sha(n)==v,n
h['actual_controls']+=[str(q)];h['binding_supplement']='Eight actual WriteGameText(A1) callbacks: fullqueue stale83/publishedROM3 rejects palette withACKFF, actualNMI flush then genuineWriteGameText retries complete30Btext+7Bpalette; actualnextnormalNMI provesoriginalclassP0+blackBG. Firstfrozenhandoff unchanged.';h['bindings'].update(d['bindings']);h['bindings'].update({str(p):sha(p),str(q):sha(q),str(Path(__file__).resolve()):sha(__file__)})
out=O/'handoff-qualified-v2.json';assert not out.exists();out.write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(path=str(out),sha256=sha(out),candidate=h['candidate'],bindings=len(h['bindings']))),flush=True)
