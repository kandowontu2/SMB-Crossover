"""Freeze the finite Mega/Proto source/CPU presentation experiment; no deployment."""
from pathlib import Path
import ast,difflib,hashlib,json,shutil,sys,zipfile
import py65
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'mm-proto-shot-mux-v4';BASE=D/'root-chip-hud-composed-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ready=P/'ready-v1';ready.mkdir(exist_ok=False);(ready/'tools').mkdir()
 assert sha(P/'candidate.nes')=='c5b65d96f6d76d4e9ebc62b5b28ae02e9cdea838414035fb1b2d4e0e4b706e48'
 old=json.loads((BASE/'source-manifest.json').read_text());files={q.relative_to(P/'source').as_posix():sha(q)for q in(P/'source').rglob('*')if q.is_file()};assert set(old)==set(files)
 changed=[n for n in old if old[n]!=files[n]];assert set(changed)=={'src/protoman_legacy_shots.inc','smb1base-mmc5-expanded.cfg'}
 for n,h in old.items():assert sha(BASE/'source'/n)==h,n
 (ready/'source-bindings.json').write_text(json.dumps(files,indent=2)+'\n')
 with zipfile.ZipFile(ready/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n in sorted(files):z.write(P/'source'/n,n)
 with zipfile.ZipFile(ready/'source.zip')as z:
  assert z.testzip()is None and len(z.namelist())==len(files)
  for n,h in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
 patch=''
 for n in changed:patch+=''.join(difflib.unified_diff((BASE/'source'/n).read_bytes().decode().splitlines(keepends=True),(P/'source'/n).read_bytes().decode().splitlines(keepends=True),fromfile='a/'+n,tofile='b/'+n))
 (ready/'review.patch').write_bytes(patch.encode())
 proofs=[P/'proof.json',P/'cpu-pilot-v1/proof.json',P/'cpu-full-v1/proof.json',P/'controls-v1/proof.json',P/'witness-v2/proof.json']
 for q in proofs:assert json.loads(q.read_text())['passed'],q
 cpu=json.loads((P/'cpu-full-v1/proof.json').read_text());assert cpu['cases']==7072 and cpu['actual_IRQ_cases']==88
 negative=dict(prepare_v1='Assembly failed malformed Population directive; original build-command log retained.',prepare_v2='Unqualified duplicate Attributes alias layout checker failed; CPU pilot independently exposed real Y=type clobber. Original terminal CPU assertion not separately saved.',prepare_v3='Qualified checker caught actual417B shift of genuine later bank66 symbols. No pass claimed.',prepare_v4='Fixes selected Y and source-declares helper after all genuine existing bank66 segments.',witness_v1='Incorrect8px sprite-height assumption failed immutable original first-eight slots; no pass.',witness_v2='Uses real immutable visibility.csv PPUCTRL bit5 to establish16px height. All original first-eight assertions retained.',native_run=False,limits='Early assertion terminal output is not invented as a retained raw log.')
 (ready/'negative-classification.json').write_text(json.dumps(negative,indent=2)+'\n')
 report=R/'docs/qa/mm-proto-shot-mux-2026-10-26.txt';shutil.copyfile(report,ready/report.name)
 own=sorted(q for q in(R/'tools/audit').glob('mm_proto_shot_mux_*')if q.is_file())
 for q in own:shutil.copyfile(q,ready/'tools'/q.name)
 deps=set(own);pending=[q for q in own if q.suffix=='.py']
 while pending:
  q=pending.pop();names=[]
  for n in ast.walk(ast.parse(q.read_text())):
   if isinstance(n,ast.ImportFrom)and n.module:names.append(n.module)
   elif isinstance(n,ast.Import):names.extend(v.name for v in n.names)
  for name in names:
   for local in[R/'tools/audit'/(name+'.py'),R/'tools'/(name+'.py')]:
    if local.is_file()and local not in deps:deps.add(local);pending.append(local)
 deps.update([report,R/'tools/build_mmc5_expanded.py',R/'tools/prepare_cv3_dmc_mirror.py',Path(sys.executable),BASE/'candidate.nes',BASE/'candidate.dbg',BASE/'candidate.map',BASE/'source-manifest.json',D/'root-megaman-lowbody-probe-v1/attribution.json',D/'root-megaman-lowbody-probe-v1/proof.json',D/'root-megaman-lowbody-probe-v1/readiness.json',D/'root-megaman-lowbody-probe-v1/native/visibility.csv'])
 for folder in[R/'tools/Windows/cc65',Path(py65.__file__).parent]:deps.update(q for q in folder.rglob('*')if q.is_file()and'__pycache__'not in q.parts)
 (ready/'dependencies.json').write_text(json.dumps({str(q):sha(q)for q in sorted(deps)},indent=2)+'\n')
 commands=dict(prepare=[sys.executable,str(R/'tools/audit/mm_proto_shot_mux_prepare_v4.py'),'--output','<new external packet>'],CPU=[sys.executable,str(R/'tools/audit/mm_proto_shot_mux_cpu_v1.py'),'--parent',str(BASE/'candidate.nes'),'--candidate','<new packet>/candidate.nes','--output','<new external CPU output>'],controls=[sys.executable,str(R/'tools/audit/mm_proto_shot_mux_controls_v1.py'),'--packet','<new external packet>'],witness=[sys.executable,str(R/'tools/audit/mm_proto_shot_mux_witness_v2.py'),'--output','<new external witness output>'],native_grant=False)
 (ready/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 catalog={str(q):sha(q)for q in P.rglob('*')if q.is_file()and not any(v.endswith('-objects')for v in q.parts)}
 for v in[1,2,3]:
  early=D/f'mm-proto-shot-mux-v{v}'
  for n in['build-command.json','source-manifest.json','candidate.nes','candidate.dbg','candidate.map','source/src/protoman_legacy_shots.inc']:
   q=early/n
   if q.is_file():catalog[str(q)]=sha(q)
 for path,h in catalog.items():assert sha(path)==h,path
 (ready/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
 noninputs=[n for n in old if n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map']or'__pycache__'in Path(n).parts]
 for n,h in old.items():
  if n not in noninputs:assert sha(R/n)==h,('ROOT input changed',n)
 result=dict(passed=True,source_only=True,native_run=False,installed=False,parent_ROM_sha256=sha(BASE/'candidate.nes'),ROM_sha256=sha(P/'candidate.nes'),source_members=len(files),changed_existing_source=changed,new_RAM_bytes=0,changed_PRG_bytes=420,all_old_addresses_CHR_unrelated_banks_exact=True,CPU_cases=cpu['cases'],actual_IRQ_cases=cpu['actual_IRQ_cases'],source_archive_sha256=sha(ready/'source.zip'),source_bindings_sha256=sha(ready/'source-bindings.json'),review_patch_sha256=sha(ready/'review.patch'),owned_tools=len(own),dependencies=len(deps),dependencies_sha256=sha(ready/'dependencies.json'),catalog_files=len(catalog),catalog_sha256=sha(ready/'catalog.json'),proofs={str(q.relative_to(P)):sha(q)for q in proofs},report_sha256=sha(report),ROOT_production_inputs_unchanged=True,limits='Uninstalled presentation experiment. Lone active shot+142cycles and clipped two-live+48 remain risks. Source-construction fairness is not physical publication fairness. Counterfactual admits most, not all, captured body witnesses. Actual native output/age/cadence/interrupt/CHR guards must qualify before adoption; no native command/grant included.')
 (ready/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
