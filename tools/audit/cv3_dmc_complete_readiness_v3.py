"""Correct v2 catalog by independently enumerating deployable source versus accepted8ff."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-dmc-complete-v1')
BASE='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
CAND='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da'
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(Path(p).read_bytes())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 source=D/'final-optimized-current8ff-v2/source-final';assert sha(source.parent/'candidate.nes')==CAND
 assert sha(Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes'))==BASE
 commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
 changed=[];allfiles=[];patch=''
 for f in sorted(source.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(source)
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  old=ROOT/rel;new=f.read_bytes();before=old.read_bytes()if old.exists()else None
  allfiles.append(dict(path=rel.as_posix(),candidate_sha256=digest(new),baseline_sha256=digest(before)if before is not None else None))
  if new==before:continue
  rec=dict(path=rel.as_posix(),sha256=digest(new),baseline_sha256=digest(before)if before is not None else None,bytes=len(new))
  if before is not None:
   original=subprocess.run(['git','show',commit+':'+rel.as_posix()],cwd=ROOT,capture_output=True,check=True).stdout;assert before.replace(b'\r\n',b'\n')==original.replace(b'\r\n',b'\n'),(rel,'Accepted worktree/Git semantic source mismatch')
   rec['original_git_sha256']=digest(original);rec['worktree_git_EOL_only_difference']=before!=original
   rec['original_git_EOL']='CRLF'if b'\r\n'in original else'LF';rec['candidate_EOL']='CRLF'if b'\r\n'in new else'LF';assert rec['original_git_EOL']==rec['candidate_EOL'],rel
  changed.append(rec)
  if f.suffix in['.s','.inc','.cfg','.py']:patch+=''.join(difflib.unified_diff(before.decode().splitlines(True)if before is not None else[],new.decode().splitlines(True),fromfile='a/'+rel.as_posix()if before is not None else'/dev/null',tofile='b/'+rel.as_posix()))
 prev=D/'source-readiness-optimized-current8ff-v2/readiness.json';v2=json.loads(prev.read_text());expected={r['path']for r in v2['source_files']}|{'src/roster_audio.s'}
 assert{r['path']for r in changed}==expected and len(changed)==20
 assert all(r['path']!='src/roster_audio.s'for r in v2['source_files'])
 original=next(r for r in changed if r['path']=='src/roster_audio.s');assert original['original_git_EOL']==original['candidate_EOL']=='LF'
 (out/'all-deployable-files.json').write_text(json.dumps(allfiles,indent=2)+'\n');(out/'implementation-vs-current8ff.patch').write_text(patch,newline='\n')
 result=dict(v2,status='SOURCE_CPU_READY_NATIVE_UNQUALIFIED_CORRECTED_CATALOG_V3',source_files=changed,source_manifest_sha256=digest(json.dumps(changed,sort_keys=True).encode()),accepted_baseline_git_commit=commit,all_deployable_files_enumerated=len(allfiles),all_deployable_files_manifest_sha256=sha(out/'all-deployable-files.json'),full_text_patch_sha256=sha(out/'implementation-vs-current8ff.patch'),catalog_correction=dict(incomplete_v2_receipt_sha256=sha(prev),missing_path='src/roster_audio.s',old_count=19,corrected_count=20,ROM_source_CPU_unchanged=True),tool_sha256=sha(__file__))
 (out/'readiness.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(Path(__file__),out/Path(__file__).name)
 print(json.dumps(dict(readiness_sha256=sha(out/'readiness.json'),source_manifest_sha256=result['source_manifest_sha256'],deployable_files=result['all_deployable_files_enumerated'],changed_files=len(changed),roster_audio_original_git_sha256=original['baseline_sha256'],roster_audio_candidate_sha256=original['sha256']),indent=2))
if __name__=='__main__':main()
