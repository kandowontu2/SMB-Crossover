"""Exact256-ring source/catalog/PC/storage/ordinary build qualification."""
from pathlib import Path
import argparse,concurrent.futures,difflib,hashlib,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'cv3-remaining-current50b-v1/baseline-source'
PARENT=D/'cv3-remaining-queue-v8/qualified-v1/source-final'
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(Path(p).read_bytes())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);stage=a.output/'source-final';shutil.copytree(a.prepared/'source',stage)
 old,new=load(a.prepared/'baseline.nes'),load(a.prepared/'candidate.nes');assert sha(a.prepared/'baseline.nes')=='7b0a2cbdd806ff057d86c1af1834ecac5d34e1bb1747852e93d6ca2ec3d2fec2'
 oq,nq=qualified(a.prepared/'baseline.nes'),qualified(a.prepared/'candidate.nes');deltas={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v}
 private={'Cv3FxProducer','Cv3FxQueueCommand','Cv3FxCancelConsumer','Cv3FxDrain','Cv3FxOwnerInit'};assert len(deltas)==23 and all(k==('Cv3FxQueue',)or k[0]in private for k in deltas)
 refs=[]
 for f in(stage/'src').rglob('*'):
  if not f.is_file()or f.suffix not in['.s','.inc']:continue
  text=f.read_text()
  for k in deltas:
   if len(k)>1 and '::'.join(k)in text:refs.append(dict(path=f.relative_to(stage).as_posix(),name='::'.join(k)))
 assert not refs,refs
 for name in ['Cv3FxOwnerInit','Cv3FxTick','Cv3FxMusicInit','Cv3FxSpawn','Cv3FxBatEnter','Cv3FxCancel','Cv3NoiseSceneReset','Cv3FxService','Cv3SaveAudioZp','Cv3RestoreAudioZp','Cv3Spawn','Cv3SpawnAudioType']:
  assert address(old,name)==address(new,name)and old['syms'][name]['size']==new['syms'][name]['size'],name
 for name in ['Cv3FxService','Cv3SaveAudioZp','Cv3RestoreAudioZp','Cv3FxResidentDispatch','Cv3FxResidentNoise']:
  n=int(old['syms'][name]['size'],0);assert old['raw'][location(old,name):location(old,name)+n]==new['raw'][location(new,name):location(new,name)+n],name
 frames=[n for n in old['syms']if re.fullmatch(r'Cv3Fx(?:1F|13|15|24|21|2F)(?:Noise|Pulse)Frame\d{3}',n)]
 for name in frames:
  assert address(old,name)==address(new,name)and location(old,name)==location(new,name);start=location(old,name);size=int(old['syms'][name]['size'],0)if'size'in old['syms'][name]else 1;assert old['raw'][start:start+size]==new['raw'][start:start+size]
 changed=[]
 for n in range(128):
  lo=16+n*8192;aa,bb=old['raw'][lo:lo+8192],new['raw'][lo:lo+8192]
  if aa!=bb:changed.append(dict(bank=n,bytes=sum(x!=y for x,y in zip(aa,bb))))
 assert {r['bank']for r in changed}=={28,29,82,84};assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 assert address(new,'Cv3FxQueue')==address(new,'RgAudioRam')+256
 assert address(new,'Cv3FxQueue')+256==address(new,'RgAudioZp')
 fx=(stage/'src/cv3_remaining_source_fx.s').read_text();roster=(stage/'src/roster_audio.s').read_text()
 assert'Cv3FxQueue=RgAudioRam+$100'in fx and 'Cv3FxProducerFast'in fx and 'jsr Cv3FxMuteGate'in roster
 assert 'jmp KeptUpper ; upper channel RAM'in roster and 'genuine8-byte cold continuation'in roster
 assert fx.count('inc Cv3FxQueueHead')==3 and 'sta Cv3FxQueueHead'not in fx
 files=[];source_files=[];incremental=[];patch='';incpatch=''
 for f in sorted(stage.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(stage)
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  after=f.read_bytes();base=BASE/rel;before=base.read_bytes()if base.exists()else None;parent=PARENT/rel;prior=parent.read_bytes()if parent.exists()else None
  files.append(dict(path=rel.as_posix(),sha256=digest(after),accepted50b_sha256=digest(before)if before is not None else None,parent7b0_sha256=digest(prior)if prior is not None else None))
  if after!=prior:
   incremental.append(dict(path=rel.as_posix(),sha256=digest(after),old_sha256=digest(prior)if prior is not None else None));incpatch+=''.join(difflib.unified_diff(prior.decode().splitlines(True)if prior is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix(),tofile='b/'+rel.as_posix()))
  if after==before:continue
  rec=dict(path=rel.as_posix(),sha256=digest(after),bytes=len(after),old_sha256=digest(before)if before is not None else None,EOL='CRLF'if b'\r\n'in after else'LF')
  if before is not None:
   git=subprocess.run(['git','show','HEAD:'+rel.as_posix()],cwd=ROOT,capture_output=True,check=True).stdout;assert git.replace(b'\r\n',b'\n')==before.replace(b'\r\n',b'\n');rec.update(original_Git_sha256=digest(git),original_Git_EOL='CRLF'if b'\r\n'in git else'LF');assert rec['EOL']==rec['original_Git_EOL']
  source_files.append(rec);patch+=''.join(difflib.unified_diff(before.decode().splitlines(True)if before is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix()if before is not None else'/dev/null',tofile='b/'+rel.as_posix()))
 assert len(source_files)==8 and {r['path']for r in incremental}=={'src/cv3_combat.s','src/cv3_remaining_source_fx.s','src/roster_audio.s'}
 (a.output/'all-deployable-files.json').write_text(json.dumps(files,indent=2)+'\n');(a.output/'implementation.patch').write_text(patch,newline='\n');(a.output/'incremental-from7b0.patch').write_text(incpatch,newline='\n')
 def build(name,flag=None):
  cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/(name+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  with(a.output/(name+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(name,(a.output/(name+'.host.log')).read_text()[-5000:]);return sha(a.output/(name+'.nes'))
 assert build('candidate')==sha(a.prepared/'candidate.nes')
 # Compiler generated files are shared by variants, so build sequentially.
 ordinary=[dict(mapper=n,sha256=build('ordinary-'+n,n))for n in['mmc3','mmc5']]
 assert ordinary==[dict(mapper='mmc3',sha256='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),dict(mapper='mmc5',sha256='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]
 result=dict(passed=True,accepted=False,status='FROZEN_SOURCE_LAYOUT_ORDINARY_BUILDS_ONLY',ROM_sha256=sha(a.prepared/'candidate.nes'),parent7b0_ROM_sha256=sha(a.prepared/'baseline.nes'),adopted50b_ROM_sha256=sha(D/'cv3-remaining-current50b-v1/baseline.nes'),source_files=source_files,incremental_files=incremental,all_deployable_files=len(files),all_deployable_files_sha256=sha(a.output/'all-deployable-files.json'),implementation_patch_sha256=sha(a.output/'implementation.patch'),incremental_patch_sha256=sha(a.output/'incremental-from7b0.patch'),legitimate_symbol_exceptions=[dict(scope=list(k),old=v[0],new=v[1],reason='Queue storage alias explicitly relocated within existing channel RAM.'if k==('Cv3FxQueue',)else'Genuine private queue/consumer branch or helper moved/removed; every original public entry retained, no fake alias.')for k,v in sorted(deltas.items())],retained_qualified_symbols=len(oq)-len(deltas),source_frame_PC_count=len(frames),service_resident_Save_Restore_and_frames_byte_exact=True,changed_banks=changed,all_other_banks_header_CHR_DMC125127_Mac_Mike_Roll_Pbar_exact=True,new_allocated_RAM_CHR=0,queue_address=address(new,'Cv3FxQueue'),physical_slots=256,logical_capacity=64,ordinary_flagoff=ordinary,scope='Private source/catalog/ABI/layout/flagoff build qualification. Protocol/cold/mute/capacity/ordinary/DMC/IRQ/cost receipts remain separate; no native or adoption claim.',tool_sha256=sha(__file__))
 (a.output/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(__file__,a.output/Path(__file__).name);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
