"""Freeze final source, regenerate sample include, exact build and ordinary targets."""
from pathlib import Path
import argparse,concurrent.futures,difflib,hashlib,importlib.util,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);stage=out/'source-final';shutil.copytree(a.prepared/'source',stage)
 f=stage/'tools/reference/build_remaining_sfx.py';s=f.read_bytes();before=b"(ROOT/'audio/remaining-source-sfx.inc').write_text('\\n'.join(lines)+'\\n')";after=b"(ROOT/'audio/remaining-source-sfx.inc').write_bytes(('\\n'.join(lines)+'\\n').encode())";assert s.count(before)==1 or s.count(after)==1;f.write_bytes(s.replace(before,after))
 source=ROOT/'build/reference-remaining-sfx';assert source.is_dir();shutil.copytree(source,stage/'build/reference-remaining-sfx')
 (stage/'tests/fixtures').mkdir(parents=True);(stage/'docs/reference').mkdir(parents=True)
 sample=stage/'audio/remaining-source-sfx.inc';initial=sample.read_bytes();spec=importlib.util.spec_from_file_location('private_remaining',f);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.main();assert sample.read_bytes()==initial,'Durable generated include drift'
 def build(root,name,flag=None):
  command=[sys.executable,str(root/'tools/build_mmc5_expanded.py'),'--workspace',str(root),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/(name+'.nes'))]
  if flag:command+=['--flag-off',flag]
  with(out/(name+'.host.log')).open('w')as log:r=subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(name,(out/(name+'.host.log')).read_text()[-5000:]);return sha(out/(name+'.nes'))
 final=build(stage,'candidate');assert final==json.loads((a.prepared/'prepare.json').read_text())['candidate_ROM_sha256']
 spec=importlib.util.spec_from_file_location('private_mirror',stage/'tools/prepare_cv3_dmc_mirror.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.prepare(stage,out/'candidate.nes');assert sha(out/'candidate.nes')==final
 def ordinary(mapper):
  old=build(a.prepared/'baseline-source','baseline-'+mapper,mapper);new=build(stage,'candidate-'+mapper,mapper);assert old==new;return dict(mapper=mapper,sha256=new,byte_identical=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:ordinary_results=list(pool.map(ordinary,('mmc3','mmc5')))
 changed=[];patch='';baseline=a.prepared/'baseline-source'
 for q in stage.rglob('*'):
  if not q.is_file()or'__pycache__'in q.parts:continue
  rel=q.relative_to(stage)
  if rel.parts[0]in('build','tests','docs'):continue
  b=baseline/rel
  if not b.exists()and(ROOT/rel).exists():
   original=subprocess.run(['git','show','HEAD:'+rel.as_posix()],cwd=ROOT,capture_output=True,check=True).stdout;b=out/'baseline-extra'/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(original)
  if b.exists()and q.read_bytes()==b.read_bytes():continue
  rec=dict(path=rel.as_posix(),sha256=sha(q))
  if b.exists():
   original=subprocess.run(['git','show','HEAD:'+rel.as_posix()],cwd=ROOT,capture_output=True,check=True).stdout
   original_eol='CRLF'if b'\r\n'in original else'LF';actual='CRLF'if b'\r\n'in q.read_bytes()else'LF';assert original_eol==actual,(rel,original_eol,actual);rec['original_git_EOL']=original_eol
  changed.append(rec)
  if q.suffix in('.s','.inc','.py','.cfg'):patch+=''.join(difflib.unified_diff(b.read_text().splitlines(True)if b.exists()else[],q.read_text().splitlines(True),fromfile='a/'+rel.as_posix()if b.exists()else'/dev/null',tofile='b/'+rel.as_posix()))
 (out/'implementation.patch').write_text(patch)
 # Inspect the actual frozen scripts used by the previously adopted suites.
 scripts=[]
 for dirname in('cv3-primary-sfx-v1','cv3-dmc-followup-v1'):
  for q in(D/dirname).rglob('run.lua'):
   text=q.read_text();head=text.splitlines()[0]
   if 'CONFIG'not in head:continue
   assert not re.search(r'\b(?:True|False)\b',head),str(q)
   flags={k:re.findall(r'\["'+k+r'"\]=([^,}]+)',head)for k in('observe','new_route','expected_dmc','mode')}
   assert all(v.lstrip('-').isdigit()for vs in flags.values()for v in vs),(q,flags)
   scripts.append(dict(path=str(q),sha256=sha(q),integer_flags=flags,mode_write=next((l.strip()for l in text.splitlines()if "w('CrossoverBehaviorVersion'"in l),None)))
 (out/'prior-cv3-serializer-attestation.json').write_text(json.dumps(dict(scripts=scripts,no_Python_bool_tokens_in_generated_configs=True,integer_mode_zero_is_truthy_in_Lua=True,scope='Frozen generated configurations and deterministic emu.write seed paths only; does not claim a recorded RAM mode readback absent from the original evidence.'),indent=2)+'\n')
 result=dict(passed=True,accepted=False,ROM_sha256=final,source_files=changed,source_existing_EOL_from_git_HEAD_exact=True,durable_remaining_producer_byte_exact=True,post_link_mirror_idempotent=True,ordinary_targets=ordinary_results,prior_generated_CV3_scripts_inspected=len(scripts),source_manifest_sha256=hashlib.sha256(json.dumps(changed,sort_keys=True).encode()).hexdigest(),scope='Private source/build/CPU proposal. No native worker used, no ROM installed or source adopted. Separate native mapping/DMA/audio/cadence qualification and composition on current Mac are required.')
 (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
