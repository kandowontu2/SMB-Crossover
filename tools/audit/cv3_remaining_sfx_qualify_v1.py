"""Freeze narrow noise source/producer/flag-off/layout proof; never install."""
from pathlib import Path
import argparse, concurrent.futures, difflib, hashlib, importlib.util, json, shutil, subprocess, sys
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load, address, location
ROOT=Path(__file__).resolve().parents[2]
BASE='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da'
CAND='ece2b4df0564f6710df8da4694c891f77afee4b25da4e49f0ada90d0b6454d94'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 assert sha(a.prepared/'baseline.nes')==BASE and sha(a.prepared/'candidate.nes')==CAND
 stage=out/'source-final';shutil.copytree(a.prepared/'source',stage)
 before=(stage/'audio/remaining-source-sfx.inc').read_bytes();f=stage/'tools/reference/build_remaining_sfx.py';spec=importlib.util.spec_from_file_location('remaining_producer',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main();assert before==(stage/'audio/remaining-source-sfx.inc').read_bytes()
 def build(name,flag=None):
  cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/(name+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  with(out/(name+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(name,(out/(name+'.host.log')).read_text()[-6000:]);return sha(out/(name+'.nes'))
 assert build('candidate')==CAND
 f=stage/'tools/prepare_cv3_dmc_mirror.py';spec=importlib.util.spec_from_file_location('mirror_producer',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.prepare(stage,out/'candidate.nes');assert sha(out/'candidate.nes')==CAND
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:ordinary=list(pool.map(lambda n:dict(mapper=n,sha256=build('ordinary-'+n,n)),('mmc3','mmc5')))
 assert ordinary==[dict(mapper='mmc3',sha256='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),dict(mapper='mmc5',sha256='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]
 old,new=load(a.prepared/'baseline.nes'),load(out/'candidate.nes');oq,nq=qualified(a.prepared/'baseline.nes'),qualified(out/'candidate.nes');changed_symbols={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v}
 assert changed_symbols=={('Cv3SpawnAudioType','Done'):(0xb3eb,None)}
 baseline_source=a.prepared.parent.parent/'cv3-dmc-complete-v1/final-optimized-current8ff-v2/source-final'
 # The explicit accepted frozen parent, not mutable ROOT, owns this comparison.
 baseline_source=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-dmc-complete-v1/final-optimized-current8ff-v2/source-final')
 changed=[];allfiles=[];patch='';references=[]
 for f in sorted(stage.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(stage)
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  original=baseline_source/rel;before=original.read_bytes()if original.exists()else None;after=f.read_bytes();allfiles.append(dict(path=rel.as_posix(),baseline_sha256=digest(before)if before is not None else None,candidate_sha256=digest(after)))
  if rel.suffix=='.s':
   for number,line in enumerate(after.decode().splitlines(),1):
    if 'Cv3SpawnAudioType' in line:references.append(dict(path=rel.as_posix(),line=number,text=line.strip()))
  if before==after:continue
  rec=dict(path=rel.as_posix(),sha256=digest(after),bytes=len(after),baseline_sha256=digest(before)if before is not None else None,EOL='CRLF'if b'\r\n'in after else'LF')
  if before is not None:
   git=subprocess.run(['git','show','HEAD:'+rel.as_posix()],cwd=ROOT,capture_output=True,check=True).stdout
   # Current accepted Roll changes are outside these four source files.
   assert git.replace(b'\r\n',b'\n')==before.replace(b'\r\n',b'\n'),rel
   rec['original_git_sha256']=digest(git);rec['original_git_EOL']='CRLF'if b'\r\n'in git else'LF';assert rec['EOL']==rec['original_git_EOL']
  changed.append(rec)
  if rel.suffix in['.s','.inc','.cfg','.py']:patch+=''.join(difflib.unified_diff(before.decode().splitlines(True)if before is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix()if before is not None else'/dev/null',tofile='b/'+rel.as_posix()))
 assert{r['path']for r in changed}=={'src/cv3_source_audio.s','src/cv3_dmc_complete.s','src/cv3_noise_cues.s','src/entrypoint.s'}
 assert not any('Cv3SpawnAudioType::Done'in r['text']for r in references)
 # Entire fixed windows, source mirror, original samples, Mac, HUD and CHR exact.
 banks=[]
 for n in range(128):
  ob=old['raw'][16+n*8192:16+(n+1)*8192];nb=new['raw'][16+n*8192:16+(n+1)*8192];delta=[i for i,(x,y)in enumerate(zip(ob,nb))if x!=y]
  if delta:banks.append(dict(bank=n,changed_bytes=len(delta),first_offset=min(delta),last_offset=max(delta)))
 assert{r['bank']for r in banks}=={28,29,82,84}
 assert next(r['changed_bytes']for r in banks if r['bank']==82)==1
 off=16+82*8192;delta=[i for i in range(8192)if old['raw'][off+i]!=new['raw'][off+i]]
 assert[(old['raw'][off+i],new['raw'][off+i])for i in delta]==[(0xd0,0x90)],'Existing scene-reset BNE becomes BCC for new typed27/28 only'
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 spans=[]
 for n in['Cv3NoiseCueSpawn','Cv3NoiseCueOwnerInit','Cv3NoiseCueReset','Cv3NoiseCueFlags','Cv3NoiseCuePeriods','Cv3NoiseCueVolumes']:
  s=new['syms'][n];spans.append(dict(name=n,address=address(new,n),size=int(s['size'],0),bank=(location(new,n)-16)//8192))
 (out/'all-deployable-files.json').write_text(json.dumps(allfiles,indent=2)+'\n');(out/'implementation.patch').write_text(patch,newline='\n');(out/'helper-references.json').write_text(json.dumps(references,indent=2)+'\n')
 result=dict(passed=True,accepted=False,status='SOURCE_BUILD_CPU_PACKET_ONLY_NATIVE_UNQUALIFIED_LIFECYCLE_GAP_RETAINED',baseline_ROM_sha256=BASE,ROM_sha256=CAND,durable_remaining_producer_exact=True,mirror_producer_idempotent=True,ordinary_flagoff=ordinary,source_files=changed,all_deployable_files_enumerated=len(allfiles),all_deployable_manifest_sha256=sha(out/'all-deployable-files.json'),implementation_patch_sha256=sha(out/'implementation.patch'),old_qualified_symbols=len(oq),retained_old_qualified_symbols=len(oq)-1,removed_private_label=dict(name='Cv3SpawnAudioType::Done',old_address=0xb3eb,reason='Old internal return no longer executes; new real entry jumps to source-priority queue. No external qualified-label source references; no false alias inserted.'),changed_banks=banks,helper_spans=spans,all_other_banks_including_fixed127_E125_LOWCODE126_Mac123_exact=True,CHR_exact=True,new_private_existing_slab_byte=address(new,'Cv3NoiseCue'),new_RAM_allocation=0,remaining_gates=['Native actual releases/APU/cadence/PPU unqualified','Existing private1F and proposed13/15 continue across guest-death/new-song until scene reset; source lifecycle difference retained in separate feasibility receipt','Active legacy1F getter overhead0..57 cycles and admission+103 must pass actual cadence qualification'],tool_sha256=sha(__file__))
 (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(Path(__file__),out/Path(__file__).name);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
