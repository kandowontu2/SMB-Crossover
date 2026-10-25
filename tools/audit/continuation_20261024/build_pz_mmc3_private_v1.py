"""Run the existing oversized port preparation only in an external fresh tree."""
from pathlib import Path
import configparser,subprocess,sys,json,hashlib
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
O=D/'ryu-head-oversized-mmc3-v1';O.mkdir(exist_ok=False);source=O/'source'
script=R/'tools/prepare_mmc3_oversized.py';ns=dict(__name__='_private_prepare',__file__=str(script));exec(compile(script.read_text(),str(script),'exec'),ns)
ns['ROOT']=R;ns['OUT']=source;sys.argv=[str(script),'--reference-rom',str(D/'ryu-head-candidate-v5/candidate.nes')];ns['main']()
config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini')
options={k:v for section in config.values()for k,v in section.items()};options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
rom=O/'candidate.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
with(O/'build.log').open('w')as log:p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
report=dict(compiled=p.returncode==0,exit=p.returncode,scope='Compatibility compilation of existing oversized-MMC3 preparation with adopted PZ sources, entirely external. Native behavior/menu/CHR/lag and release admission remain separate; no public install.')
if p.returncode==0:report['ROM_sha256']=hashlib.sha256(rom.read_bytes()).hexdigest()
(O/'proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));print((O/'build.log').read_text()[-1800:]if p.returncode else'')
raise SystemExit(p.returncode)
