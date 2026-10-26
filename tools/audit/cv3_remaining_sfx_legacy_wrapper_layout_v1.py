"""Freeze the three-file legacy wrapper successor and genuine symbol/storage boundaries."""
from pathlib import Path
import argparse,difflib,hashlib,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'cv3-remaining-steady-v3/source'
BASE=D/'cv3-remaining-current50b-v1/baseline-source'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(v).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old,new=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];assert sha(a.prepared/'baseline.nes')=='eaa36e56c09e87f58a85db312894f14bfd7fb5838be139fc508ae6121c9e0732'
 oq,nq=[qualified(a.prepared/(n+'.nes'))for n in['baseline','candidate']];delta={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v}
 expected={('Cv3MusicAndNoiseTick',n)for n in['RestoreMusic','Volume','Done','Reset','Continue','End']}
 assert set(delta)==expected and all(v[1]is not None for v in delta.values())
 references=[]
 for f in(a.prepared/'source/src').rglob('*'):
  if f.is_file()and f.suffix in['.s','.inc']:
   for k in delta:
    if '::'.join(k)in f.read_text():references.append(dict(path=str(f),name='::'.join(k)))
 assert not references,references
 for name in['Cv3FxTick','Cv3FxResidentDispatch','Cv3FxResidentNoise','Cv3FxResidentVolume','Cv3FxResidentPeriod','Cv3FxDrainGate','Cv3FxMuteGate','Cv3SaveAudioZp','Cv3RestoreAudioZp','Cv3FxService','Cv3FxProducerFast','Cv3FxProducer','Cv3FxSpawn','Cv3Spawn']:
  assert address(old,name)==address(new,name)and old['syms'][name].get('size')==new['syms'][name].get('size'),name
 for name in['Cv3FxTick','Cv3FxResidentDispatch','Cv3FxResidentVolume','Cv3FxResidentPeriod','Cv3FxDrainGate','Cv3FxMuteGate','Cv3SaveAudioZp','Cv3RestoreAudioZp','Cv3FxService','Cv3FxProducerFast','Cv3FxProducer','Cv3Spawn']:
  count=int(old['syms'][name].get('size','1'),0);at=location(old,name);assert at==location(new,name)and old['raw'][at:at+count]==new['raw'][at:at+count],name
 assert address(new,'Cv3FxResidentBody')==0xdb3a;assert address(new,'Cv3FxResidentBody')+int(new['syms']['Cv3FxResidentBody']['size'],0)<=0xdc00
 changed=[]
 for bank in range(128):
  at=16+bank*8192;x,y=[b['raw'][at:at+8192]for b in[old,new]]
  if x!=y:changed.append(dict(bank=bank,bytes=sum(c!=d for c,d in zip(x,y))))
 assert len(changed)==1 and changed[0]['bank']==28;assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 native=location(new,'Cv3FxNativeTick');assert address(new,'Cv3FxNativeTick')==0xda51
 assert old['raw'][native:native+67]==bytes([0xea])*67
 legacy=location(new,'Cv3MusicAndNoiseTick');wrapper=16+28*8192+(0xdc00-0xc000)
 allowed=set(range(native,native+67))|set(range(legacy,legacy+221))|set(range(wrapper,legacy))
 assert all(i in allowed for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y)
 assert sum(x!=y for x,y in zip(old['raw'][wrapper:legacy],new['raw'][wrapper:legacy]))==3
 assert address(old,'Cv3MusicAndNoiseTick')==address(new,'Cv3MusicAndNoiseTick')and location(old,'Cv3NoiseVolumeStore')==location(new,'Cv3NoiseVolumeStore')
 allfiles=[];incremental=[];deploy=[];incpatch='';fullpatch=''
 for f in sorted((a.prepared/'source').rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(a.prepared/'source')
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  after=f.read_bytes();priorfile=PARENT/rel;prior=priorfile.read_bytes()if priorfile.exists()else None;basefile=BASE/rel;base=basefile.read_bytes()if basefile.exists()else None
  allfiles.append(dict(path=rel.as_posix(),sha256=digest(after),parent_sha256=digest(prior)if prior is not None else None,accepted50b_sha256=digest(base)if base is not None else None))
  if after!=prior:
   incremental.append(dict(path=rel.as_posix(),sha256=digest(after),old_sha256=digest(prior)if prior is not None else None,EOL='CRLF'if b'\r\n'in after else'LF'));incpatch+=''.join(difflib.unified_diff(prior.decode().splitlines(True)if prior is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix(),tofile='b/'+rel.as_posix()))
  if after!=base:
   deploy.append(dict(path=rel.as_posix(),sha256=digest(after),old_sha256=digest(base)if base is not None else None,EOL='CRLF'if b'\r\n'in after else'LF'));fullpatch+=''.join(difflib.unified_diff(base.decode().splitlines(True)if base is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix()if base is not None else'/dev/null',tofile='b/'+rel.as_posix()))
 assert len(incremental)==3 and {r['path']for r in incremental}=={'src/roster_audio.s','src/cv3_source_audio.s','src/cv3_remaining_source_fx.s'}and all(r['EOL']=='LF'for r in incremental);assert len(deploy)==8
 (a.output/'all-deployable-files.json').write_text(json.dumps(allfiles,indent=2)+'\n');(a.output/'incremental-fromeaa3.patch').write_text(incpatch,newline='\n');(a.output/'implementation-from50b.patch').write_text(fullpatch,newline='\n')
 def build(name,flag=None):
  cmd=[sys.executable,str(a.prepared/'source/tools/build_mmc5_expanded.py'),'--workspace',str(a.prepared/'source'),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/(name+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  with(a.output/(name+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=a.prepared/'source',stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(name,(a.output/(name+'.host.log')).read_text()[-5000:]);return sha(a.output/(name+'.nes'))
 assert build('candidate')==sha(a.prepared/'candidate.nes')
 ordinary=[dict(mapper=n,sha256=build('ordinary-'+n,n))for n in['mmc3','mmc5']]
 assert ordinary==[dict(mapper='mmc3',sha256='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),dict(mapper='mmc5',sha256='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]
 r=dict(passed=True,native_executed=False,accepted=False,ROM_sha256=sha(a.prepared/'candidate.nes'),parent_ROM_sha256=sha(a.prepared/'baseline.nes'),source=str(a.prepared/'source'),all_deployable_files=len(allfiles),all_deployable_manifest_sha256=sha(a.output/'all-deployable-files.json'),incremental_source=incremental,deployment_source=deploy,incremental_patch_sha256=sha(a.output/'incremental-fromeaa3.patch'),implementation_patch_sha256=sha(a.output/'implementation-from50b.patch'),changed_banks=changed,all_other_banks_header_CHR_exact=True,new_RAM_CHR=0,retained_qualified_symbols=len(oq)-len(delta),legitimate_private_symbol_moves=[dict(scope=list(k),old=v[0],new=v[1],reason='Real internal legacy labels move after redundant tests are removed; original phase/source loop remains. No external game references and no fake aliases; future observer bindings must use actual labels.')for k,v in sorted(delta.items())],new_body=dict(start=address(new,'Cv3FxResidentBody'),size=int(new['syms']['Cv3FxResidentBody']['size'],0),declared_space_end=0xdc00),ordinary_flagoff=ordinary,tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
