"""One frozen remaining-family731 profile after an explicit grant. Never retries."""
from pathlib import Path
import argparse,csv,datetime,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
SHA='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
PROFILES={'pit-hard':('pit',True,1,10),'rygar-easy':('rygar',False,0,12),'rygar-hard':('rygar',True,1,12),'scrooge-easy':('scrooge',False,0,9),'scrooge-hard':('scrooge',True,1,9)}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify_manifest(path):
 z=json.loads(path.read_text())
 for q in z['bindings']:
  f=Path(q['path']);assert f.stat().st_size==q['bytes'] and sha(f)==q['sha256'],f
 return len(z['bindings'])

def collect(out,cfg):
 """Read-only independent checks. Missing raw components remain FALSE."""
 result={};errors=[]
 for name in ['native-abilities.json','ppu-capture-native-result.json']:
  f=out/name
  try:result[name]=json.loads(f.read_text())
  except Exception as e:errors.append(name+': '+str(e));result[name]={}
 native=result['native-abilities.json'];capture=result['ppu-capture-native-result.json']
 names=[q['name']for q in cfg['abilities']]
 try:
  assert native.get('passed') and native['family']==cfg['family'] and native['hard']is cfg['hard'] and native['actual_mode_readback']==cfg['mode_value']
  assert [q['q']['name']for q in native['abilities']]==names
  assert len(native['physical_collections'])==2 and all(q['transformCalls']==60 and q['ownerCalls']>0 for q in native['physical_collections'])
  assert native['nmis']>100 and native['irq_scroll_stores']>100 and native['complete_dma_checks']>100 and native['hardware_chr_checks']>1200 and native['minSP']>=128
  result['original_abilities_and_guards_passed']=True
 except Exception as e:errors.append('original ability component: '+str(e));result['original_abilities_and_guards_passed']=False
 try:
  rows=list(csv.DictReader((out/'actual-ppu-index.csv').open(newline='')));size=(out/'actual-ppu.argb').stat().st_size
  assert rows and size==len(rows)*256*240*4 and capture.get('passed') and capture['frames']==len(rows) and capture['bytes']==size
  assert [int(q['ordinal'])for q in rows]==list(range(1,len(rows)+1))
  assert all(int(b['ppu_frame'])>int(a['ppu_frame'])for a,b in zip(rows,rows[1:]))
  assert capture['actual_mode_readback']==cfg['mode_value'] and capture['original_done_seen']
  result['full_PPU_raw_index']=dict(passed=True,frames=len(rows),bytes=size,raw_sha256=sha(out/'actual-ppu.argb'),index_sha256=sha(out/'actual-ppu-index.csv'))
 except Exception as e:errors.append('full PPU raw/index: '+str(e));result['full_PPU_raw_index']=dict(passed=False)
 try:
  complete=[];starts=0;enables=0;last_id=None
  with(out/'ability-dma-epochs.jsonl').open()as stream:
   for line in stream:
    q=json.loads(line)
    if q['kind']=='completed-DMA-before-render-enable':
     assert q['id']==len(complete)+1 and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware'] and not q['differences']
     assert len(q['writes'])==256 and q['page']==2 and q['start']['pc']==0xe005
     assert q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
     for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i] and w['stamp']['mask']&24==0
     complete.append(q);last_id=q['id']
    elif q['kind']=='startFrame-hardware':
     starts+=1;assert len(q['hardware'])==256
     if q.get('completed_dma_id') and not q.get('pending_dma_id'):
      assert q['completed_dma_id']==last_id and q['hardware']==complete[-1]['source']
    elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
     enables+=1;assert q['safe'];s=q['stamp'];assert 241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274
  assert len(complete)>100 and starts>100 and enables>100
  result['independent_actual_DMA_timing']=dict(passed=True,complete256_epochs=len(complete),startFrame_snapshots=starts,scoped_safe_enables=enables,raw_sha256=sha(out/'ability-dma-epochs.jsonl'))
 except Exception as e:errors.append('actual DMA/timing: '+str(e));result['independent_actual_DMA_timing']=dict(passed=False)
 result['case_screenshots']=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(out.glob('*.argb'))if p.name!='actual-ppu.argb']
 if not result['case_screenshots']:errors.append('Missing original case screenshots')
 if (out/'first-failure.json').exists():errors.append('Original first-failure receipt exists')
 result.update(passed=not errors,errors=errors,agent_visual_review=False,visual_status='Actual whole-PPU/case-window review required separately; raw integrity is not a visual pass.')
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--profile',choices=sorted(PROFILES),required=True);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args()
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['prepared'] and not ready['native_run'] and ready['ROM_sha256']==SHA and ready['maximum_launches_per_profile']==1
 manifest=a.ready/'manifest.json';assert sha(manifest)==ready['manifest_sha256'];count=verify_manifest(manifest)
 profile=next(q for q in ready['profiles']if q['profile']==a.profile)
 out=Path(profile['output']);cfg=json.loads((out/'config.json').read_text());assert(cfg['family'],cfg['hard'],cfg['mode_value'],len(cfg['abilities']))==PROFILES[a.profile]
 assert sha(out/'candidate.nes')==SHA and sha(out/'run.lua')==profile['script_sha256']
 assert not(out/'launch.json').exists()and not(out/'proof.json').exists(),'Exactly one launch; retain failures, never retry'
 query="@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"
 assert int(subprocess.check_output(['powershell','-NoProfile','-Command',query],text=True).strip())<2
 emu=Path(ready['environment']['emulator']);assert sha(emu)==ready['environment']['emulator_sha256']
 command=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(emu),str(out/'run.lua'),str(out/'candidate.nes'),'--timeout','900']+['--option='+s for s in ready['environment']['actual_command_overrides']]
 launch=dict(ROM_sha256=SHA,ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(manifest),manifest_bindings_checked=count,runner_sha256=sha(Path(__file__)),UTC_start=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=command,profile=a.profile,maximum_launches=1,maximum_workers_this_unit=1,explicit_native_grant_flag=True)
 (out/'launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 with(out/'host.log').open('w',encoding='utf-8')as stream:
  terminal=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
 analysis=collect(out,cfg)
 unchanged=True
 try:verify_manifest(manifest)
 except Exception:unchanged=False
 proof=dict(passed=terminal.returncode==0 and analysis['passed']and unchanged,native_run=True,goal_complete=False,ROM_sha256=SHA,profile=a.profile,actual_mode_required=cfg['mode_value'],launch_sha256=sha(out/'launch.json'),ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(manifest),runner_exit=terminal.returncode,dependencies_unchanged=unchanged,analysis=analysis,output_bindings={p.name:dict(sha256=sha(p),bytes=p.stat().st_size)for p in out.iterdir()if p.is_file()and p.name!='proof.json'},native_worker_released=True,scope='ONE explicitly selected frozen remaining-family profile. Cold/real physically acquired tiers; controlled use arenas. No retry/automatic next profile/all-item/visual/audio fidelity claim. Separate saved-image review remains mandatory.')
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],exit=terminal.returncode,proof=str(out/'proof.json'),proof_sha256=sha(out/'proof.json'))));raise SystemExit(0 if proof['passed']else 1)

if __name__=='__main__':main()
