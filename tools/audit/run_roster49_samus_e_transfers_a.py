"""Try the two complete ordinary Samus tapes on actual working E, without retagging D."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-ice-integrated-e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
PARENTS={'mmc3':'root49-current-d-samus-fixed-a-2-v0-mmc3','mmc5':'root49-d-samus-m5-fixed-u-2-v0-mmc5'}
def main():
    marker=H/'route-preparation-ba.json';assert not marker.exists()
    cp=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e/manifest.json'
    c=json.loads(cp.read_text());assert sha(cp)=='65072e56ce25e03e748248cb1efdc51312378e23d099259261bc02d71a76d64b'
    def source_exact():
        for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
        for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
        for b in c['builds']:
            for z in b['artifacts'].values():assert sha(R/z['path'])==sha(R/z['frozen_path'])==z['sha256']
    source_exact();parents={};policy=V/'root49-current-c-transfers-a/identity.lua'
    for mp,tag in PARENTS.items():
        p=R/'build/roster-through-2-2'/tag;m=json.loads((p/'manifest.json').read_text())
        assert m['verified_through_2_2']and m['result']['cleared']and not m['result']['deaths']
        assert sha(p/'inputs.csv')==m['inputs_sha256']
        parents[mp]=dict(path=str(p.relative_to(R)),inputs_sha256=sha(p/'inputs.csv'),manifest_sha256=sha(p/'manifest.json'))
    marker.write_text(json.dumps(dict(status='PREPARED_ACTUAL_E_TWO_MAPPER_FIXED_CANDIDATES',script_sha256=sha(__file__),
      checkpoint_sha256=sha(cp),parents=parents,policy_sha256=sha(policy),
      phase_cap=500000000,final_reserve=50000000,global_cap=70000000000,
      limits='D tapes are candidates only. No state/ROM/register writes, death grants, final movie or all-arsenal claim.'),indent=2)+'\n')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    results=[]
    for mp in ['mmc3','mmc5']:
        paths=[q for q in H.rglob('*')if q.is_file()]
        runs=list((R/'build/roster-through-2-2').glob('root49-e-samus-transfer-a-*'))
        for p in runs:paths.extend(q for q in p.rglob('*')if q.is_file())
        total=workspace_bytes(R);size=sum(q.stat().st_size for q in paths)
        assert total+60000000<70000000000 and size+60000000+50000000<500000000,(total,size)
        b=next(z for z in c['builds']if z['mapper']==mp);rom=R/b['artifacts']['nes']['frozen_path']
        p=R/parents[mp]['path'];assert sha(p/'inputs.csv')==parents[mp]['inputs_sha256']
        args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper',mp,
          '--rom',str(rom),'--tag','root49-e-samus-transfer-a','--policy',str(policy),
          '--replay',str(p/'inputs.csv'),'--frames','36000','--timeout','480','--workspace-cap-gb','70']
        print('START',mp,flush=True)
        log=H/f'native-route-{mp}-ba.log'
        with log.open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
        out=R/f'build/roster-through-2-2/root49-e-samus-transfer-a-2-v0-{mp}'
        m=json.loads((out/'manifest.json').read_text())
        assert m['rom_sha256']==sha(rom)and m['full_frame_audit']and not m['memory_or_register_writes']
        if m['verified_through_2_2']:
            assert q.returncode==0 and sha(out/'inputs.csv')==parents[mp]['inputs_sha256']
            assert json.loads((out/'current-c-identity.json').read_text())==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
        results.append(dict(mapper=mp,exit=q.returncode,verified=m['verified_through_2_2'],
          result=m.get('result'),manifest_sha256=sha(out/'manifest.json'),host_log_sha256=sha(log)))
        source_exact()
        (H/'route-progress-ba.json').write_text(json.dumps(dict(status='RUNNING'if len(results)<2 else'BOTH_ACTUAL_E_TRANSFERS_TERMINAL',results=results),indent=2)+'\n')
        print('END',mp,m['verified_through_2_2'],m.get('result'),flush=True)
    print('DONE',sum(z['verified']for z in results),'of2',flush=True)
if __name__=='__main__':main()
