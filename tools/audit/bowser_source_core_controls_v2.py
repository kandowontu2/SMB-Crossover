"""Fix label-parser reporting setup; keep initial pre-execution negative."""
from pathlib import Path
P=Path(__file__).with_name('bowser_source_core_controls_v1.py')
s=P.read_text(encoding='utf-8').replace("out=O/'controls.json'","out=O/'controls-v2.json'")
s='\n'.join(line for line in s.splitlines()if not "labels={n:int(v,16)for n,v in re.findall(r'^al"in line)+'\n'
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
