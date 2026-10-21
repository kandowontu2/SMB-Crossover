"""Test pinned ordinary inputs on frozen D without relabeling older clears."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-d-remaining-routes-ax'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPECS=[(0,'Mario','root49-current-c-mario-fixed-a-0-v0-mmc3'),
 (1,'Mega Man','root49ex-megaman-fixed-1-v0-mmc3'),
 (4,'Link','lsr-v34-link-fixed-full-audit-a-4-v0-mmc3'),
 (5,'Simon','agent-lsr-victory-repair-c-t-fixed-a-5-v0-mmc3'),
 (6,'Pit','specialist-gq-pit-fixed-a-6-v0-mmc3'),
 (7,'Rygar','specialist-gq-rygar-fixed-a-7-v0-mmc3'),
 (8,'Luigi','root49-current-c-luigi-fixed-a-8-v0-mmc3'),
 (9,'Bass','specialist-gq-bass-fixed-a-9-v0-mmc3'),
 (10,'Ryu','agent-lsr-o-ryu-fixed-s-xstep-10-v0-mmc3')]
def main():
    H.mkdir(exist_ok=True);assert not(H/'preparation.json').exists(),'Never restart a live or completed batch under the same tag'
    cp=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json';c=json.loads(cp.read_text())
    assert sha(cp)=='1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88'
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    b=next(x for x in c['builds']if x['mapper']=='mmc3');rom=R/b['artifacts']['nes']['frozen_path']
    assert sha(rom)==b['artifacts']['nes']['sha256']
    policy=V/'root49-current-c-transfers-a/identity.lua';assert policy.exists()
    parents=[]
    for ident,name,tag in SPECS:
        p=R/'build/roster-through-2-2'/tag;m=json.loads((p/'manifest.json').read_text())
        assert m['verified_through_2_2']and m['config']['character']==ident
        assert sha(p/'inputs.csv')==m['inputs_sha256']
        parents.append(dict(character=ident,name=name,path=str(p.relative_to(R)),manifest_sha256=sha(p/'manifest.json'),inputs_sha256=sha(p/'inputs.csv')))
    (H/'preparation.json').write_text(json.dumps(dict(status='PREPARED_INDEPENDENT_FROZEN_D_CONTROLLER_TRANSFERS',
      script_sha256=sha(__file__),checkpoint_sha256=sha(cp),ROM_sha256=sha(rom),identity_policy_sha256=sha(policy),parents=parents,
      phase_cap_bytes=1000000000,final_reserve_bytes=100000000,global_cap_bytes=70000000000,
      emulated_writes=False,state_loads=False,recording=False,
      limits='Each older tape is only a candidate. Actual current image/menu identity/full-audit endpoint required. Scrooge/Sophia/Samus/Bill/Lance have separate owned investigations. No source or final media claim.'),indent=2)+'\n')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    results=[]
    for spec,parent in zip(SPECS,parents):
        ident,name,tag=spec;p=R/parent['path'];assert sha(p/'inputs.csv')==parent['inputs_sha256']
        assert sha(rom)==b['artifacts']['nes']['sha256']
        owned=list(H.rglob('*'))
        for d in (R/'build/roster-through-2-2').glob('root49-d-roster-ax-*'):owned.extend(d.rglob('*'))
        size=sum(x.stat().st_size for x in owned if x.is_file());total=workspace_bytes(R)
        assert size+60000000<900000000 and total+60000000<70000000000,(size,total)
        args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(ident),'--mapper','mmc3','--rom',str(rom),
          '--tag','root49-d-roster-ax','--policy',str(policy),'--replay',str(p/'inputs.csv'),'--frames','36000','--timeout','480','--workspace-cap-gb','70']
        print('START',name,flush=True)
        with(H/f'native-{ident}.log').open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
        out=R/f'build/roster-through-2-2/root49-d-roster-ax-{ident}-v0-mmc3'
        m=json.loads((out/'manifest.json').read_text())
        result=dict(character=ident,name=name,returncode=q.returncode,verified=bool(m.get('verified_through_2_2')),
          result=m.get('result'),manifest_sha256=sha(out/'manifest.json'),input_sha256=sha(out/'inputs.csv'))
        assert m['rom_sha256']==sha(rom)and m['full_frame_audit']and not m['memory_or_register_writes']
        if result['verified']:
            assert q.returncode==0 and result['input_sha256']==parent['inputs_sha256']
            i=json.loads((out/'current-c-identity.json').read_text());assert i['character']==ident and i['behavior']==0 and i['outlinesOff']==1
        results.append(result)
        (H/'progress.json').write_text(json.dumps(dict(status='RUNNING'if len(results)<len(SPECS)else'ALL_CANDIDATES_TERMINAL',results=results,complete_goal=False),indent=2)+'\n')
        print('END',name,result['verified'],result['result'],flush=True)
    print('DONE',sum(x['verified']for x in results),'of',len(results),flush=True)
if __name__=='__main__':main()
