"""Context-qualified ProtoHard14: strict runtime, informational human GUI watch."""
from pathlib import Path
import argparse,csv,datetime,hashlib,json,subprocess,sys
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_megaproto_common_collector_witness_v1 import ordered_case_witnesses
R=Path(__file__).resolve().parents[2]
SHA='ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
physical=lambda s:[v&0xe3 if i%4==2 else v for i,v in enumerate(s)]
def human_context_watch(path):
 try:
  raw=Path(path).read_bytes()
  return dict(available=True,path=str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),runtime_input=False,informational=True)
 except OSError as error:
  return dict(available=False,path=str(path),error=type(error).__name__,runtime_input=False,informational=True)
def collect(out,cfg):
 errors=[];parts={}
 try:
  z=json.loads((out/'native-megaproto-common.json').read_text());assert z['passed']and z['actual_mode_readback']==1 and z['hard']is True and z['acquisition']is False and z['family']=='megaman';assert len(z['cases'])==14 and[q['q']['name']for q in z['cases']]==[q['name']for q in cfg['cases']]
  for q in z['cases']:assert all(q[k]for k in['naturalCleanup','poolPassed','selectionCleanup'])and q['hits']>0 and q['damageCalls']>0
  parts['ordered_case_witnesses']=ordered_case_witnesses(out,cfg,z)
  assert z['nmis']>100 and z['irq_scroll_stores']>100 and z['hardware_chr_checks']>1200 and z['complete_dma_checks']>100 and z['minSP']>=128;parts['native_gallery']=z
 except Exception as e:errors.append('Native14common components: '+str(e))
 try:
  z=json.loads((out/'ppu-capture-native-result.json').read_text());rows=list(csv.DictReader((out/'actual-ppu-index.csv').open(newline='')));assert z['passed']and z['actual_mode_readback']==1 and z['original_done_seen']and z['frames']==len(rows)and z['bytes']==(out/'actual-ppu.argb').stat().st_size==len(rows)*245760;assert[int(q['ordinal'])for q in rows]==list(range(1,len(rows)+1))and all(int(b['ppu_frame'])>int(a['ppu_frame'])for a,b in zip(rows,rows[1:]));assert all(int(q['mode'])==1 for q in rows if int(q['updates'])>0);parts['full_actual_PPU']=dict(passed=True,frames=len(rows),bytes=len(rows)*245760,raw_sha256=sha(out/'actual-ppu.argb'),index_sha256=sha(out/'actual-ppu-index.csv'))
 except Exception as e:errors.append('FullPPU: '+str(e))
 try:
  completed=starts=enables=literal=ignored=0;last=None;protocol=cfg['dma_protocol']
  for line in(out/'ability-dma-epochs.jsonl').open():
   q=json.loads(line)
   if q['kind']=='completed-DMA-before-render-enable':
    completed+=1;assert q['id']==completed and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and physical(q['source'])==q['hardware']and not q['implemented_differences'];assert q['page']==2 and q['start']['pc']==protocol['window_start']and q['complete']['pc']==protocol['complete_pc']and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
    for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0
    rawdiff=[dict(offset=i,source=x,hardware=y)for i,(x,y)in enumerate(zip(q['source'],q['hardware']))if x!=y];assert rawdiff==list(q['differences'])==list(q['ignored_attribute_differences']);literal+=int(not rawdiff);ignored+=len(rawdiff)
    last=q
   elif q['kind']=='startFrame-hardware':
    starts+=1;assert len(q['hardware'])==256
    if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['completed_dma_id']==last['id']and q['hardware']==physical(last['source'])
   elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:enables+=1;assert q['safe']and(241<=q['stamp']['scanline']<=260 or q['stamp']['scanline']==-1 and q['stamp']['cycle']<=274)
  assert min(completed,starts,enables)>100;parts['actual_hardware']=dict(passed=True,complete256DMA=completed,startFrames=starts,safe_enables=enables,literal_byte_equal_DMA=literal,ignored_attribute_differences=ignored,physical_encoding_exact_DMA=completed,raw_sha256=sha(out/'ability-dma-epochs.jsonl'))
 except Exception as e:errors.append('ActualDMA/timing: '+str(e))
 if(out/'first-failure.json').exists():errors.append('FirstFALSE retained')
 return dict(passed=not errors,errors=errors,components=parts,agent_visual_review=False,scope='B controlled use only. Native mechanics/raw integrity, not independent effect/HUD pixel or audio/fairness verdict.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',required=True,type=Path);p.add_argument('--native-grant',required=True,action='store_true');a=p.parse_args();ready=json.loads((a.ready/'proof.json').read_text());assert ready['profile_local_OAM_encoding']=='attributeE3-v2';assert ready['prepared']and not ready['native_run']and ready['ROM_sha256']==SHA and ready['profile']=='proto-hard-common'and ready['maximum_cases']==14;assert sha(a.ready/'manifest.json')==ready['manifest_sha256'];count=verify_manifest(a.ready/'manifest.json');grant=a.ready/'ROOT-grant.json';g=json.loads(grant.read_text());assert g['ready_sha256']==sha(a.ready/'proof.json')and g['maximum_launches']==1 and g['profile']=='proto-hard-common';out=Path(ready['output']);cfg=json.loads((out/'config.json').read_text());assert cfg['identity']['owner']==1 and cfg['identity']['variant']==1 and cfg['mode_value']==1 and len(cfg['cases'])==14;assert sha(out/'candidate.nes')==SHA and sha(out/'run.lua')==ready['script_sha256']and not(out/'launch.json').exists()and not(out/'proof.json').exists()
 human_pre=human_context_watch(ready['environment']['human_context_watch_path'])
 live=int(subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"],text=True).strip());assert live<2;env=ready['environment'];exe=Path(env['emulator']);assert sha(exe)==env['emulator_sha256'];cmd=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(exe),str(out/'run.lua'),str(out/'candidate.nes'),'--timeout','1800']+['--option='+s for s in env['actual_command_overrides']];(out/'launch.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ROM_sha256=SHA,ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(a.ready/'manifest.json'),grant_sha256=sha(grant),bindings_verified=count,command=cmd,maximum_launches=1,maximum_owned_workers=1,profile='proto-hard-common',lane='B',acquisition=False,human_context_pre=human_pre,human_context_runtime_input=False),indent=2)+'\n')
 with(out/'host.log').open('w',encoding='utf-8')as f:run=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 analyzed=collect(out,cfg);unchanged=True
 try:verify_manifest(a.ready/'manifest.json')
 except Exception:unchanged=False
 proof=dict(passed=run.returncode==0 and analyzed['passed']and unchanged,native_run=True,ROM_sha256=SHA,runner_exit=run.returncode,analysis=analyzed,dependencies_unchanged=unchanged,native_worker_released=True,human_context_pre=human_pre,human_context_post=human_context_watch(env['human_context_watch_path']),human_context_runtime_input=False,ready_sha256=sha(a.ready/'proof.json'),bindings={q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in out.iterdir()if q.is_file()and q.name!='proof.json'});(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],proof_sha256=sha(out/'proof.json'))));raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
