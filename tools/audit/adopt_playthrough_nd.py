"""Install the first three reviewed playthrough packets plus restored Bass art."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'new-roster-1-1-nd/adoption-a';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changes={}
def add(name,path,expected=None,before=None):
 name=Path(name).as_posix();target=R/name
 assert name not in changes
 if expected:assert sha(path)==expected,(name,'packet hash')
 if before:assert sha(target)==before,(name,'current preimage')
 if target.exists()and target.read_bytes()==path.read_bytes():return
 changes[name]=dict(source=path,before=sha(target)if target.exists()else None,after=sha(path))
A=V/'play-proto-dw-z2-nd/final-overlay';a=json.loads((A/'manifest.json').read_text())
for name,h in a['owned_source_files'].items():add(name,A/name,h)
B=V/'play-kirby-chip-dale-nd'
for item in json.loads((B/'source-overlay-manifest.json').read_text()):add(item['path'],B/'source-overlay'/item['path'],item['after'],item['before'])
C=V/'play-cv3-nd/adoption-packet';c=json.loads((C/'manifest.json').read_text());assert c['passed']
for name,item in c['owned'].items():add(name,C/name,item['after_sha256'],item['before_sha256'])
D=V/'new-roster-1-1-nd/bass-final-overlay-v3'
for name in('src/bass_metasprites.inc','src/bass_special_poses.inc','chr/characters/crossover-expanded.chr','chr/characters/special-bass-body.chr','chr/characters/packed-mmc3.chr','chr/characters/packed-mmc5.chr','chr/characters/packed-mmc5-expanded.chr'):add(name,D/name)
add('chr/characters/bass-arm-source-plan.json',V/'new-roster-1-1-nd/bass-arm-optimized/plan.json')
report={n:{k:v for k,v in d.items()if k!='source'}for n,d in changes.items()}
(O/'plan.json').write_text(json.dumps(report,indent=2)+'\n')
for name,item in changes.items():
 target=R/name
 if target.exists():
  dest=O/'before'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,dest)
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(item['source'],target);assert sha(target)==item['after']
(O/'receipt.json').write_text(json.dumps(dict(changed_files=report,packets=[str(A),str(B),str(C),str(D)]),indent=2)+'\n')
print(json.dumps(dict(installed_files=len(changes),receipt=str(O/'receipt.json'))))
