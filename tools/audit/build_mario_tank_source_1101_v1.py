"""Compile only the author's declared runtime build graph, no bundled tools."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_source_1101_v1 import O,COMMIT,donor,fetch,sha
from private_build_outputs_v1 import validate
S=O/'source';B=O/'author-build';CC=R/'tools/Windows/cc65/bin'
def main():
 B.mkdir(exist_ok=True);(B/'objects').mkdir(exist_ok=True)
 for p in (B/'objects').glob('*.o'):
  assert p.resolve().is_relative_to(O.resolve());p.unlink()
 cm=(S/'CMakeLists.txt').read_text();paths=re.findall(r'^\s+((?:src|inc|chr)/[^\s)]+)',cm,re.M)
 paths+=['inc/memory_p.inc','inc/metasprite_p.inc','inc/player.inc','chr/titlescreen.bin']
 for name in dict.fromkeys(paths):
  p=S/name;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.write_bytes(fetch('https://raw.githubusercontent.com/AleFunky/mariothetank/'+COMMIT+'/'+name))
 commands=[];objects=[]
 def run(cmd):
  guard=validate(cmd,O,cwd=S);done=subprocess.run(cmd,cwd=S,capture_output=True,text=True)
  commands.append(dict(command=cmd,guard=guard,returncode=done.returncode,stderr=done.stderr));(O/'author-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
  assert done.returncode==0,done.stderr
 for name in paths:
  if not name.endswith('.s'):continue
  obj=B/'objects'/(str(Path(name).with_suffix('')).replace('\\','-').replace('/','-')+'.o')
  assert obj not in objects,('Unique source basenames required',obj)
  cmd=[str(CC/'ca65.exe'),'-g','-I',str(S/'inc'),'--bin-include-dir',str(S/'src'),'-o',str(obj),str(S/name)]
  run(cmd);objects.append(obj)
 output=B/'donor-source.nes'
 run([str(CC/'ld65.exe'),'-C',str(S/'src/nes.cfg'),'-o',str(output),'--dbgfile',str(output.with_suffix('.dbg')),'-Ln',str(output.with_suffix('.lbl')),'-m',str(B/'map.txt'),*[str(p)for p in objects]])
 expected,identity=donor();actual=output.read_bytes();diff=[i for i,(x,y)in enumerate(zip(expected,actual))if x!=y]
 result=dict(passed=actual==expected,source_commit=COMMIT,donor_sha256=sha(expected),assembled_sha256=sha(actual),same_length=len(expected)==len(actual),changed_bytes=len(diff),first_differences=diff[:50],objects=len(objects),runtime_inputs={n:sha((S/n).read_bytes())for n in dict.fromkeys(paths)},scope='Exact pinned author runtime graph only; no bundled binaries, editors, broad repository checkout or external source trees.')
 (O/'author-reproduction.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='runtime_inputs'}))
if __name__=='__main__':main()
