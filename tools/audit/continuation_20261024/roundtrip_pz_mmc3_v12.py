from pathlib import Path
import json,hashlib,zipfile,subprocess,sys,configparser
D=Path(__file__).resolve().parent;R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');M=D/'ryu-head-oversized-mmc3-v12';O=M/'roundtrip-v1';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=M/'source';hashes={p.relative_to(source).as_posix():sha(p)for p in source.rglob('*')if p.is_file()and p.suffix not in('.o','.pyc')and '__pycache__'not in p.parts}
with zipfile.ZipFile(O/'prepared-source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for name in sorted(hashes):z.write(source/name,name)
assert all(sha(source/n)==h for n,h in hashes.items())
fresh=O/'source';fresh.mkdir()
with zipfile.ZipFile(O/'prepared-source.zip')as z:z.extractall(fresh)
c=configparser.ConfigParser();c.optionxform=str;c.read(fresh/'build_options.ini');opts={k:v for s in c.values()for k,v in s.items()};opts.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
rom=O/'candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(fresh/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(fresh),'--asm-include-dir',str(fresh/'src'),'--asm-include-dir',str(fresh),'--bin-include-dir',str(fresh),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
for k,v in opts.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
cmd+=[str(fresh/'src/main.c'),str(fresh/'src/entrypoint.s')]
(O/'binding.json').write_text(json.dumps(dict(ROM_sha256=sha(M/'candidate.nes'),source_files=hashes,source_zip_sha256=sha(O/'prepared-source.zip'),compiler_sha256=sha(R/'tools/Windows/cc65/bin/cl65.exe'),command=cmd),indent=2))
with(O/'build.log').open('w')as f:p=subprocess.run(cmd,cwd=fresh,stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'build.log').read_text()[-2000:]
assert sha(rom)==sha(M/'candidate.nes')
q=dict(passed=True,prepared_source_bundle_roundtrip_exact=True,ROM_sha256=sha(rom),source_zip_sha256=sha(O/'prepared-source.zip'),source_files=len(hashes),goal_complete=False,scope='Self-contained prepared-source rebuild; the root canonical preparation pipeline is not yet integrated or certified, and no release installed. Native campaign/item/fidelity and physical hardware qualification remain separate.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q))
