"""Verify/copy frozen current SMB2 world sound source evidence; no Git edits."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2];P=R/'build/smb2-current-world-sfx-v12'
O=R/'docs/qa/checkpoints/2026-10-30/smb2-current-world-sfx-source'
def bind(p):
 p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 assert not O.exists();h=json.loads((P/'handoff.json').read_text())
 for z in h['bindings']:assert bind(z['path'])==z,z['path']
 with zipfile.ZipFile(P/'source-only.zip')as a:
  assert a.testzip()is None;members=a.namelist()
  for name in members:
   f=R/name;assert f.is_file()and a.read(name)==f.read_bytes(),name
   assert f.suffix.lower()not in['.nes','.exe','.o','.dep','.dbg','.lbl','.map'],name
 O.mkdir(parents=True);copies=[]
 names=['handoff.json','HANDOFF.md','source-only.zip','source-closure.json','world-controls.json','current-controls.json','pause-controls.json','loader-controls.json','pause-first-negative.json','pause-negative/handoff.json','world-first-negative.json','fixture-corrections.json','output-guard-controls.json']
 for name in names:
  src=P/name;dst=O/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
  assert src.read_bytes()==dst.read_bytes();copies.append(dict(original=bind(src),copy=bind(dst)))
 out=dict(status=h['status'],tool=bind(__file__),original_handoff=bind(P/'handoff.json'),candidate=h['candidate'],bindings=len(h['bindings']),source_zip_members=len(members),copies=copies,limits=h['limits'],previous_current_C82_checkpoint=bind(R/'docs/qa/checkpoints/2026-10-30/smb2-current-joint-c82-source/receipt.json'),no_native_or_shared_installation=True)
 (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(receipt=bind(O/'receipt.json'),bindings=len(h['bindings']),members=len(members),copied_files=len(copies)),indent=2))
if __name__=='__main__':main()
