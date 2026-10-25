"""Private resident source/ABI/storage/producer/flag-off freeze; no native acceptance."""
from pathlib import Path
import argparse,concurrent.futures,difflib,hashlib,importlib.util,json,re,shutil,subprocess,sys
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load,address,location
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'cv3-remaining-current50b-v1/baseline-source'
HELD=D/'cv3-remaining-stubs-v2/qualified-v1/source-final'
PRIVATE={'Return','NoiseRunning','NoiseRelease','Done','PR','PulseRelease','NoiseTick'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def bank(b,n):return b['raw'][16+n*8192:16+(n+1)*8192]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);stage=out/'source-final';shutil.copytree(a.prepared/'source',stage);candidate=sha(a.prepared/'candidate.nes');assert sha(a.prepared/'baseline.nes')=='2e005c8e2acde44bc184459d92b2966ee488b92819dd91151577fdf444b751df'
 before=(stage/'audio/remaining-source-sfx.inc').read_bytes();producer=stage/'tools/reference/build_remaining_sfx.py';spec=importlib.util.spec_from_file_location('resident_original_producer',producer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main();assert before==(stage/'audio/remaining-source-sfx.inc').read_bytes()
 def build(name,flag=None):
  cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/(name+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  with(out/(name+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(name,(out/(name+'.host.log')).read_text()[-6000:]);return sha(out/(name+'.nes'))
 assert build('candidate')==candidate
 mirror=stage/'tools/prepare_cv3_dmc_mirror.py';spec=importlib.util.spec_from_file_location('resident_mirror_producer',mirror);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.prepare(stage,out/'candidate.nes');assert sha(out/'candidate.nes')==candidate
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:ordinary=list(pool.map(lambda n:dict(mapper=n,sha256=build('ordinary-'+n,n)),('mmc3','mmc5')))
 assert ordinary==[dict(mapper='mmc3',sha256='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),dict(mapper='mmc5',sha256='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]
 old,new=load(a.prepared/'baseline.nes'),load(out/'candidate.nes');oq,nq=qualified(a.prepared/'baseline.nes'),qualified(out/'candidate.nes');deltas={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v};assert set(deltas)=={('Cv3FxService',n)for n in PRIVATE},deltas
 for n in ['Cv3FxTick','Cv3FxService','Cv3FxMusicInit','Cv3FxLegacyNoiseHigh','Cv3SaveAudioZp','Cv3RestoreAudioZp']:
  assert address(old,n)==address(new,n)and old['syms'][n]['size']==new['syms'][n]['size']
 for n in ['Cv3SaveAudioZp','Cv3RestoreAudioZp','Cv3FxMusicInit','Cv3FxLegacyNoiseHigh']:
  size=int(old['syms'][n]['size'],0);assert old['raw'][location(old,n):location(old,n)+size]==new['raw'][location(new,n):location(new,n)+size]
 assert int(new['syms']['Cv3RestoreAudioZp']['size'],0)==247,'Existing restore already unrolled; no assumed loop saving'
 frames=[n for n in old['syms']if re.fullmatch(r'Cv3Fx(?:1F|13|15|24|21|2F)(?:Noise|Pulse)Frame\d{3}',n)]
 for n in frames:assert address(old,n)==address(new,n)and location(old,n)==location(new,n)
 srcoffset=location(old,'Cv3FxService')-16-82*8192;srcsize=int(old['syms']['Cv3FxService']['size'],0);assert all(x==y or srcoffset<=i<srcoffset+srcsize for i,(x,y)in enumerate(zip(bank(old,82),bank(new,82))))
 changed_banks=[dict(bank=n,changed_bytes=sum(x!=y for x,y in zip(bank(old,n),bank(new,n))))for n in range(128)if bank(old,n)!=bank(new,n)];assert {r['bank']for r in changed_banks}=={28,82}
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 files=[];changed=[];incremental=[];refs=[];patch='';incremental_patch=''
 for f in sorted(stage.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(stage)
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  after=f.read_bytes();oldfile=BASE/rel;before=oldfile.read_bytes()if oldfile.exists()else None;heldfile=HELD/rel;held=heldfile.read_bytes()if heldfile.exists()else None;files.append(dict(path=rel.as_posix(),candidate_sha256=digest(after),baseline_sha256=digest(before)if before is not None else None,held2e_sha256=digest(held)if held is not None else None))
  if rel.suffix=='.s':
   refs.extend(dict(path=rel.as_posix(),line=i,text=t.strip())for i,t in enumerate(after.decode().splitlines(),1)if re.search(r'Cv3FxService::(?:'+('|'.join(PRIVATE))+')\b',t))
  if held!=after:
   incremental.append(dict(path=rel.as_posix(),before_sha256=digest(held)if held is not None else None,after_sha256=digest(after)))
   incremental_patch+=''.join(difflib.unified_diff(held.decode().splitlines(True)if held is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix()if held is not None else'/dev/null',tofile='b/'+rel.as_posix()))
  if before==after:continue
  rec=dict(path=rel.as_posix(),sha256=digest(after),bytes=len(after),baseline_sha256=digest(before)if before is not None else None,EOL='CRLF'if b'\r\n'in after else'LF')
  if before is not None:
   git=subprocess.run(['git','show','HEAD:'+rel.as_posix()],cwd=ROOT,capture_output=True,check=True).stdout;assert git.replace(b'\r\n',b'\n')==before.replace(b'\r\n',b'\n');rec.update(original_git_sha256=digest(git),original_git_EOL='CRLF'if b'\r\n'in git else'LF');assert rec['EOL']==rec['original_git_EOL']
  changed.append(rec);patch+=''.join(difflib.unified_diff(before.decode().splitlines(True)if before is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix()if before is not None else'/dev/null',tofile='b/'+rel.as_posix()))
 assert not refs and len(changed)==7 and {r['path']for r in incremental}=={'src/cv3_remaining_source_fx.s'},(refs,incremental)
 (out/'all-deployable-files.json').write_text(json.dumps(files,indent=2)+'\n');(out/'implementation.patch').write_text(patch,newline='\n');(out/'incremental-from2e.patch').write_text(incremental_patch,newline='\n')
 seg=next(s for s in new['segs'].values()if s['name'].strip('"')=='CV_AUDIO');end=int(seg['start'],0)+int(seg['size'],0);assert end==0xdaf4
 result=dict(passed=True,accepted=False,status='SOURCE_CPU_READY_NATIVE_UNQUALIFIED',ROM_sha256=candidate,held2e_ROM_sha256=sha(a.prepared/'baseline.nes'),adopted_parent_ROM_sha256='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363',source_files=changed,incremental_source_files=incremental,all_deployable_files=len(files),all_deployable_manifest_sha256=sha(out/'all-deployable-files.json'),full_patch_sha256=sha(out/'implementation.patch'),incremental_patch_sha256=sha(out/'incremental-from2e.patch'),legitimate_symbol_moves=[dict(scope=list(k),before=v[0],after=v[1],reason='Genuine internal control block/stack-return moves from inline Peek and shared fallthrough tail; no external source reference, no fake alias.')for k,v in sorted(deltas.items())],retained_held2e_symbols=len(oq)-len(deltas),frame_packet_PC_count=len(frames),all_frame_packet_PC_exact=True,new_RAM_CHR_bytes=0,incremental_changed_banks=changed_banks,C28_new_resident_bytes=end-0xd9bc,C28_end=end,C28_slack_remaining=0xdc00-end,A82_end=0xbb0f,A82_free=1265,all_existing_CV1_Save_Restore_code_and_public_spans_exact=True,Mac_Roll_Mike_Pbar_fixed127_mirror125_all_other_banks_exact=True,original_remaining_producer_and_mirror_idempotent=True,ordinary_flagoff=ordinary,tool_sha256=sha(__file__),scope='Private source/CPU/layout only. Native timing/guards must run fresh on this exact hash and any later display-timing composition. Original held2e remains rejected.')
 (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(__file__,out/Path(__file__).name);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
