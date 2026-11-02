"""Compact explicit Prince source/proposal checkpoint; no ROM/DBG or trees."""
from pathlib import Path
import hashlib,json,zipfile
import audit_prince_pool_1102_v1 as A
R,O=A.R,A.O
SOURCES=[
 'tools/reference/prince_original_cpu_1101_v1.py',
 *['tools/audit/'+n for n in[
 'discover_prince_actor_1101_v1.py','recover_prince_core_1101_v1.py',
 'check_prince_core_1101_v1.py','recover_prince_art_1101_v1.py',
 'pack_prince_resources_1101_v1.py','check_prince_sequence_1101_v1.py',
 'audit_prince_pattern_equivalence_1102_v1.py','audit_prince_pool_1102_v1.py',
 'check_prince_replacement_pages_1102_v1.py','check_prince_chr_publication_1102_v1.py',
 'audit_prince_resident_padding_1102_v1.py','check_prince_mac_padding_consumers_1102_v1.py',
 'prepare_prince_pool_layout_1102_v1.py','check_prince_world_contract_1102_v1.py',
 'prepare_prince_source_checkpoint_1102_v1.py']],
 'docs/qa/prince-source-core-1101-v1.md']
RECEIPTS=['core-recovery.json','core-CPU.json','source-sequencing-CPU.json','source-art.json',
 'resource-request.json','pattern-equivalence.json','pool-proposal.json','replacement-pages.json',
 'smb3-pages.json','writer-preservation.json','new-owner-pages.json','upper2-finite-domains.json',
 'publication-CPU-controls.json','resident-padding-proposal.json','resident-pad-consumers.json',
 'pooled-layout.json','world-contract.json']


def main():
 files={p:(R/p).read_bytes()for p in SOURCES};thin={}
 for n in RECEIPTS:
  q=json.loads((O/n).read_text())
  if n=='core-recovery.json':q.pop('instructions')
  if n=='source-art.json':q.pop('poses')
  thin[n]=q
 files['receipts/proofs.json']=json.dumps(thin,separators=(',',':')).encode()
 grant=R/'docs/qa/allocations/prince-1102-v1.json'
 files[grant.relative_to(R).as_posix()]=grant.read_bytes()
 manifest=dict(source_checkpoint_only=True,ROM_DBG_included=False,source_commit_files=SOURCES,receipt_source_files=RECEIPTS,large_receipt_tables_omitted=['core-recovery.instructions','source-art.poses'],members={p:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest())for p,v in files.items()},scope='Durable original-source extraction and differential recipes plus exact source-pool/padding proposal receipts and formal grant. Native playability not claimed. Original local donor and existing repository tools/models required for reproduction.')
 files['manifest.json']=json.dumps(manifest,indent=2).encode()
 target=O/'source-checkpoint.zip'
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name,data in files.items():z.writestr(name,data)
 assert target.stat().st_size<100000,target.stat().st_size
 with zipfile.ZipFile(target)as z:
  assert z.testzip()is None
  for name,data in files.items():assert z.read(name)==data
 q=dict(passed=True,bytes=target.stat().st_size,sha256=A.sha(target),members=len(files),no_ROM_DBG=True,explicit_commit_files=SOURCES,zip=target.relative_to(R).as_posix())
 (O/'source-checkpoint-manifest.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
