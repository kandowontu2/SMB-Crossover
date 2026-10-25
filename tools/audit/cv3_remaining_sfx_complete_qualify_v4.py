"""Freeze full source/producers/flag-off/ABI/layout; not native acceptance."""
from pathlib import Path
import argparse,concurrent.futures,difflib,hashlib,importlib.util,json,shutil,subprocess,sys
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load,address,location
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
CAND='2e005c8e2acde44bc184459d92b2966ee488b92819dd91151577fdf444b751df'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);assert sha(a.prepared/'baseline.nes')==BASE and sha(a.prepared/'candidate.nes')==CAND
 stage=out/'source-final';shutil.copytree(a.prepared/'source',stage);base_source=D/'cv3-remaining-current50b-v1/baseline-source'
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
 old,new=load(a.prepared/'baseline.nes'),load(out/'candidate.nes');oq,nq=qualified(a.prepared/'baseline.nes'),qualified(out/'candidate.nes');deltas={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v};assert deltas=={('Cv3SpawnAudioType','Done'):(0xb3eb,None),('_FARCALL_COUNT',):(oq[('_FARCALL_COUNT',)],oq[('_FARCALL_COUNT',)]+1)},deltas
 allfiles=[];changed=[];patch='';refs=[]
 for f in sorted(stage.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(stage)
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  oldfile=base_source/rel;before=oldfile.read_bytes()if oldfile.exists()else None;after=f.read_bytes();allfiles.append(dict(path=rel.as_posix(),baseline_sha256=digest(before)if before is not None else None,candidate_sha256=digest(after)))
  if rel.suffix=='.s':
   refs +=[dict(path=rel.as_posix(),line=i,text=line.strip())for i,line in enumerate(after.decode().splitlines(),1)if 'Cv3SpawnAudioType'in line]
  if before==after:continue
  rec=dict(path=rel.as_posix(),sha256=digest(after),bytes=len(after),baseline_sha256=digest(before)if before is not None else None,EOL='CRLF'if b'\r\n'in after else'LF')
  if before is not None:
   git=subprocess.run(['git','show','HEAD:'+rel.as_posix()],cwd=ROOT,capture_output=True,check=True).stdout;assert git.replace(b'\r\n',b'\n')==before.replace(b'\r\n',b'\n'),rel;rec['original_git_sha256']=digest(git);rec['original_git_EOL']='CRLF'if b'\r\n'in git else'LF';assert rec['EOL']==rec['original_git_EOL']
  changed.append(rec)
  if rel.suffix in['.s','.inc','.cfg','.py']:patch+=''.join(difflib.unified_diff(before.decode().splitlines(True)if before is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix()if before is not None else'/dev/null',tofile='b/'+rel.as_posix()))
 expected={'src/cv3_source_audio.s','src/cv3_dmc_complete.s','src/cv3_remaining_source_fx.s','src/entrypoint.s','src/roster_audio.s','src/megaman_death.s','src/cv3_abilities.s'};assert{r['path']for r in changed}==expected
 assert not any('Cv3SpawnAudioType::Done'in r['text']for r in refs)
 def bank(b,n):return b['raw'][16+n*8192:16+(n+1)*8192]
 banks=[]
 for n in range(128):
  ob,nb=bank(old,n),bank(new,n);delta=[i for i,(x,y)in enumerate(zip(ob,nb))if x!=y]
  if delta:banks.append(dict(bank=n,changed_bytes=len(delta),first_offset=min(delta),last_offset=max(delta)))
 assert{r['bank']for r in banks}=={2,28,29,82,84}
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 entry=address(old,'UnionDeathStartCore')-0xa000;size=int(old['syms']['UnionDeathStartCore']['size'],0);death_changes=[i for i,(x,y)in enumerate(zip(bank(old,2),bank(new,2)))if x!=y];assert len(death_changes)==3 and all(entry<=i<entry+size for i in death_changes)
 assert all(bank(old,2)[i-1]==bank(new,2)[i-1]==0xa9 for i in death_changes),'Only original cold UnionDeathStartCore farcall immediate operands change'
 assert bank(old,125)==bank(new,125)and bank(old,127)==bank(new,127),'Both complete resident/mirror banks stay exact'
 samples=[]
 for name in['BassWaterDpcm','AvDmcLinkTakeDamage','AvDmcSimonTakeDamage']:
  lo,hi=location(old,name),location(old,name+'End');assert lo==location(new,name)and hi==location(new,name+'End')and old['raw'][lo:hi]==new['raw'][lo:hi];samples.append(dict(name=name,address=address(new,name),bytes=hi-lo,sha256=digest(new['raw'][lo:hi])))
 storage=[]
 segs={s['name'].strip('"'):s for s in new['segs'].values()}
 for name,limit in[('CV_AUDIO',0xdc00),('CV3_GRIP',0xc000),('X5_AUDIO_MIX',0xc000)]:
  s=segs[name];begin=int(s['start'],0);size=int(s['size'],0);pos=int(s['ooffs'],0);storage.append(dict(name=name,segment_first_bank=(pos-16)//8192,segment_last_bank=(pos+size-17)//8192,free_span_physical_bank=(pos+size-16)//8192,end_exclusive=begin+size,free_bytes=limit-begin-size));assert begin+size<=limit
 (out/'all-deployable-files.json').write_text(json.dumps(allfiles,indent=2)+'\n');(out/'implementation.patch').write_text(patch,newline='\n');(out/'removed-private-label-references.json').write_text(json.dumps(refs,indent=2)+'\n')
 result=dict(passed=True,accepted=False,status='SOURCE_BUILD_CPU_READY_NATIVE_UNQUALIFIED',baseline_ROM_sha256=BASE,ROM_sha256=CAND,source_files=changed,all_deployable_files_enumerated=len(allfiles),all_deployable_manifest_sha256=sha(out/'all-deployable-files.json'),patch_sha256=sha(out/'implementation.patch'),durable_remaining_producer_exact=True,mirror_idempotent=True,ordinary_flagoff=ordinary,retained_old_qualified_symbols=len(oq)-2,legitimate_symbol_exceptions=[dict(name='Cv3SpawnAudioType::Done',before=0xb3eb,after=None,reason='Obsolete internal old return is removed, no external source reference and no fake alias.'),dict(name='_FARCALL_COUNT',before=oq[('_FARCALL_COUNT',)],after=nq[('_FARCALL_COUNT',)],reason='One actual new cold death bridge tail-farcall; existing fiveSMC addresses remain unchanged.')],changed_banks=banks,bank2_changes_only_actual_existing_UnionDeathStartCore_call_immediate_operands=death_changes,resident127_and_mirror125_all_bytes_exact=True,Mac123_and_gate_LOWCODE126_Samus_and_every_other_bank_exact=True,original_fixed_samples_exact=samples,CHR_exact=True,linked_remaining_storage=storage,new_RAM_allocation=0,private_existing_slab_used=[36,56],cold_owner_tail_exact38B=int(new['syms']['Cv3FxOwnerInit']['size'],0)==38,scope='Private exact source/producer/link/layout/ABI readiness only. Native actual release/visual/audio/bus/mapping/cadence and new source-effect strict native cadence on current50b remain required.',tool_sha256=sha(__file__))
 assert result['cold_owner_tail_exact38B'];(out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(Path(__file__),out/Path(__file__).name);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
