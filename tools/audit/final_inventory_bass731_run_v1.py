"""One explicitly granted frozen Bass B-only gallery; never retries/auto-advances."""
from pathlib import Path
import argparse,csv,datetime,hashlib,json,subprocess,sys
from final_item_abilities_remaining731_run_v1 import verify_manifest
ROOT=Path(__file__).resolve().parents[2]
SHA='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def collect(out,cfg):
 errors=[];result={}
 try:
  n=json.loads((out/'native-bass-gallery.json').read_text());assert n['passed']and n['actual_mode_readback']==cfg['mode_value']and n['hard']is cfg['hard']and n['acquisition']is False
  assert [r['q']['name']for r in n['cases']]==[q['name']for q in cfg['cases']]
  assert len(n['cases'])==16
  for r in n['cases']:assert all(r[k]for k in ['naturalCleanup','emptyChecked','poolPassed','selectionCleanup'])and r['hits']>0 and r['damageCalls']>0
  assert n['nmis']>100 and n['irq_scroll_stores']>100 and n['hardware_chr_checks']>1200 and n['complete_dma_checks']>100 and n['minSP']>=128
  result['native_gallery']=n
 except Exception as e:errors.append('native B-gallery: '+str(e))
 try:
  c=json.loads((out/'ppu-capture-native-result.json').read_text());rows=list(csv.DictReader((out/'actual-ppu-index.csv').open(newline='')));size=(out/'actual-ppu.argb').stat().st_size
  assert c['passed']and c['actual_mode_readback']==cfg['mode_value']and c['original_done_seen']and c['frames']==len(rows)and c['bytes']==size==len(rows)*256*240*4
  assert [int(q['ordinal'])for q in rows]==list(range(1,len(rows)+1))and all(int(b['ppu_frame'])>int(a['ppu_frame'])for a,b in zip(rows,rows[1:]))
  result['full_PPU']=dict(passed=True,frames=len(rows),bytes=size,raw_sha256=sha(out/'actual-ppu.argb'),index_sha256=sha(out/'actual-ppu-index.csv'))
 except Exception as e:errors.append('full PPU: '+str(e))
 try:
  completed=[];starts=enables=pending=0
  for line in (out/'ability-dma-epochs.jsonl').open():
   q=json.loads(line)
   if q['kind']=='completed-DMA-before-render-enable':
    assert q['id']==len(completed)+1 and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware']and not q['differences']
    assert len(q['writes'])==256 and q['page']==2 and q['start']['pc']==0xe005 and q['complete']['pc']==0xe008
    assert q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
    for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0
    completed.append(q)
   elif q['kind']=='startFrame-hardware':
    starts+=1;pending+=bool(q.get('pending_dma_id'));assert len(q['hardware'])==256
    if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['completed_dma_id']==completed[-1]['id']and q['hardware']==completed[-1]['source']
   elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
    enables+=1;s=q['stamp'];assert q['safe']and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274)
  assert len(completed)>100 and starts>100 and enables>100
  result['actual_hardware']=dict(passed=True,completed256DMAs=len(completed),startFrame_snapshots=starts,classified_pending_starts=pending,safe_scoped_enables=enables,raw_sha256=sha(out/'ability-dma-epochs.jsonl'))
 except Exception as e:errors.append('actual DMA/PPU timing: '+str(e))
 result['case_screenshots']=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(out.glob('*.argb'))if p.name!='actual-ppu.argb']
 if not result['case_screenshots']:errors.append('Missing actual case captures')
 if (out/'first-failure.json').exists():errors.append('First failure retained')
 return dict(passed=not errors,errors=errors,components=result,agent_visual_review=False,scope='Mechanical/raw evidence only; independent saved-image/HUD/effect review remains required. No acquisition claim.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--profile',choices=['bass-easy','bass-hard'],required=True);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args()
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['prepared']and not ready['native_run']and ready['ROM_sha256']==SHA
 manifest=a.ready/'manifest.json';assert sha(manifest)==ready['manifest_sha256'];bindings=verify_manifest(manifest)
 z=next(q for q in ready['profiles']if q['profile']==a.profile);out=Path(z['output']);cfg=json.loads((out/'config.json').read_text())
 assert len(cfg['cases'])==16 and cfg['mode_value']==int(a.profile=='bass-hard')and cfg['hard']is(a.profile=='bass-hard')
 assert sha(out/'candidate.nes')==SHA and sha(out/'run.lua')==z['script_sha256']and not(out/'launch.json').exists()and not(out/'proof.json').exists()
 count=int(subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"],text=True).strip());assert count<2
 env=ready['environment'];emu=Path(env['emulator']);assert sha(emu)==env['emulator_sha256']
 command=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(emu),str(out/'run.lua'),str(out/'candidate.nes'),'--timeout','1800']+['--option='+s for s in env['actual_command_overrides']]
 launch=dict(ROM_sha256=SHA,ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(manifest),bindings_verified=bindings,runner_sha256=sha(Path(__file__)),UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=command,profile=a.profile,maximum_launches=1,maximum_owned_workers=1,native_grant_flag=True,lane='B',acquisition=False)
 (out/'launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 with(out/'host.log').open('w',encoding='utf-8')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
 analysis=collect(out,cfg);unchanged=True
 try:verify_manifest(manifest)
 except Exception:unchanged=False
 proof=dict(passed=r.returncode==0 and analysis['passed']and unchanged,native_run=True,ROM_sha256=SHA,profile=a.profile,actual_numeric_mode=cfg['mode_value'],runner_exit=r.returncode,analysis=analysis,dependencies_unchanged=unchanged,launch_sha256=sha(out/'launch.json'),ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(manifest),native_worker_released=True,bindings={p.name:dict(sha256=sha(p),bytes=p.stat().st_size)for p in out.iterdir()if p.is_file()and p.name!='proof.json'})
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],proof=str(out/'proof.json'),sha256=sha(out/'proof.json'))));raise SystemExit(0 if proof['passed']else 1)

if __name__=='__main__':main()
