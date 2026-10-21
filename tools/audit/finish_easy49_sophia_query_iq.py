"""Complete IP's retained host path-spelling failure, without source edits."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'agent49-e-sophia-union-a';D=V/'root49-sophia-query-perf-ip';S=D/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert not (D/'preparation.json').exists()and not (D/'build-driver.py').exists()
 cat=json.loads((P/'source-catalog-e.json').read_text());changed=[]
 for n,h in cat.items():
  assert sha(P/'source-e'/n)==h,n
  if sha(S/n)!=h:changed.append(n)
 assert changed==['src/sophia_source_terrain.s'],changed
 driver=(P/'build-driver-e.py').read_text();old=repr((P/'source-e').as_posix());assert driver.count(old)==1
 (D/'build-driver.py').write_text(driver.replace(old,repr(S.as_posix())))
 record=dict(status='PRIVATE_DIRECT_QUERY_PROTOTYPE_PREPARED_HOST_PATH_CORRECTED',source_catalog={n:sha(S/n)for n in cat},parent_source_snapshot_sha256=sha(P/'source-only-snapshot-e.json'),script_sha256=sha(__file__),original_preparer_sha256=sha(R/'tools/audit/prepare_easy49_sophia_query_ip.py'),retained_host_negative='IP copied/patched source correctly, then asserted a Windows backslash ROOT spelling while the actual parent driver uses forward slashes. No driver was emitted. Two attempted builds reported missing driver; no ROM was built. IQ changes only host driver path spelling, no source.',retained_failed_build_logs={m:sha(D/('build-'+m+'.log'))for m in ['mmc3','mmc5']},main_changed=False,scope='Pointer-only optimization prototype. Exact query ABI/fullRAM with individually enumerated removed push residues/ordered semantic writes/measured cycles required. Not actual native/route/interrupt proof.')
 (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status'])


if __name__=='__main__':main()
