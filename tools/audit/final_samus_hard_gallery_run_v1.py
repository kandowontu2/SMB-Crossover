"""One explicitly granted eight-case Hard Samus run; never retries."""
from pathlib import Path
import argparse,csv,datetime,hashlib,json,subprocess,sys
from final_item_abilities_remaining731_run_v1 import verify_manifest
ROOT=Path(__file__).resolve().parents[2]
SHA='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def collect(out,cfg):
 errors=[];parts={}
 try:
  n=json.loads((out/'native-samus-gallery.json').read_text());assert n['passed']and n['actual_mode_readback']==1 and n['hard']is True and n['acquisition']is False
  assert len(n['cases'])==8 and[q['q']['name']for q in n['cases']]==[q['name']for q in cfg['cases']]
  for q,p in zip(n['cases'],cfg['cases']):
   assert q['completed']and len(q['stages'])==len(p['tasks'])
   for s,t in zip(q['stages'],p['tasks']):assert s['passed']and s['completed']and s['kind']==t['kind']and s['face']==t['face']
  assert n['nmis']>100 and n['irq_scroll_stores']>100 and n['hardware_chr_checks']>1200 and n['complete_dma_checks']>100 and n['minSP']>=128
  parts['eight_native_cases']=n
 except Exception as e:errors.append('Native Samus cases: '+str(e))
 try:
  c=json.loads((out/'ppu-capture-native-result.json').read_text());rows=list(csv.DictReader((out/'actual-ppu-index.csv').open(newline='')));size=(out/'actual-ppu.argb').stat().st_size
  assert c['passed']and c['actual_mode_readback']==1 and c['original_done_seen']and c['frames']==len(rows)and size==c['bytes']==len(rows)*245760
  assert[int(q['ordinal'])for q in rows]==list(range(1,len(rows)+1))and all(int(b['ppu_frame'])>int(a['ppu_frame'])for a,b in zip(rows,rows[1:]))
  assert all(int(q['mode'])==1 for q in rows if int(q['updates'])>0)
  parts['full_actual_PPU']=dict(passed=True,frames=len(rows),bytes=size,raw_sha256=sha(out/'actual-ppu.argb'),index_sha256=sha(out/'actual-ppu-index.csv'))
 except Exception as e:errors.append('Full PPU: '+str(e))
 try:
  completed=starts=enables=pending=0;last=None;protocol=cfg['dma_protocol']
  for line in(out/'ability-dma-epochs.jsonl').open():
   q=json.loads(line)
   if q['kind']=='completed-DMA-before-render-enable':
    completed+=1;assert q['id']==completed and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware']and not q['differences']
    assert len(q['writes'])==256 and q['page']==2 and q['start']['pc']==protocol['window_start']and q['complete']['pc']==protocol['complete_pc']
    assert q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
    for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0
    last=q
   elif q['kind']=='startFrame-hardware':
    starts+=1;pending+=bool(q.get('pending_dma_id'));assert len(q['hardware'])==256
    if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert last and q['completed_dma_id']==last['id']and q['hardware']==last['source']
   elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
    enables+=1;s=q['stamp'];assert q['safe']and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274)
  assert completed>100 and starts>100 and enables>100
  parts['actual_hardware']=dict(passed=True,complete256DMAs=completed,startFrames=starts,classified_pending=pending,safe_scoped_enables=enables,raw_sha256=sha(out/'ability-dma-epochs.jsonl'))
 except Exception as e:errors.append('Full physical DMA/timing: '+str(e))
 caps=[p for p in out.glob('*.argb')if p.name not in['actual-ppu.argb','first-failure.argb']]
 if not caps:errors.append('Missing actual case captures')
 parts['case_captures']=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(caps)]
 if(out/'first-failure.json').exists():errors.append('First FALSE retained')
 return dict(passed=not errors,errors=errors,components=parts,agent_visual_review=False,scope='Mechanical/current physical records only. B seeded abilities, not acquisition. Independent actual full-frame/effect/HUD/opaque-pixel review remains required.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',required=True,type=Path);p.add_argument('--native-grant',required=True,action='store_true');a=p.parse_args()
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['prepared']and not ready['native_run']and ready['ROM_sha256']==SHA and ready['mode_value']==1 and ready['maximum_cases']==8
 manifest=a.ready/'manifest.json';assert sha(manifest)==ready['manifest_sha256'];verified=verify_manifest(manifest);out=Path(ready['output'])
 assert sha(out/'candidate.nes')==SHA and sha(out/'run.lua')==ready['script_sha256']and not(out/'launch.json').exists()and not(out/'proof.json').exists()
 grant=a.ready/'ROOT-grant.json';g=json.loads(grant.read_text());assert g['ready_sha256']==sha(a.ready/'proof.json')and g['maximum_launches']==1 and g['profile']=='samus-hard'
 live=int(subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"],text=True).strip());assert live<2
 env=ready['environment'];exe=Path(env['emulator']);assert sha(exe)==env['emulator_sha256']
 cmd=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(exe),str(out/'run.lua'),str(out/'candidate.nes'),'--timeout','1800']+['--option='+s for s in env['actual_command_overrides']]
 launch=dict(ROM_sha256=SHA,ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(manifest),grant_sha256=sha(grant),bindings_verified=verified,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=cmd,maximum_launches=1,maximum_owned_workers=1,profile='samus-hard',lane='B',acquisition=False)
 (out/'launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 with(out/'host.log').open('w',encoding='utf-8')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 cfg=json.loads((out/'config.json').read_text());analysis=collect(out,cfg);unchanged=True
 try:verify_manifest(manifest)
 except Exception:unchanged=False
 proof=dict(passed=r.returncode==0 and analysis['passed']and unchanged,native_run=True,ROM_sha256=SHA,actual_numeric_mode=1,runner_exit=r.returncode,analysis=analysis,dependencies_unchanged=unchanged,ready_sha256=sha(a.ready/'proof.json'),native_worker_released=True,bindings={p.name:dict(sha256=sha(p),bytes=p.stat().st_size)for p in out.iterdir()if p.is_file()and p.name!='proof.json'})
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],proof_sha256=sha(out/'proof.json'))));raise SystemExit(0 if proof['passed']else 1)

if __name__=='__main__':main()
