from pathlib import Path
import importlib.util,sys,json,hashlib
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-menu-source-pz-v1';O.mkdir(exist_ok=False)
f=R/'tools/audit/capture_roster_menu.py';s=importlib.util.spec_from_file_location('capture37',f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.CASES=[(n,slot,ch,'RlVariant',0)if n=='Bass'else(n,slot,ch,'VvVariant',0)if n=='Vic Viper'else(n,slot,ch,var,val)for n,slot,ch,var,val in m.CASES]
m.CASES += [('Roll',9,9,'RlVariant',1),('Octopus',17,18,'VvVariant',1),('TwinBee',17,18,'VvVariant',2),('Pentarou',17,18,'VvVariant',3)]
assert len(m.CASES)==37
results=[]
for setting in ('off','on'):
 sys.argv=[str(f),'--rom',str(D/'ryu-head-candidate-v5/candidate.nes'),'--output',str(O/('source-sprite-'+setting))]+(['--outlines']if setting=='on'else[])
 code=m.main();results.append(dict(setting=setting,exit=code))
 (O/'progress.json').write_text(json.dumps(dict(complete=False,source_driver_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),results=results),indent=2))
 assert code==0,setting
(O/'progress.json').write_text(json.dumps(dict(complete=True,source_driver_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),results=results),indent=2))
