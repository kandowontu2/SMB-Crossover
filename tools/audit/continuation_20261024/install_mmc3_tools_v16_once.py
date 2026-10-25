"""Install only verified preparation tools, then rebuild their private output."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-tools-v16';q=json.loads((O/'staging-proof.json').read_text());assert q['passed']and not q['adopted']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=R/'build/verification/mmc3-tools-current-v16/proof.json';assert not receipt.exists(),'One-shot installation already has a receipt'
packet=json.loads((D/'ryu-head-packet-v5/packet.json').read_text());expected=packet['source_files']
assert all(sha(R/name)==digest for name,digest in expected.items()),'Root PZ catalog changed before tool installation'
before=O/'root-before';before.mkdir(exist_ok=False)
occupied=sum(os.stat(Path(dp)/n,follow_symlinks=False).st_size for dp,dn,names in os.walk(R,followlinks=False)for n in names)
growth=0
for name,digest in q['staged_tools'].items():
 p=R/name;assert p.resolve().is_relative_to(R.resolve());assert sha(O/name)==digest
 assert (sha(p)if p.exists()else None)==q['root_before'][name],name
 if p.exists():b=before/name;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
 growth+=(O/name).stat().st_size-(p.stat().st_size if p.exists()else 0)
assert occupied+growth+20000<30_000_000_000,(occupied,growth)
try:
 for name in q['staged_tools']:
  target=R/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/name,target)
 build=O/'canonical-build'
 with(O/'canonical-build.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/build_mmc3_oversized.py'),'--reference-rom',str(R/'build/checkpoints/native-head-pz/candidate.nes'),'--output-dir',str(build)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,(O/'canonical-build.log').read_text()[-3000:]
 rom=build/'smb-crossover-mmc3-oversized.nes';assert sha(rom)==q['expected_ROM_sha256']
 changed={n:dict(before=v,after=sha(R/n))for n,v in expected.items()if sha(R/n)!=v}
 assert set(changed)=={'tools/prepare_mmc3_oversized.py','tools/build_mmc3_oversized.py'},changed
 proof=dict(passed=True,installed_tools=q['staged_tools'],catalog_changes=changed,all_game_source_and_other_catalog_files_unchanged=True,ROM_sha256=sha(rom),private_output=str(rom),public_release_installed=False,workspace_bytes_before=occupied,installed_byte_growth=growth,workspace_cap_bytes=30_000_000_000,goal_complete=False,scope='Verified build-tool integration only. Canonical source preparation now reproduces the exact already-tested private MMC3 candidate, using external outputs. Existing private native mapper receipts apply to these identical ROM bytes; full MMC3 campaigns/items/fidelity and physical hardware remain separate.')
 receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(proof,indent=2));q['adopted']=True;q['installed_receipt']=str(receipt);(O/'installation.json').write_text(json.dumps(q,indent=2));print(json.dumps(proof),flush=True)
except BaseException:
 for name in q['staged_tools']:
  target=R/name;assert target.resolve().is_relative_to(R.resolve())
  if q['root_before'][name]is None:
   if target.exists():target.unlink()
  else:shutil.copy2(before/name,target)
 raise
