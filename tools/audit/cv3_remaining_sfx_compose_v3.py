"""Compose only frozen708 delta on frozen current Roll50b5, preserving its bindings."""
from pathlib import Path
import argparse,concurrent.futures,difflib,hashlib,importlib.util,json,shutil,subprocess,sys
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load,address,location
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
MIKE=D/'mike-native-current5ec-v1'
CURRENT=D/'roll-fade-current9e0e-v1'
PROPOSED=D/'cv3-remaining-sfx-v1/full-qualified-v3'
OLD=D/'cv3-dmc-complete-v1/final-optimized-current8ff-v2/source-final'
BASE='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 ready=ROOT/'tools/audit/cv3_remaining_sfx_ready_v1.json';assert sha(ready)=='7e99f971770660f062afcae4ee31488e12946b79dc73d47cab2338c44fafacae';assert sha(CURRENT/'candidate.nes')==BASE
 roll_adoption=CURRENT/'adoption-v1/proof.json';assert sha(roll_adoption)=='7505565fa254edf183dfd210951d78978b1611c207272c834027c420ecc92466';roll=json.loads(roll_adoption.read_text())['source_files']
 bindings=json.loads((MIKE/'ready-v1/source-bindings.json').read_text());source_bindings={k[7:]:v for k,v in bindings.items()if k.startswith('source/')};assert len(source_bindings)==4
 for rel,value in source_bindings.items():assert sha(MIKE/'source'/rel)==value
 for rel,rec in roll.items():assert sha(CURRENT/'overlay'/rel)==rec['after_sha256']
 overlay_delta=[]
 for f in (CURRENT/'overlay').rglob('*'):
  if not f.is_file():continue
  rel=f.relative_to(CURRENT/'overlay');old=MIKE/'source'/rel
  if not old.exists()or old.read_bytes()!=f.read_bytes():overlay_delta.append(rel.as_posix())
 assert set(overlay_delta)==set(roll),overlay_delta
 baseline=out/'baseline-source';stage=out/'source'
 # Mike's frozen overlay owns every src/inc/config file; its build support
 # and unchanged assets are separate pinned inputs, not an old source overlay.
 shutil.copytree(OLD,baseline,ignore=lambda directory,names:[n for n in names if Path(directory)==OLD and n in['src','inc','smb1base-mmc5-expanded.cfg']])
 for top in['src','inc']:shutil.copytree(CURRENT/'overlay'/top,baseline/top)
 shutil.copyfile(CURRENT/'overlay/smb1base-mmc5-expanded.cfg',baseline/'smb1base-mmc5-expanded.cfg')
 assets=json.loads((MIKE/'frozen-inputs.json').read_text())['shared_assets']
 for rel,value in assets.items():
  f=ROOT/rel;assert sha(f)==value,('Current shared input drift',rel);dest=baseline/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
 shutil.copytree(baseline,stage);proposal=json.loads((PROPOSED/'qualification.json').read_text());applied=[]
 for rec in proposal['source_files']:
  rel=rec['path'];original=baseline/rel;donor=PROPOSED/'source-final'/rel;assert sha(donor)==rec['sha256'];before=original.read_bytes()if original.exists()else None
  if rel=='src/entrypoint.s':
   assert digest(before)==source_bindings[rel];old=b'.include "cv3_dmc_complete.s"';new=old+b'\r\n.include "cv3_remaining_source_fx.s"';assert before.count(old)==1 and b'cv3_remaining_source_fx'not in before;after=before.replace(old,new);assert after.replace(b'\r\n.include "cv3_remaining_source_fx.s"',b'')==before
  else:
   expected=(OLD/rel).read_bytes()if(OLD/rel).exists()else None;assert before==expected,(rel,'Current source contains an independent edit; do not overwrite');after=donor.read_bytes()
  (stage/rel).write_bytes(after);applied.append(dict(path=rel,before_sha256=digest(before)if before is not None else None,after_sha256=digest(after)))
 for rel,rec in roll.items():assert sha(stage/rel)==rec['after_sha256']
 for rel,value in source_bindings.items():
  if rel=='src/entrypoint.s':continue
  assert sha(stage/rel)==value,'Preserve all four Mike source bindings except intended additive entrypoint include'
 def build(where,name,flag=None):
  cmd=[sys.executable,str(where/'tools/build_mmc5_expanded.py'),'--workspace',str(where),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/(name+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  with(out/(name+'.host.log')).open('w')as f:r=subprocess.run(cmd,cwd=where,stdout=f,stderr=subprocess.STDOUT)
  assert not r.returncode,(out/(name+'.host.log')).read_text()[-6000:];return sha(out/(name+'.nes'))
 assert build(baseline,'baseline')==BASE;candidate=build(stage,'candidate')
 sample=stage/'audio/remaining-source-sfx.inc';before=sample.read_bytes();f=stage/'tools/reference/build_remaining_sfx.py';spec=importlib.util.spec_from_file_location('producer',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main();assert before==sample.read_bytes()
 f=stage/'tools/prepare_cv3_dmc_mirror.py';spec=importlib.util.spec_from_file_location('mirror',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.prepare(stage,out/'candidate.nes');assert sha(out/'candidate.nes')==candidate
 def ordinary(mapper):
  old=build(baseline,'baseline-'+mapper,mapper);new=build(stage,'candidate-'+mapper,mapper);assert old==new;return dict(mapper=mapper,sha256=new)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:flags=list(pool.map(ordinary,['mmc3','mmc5']))
 oq,nq=qualified(out/'baseline.nes'),qualified(out/'candidate.nes');delta={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v};assert delta=={('Cv3SpawnAudioType','Done'):(0xb3eb,None),('_FARCALL_COUNT',):(oq[('_FARCALL_COUNT',)],oq[('_FARCALL_COUNT',)]+1)},delta
 old,new=load(out/'baseline.nes'),load(out/'candidate.nes');donor=load(PROPOSED/'candidate.nes');banks=[]
 def bank(b,n):return b['raw'][16+n*8192:16+(n+1)*8192]
 for n in range(128):
  dif=[i for i,(x,y)in enumerate(zip(bank(old,n),bank(new,n)))if x!=y]
  if dif:banks.append(dict(bank=n,changed_bytes=len(dif)));assert bank(new,n)==bank(donor,n),('Complete intended changed-bank equality',n)
  else:assert bank(old,n)==bank(new,n)
 assert{r['bank']for r in banks}=={2,28,29,82,84};assert old['raw'][:16]==new['raw'][:16]and old['raw'][1048592:]==new['raw'][1048592:]
 changed=[];allfiles=[];patch=''
 for f in sorted(stage.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(stage)
  if rel.parts[0]in['build','tests','docs']or rel.parts[:2]==('tools','audit'):continue
  oldfile=baseline/rel;before=oldfile.read_bytes()if oldfile.exists()else None;after=f.read_bytes();allfiles.append(dict(path=rel.as_posix(),baseline_sha256=digest(before)if before is not None else None,candidate_sha256=digest(after)))
  if before==after:continue
  eol='CRLF'if b'\r\n'in after else'LF'
  if before is not None:assert eol==('CRLF'if b'\r\n'in before else'LF')
  changed.append(dict(path=rel.as_posix(),sha256=digest(after),before_sha256=digest(before)if before is not None else None,EOL=eol))
  if rel.suffix in['.s','.inc','.cfg','.py']:patch+=''.join(difflib.unified_diff(before.decode().splitlines(True)if before is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix()if before is not None else'/dev/null',tofile='b/'+rel.as_posix()))
 assert len(changed)==7 and{r['path']for r in changed}=={r['path']for r in applied};(out/'all-deployable-files.json').write_text(json.dumps(allfiles,indent=2)+'\n');(out/'implementation.patch').write_text(patch,newline='\n')
 result=dict(passed=True,accepted=False,status='CURRENT50B5_SOURCE_COMPOSED_CPU_NATIVE_PENDING',ROM_sha256=candidate,baseline_ROM_sha256=BASE,source_files=changed,all_deployable_files=len(allfiles),all_deployable_manifest_sha256=sha(out/'all-deployable-files.json'),patch_sha256=sha(out/'implementation.patch'),Mike_four_source_bindings_before=source_bindings,Mike_entrypoint_additive_include_only=True,Roll_three_source_bindings_exact=roll,Roll_adoption_sha256=sha(roll_adoption),retained_existing_qualified_symbols=len(oq)-2,legitimate_removed_private_label='Cv3SpawnAudioType::Done',actual_FARCALL_COUNT_delta=1,changed_banks=banks,changed_banks_all_equal_frozen708=True,all_other_current_banks_including_Mike115_38_126_Roll119_Pbar86_Mac_resident127_mirror125_exact=True,CHR_exact=True,durable_remaining_producer_exact=True,mirror_idempotent=True,ordinary_flagoff=flags,tool_sha256=sha(__file__),scope='Exact fresh current50b5 composition only; prior708 CPU/native claims are not transferred. New exact CPU/lifecycle/IRQ/ordinary/native qualification required before adoption.')
 (out/'composition.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
