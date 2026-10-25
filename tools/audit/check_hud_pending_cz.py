"""Native current-parent negative and both-map private busy-guard checks."""
from pathlib import Path
import concurrent.futures,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'hud-pending-native-db'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not O.exists();O.mkdir()
    p=V/'agent49g-samus-crouch-fix-proposal-b/image.py';s=importlib.util.spec_from_file_location('hud_cz_image',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
    jobs=[]
    for version in('CW','CY'):
        for mapper in('mmc3','mmc5'):
            folder=O/f'{version}-{mapper}';folder.mkdir()
            rom=(R/'build'if version=='CW'else V/'hud-current-cy/source/build')/f'smb-crossover-{mapper}.nes';im=a.Image(rom)
            config=dict(entry=im.hook('BlockObjMT_Updater'),write=im.hook('WriteBlockMetatile'),pending=im.ram.get('HudStatusPending',0x7ffd),bootstrap=(R/'tests/menu-bootstrap.lua').as_posix())
            fixture=folder/'component.lua';fixture.write_text('HUD_CONSUMER_CONFIG='+a.lua(config)+'\ndofile('+a.lua((R/'tools/audit/hud_pending_consumer_cz.lua').as_posix())+')\n',encoding='utf-8')
            (folder/'binding.json').write_text(json.dumps(dict(ROM=im.metadata(),config=config,fixture_sha256=sha(fixture),observer_sha256=sha(R/'tools/audit/hud_pending_consumer_cz.lua')),indent=2)+'\n',encoding='utf-8')
            command=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder/'native'),str(fixture),str(rom),'--timeout','90']
            jobs.append((version,mapper,folder,command))
    def run(job):
        version,mapper,folder,command=job
        with(folder/'host.log').open('wb')as log:p=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
        text=(folder/'host.log').read_text(encoding='utf-8')
        expected=p.returncode==0 if version=='CY'else p.returncode!=0 and 'Pending numeric HUD work must prevent native terrain replacement'in text
        print(version,mapper,p.returncode,expected,flush=True)
        return dict(version=version,mapper=mapper,exit=p.returncode,expected_result=expected,log_sha256=sha(folder/'host.log'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(run,jobs))
    report=dict(passed=all(z['expected_result']for z in results),results=results,scope='Authored native consumer arenas; old parent does not have deferred producers, so its failure is only a counterfactual pending-state control, not an installed-CW defect.',goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert report['passed']
if __name__=='__main__':main()
