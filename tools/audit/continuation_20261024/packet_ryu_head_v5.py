from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,sys,zipfile
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
parent=R/'build/checkpoints/native-rest-py';candidate=D/'ryu-head-candidate-v5';out=D/'ryu-head-packet-v5';out.mkdir(exist_ok=False);source=out/'source';source.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((parent/'manifest.json').read_text());changes={}
for name,digest in m['source_files'].items():
 p=R/name;assert sha(p)==digest,name;q=source/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ['src/ryu_source_head.s']:
 p=candidate/'source'/name;q=source/name;changes[name]=dict(before=sha(q),after=sha(p));shutil.copy2(p,q)
files={p.relative_to(source).as_posix():sha(p)for p in source.rglob('*')if p.is_file()}
with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for name in sorted(files):z.write(source/name,name)
roundtrip=out/'roundtrip';roundtrip.mkdir()
with zipfile.ZipFile(out/'source.zip')as z:z.extractall(roundtrip)
assert {p.relative_to(roundtrip).as_posix():sha(p)for p in roundtrip.rglob('*')if p.is_file()}==files
builds={}
for key in ['expanded','mmc3','mmc5']:
 target=out/(key+'.nes');cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--workspace',str(roundtrip),'--compiler',str(R/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(target)]
 if key!='expanded':cmd+=['--flag-off',key]
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(out/(key+'-host.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,(key,p.stdout+p.stderr)
 builds[key]=sha(target);print(key,builds[key],flush=True)
assert builds['expanded']==sha(candidate/'candidate.nes')
assert builds['mmc3']=='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'
assert builds['mmc5']=='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'
with(candidate/'candidate.dbg').open('rb')as f,(out/'candidate.dbg.gz').open('wb')as target,gzip.GzipFile(fileobj=target,mode='wb',mtime=0)as z:shutil.copyfileobj(f,z)
q=dict(passed=True,goal_complete=False,ROM_sha256=builds['expanded'],parent_ROM_sha256=sha(parent/'candidate.nes'),source_zip_sha256=sha(out/'source.zip'),source_file_count=len(files),source_files=files,changes=changes,builds=builds,source_only_roundtrip_exact=True,ordinary_flag_off_unchanged=True)
(out/'packet.json').write_text(json.dumps(q,indent=2)+'\n')
