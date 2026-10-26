"""Private source composition of exact2cb5 CV3 onto exactf35f Parodius parent."""
from pathlib import Path
import argparse,collections,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load
from check_tmnt_audio_fallback_oc import qualified
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(x).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);parent=D/'parodius-hud-cancel-candidate-v1';cv=D/'cv3-remaining-legacy-wrapper-v2';base=D/'cv3-remaining-current50b-v1/baseline-source';assert sha(parent/'candidate.nes')=='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631';assert sha(cv/'candidate.nes')=='2cb5fca0757c3e347c264eab0bf3f22bd02d851787f38802a4af3cb0c3aa1fa5';source=a.output/'source';shutil.copytree(parent/'source',source);manifest=json.loads((cv/'layout-v1/proof.json').read_text());rows=[];patch=''
 for q in manifest['deployment_source']:
  f=source/q['path'];old=f.read_bytes()if f.exists()else None;after=(cv/'source'/q['path']).read_bytes();assert digest(after)==q['sha256']
  if q['path']=='src/entrypoint.s':
   assert after.replace(b'.include "cv3_remaining_source_fx.s"\r\n',b'')==(base/q['path']).read_bytes();assert old is not None and b'parodius_hud_queue.s'in old and b'nmi_vram_fast.s'in old and b'cv3_remaining_source_fx.s'not in old
   after=old+b'\r\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\r\n.include "cv3_remaining_source_fx.s"\r\n.endif\r\n'
  else:assert (digest(old)if old is not None else None)==q['old_sha256'],('Unexpected source overlap',q['path'])
  f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(after);rows.append(dict(path=q['path'],parent_sha256=digest(old)if old is not None else None,sha256=digest(after),raw_f35_prefix_preserved=q['path']=='src/entrypoint.s'))
  patch+=''.join(difflib.unified_diff(old.decode().splitlines(True)if old is not None else[],after.decode().splitlines(True),fromfile='a/'+q['path']if old is not None else'/dev/null',tofile='b/'+q['path']))
 (a.output/'implementation-fromf35.patch').write_text(patch,newline='\n')
 for ext in['.nes','.dbg','.lbl']:shutil.copyfile(parent/('candidate'+ext),a.output/('baseline'+ext))
 cmd=[sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
 with(a.output/'build-host.log').open('w')as log:z=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
 assert not z.returncode,(a.output/'build-host.log').read_text()[-6000:]
 b,c,f=[load(x/'candidate.nes')for x in[parent,cv,a.output]];assert b['raw'][:16]==c['raw'][:16]==f['raw'][:16];assert b['raw'][16+128*8192:]==c['raw'][16+128*8192:]==f['raw'][16+128*8192:]
 cvbanks={i for i in range(128)if c['raw'][16+i*8192:16+(i+1)*8192]!=(D/'cv3-remaining-current50b-v1/baseline.nes').read_bytes()[16+i*8192:16+(i+1)*8192]};assert cvbanks=={2,28,29,82,84}
 banks=[]
 for i in range(128):
  lo,hi=16+i*8192,16+(i+1)*8192;expect=c if i in cvbanks else b;assert f['raw'][lo:hi]==expect['raw'][lo:hi],('Bank mismatch',i)
  if f['raw'][lo:hi]!=b['raw'][lo:hi]:banks.append(dict(bank=i,changed_bytes=sum(x!=y for x,y in zip(f['raw'][lo:hi],b['raw'][lo:hi]))))
 oq,nq=[qualified(x/'candidate.nes')for x in[parent,a.output]];delta={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v};expected={('Cv3MusicAndNoiseTick',n)for n in['RestoreMusic','Volume','Done','Reset','Continue','End']};assert set(delta)==expected,delta
 files=[];changed=[]
 for f in sorted(source.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(source)
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  prior=parent/'source'/rel;h=sha(f);old=sha(prior)if prior.exists()else None;files.append(dict(path=rel.as_posix(),sha256=h,parent_sha256=old))
  if h!=old:changed.append(rel.as_posix())
 assert set(changed)=={q['path']for q in rows};assert len(rows)==8
 (a.output/'all-deployable-files.json').write_text(json.dumps(files,indent=2)+'\n');r=dict(prepared=True,native_executed=False,adopted=False,status='PRIVATE_F35_PLUS_CV3_SOURCE_COMPOSITION_UNQUALIFIED',ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(parent/'candidate.nes'),CV3_donor_sha256=sha(cv/'candidate.nes'),source=str(source),all_deployable_files=len(files),manifest_sha256=sha(a.output/'all-deployable-files.json'),changed_source=rows,changed_banks_vsf35=banks,all_nonCV3_banks_exact_f35=True,all_CV3_banks_exact2cb5=True,header_CHR_exact=True,all_f35_source_outside8_exact=True,f35_config_vic_queue_raw_exact=True,retained_qualified_symbols=len(oq)-len(delta),legitimate_private_symbol_moves=[dict(scope=list(k),old=v[0],new=v[1])for k,v in sorted(delta.items())],sourcepatch_sha256=sha(a.output/'implementation-fromf35.patch'),tool_sha256=sha(__file__),scope='Exact f35 source frozen and only intended CV3 eight-file delta composed. Shared entrypoint retains every original f35 byte as prefix and appends guarded FX include, preserving earlier macro IDs. No game/code/art/default production writes or native launch; f35 sixth aggregate remains incomplete and parent unaccepted. Further CPU/ABI/source/queue/IRQ checks required.')
 (a.output/'prepared.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
