"""Run exactly one separately granted legal Bill/Lance Hard profile."""
from pathlib import Path
import argparse,csv,datetime,json,subprocess,sys
from final_bill_lance_hard_gallery_source_v1 import SHA,ROOT,sha
from final_item_abilities_remaining731_run_v1 import verify_manifest


def collect(out,cfg):
    errors=[];parts={}
    try:
        n=json.loads((out/'native-bill-gallery.json').read_text())
        assert n['passed'] and n['actual_mode_readback']==1 and not n['acquisition']
        assert n['actual_variant_readback']==n['variant']==cfg['variant']
        assert len(n['cases'])==7
        for q,p in zip(n['cases'],cfg['cases']):
            assert q['q']==p and q['completed'] and len(q['stages'])==len(p['tasks'])
            assert [z['item']for z in q['grants']]==p['incremental_grants']
            assert q['collectCalls']==len(q['grants'])
            for s,t in zip(q['stages'],p['tasks']):
                assert s['passed'] and s['completed'] and s['kind']==t['kind'] and s['face']==t['face'] and s['naturalPoolEmpty']
                assert s['spawns'] and s['draws']>0
                if t['kind']=='contact':assert s['hits']>0 and s['damageCalls']>0
                if t['kind']=='terrain':
                    assert s['blockCalls']>0
                    if p['terrain_behavior']=='bypass-plain-ground':assert s['groundCrossed'] and s['impacts']==0
                    else:assert s['impacts']>0
        assert n['nmis']>100 and n['irq_scroll_stores']>100 and n['hardware_chr_checks']>1200 and n['complete_dma_checks']>100 and n['minSP']>=128
        parts['seven_legal_native_cases']=n
    except Exception as e:errors.append('Native cases: '+str(e))
    try:
        c=json.loads((out/'ppu-capture-native-result.json').read_text())
        rows=list(csv.DictReader((out/'actual-ppu-index.csv').open(newline='')))
        size=(out/'actual-ppu.argb').stat().st_size
        assert c['passed'] and c['actual_mode_readback']==1 and c['original_done_seen']
        assert c['frames']==len(rows) and size==c['bytes']==len(rows)*245760
        assert [int(q['ordinal'])for q in rows]==list(range(1,len(rows)+1))
        assert all(int(y['ppu_frame'])>int(x['ppu_frame'])for x,y in zip(rows,rows[1:]))
        assert all(int(q['mode'])==1 for q in rows if int(q['updates'])>0)
        parts['actual_full_PPU']=dict(passed=True,frames=len(rows),bytes=size,raw_sha256=sha(out/'actual-ppu.argb'),index_sha256=sha(out/'actual-ppu-index.csv'))
    except Exception as e:errors.append('Full PPU: '+str(e))
    try:
        completed=starts=enables=pending=0;last=None;p=cfg['dma_protocol']
        for line in(out/'ability-dma-epochs.jsonl').open():
            q=json.loads(line)
            if q['kind']=='completed-DMA-before-render-enable':
                completed+=1
                assert q['id']==completed and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware']and not q['differences']
                assert len(q['writes'])==256 and q['page']==2 and q['start']['pc']==p['window_start']and q['complete']['pc']==p['complete_pc']
                assert q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
                for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0
                last=q
            elif q['kind']=='startFrame-hardware':
                starts+=1;pending+=bool(q.get('pending_dma_id'));assert len(q['hardware'])==256
                if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert last and q['completed_dma_id']==last['id']and q['hardware']==last['source']
            elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
                enables+=1;s=q['stamp'];assert q['safe']and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274)
        assert completed>100 and starts>100 and enables>100
        parts['hardware']=dict(passed=True,complete256DMAs=completed,startFrames=starts,classified_pending=pending,safe_scoped_enables=enables,raw_sha256=sha(out/'ability-dma-epochs.jsonl'))
    except Exception as e:errors.append('Full physical DMA/timing: '+str(e))
    try:
        rows=list(csv.DictReader((out/'bill-cadence.csv').open(newline='')))
        entries=[q for q in rows if q['kind']=='entry'];finishes=[q for q in rows if q['kind']=='finish']
        assert len(entries)>100 and len(finishes)>100
        assert all(int(y['cycle'])>int(x['cycle'])for x,y in zip(rows,rows[1:]))
        parts['cadence']=dict(passed=True,entries=len(entries),finishes=len(finishes),raw_sha256=sha(out/'bill-cadence.csv'),scope='Actual current workload stamps; no different-ROM timing comparison or universal no-lag claim.')
    except Exception as e:errors.append('Main cadence: '+str(e))
    caps=[p for p in out.glob('*.argb')if p.name not in['actual-ppu.argb','first-failure.argb']]
    if not caps:errors.append('Missing actual case captures')
    parts['case_captures']=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(caps)]
    if(out/'first-failure.json').exists():errors.append('First FALSE retained')
    return dict(passed=not errors,errors=errors,components=parts,agent_visual_review=False,
        scope='B controlled legal use with real staged-mature-item collision/grant. No native questionblock/rise/random-drop acquisition or waveform claim; actual full images still require separate review.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ready',type=Path,required=True);p.add_argument('--profile',choices=['bill-hard','lance-hard'],required=True)
    p.add_argument('--native-grant',required=True,action='store_true');a=p.parse_args()
    ready=json.loads((a.ready/'proof.json').read_text());assert ready['prepared']and not ready['native_run']and ready['ROM_sha256']==SHA and ready['cases_per_identity']==7
    manifest=a.ready/'manifest.json';assert sha(manifest)==ready['manifest_sha256'];verified=verify_manifest(manifest)
    row=next(q for q in ready['profiles']if q['profile']==a.profile);out=Path(row['output'])
    assert sha(out/'run.lua')==row['script_sha256']and not(out/'launch.json').exists()
    grant=a.ready/('ROOT-grant-'+a.profile+'.json');g=json.loads(grant.read_text())
    assert g['native_grant_explicit'] and g['ready_sha256']==sha(a.ready/'proof.json')and g['maximum_launches']==1 and g['profile']==a.profile
    live=int(subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"],text=True).strip());assert live<2
    env=ready['environment']
    for n in ['emulator','core','worker_settings','user_settings']:assert sha(env[n])==env[n+'_sha256']
    rom=Path(ready['ROM']);assert sha(rom)==SHA
    cmd=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',env['emulator'],str(out/'run.lua'),str(rom),'--timeout','1800']+['--option='+s for s in env['actual_command_overrides']]
    with(out/'launch.json').open('x',encoding='utf-8')as f:json.dump(dict(ROM_sha256=SHA,profile=a.profile,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ready_sha256=sha(a.ready/'proof.json'),manifest_sha256=sha(manifest),grant_sha256=sha(grant),bindings_verified=verified,command=cmd,maximum_launches=1,maximum_owned_workers=1),f,indent=2)
    with(out/'host.log').open('x',encoding='utf-8')as f:z=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
    cfg=json.loads((out/'config.json').read_text());analysis=collect(out,cfg);unchanged=True
    try:verify_manifest(manifest)
    except Exception:unchanged=False
    result=dict(passed=z.returncode==0 and analysis['passed']and unchanged,native_run=True,ROM_sha256=SHA,profile=a.profile,runner_exit=z.returncode,analysis=analysis,dependencies_unchanged=unchanged,worker_released=True,launches=1,retries=0,ready_sha256=sha(a.ready/'proof.json'),bindings={str(f):dict(sha256=sha(f),bytes=f.stat().st_size)for f in out.iterdir()if f.is_file()and f.name!='proof.json'})
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],worker_released=True,proof_sha256=sha(out/'proof.json'))));raise SystemExit(0 if result['passed']else 1)


if __name__=='__main__':main()
