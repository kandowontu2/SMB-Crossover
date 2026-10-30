"""Verify and archive frozen private Benj graphics/Fresh evidence; no Git."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-30/benj-host-graphics-fresh-source'
def bind(p):
 p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 assert not O.exists();stages=[];copies=[]
 for version in['v2','v3']:
  p=R/f'build/benj-mario-native-host-{version}';h=json.loads((p/'handoff.json').read_text())
  for z in h['bindings']:assert bind(z['path'])==z,z['path']
  with zipfile.ZipFile(p/'source-only.zip')as a:
   assert a.testzip()is None;members=a.namelist()
   for n in members:
    f=R/n;assert f.is_file()and f.read_bytes()==a.read(n),n
    assert f.suffix.lower()not in['.nes','.exe','.o','.dep','.dbg','.lbl','.map'],n
  for name in['handoff.json','HANDOFF.md','source-only.zip','source-closure.json','graphics-controls.json']+(['controls.json']if version=='v3'else[]):
   src=p/name;dst=O/version/name;dst.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();copies.append(dict(original=bind(src),copy=bind(dst)))
  stages.append(dict(version=version,candidate=h['candidate'],handoff=bind(p/'handoff.json'),bindings=len(h['bindings']),source_members=len(members),status=h['status'],limits=h['limits']))
 (O/'receipt.json').write_text(json.dumps(dict(tool=bind(__file__),stages=stages,copies=copies,no_native_or_install=True),indent=2)+'\n')
 print(json.dumps(dict(receipt=bind(O/'receipt.json'),stages=stages),indent=2))
if __name__=='__main__':main()
