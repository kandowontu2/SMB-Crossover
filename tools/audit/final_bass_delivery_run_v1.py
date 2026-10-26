"""One separately granted four-reward Bass physical-delivery run, never retries."""
from pathlib import Path
import argparse,csv,datetime,hashlib,json,subprocess,sys
from final_item_abilities_remaining731_run_v1 import verify_manifest
ROOT=Path(__file__).resolve().parents[2]
SHA='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def collect(out):
 errors=[];parts={}
 try:
  n=json.loads((out/'native-bass-delivery.json').read_text());assert n['passed']and n['actual_mode_readback']==0 and n['hard']is False and n['acquisition']is True
  rows=n['cases'];assert len(rows)==4 and [r['item']for r in rows[:1]]==[0]and len({r['item']for r in rows[1:]})==3
  for r in rows:
   assert r['prepareCalls']==r['ownerCalls']==1 and r['headObserved']and r['revealed']<=r['mature']<r['contactAligned']<=r['collected']<r['complete']
   assert r['after']==r['before']|(1<<r['item'])and r['transformCalls']==(60 if r['item']==0 else 0)and r['grantCalls']==(0 if r['item']==0 else 1)
   if r['item']>0:assert r['riseCalls']==48 and r['drawCalls']>0
   if r['item']==8:assert r['passiveSkipped']
   else:assert r['useObserved']and r['naturalCleanup']and(r['item']==0 or r['spends'])
  assert n['nmis']>100 and n['irq_scroll_stores']>100 and n['hardware_chr_checks']>1200 and n['complete_dma_checks']>100 and n['minSP']>=128
  parts['physical_native']=n
 except Exception as e:errors.append('Physical native: '+str(e))
 try:
  c=json.loads((out/'ppu-capture-native-result.json').read_text());rows=list(csv.DictReader((out/'actual-ppu-index.csv').open(newline='')));size=(out/'actual-ppu.argb').stat().st_size
  assert c['passed']and c['actual_mode_readback']==0 and c['original_done_seen']and c['frames']==len(rows)and c['bytes']==size==len(rows)*256*240*4
  assert [int(q['ordinal'])for q in rows]==list(range(1,len(rows)+1))and all(int(b['ppu_frame'])>int(a['ppu_frame'])for a,b in zip(rows,rows[1:]))
  parts['full_PPU']=dict(passed=True,frames=len(rows),bytes=size,raw_sha256=sha(out/'actual-ppu.argb'),index_sha256=sha(out/'actual-ppu-index.csv'))
 except Exception as e:errors.append('Full PPU: '+str(e))
 try:
  completed=[];starts=enables=pending=0
  for line in(out/'ability-dma-epochs.jsonl').open():
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
  parts['actual_hardware']=dict(passed=True,complete256DMAs=len(completed),startFrames=starts,classified_pending=pending,safe_enables=enables,raw_sha256=sha(out/'ability-dma-epochs.jsonl'))
 except Exception as e:errors.append('Actual hardware: '+str(e))
 caps=[q for q in out.glob('reward-*.argb')];assert caps
 parts['captures']=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(caps)]
 if(out/'first-failure.json').exists():errors.append('Original first failure retained')
 return dict(passed=not errors,errors=errors,components=parts,agent_visual_review=False,scope='Four physical delivery components; explicit world/native-boundary and post-rise contact staging. Independent actual images/pixels remain required; not an all-item/campaign certificate.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',required=True,type=Path);p.add_argument('--native-grant',required=True,action='store_true');a=p.parse_args()
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['prepared']and not ready['native_run']and ready['ROM_sha256']==SHA and ready['mode_value']==0 and ready['maximum_rewards']==4
 assert sha(a.ready/'manifest.json')==ready['manifest_sha256'];count=verify_manifest(a.ready/'manifest.json');out=Path(ready['output']);assert sha(out/'candidate.nes')==SHA and sha(out/'run.lua')==ready['script_sha256']and not(out/'launch.json').exists()and not(out/'proof.json').exists()
 # The parent creates this only after reviewing frozen readiness; preparation
 # alone does not grant a native process.
 grant=a.ready/'ROOT-grant.json';g=json.loads(grant.read_text());assert g['ready_sha256']==sha(a.ready/'proof.json')and g['maximum_launches']==1 and g['profile']==ready['profile']
 live=int(subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"],text=True).strip());assert live<2
 env=ready['environment'];emulator=Path(env['emulator']);assert sha(emulator)==env['emulator_sha256']
 cmd=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(emulator),str(out/'run.lua'),str(out/'candidate.nes'),'--timeout','1200']+['--option='+s for s in env['actual_command_overrides']]
 launch=dict(ROM_sha256=SHA,ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=ready['manifest_sha256'],bindings_verified=count,grant_sha256=sha(grant),UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=cmd,maximum_launches=1,maximum_owned_workers=1,profile=ready['profile'],post_rise_contact_alignment=True)
 (out/'launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 with(out/'host.log').open('w',encoding='utf-8')as f:run=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 analysis=collect(out);unchanged=True
 try:verify_manifest(a.ready/'manifest.json')
 except Exception:unchanged=False
 proof=dict(passed=run.returncode==0 and analysis['passed']and unchanged,native_run=True,ROM_sha256=SHA,actual_numeric_mode=0,runner_exit=run.returncode,analysis=analysis,dependencies_unchanged=unchanged,ready_sha256=sha(a.ready/'proof.json'),native_worker_released=True,bindings={q.name:dict(sha256=sha(q),bytes=q.stat().st_size)for q in out.iterdir()if q.is_file()and q.name!='proof.json'})
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],proof_sha256=sha(out/'proof.json'))));raise SystemExit(0 if proof['passed']else 1)

if __name__=='__main__':main()
