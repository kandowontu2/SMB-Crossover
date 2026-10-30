"""Export predecessor/proposal negatives without modifying frozen v6/v7."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[1];D=R/'docs/qa/checkpoints/2026-10-30/smb2-current-cold-typed-source'
def bind(p):
 p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 paths=[
 'build/smb2-roll-current-relocation-v5/handoff.json',
 'build/smb2-roll-current-relocation-v5/source-only.zip',
 'build/smb2-roll-current-relocation-v5/HANDOFF.md',
 'build/smb2-roll-current-relocation-v5/consumer-inventory.json',
 'build/smb2-roll-current-relocation-v5/inherited-harness-negatives.json',
 'build/smb2-roll-current-relocation-v5/prediction-negative.json',
 'build/smb2-roll-tail-reclaim-v4/handoff.json',
 'build/smb2-roll-status-fix-v3/handoff.json',
 'build/smb2-roll-status-reclaim-v2/negative.json',
 'build/smb2-current-component-v1/handoff.json',
 'build/smb2-current-component-v1/INTEGRATION.md',
 'build/smb2-current-component-v1/native-imports.json',
 'build/smb2-current-cold-init-v6/harness-negatives.json',
 'build/smb2-current-typed-services-v7/proposal-negatives.json',
 'build/smb2-current-typed-services-v7/controls.json',
 'build/smb2-current-typed-services-v7/build.py',
 'tools/smb2_roll_relocation_controls_v1.py',
 'tools/prepare_cv3_dmc_mirror.py']
 assert not(D/'predecessor-supplement.zip').exists()
 h=json.loads((R/paths[0]).read_text())
 for z in h['bindings']:assert bind(z['path'])==z,z['path']
 with zipfile.ZipFile(D/'predecessor-supplement.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as a:
  for p in paths:a.write(R/p,p)
  a.write(__file__,'build/smb2-current-checkpoint-supplement-v1.py')
 shutil.copyfile(__file__,D/'supplement-export.py')
 out=dict(status='IMMUTABLE_PREDECESSOR_AND_OLD_PATH_ABI_NEGATIVES_SUPPLEMENT',prior_checkpoint_receipt=bind(D/'receipt.json'),predecessor=bind(R/paths[0]),source_archive=bind(D/'predecessor-supplement.zip'),members=[bind(R/p)for p in paths],tool=bind(D/'supplement-export.py'),note='Frozen v6/v7 archives unchanged. Their sourceZIPs already include actual relocated Roll sources, dmc-clones.s and final127.bin; this supplement adds predecessor builder/sourcearchive and explicit rejected status-byte/oldpath/ABI receipts. Original external NES ROM is hash-bound by predecessor; never copied here.')
 (D/'supplement.json').write_text(json.dumps(out,indent=2)+'\n')
 with zipfile.ZipFile(D/'predecessor-supplement.zip')as a:assert a.testzip()is None
 print(json.dumps(dict(supplement=bind(D/'supplement.json'),archive=bind(D/'predecessor-supplement.zip')),indent=2))
if __name__=='__main__':main()
