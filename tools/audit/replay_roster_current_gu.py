"""Transfer the twelve untested legacy Easy routes to immutable current GO ROM."""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/roster-current-gu'
CP=R/'build/checkpoints/weapons-source-go';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir()
    cp=json.loads((CP/'manifest.json').read_text());rom=CP/'build/smb-crossover-mmc3.nes'
    assert sha(rom)==cp['ROMs']['mmc3']
    tasks=[]
    for char in range(13):
        if char in(7,9):continue  # Actual current proofs/negatives already exist.
        for variant in ((0,1)if char==3 else(0,)):
            old=R/f'build/roster-through-2-2/claude-final-video-{char}-v{variant}-mmc3'
            manifest=json.loads((old/'manifest.json').read_text());assert manifest['verified_through_2_2']
            assert sha(old/'inputs.csv')==manifest['inputs_sha256']
            tasks.append(dict(character=char,variant=variant,old_manifest_sha256=sha(old/'manifest.json'),inputs_sha256=sha(old/'inputs.csv'),old=old,frames=manifest['config']['limit']))
    assert len(tasks)==12
    def run(t):
        tag='root-roster-go-gu';name=f'{t["character"]}-v{t["variant"]}-mmc3'
        command=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(t['character']),'--variant',str(t['variant']),'--mapper','mmc3','--rom',str(rom),'--tag',tag,'--replay',str(t['old']/'inputs.csv'),'--frames',str(t['frames']),'--timeout','360','--workspace-cap-gb','100']
        with(O/(name+'-host.log')).open('wb')as f:z=subprocess.run(command,cwd=R,stdout=f,stderr=subprocess.STDOUT)
        out=R/'build/roster-through-2-2'/f'{tag}-{name}'
        path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{}
        result=dict(character=t['character'],variant=t['variant'],exit=z.returncode,ROM_sha256=sha(rom),inputs_sha256=t['inputs_sha256'],old_manifest_sha256=t['old_manifest_sha256'],manifest_sha256=sha(path)if path.exists()else None,verified_through_2_2=m.get('verified_through_2_2',False),result=m.get('result'),output=str(out.relative_to(R)))
        (O/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        print('ROSTER',name,'PASS'if result['verified_through_2_2']else'RETAINED_FAILURE',result['result'],flush=True)
        return result
    (O/'preparation.json').write_text(json.dumps(dict(checkpoint_sha256=sha(CP/'manifest.json'),ROM_sha256=sha(rom),tasks=[{k:str(v)if isinstance(v,Path)else v for k,v in t.items()}for t in tasks],scope='Fresh coldboot ordinary fixed controller replay, Easy/MMC3 only. No savestate loads or memory writes, no final A/V capture or full weapon/Hard certification.',goal_complete=False),indent=2)+'\n')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(run,tasks))
    (O/'summary.json').write_text(json.dumps(dict(status='TERMINAL_CURRENT_GO_ROUTE_TRANSFER_MATRIX',cases=results,passed=sum(z['verified_through_2_2']for z in results),failed=sum(not z['verified_through_2_2']for z in results),goal_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
