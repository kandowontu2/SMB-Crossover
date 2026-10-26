"""Run only an explicitly granted exact641 discovery/replay pair; stop first FALSE."""
from pathlib import Path
import argparse,csv,datetime,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
ROM='641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        while z:=f.read(2**20):h.update(z)
    return h.hexdigest()
def get(p):return json.loads(Path(p).read_text())if Path(p).exists()else{}
def put(p,q):assert not p.exists(),p;p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def checks(folder,phase):
    result=get(folder/'result.json');chrproof=get(folder/'chr-commit.json');motion=get(folder/'completed-loop-motion.json');extra=get(folder/'route-observation-result.json')
    ok=result.get('cleared')is True and result.get('deaths')==0 and result.get('world_1_1_seen')is True and '0-1'in result.get('stage_entries',{})
    ok=ok and chrproof.get('passed')is True and motion.get('passed')is True and extra.get('passed')is True
    ok=ok and (extra.get('actual_numeric_mode'),extra.get('actual_character'),extra.get('actual_variant'))==(0,8,1)
    evidence=dict(result=result,CHR=chrproof,motion=motion,observer=extra)
    if ok:
        assert extra['ordinaryStompReturns']>0 and extra['nmiChecks']>0 and extra['irqChecks']>0
        assert (folder/'actual-ppu.argb').stat().st_size==extra['fullPPUframes']*256*240*4
        with(folder/'actual-ppu-index.csv').open()as f:rows=list(csv.DictReader(f))
        assert len(rows)==extra['fullPPUframes'] and [int(z['ordinal'])for z in rows]==list(range(1,len(rows)+1))
        assert int(rows[-1]['ppuFrame'])==result['frames']
        dmas=0;starts=0;enables=0
        with(folder/'ability-dma-epochs.jsonl').open()as f:
            for line in f:
                z=json.loads(line)
                if z['kind']=='completed-DMA-before-render-enable':
                    dmas+=1;assert len(z['source'])==len(z['hardware'])==len(z['writes'])==256
                    assert z['source']==z['hardware'] and z['differences']=={}
                    assert z['page']==2 and z['start']['pc']==0xe005 and z['complete']['pc']==0xe008
                    assert z['start']['mask']&24==z['complete']['mask']&24==0
                    assert [w['value']for w in z['writes']]==z['source']
                    assert [w['stamp']['oamaddr']for w in z['writes']]==list(range(256))
                    assert all(w['stamp']['mask']&24==0 for w in z['writes'])
                elif z['kind']=='startFrame-hardware':starts+=1
                elif z['kind']=='actual-PPUMASK-write'and z['scoped']and z['enabling']:
                    enables+=1;assert z['safe']
        assert dmas>0 and starts>0 and enables>0
        evidence.update(full256_DMA=dmas,startFrame_snapshots=starts,scoped_safe_enables=enables,
                        exact_fullPPU_sha256=sha(folder/'actual-ppu.argb'),frames=len(rows))
    return bool(ok),evidence


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--expected-readiness-sha256',required=True);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args()
    ready=a.packet/'readiness.json';assert sha(ready)==a.expected_readiness_sha256;q=get(ready)
    assert q['ROM_sha256']==ROM and q['maximum_launches']==2 and q['native_workers']==1 and q['automatic_retries']==0 and q['stop_first_failure']
    assert [z['name']for z in q['profiles']]==['discovery','replay']
    def preflight():
        for f,h in q['bindings'].items():assert sha(f)==h,f
        for n in ['emulator','core','worker_settings','user_settings']:assert sha(q['environment'][n])==q['environment'][n+'_sha256'],n
    preflight();put(a.packet/'launch.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),explicit_grant=True,maximum_launches=2,retries=0,readiness_sha256=sha(ready)))
    results=[]
    for phase in q['profiles']:
        preflight();folder=Path(phase['fixture']);assert not(folder/'result.json').exists()
        if phase['name']=='replay':
            assert len(results)==1 and results[0]['passed'];source=a.packet/'discovery'
            put(folder/'actual-input-bindings.json',dict(source_discovery_receipt_sha256=sha(source/'native-receipt.json'),inputs_sha256=sha(source/'inputs.csv'),trace_sha256=sha(source/'trace.csv'),result_sha256=sha(source/'result.json'),fullPPU_sha256=sha(source/'actual-ppu.argb'),source_files_untouched=True))
        with(folder/'native-host.log').open('x',encoding='utf-8')as log:r=subprocess.run(phase['command'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        preflight();ok,evidence=checks(folder,phase['name']);ok=ok and r.returncode==0
        if phase['name']=='replay'and ok:
            for n in ['inputs.csv','trace.csv','result.json','actual-ppu.argb','actual-ppu-index.csv','route-observation.jsonl','ability-dma-epochs.jsonl','chr-commit.csv','completed-loop-motion.csv']:
                assert sha(folder/n)==sha(a.packet/'discovery'/n),('Independent exact-input observation mismatch',n)
            evidence['fixed_inputs_trace_fullPPU_all_observer_streams_exact']=True
        row=dict(name=phase['name'],passed=bool(ok),exit=r.returncode,retries=0,evidence=evidence)
        put(folder/'native-receipt.json',row);results.append(row)
        put(a.packet/('progress-'+str(len(results))+'.json'),dict(results=results))
        print(json.dumps(dict(name=phase['name'],passed=bool(ok),exit=r.returncode)),flush=True)
        if not ok:break
    proof=dict(passed=len(results)==2 and all(z['passed']for z in results),ROM_sha256=ROM,actual_native_launches=len(results),retries=0,native_worker_released=True,adopted=False,results=results,
               scope='Finite exact641 LuigiEasy natural1-1 discovery and independent fixed-input replay only; source/art/audio/everyitem/Hard/fullcampaign and global lag conclusions remain separate.')
    put(a.packet/'native-proof.json',proof);return 0 if proof['passed']else 1


if __name__=='__main__':raise SystemExit(main())
