"""Actual compiler dependency closure and independent same-ROM full relink."""
from pathlib import Path
import configparser,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];O=R/'build/kamikaze-mario-host-v4';C=R/'tools/Windows/cc65/bin'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 target=O/'source-closure.json';assert not target.exists()
 conf=configparser.ConfigParser();conf.optionxform=str;conf.read(R/'build_options.ini');defs={k:v for s in conf.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 commands=[];deps={};ov=O/'overlay'
 def execute(cmd):
  p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);commands.append(cmd);assert p.returncode==0,p.stdout+p.stderr
 def ingest(dep):
  for word in re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':')):
   p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve();assert p.is_file(),p;deps[str(p)]=sha(p)
 for name,src in[('main',O/'candidate-objects/entrypoint.s'),('skin',O/'kamikaze_chr.s')]:
  cmd=[str(C/'ca65.exe'),'--cpu','6502x','-g','-I',str(ov/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(ov),'--bin-include-dir',str(R),'--create-full-dep',str(O/(name+'-full.d')),'-o',str(O/(name+'-full.o'))]
  for k,v in defs.items():cmd+=['-D',k+'='+v]
  execute(cmd+[str(src)]);ingest(O/(name+'-full.d'))
 cmd=[str(C/'cc65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-T','-I',str(R),'--create-full-dep',str(O/'c-full.d'),'-o',str(O/'c-full.s')]
 for k,v in defs.items():cmd+=['-D',k+'='+v]
 execute(cmd+[str(O/'candidate-objects/main.c')]);ingest(O/'c-full.d')
 execute([str(C/'ca65.exe'),'--cpu','6502x','-t','nes','-g','-o',str(O/'c-full.o'),str(O/'c-full.s')])
 rebuilt=O/'independent.nes'
 execute([str(C/'cl65.exe'),'--cpu','6502x','-t','nes','-C',str(ov/'smb1base-mmc5-expanded.cfg'),'-Ln',str(rebuilt.with_suffix('.lbl')),'--ld-args','--dbgfile,'+str(rebuilt.with_suffix('.dbg')),'-o',str(rebuilt),str(O/'c-full.o'),str(O/'main-full.o'),str(O/'skin-full.o')])
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare
 prepare(R,rebuilt);assert sha(rebuilt)==sha(O/'candidate.nes'),'Independent genuine full relink differs'
 assert str((R/'src/kamikaze_mario.s').resolve())in deps
 assert str((R/'chr/characters/kamikaze-mario-source-v2.chr').resolve())in deps
 files=set(Path(p)for p in deps)|{Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'build.json',R/'build_options.ini',R/'tools/build_mmc5_expanded.py',R/'tools/prepare_cv3_dmc_mirror.py',ov/'smb1base-mmc5-expanded.cfg'}
 for n in['cl65.exe','ca65.exe','cc65.exe','ld65.exe']:files.add(C/n)
 proof=dict(passed=True,source_only=True,native_run=False,actual_compiler_dependencies=len(deps),independent_same_ROM_relink=True,regenerated_125_from_final_127=True,commands=commands,actual_dependencies=deps,bindings={str(p.resolve()):sha(p)for p in files})
 assert all(sha(p)==h for p,h in proof['bindings'].items());target.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,dependencies=len(deps),sha256=sha(target))))
if __name__=='__main__':main()
