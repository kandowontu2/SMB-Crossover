"""Read-only verify frozen SMB2 cohorts, then copy compact source evidence."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-30/smb2-current-main-nmi-source'
def bind(p):
 p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 assert not O.exists();O.mkdir(parents=True);packets=[];copies=[]
 for label,folder in [('main','smb2-current-main-cohort-v9'),('nmi','smb2-current-nmi-audio-v10')]:
  p=R/'build'/folder;h=json.loads((p/'handoff.json').read_text())
  for z in h['bindings']:assert bind(z['path'])==z,z['path']
  with zipfile.ZipFile(p/'source-only.zip')as a:
   assert a.testzip()is None;members=a.namelist()
   for n in members:
    f=R/n;assert f.is_file()and a.read(n)==f.read_bytes(),n
  names=['handoff.json','HANDOFF.md','source-closure.json','source-only.zip']
  names+=['main-controls.json','foreign-controls.json','layout-controls.json','stale-dmc-predecessor-negative.json']if label=='main'else['controls.json','seams-controls.json','gameplay-controls.json','fresh-reclaim-proof.json','gameplay-first-negative.json']
  dest=O/label;dest.mkdir()
  for n in names:
   src=p/n;dst=dest/n;shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();copies.append(dict(original=bind(src),copy=bind(dst)))
  packets.append(dict(kind=label,original_handoff=bind(p/'handoff.json'),candidate=h['candidate'],bindings=len(h['bindings']),source_zip_members=len(members),description=h['description'],limits=h['limits']))
 # Retain actual v8 product negative, not just its interpretation.
 neg=R/'build/smb2-current-main-cohort-v8';dest=O/'prior-negative';dest.mkdir()
 for n in ['negative-handoff.json','negative-source.zip','first-main-negative.json','contact-probe.json']:
  src=neg/n;dst=dest/n;shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();copies.append(dict(original=bind(src),copy=bind(dst)))
 prior=R/'docs/qa/checkpoints/2026-10-30/smb2-current-cold-typed-source/receipt.json'
 out=dict(status='PRIVATE_SMB2_TRUE_MAIN_CARRY_NMI_SOURCE_CPU_PASS_STILL_PENDING',tool=bind(__file__),packets=packets,copies=copies,previous_cold_typed_and_Roll_predecessor_checkpoint=bind(prior),no_native_or_shared_installation=True,scope='Source exact current52/Kama/Celeste preserved; all4SMB2 pending. v9 realGameLoop and v10 realNMI/audio sound acquisition are independent predecessor common cohorts, not blindly overlayable onto current FF/Ar/Quick. WorldSFXmixer and coordinated shared ingress still pending. ForeignMain +159..497CPU and foreignNMI +51CPU explicitly unqualified.')
 (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(receipt=bind(O/'receipt.json'),bindings=sum(p['bindings']for p in packets),zip_members=sum(p['source_zip_members']for p in packets),copied_files=len(copies)),indent=2))
if __name__=='__main__':main()
