from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'packet-current-v3';O.mkdir(exist_ok=False);S=O/'source';S.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=json.loads((P/'packet-v1/packet.json').read_text());assert parent['passed']
installed=json.loads((R/'build/verification/mmc3-tools-current-v16/proof.json').read_text());fix=json.loads((R/'build/verification/mmc3-tools-current-v18/proof.json').read_text());assert installed['passed']and fix['passed']and fix['adopted']
tool_hashes=dict(installed['installed_tools']);tool_hashes['tools/mmc3_oversized/repairs.json']=fix['new_repair_recipe_sha256']
assert all(sha(R/n)==h for n,h in tool_hashes.items())
with zipfile.ZipFile(P/'packet-v1/source.zip')as z:z.extractall(S)
assert all(sha(S/n)==h for n,h in parent['source_files'].items())
for name in tool_hashes:
 target=S/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,target)
names=set(parent['source_files'])|set(tool_hashes);files={n:sha(S/n)for n in sorted(names)};assert len(files)==1220
report=dict(passed=False,ROM_sha256=parent['ROM_sha256'],parent_ROM_sha256=parent['parent_ROM_sha256'],source_files=files,source_file_count=len(files),builds={},MMC3_current_tool_compatibility=str(R/'build/verification/mmc3-tools-current-v18/proof.json'),scope='Current source packet includes the independently qualified MMC5 query shortcut and installed self-contained MMC3 tools. Exact expanded and ordinary flag-off builds required; MMC3 exact compilation is separately qualified. No source adoption occurs in this staging script.')
for name,extra,expected in [('mmc5-expanded',[],report['ROM_sha256']),('mmc3',['--flag-off','mmc3'],'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5',['--flag-off','mmc5'],'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
 output=O/(name+'.nes')
 with(O/(name+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(S/'tools/build_mmc5_expanded.py'),'--workspace',str(S),'--compiler',str(R/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(output),*extra],cwd=S,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,(name,(O/(name+'.log')).read_text()[-2500:]);assert sha(output)==expected,(name,sha(output))
 report['builds'][name]=dict(exact=True,ROM_sha256=sha(output));(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(build=name,ROM_sha256=sha(output))),flush=True)
with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for n in sorted(files):z.write(S/n,n)
assert all(sha(S/n)==h for n,h in files.items());report.update(passed=True,source_zip_sha256=sha(O/'source.zip'),source_only_roundtrip_exact=True,ordinary_flag_off_unchanged=True)
(O/'packet.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(passed=True,source_files=len(files),source_zip_sha256=report['source_zip_sha256'])),flush=True)
