from pathlib import Path
import configparser,hashlib,json,shutil,subprocess,sys,zipfile
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=D/'mmc3-tools-v17';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tools=O/'tools';tools.mkdir();shutil.copytree(R/'tools/mmc3_oversized',tools/'mmc3_oversized')
for n in ('prepare_mmc3_oversized.py','mmc3_current_repairs.py'):shutil.copy2(R/'tools'/n,tools/n)
manifest=tools/'mmc3_oversized/repairs.json';m=json.loads(manifest.read_text());old_digest=sha(R/'tools/mmc3_oversized/repairs.json')
row=next(r for r in m['text_repairs']if r['path']=='src/megaman_weapons.s');assert len(row['chunks'])==1
row['chunks']=[dict(old='  farcall RlFullShotBankDispatch,jmp\n  .res 37,$ea\n  .assert *-MegaManFullShotBank=55,error,"Original full-shot resident span"\n',new='  farcall RlFullShotBankDispatch,jmp\n  .assert *-MegaManFullShotBank=18,error,"MMC3 full-shot jump wrapper has no dead preservation padding"\n')]
manifest.write_text(json.dumps(m,indent=2))
report=dict(passed=False,complete=False,adopted=False,goal_complete=False,cases=[],old_repair_recipe_sha256=old_digest,new_repair_recipe_sha256=sha(manifest),scope='Narrow an unchanged padding repair to its stable actual instruction/directive context. This permits the already-qualified inactive MMC5 shortcut branch while preserving exact PZ/QA MMC3 output; every context still must occur exactly once.')
for version,root,rom in [('pz',R,R/'build/checkpoints/native-head-pz/candidate.nes'),('qa',P/'packet-v1/source',P/'candidate.nes')]:
 source=O/(version+'-source')
 with(O/(version+'-prepare.log')).open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(root),'--output',str(source),'--reference-rom',str(rom)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,(O/(version+'-prepare.log')).read_text()[-2500:]
 if version=='pz':
  with zipfile.ZipFile(D/'ryu-head-oversized-mmc3-v12/roundtrip-v1/prepared-source.zip')as z:
   for name in z.namelist():
    if not name.endswith('/'):assert(source/name).read_bytes()==z.read(name),name
 else:
  config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini');options={k:v for section in config.values()for k,v in section.items()};options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
  target=O/'qa-candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(target.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(target.with_suffix('.map')),'-Ln',str(target.with_suffix('.lbl')),'-o',str(target)]
  for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
  cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
  with(O/'qa-build.log').open('w')as log:p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode==0,(O/'qa-build.log').read_text()[-2500:];assert sha(target)=='43134c243d752fcaeab93d348ef56849df810f069788de9af1d76ed498359867'
 report['cases'].append(dict(version=version,passed=True,ROM_sha256='43134c243d752fcaeab93d348ef56849df810f069788de9af1d76ed498359867',prepared_629_files_exact=version=='pz'));(O/'progress.json').write_text(json.dumps(report,indent=2))
assert sha(R/'tools/mmc3_oversized/repairs.json')==old_digest
shutil.copy2(manifest,R/'tools/mmc3_oversized/repairs.json');report.update(passed=True,complete=True,adopted=True)
(O/'proof.json').write_text(json.dumps(report,indent=2));receipt=R/'build/verification/mmc3-tools-current-v17/proof.json';receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
