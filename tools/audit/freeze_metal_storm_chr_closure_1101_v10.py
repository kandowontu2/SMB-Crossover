"""Freeze compact shared consumer inventory and aggregate publication proof."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/metal-storm-chr-closure-1101-v10'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NAMES=['capture_metal_storm_chr_inputs_1101_v10.py','audit_metal_storm_chr_domains_1101_v10.py','check_metal_storm_chr_publication_1101_v10.py','close_metal_storm_chr_owners_1101_v10.py','freeze_metal_storm_chr_closure_1101_v10.py']
def main():
 assert not(OUT/'source-stage.json').exists()
 sources=[ROOT/'tools/audit'/n for n in NAMES]+[ROOT/'tools/reference/metal_storm_chr_closure_1101_v10.md']
 receipts=[OUT/n for n in['current-consumer-inputs.json','source-domains.json','publication-CPU-controls.json','replaced-owner-controls.json','consumer-closure.json']]
 for p in receipts:
  q=json.loads(p.read_text());assert q['passed']
  for name,h in q.get('bindings',{}).items():assert sha(name)==h,name
 result=json.loads(receipts[-1].read_text());assert result['consumer_closure_passed']and not result['resource_granted']
 manifest=dict(files={p.relative_to(ROOT).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in sources+receipts},external_packets={str(p.resolve()):sha(p)for p in[ROOT/'build/metal-storm-coexistence-1101-v9/source-proof.zip',ROOT/'build/metal-storm-resource-host-1101-v8/source-proof.zip',ROOT/'docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/source.zip']},native=False,installed=False,resource_granted=False,consumer_closure_passed=True,current_ROM_sha256=result['current_ROM_sha256'],scope=result['scope'])
 (OUT/'hash-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 archive=OUT/'source-proof.zip';assert not archive.exists()
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sources+receipts:z.write(p,p.relative_to(ROOT).as_posix())
  z.write(OUT/'hash-manifest.json','hash-manifest.json')
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None and not any(n.endswith(('.nes','.fds','.o','.dbg','.lbl','.bin'))for n in z.namelist())
 stage=dict(passed=True,native=False,installed=False,resource_granted=False,consumer_closure_passed=True,archive=str(archive.resolve()),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,archive_members=len(sources)+len(receipts)+1,source_paths=[p.relative_to(ROOT).as_posix()for p in sources],current_ROM_sha256=result['current_ROM_sha256'],Metal_proposed_pages=result['proposed_Metal_pages'],Tank_proposed_pages=result['proposed_Tank_pages'],owned_Thomas511=True,next='Root review/grant, then actual source-preserving host allocation/loader/Main/ISR/native qualification.',bindings={str(p.resolve()):sha(p)for p in sources+receipts+[OUT/'hash-manifest.json']})
 (OUT/'source-stage.json').write_text(json.dumps(stage,indent=2)+'\n');print(json.dumps({k:v for k,v in stage.items()if k not in['bindings','source_paths']}))
if __name__=='__main__':main()
