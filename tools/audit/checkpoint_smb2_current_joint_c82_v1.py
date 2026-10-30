"""Verify frozen current S2/Roll/C82 leaf, then copy compact source evidence."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/smb2-current-joint-source-v11'
O=R/'docs/qa/checkpoints/2026-10-30/smb2-current-joint-c82-source'

def bind(p):
 p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def main():
 assert not O.exists()
 h=json.loads((P/'handoff.json').read_text())
 assert h['candidate']['sha256']=='c15b50da02221e2e3ae4339d6552808bbe1540ada0bf25803ee5a0da98cb995e'
 for z in h['bindings']:assert bind(z['path'])==z,z['path']
 with zipfile.ZipFile(P/'source-only.zip')as a:
  assert a.testzip()is None
  members=a.namelist()
  for n in members:
   assert Path(n).suffix.lower()not in['.nes','.exe','.o','.dep','.dbg','.lbl','.map'],n
   p=R/n;assert p.is_file()and a.read(n)==p.read_bytes(),n
 O.mkdir(parents=True);copies=[]
 names=['handoff.json','HANDOFF.md','source-closure.json','source-only.zip','integration-api.json',
  'current-controls.json','layout-controls.json','main-controls.json','loader-controls.json',
  'output-guard-controls.json','actual-public-export-inventory.json','build-proof.json',
  'current-first-negative.json','main-first-negative.json','layout-unexplained-negative.json',
  'recovery-only/exact-original-recovery-proof.json']
 for name in names:
  src=P/name;dst=O/name;dst.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes()
  copies.append(dict(original=bind(src),copy=bind(dst)))
 out=dict(status=h['status'],tool=bind(__file__),original_handoff=bind(P/'handoff.json'),candidate=h['candidate'],
  bindings=len(h['bindings']),source_zip_members=len(members),copies=copies,
  previous_Main_NMI_checkpoint=bind(R/'docs/qa/checkpoints/2026-10-30/smb2-current-main-nmi-source/receipt.json'),
  description=h['description'],limits=h['limits'],no_native_or_shared_installation=True,
  scope='Genuine current8062 source rebase; current Main delta0..0 versus qualified Roll fix-only reference; foreign NMI+132 CPU explicitly unqualified. C82 real vector/DMC/Quick loader passes. Raw25 natural foreground/lifecycle and world SFX mixer pending; four SMB2 profiles remain pending. Exact recovery proof and build-output guard retained without normalizing old receipts.')
 (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(receipt=bind(O/'receipt.json'),bindings=len(h['bindings']),zip_members=len(members),copied_files=len(copies)),indent=2))

if __name__=='__main__':main()
