"""Observe player OAM/CHR agreement through actual cold selection/movement."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re
from capture_roster_menu import CASES

ROOT=Path(__file__).resolve().parents[2]


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--names',nargs='+',required=True);args=p.parse_args()
 rom=args.rom.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
 labels={m[2]:int(m[1],16)for line in rom.with_suffix('.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
 cases=CASES+[(name,17,18,'VvVariant',variant)for name,variant in(('Octopus',1),('TwinBee',2),('Pentarou',3))]+[('Roll',9,9,'RlVariant',1)]
 selected=[c for c in cases if c[0]in args.names];assert len(selected)==len(args.names)
 spec=importlib.util.spec_from_file_location('chr_commit_mesen',ROOT/'tools/run_mesen.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
 template=(ROOT/'tests/full-roster-entry.lua').read_text();observer=(ROOT/'tools/audit/chr_commit_observer.lua').read_text()
 template=template.replace("   print('PASS '..TARGET_NAME","   chrCommit.finish()\n   print('PASS '..TARGET_NAME")
 results={}
 for name,slot,char,var,variant in selected:
  folder=out/name.lower().replace(' ','-');folder.mkdir();runner.ROOT=folder
  menu={'Samus':'SAMUS ARAN','Bill':'BILL RIZER','Lance':'LANCE BEAN','Simon':'SIMON BELMONT','Scrooge':'SCROOGE MCDUCK','Darkwing':'DARKWING DUCK','Ryu':'RYU HAYABUSA','Sophia':'SOPHIA III'}.get(name,name.upper())
  constants=dict(TARGET_NAME=name,TARGET_MENU_NAME=menu,TARGET_SLOT=slot,TARGET_CHARACTER=char,TARGET_VARIANT_ADDRESS=labels[var]if var else 0,TARGET_VARIANT=variant)
  text='\n'.join(k+'='+json.dumps(v)for k,v in constants.items())+'\nlocal chrCommit=(function()\n'+observer+'\nend)()({})\n'+template
  script=folder/'entry.lua';script.write_text(text)
  code=runner.run(script,rom,timeout=45,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
  proof=folder/'build/verification/chr-commit.json';result=json.loads(proof.read_text())if proof.exists()else dict(passed=False)
  results[name]=dict(exit=code,proof=result,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
  report=dict(rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),passed=all(r['exit']==0 and r['proof']['passed']for r in results.values()),observer_sha256=hashlib.sha256(observer.encode()).hexdigest(),results=results)
  (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
  print(name,code,result,flush=True)
 return 0 if report['passed']else 1


if __name__=='__main__':raise SystemExit(main())
