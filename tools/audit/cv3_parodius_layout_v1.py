"""Qualify already built private composition, retaining strict first catalog failure."""
from pathlib import Path
import argparse,collections,hashlib,json,shutil
from check_tmnt_render_oa import load,address
from check_tmnt_audio_fallback_oc import qualified
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);f35=D/'parodius-hud-cancel-candidate-v1';cv=D/'cv3-remaining-legacy-wrapper-v2';base=D/'cv3-remaining-current50b-v1/baseline.nes';sources=a.prepared/'source';assert sha(a.prepared/'candidate.nes')=='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682';assert sha(f35/'candidate.nes')=='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631';assert sha(cv/'candidate.nes')=='2cb5fca0757c3e347c264eab0bf3f22bd02d851787f38802a4af3cb0c3aa1fa5'
 raws={n:p.read_bytes()for n,p in[('parent',f35/'candidate.nes'),('CV3',cv/'candidate.nes'),('candidate',a.prepared/'candidate.nes'),('accepted50b',base)]};assert len({x[:16]for x in raws.values()})==len({x[16+128*8192:]for x in raws.values()})==1
 cvbanks={i for i in range(128)if raws['CV3'][16+i*8192:16+(i+1)*8192]!=raws['accepted50b'][16+i*8192:16+(i+1)*8192]};assert cvbanks=={2,28,29,82,84};banks=[]
 for i in range(128):
  lo,hi=16+i*8192,16+(i+1)*8192;owner='CV3'if i in cvbanks else'parent';assert raws['candidate'][lo:hi]==raws[owner][lo:hi],i
  if raws['candidate'][lo:hi]!=raws['parent'][lo:hi]:banks.append(dict(bank=i,changed_bytes=sum(x!=y for x,y in zip(raws['candidate'][lo:hi],raws['parent'][lo:hi]))))
 oq,nq=[qualified(p)for p in[f35/'candidate.nes',a.prepared/'candidate.nes']];delta={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v};moved={('Cv3MusicAndNoiseTick',n)for n in['RestoreMusic','Volume','Done','Reset','Continue','End']};removed={('Cv3NoiseSceneReset','Variant'),('Cv3NoiseSceneReset','Owner'),('Cv3SpawnAudioType','Done')};expected=moved|removed|{('_FARCALL_COUNT',)};assert set(delta)==expected,delta;assert all(delta[k][1]is None for k in removed);assert delta[('_FARCALL_COUNT',)]==(1153,1154)
 refs=[]
 for f in(sources/'src').rglob('*'):
  if f.is_file()and f.suffix in['.s','.inc']:
   for k in removed|moved:
    if '::'.join(k)in f.read_text():refs.append(dict(path=str(f),name='::'.join(k)))
 assert not refs,refs
 files=[];changes=[];deploy=json.loads((cv/'layout-v1/proof.json').read_text())['deployment_source'];cvpaths={r['path']for r in deploy};assert len(cvpaths)==8
 for f in sorted(sources.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(sources)
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  prev=f35/'source'/rel;old=sha(prev)if prev.exists()else None;h=sha(f);files.append(dict(path=rel.as_posix(),sha256=h,parent_sha256=old))
  if h!=old:changes.append(rel.as_posix())
 assert set(changes)==cvpaths
 for r in deploy:
  if r['path']=='src/entrypoint.s':
   old=(f35/'source'/r['path']).read_bytes();new=(sources/r['path']).read_bytes();assert new==old+b'\r\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\r\n.include "cv3_remaining_source_fx.s"\r\n.endif\r\n'
  else:assert sha(sources/r['path'])==r['sha256']
 for n in['src/parodius_hud_queue.s','src/vic_adapter.s','smb1base-mmc5-expanded.cfg','src/nmi_vram_fast.s']:assert sha(sources/n)==sha(f35/'source'/n)
 # Existing B code, added shared queue code and every genuine helper symbol retain addresses.
 b,n=[load(p)for p in[f35/'candidate.nes',a.prepared/'candidate.nes']]
 for name in['PnHudCancelLife','PnHudCancelRestore','PnHudCancelGateway','PnHudCancelWork','PnHudNewLife','VvDeathHudCancelled','NonMaskableInterrupt','AudioUpdate','IrqScrollSplit','Cv3NoiseSceneReset','Cv3SpawnAudioType']:assert address(b,name)==address(n,name),name
 (a.output/'all-deployable-files.json').write_text(json.dumps(files,indent=2)+'\n')
 pairs=[]
 for name,prior in[('cv3-donor-pair-v1',cv/'candidate.nes'),('hot-source-pair-v1',D/'cv3-remaining-steady-v3/candidate.nes'),('ordinary-f35-pair-v1',f35/'candidate.nes')]:
  folder=a.prepared/name;folder.mkdir(exist_ok=False)
  for stem,rom in[('baseline',prior),('candidate',a.prepared/'candidate.nes')]:
   for ext in['.nes','.dbg','.lbl']:shutil.copyfile(rom.with_suffix(ext),folder/(stem+ext))
  pairs.append(dict(name=name,baseline_sha256=sha(folder/'baseline.nes'),candidate_sha256=sha(folder/'candidate.nes')))
 failure=dict(retained_failure=True,native_executed=False,first_tool='cv3_parodius_compose_v1.py',error='Strict symbol assertion omitted three already genuine removed private labels and one build-only farcall counter from the FULL50b-to-CV3 delta. ROM compilation and disjoint bank proof had passed. No new source change, no native execution.',actual_extra_exceptions=[dict(scope=list(k),old=delta[k][0],new=delta[k][1])for k in sorted(removed|{('_FARCALL_COUNT',)})]);(a.output/'first-catalog-failure.json').write_text(json.dumps(failure,indent=2)+'\n')
 result=dict(passed=True,native_executed=False,adopted=False,status='PRIVATE_F35_PLUS_CV3_LAYOUT_SOURCE_MATCHED_CPU_PENDING',ROM_sha256=sha(a.prepared/'candidate.nes'),parent_ROM_sha256=sha(f35/'candidate.nes'),CV3_donor_sha256=sha(cv/'candidate.nes'),source=str(sources),all_deployable_files=len(files),manifest_sha256=sha(a.output/'all-deployable-files.json'),changed_source=changes,changed_banks_vs_f35=banks,all_other_banks_header_CHR_exact_f35=True,all_CV3_banks_exact2cb5=True,f35_queue_vic_config_nmi_files_raw_exact=True,entrypoint_all_f35_raw_bytes_retained_as_prefix=True,retained_qualified_symbols=len(oq)-len(delta),legitimate_symbol_exceptions=[dict(scope=list(k),old=v[0],new=v[1],reason='Actual internal legacy branch movement'if k in moved else'Genuine removed old branch; no external references or fake aliases'if k in removed else'Build-only count +1 for actual existing cold death-owner farcall; no PC/RAM allocation')for k,v in sorted(delta.items())],source_pairs=pairs,first_failure=sha(a.output/'first-catalog-failure.json'),tool_sha256=sha(__file__),scope='Full current-f35 source correspondence and exact per-bank composition, genuine old symbols and raw source ownership only. Three old private removals and build-only farcall count already part of full CV3 delta are disclosed rather than faked. No native grant/adoption or transfer of parent/eaa3 native claims.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='legitimate_symbol_exceptions'},indent=2))
if __name__=='__main__':main()
