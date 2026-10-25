"""Freeze optimized source; original-source producer, exact fresh link, ordinary gates."""
from pathlib import Path
import argparse,concurrent.futures,difflib,hashlib,importlib.util,json,shutil,subprocess,sys
from check_tmnt_audio_fallback_oc import qualified
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-dmc-complete-v1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--prepared',type=Path,required=True);a.add_argument('--output',type=Path,required=True);q=a.parse_args();out=q.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);source=out/'source-final';shutil.copytree(q.prepared/'source',source)
 before=(source/'audio/remaining-source-sfx.inc').read_bytes();p=source/'tools/reference/build_remaining_sfx.py';spec=importlib.util.spec_from_file_location('durable',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main();assert before==(source/'audio/remaining-source-sfx.inc').read_bytes()
 def build(name,flag=None):
  cmd=[sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/(name+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  with(out/(name+'.host.log')).open('w')as f:r=subprocess.run(cmd,cwd=source,stdout=f,stderr=subprocess.STDOUT)
  assert not r.returncode,(out/(name+'.host.log')).read_text()[-6000:]
  return sha(out/(name+'.nes'))
 candidate=build('candidate');assert candidate==sha(q.prepared/'candidate.nes')
 p=source/'tools/prepare_cv3_dmc_mirror.py';spec=importlib.util.spec_from_file_location('mirror',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.prepare(source,out/'candidate.nes');assert candidate==sha(out/'candidate.nes')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:ordinary=list(pool.map(lambda n:dict(mapper=n,sha256=build('ordinary-'+n,n)),('mmc3','mmc5')))
 assert ordinary==[dict(mapper='mmc3',sha256='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),dict(mapper='mmc5',sha256='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]
 old=qualified(q.prepared/'held-candidate.nes');new=qualified(out/'candidate.nes');assert all(new.get(n)==v for n,v in old.items())
 held=D/'final-current8ff-v1/source-final';patch='';changed=[]
 for rel in ['src/roster_audio.s','src/cv3_dmc_complete.s']:
  original=(held/rel).read_bytes();actual=(source/rel).read_bytes();assert original!=actual
  oldeol='CRLF'if b'\r\n'in original else'LF';neweol='CRLF'if b'\r\n'in actual else'LF';assert oldeol==neweol
  changed.append(dict(path=rel,sha256=sha(source/rel),EOL=neweol));patch+=''.join(difflib.unified_diff(original.decode().splitlines(True),actual.decode().splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
 (out/'incremental-held-e6b.patch').write_text(patch,newline='\n')
 result=dict(passed=True,accepted=False,ROM_sha256=candidate,held_ROM_sha256=sha(q.prepared/'held-candidate.nes'),source_existing_EOL_preserved=True,producer_byte_exact=True,mirror_idempotent=True,all_held_qualified_symbols_exact=len(old),source_changes_from_held=changed,incremental_patch_sha256=sha(out/'incremental-held-e6b.patch'),ordinary_flagoff=ordinary,scope='Private source/CPU optimization readiness only. Exact4c70 native validation has not run. Held e6b native draw regression remains rejected; no transfer of its behavior proof to optimized hash.')
 (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
