from pathlib import Path
import zipfile,hashlib,json,subprocess,sys,shutil,datetime
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'native-probes-qa-v2/packet-v1';O.mkdir(exist_ok=False);S=O/'source';S.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parent=json.loads((D/'ryu-head-packet-v5/packet.json').read_text())
assert all(sha(R/n)==h for n,h in parent['source_files'].items())
with zipfile.ZipFile(D/'ryu-head-packet-v5/source.zip')as z:z.extractall(S)
assert all(sha(S/n)==h for n,h in parent['source_files'].items())
for name in ('src/characters.s','src/megaman_weapons.s'):shutil.copy2(D/'native-probes-qa-v2/source'/name,S/name)
p=S/'src/megaman_weapons.s';t=p.read_text();a='  .res 3,$ea\n .else\n  .res 37,$ea\n .endif\n  .assert *-MegaManFullShotBank=55,error,"Original full-shot resident span"';b='  .res 3,$ea\n  .assert *-MegaManFullShotBank=55,error,"Original full-shot resident span"\n .else\n  .res 37,$ea\n  .assert *-MegaManFullShotBank=55,error,"Original full-shot resident span"\n .endif';assert t.count(a)==1;t=t.replace(a,b);p.write_text(t)
files={n:sha(S/n)for n in parent['source_files']};changes={n:dict(before=h,after=files[n])for n,h in parent['source_files'].items()if h!=files[n]};assert set(changes)=={'src/characters.s','src/megaman_weapons.s'}
report=dict(passed=False,ROM_sha256='054d9e33a84f628947b0dea15914ba2aae7796ca610a25548eab96407064384a',parent_ROM_sha256=parent['ROM_sha256'],source_files=files,changes=changes,builds={},scope='Non-code assertion layout retains the existing private MMC3 padding transform signature; runtime evidence remains bound to exact ROM bytes, which the roundtrip must reproduce. No source adopted here.')
for name,extra,expected in [('mmc5-expanded',[],report['ROM_sha256']),('mmc3',['--flag-off','mmc3'],'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5',['--flag-off','mmc5'],'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
 output=O/(name+'.nes')
 with(O/(name+'.log')).open('w')as f:p=subprocess.run([sys.executable,str(S/'tools/build_mmc5_expanded.py'),'--workspace',str(S),'--compiler',str(R/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(output),*extra],cwd=S,stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0,(name,(O/(name+'.log')).read_text()[-2000:]);assert sha(output)==expected,(name,sha(output),expected)
 report['builds'][name]=dict(exact=True,ROM_sha256=sha(output));(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(build=name,ROM_sha256=sha(output))),flush=True)
with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for n in sorted(files):z.write(S/n,n)
assert all(sha(S/n)==h for n,h in files.items());report['source_zip_sha256']=sha(O/'source.zip');report['passed']=True;report['source_only_roundtrip_exact']=True;report['ordinary_flag_off_unchanged']=True;report['source_file_count']=len(files)
(O/'packet.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(passed=True,source_files=len(files),source_zip_sha256=report['source_zip_sha256'])),flush=True)
