"""Current CI/CJ Water timings, with real world actors and journaled equipment."""
from pathlib import Path
import collections, concurrent.futures, hashlib, importlib.util, json, statistics, subprocess, sys

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
O=V/'water-visible-profile-cm'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def main():
    assert not O.exists();O.mkdir()
    sys.path.insert(0,str(R/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used=workspace_bytes(R);assert used+250_000_000<100_000_000_000
    a=load('water_cm_image',V/'agent49g-samus-crouch-fix-proposal-b/image.py')
    template=load('water_cm_template',R/'tools/audit/profile_roster49_water_live_hb.py')
    profiler=V/'root49-water-live-profile-hb/profile.lua'
    noop=V/'root49-water-live-profile-hb/noop.lua'
    observer=V/'agent49-water-visible-j-a/caller_k.lua'
    previous=R/'build/checkpoints/firebar-budget-ci'
    cp=json.loads((previous/'manifest.json').read_text())
    jobs=[]
    for revision in ('CI','CJ'):
        for mapper in ('mmc3','mmc5'):
            rom=(previous/'build'if revision=='CI'else R/'build')/f'smb-crossover-{mapper}.nes'
            im=a.Image(rom)
            if revision=='CI':assert sha(rom)==cp['ROMs'][mapper]
            specs={'GameLoop':('GameLoop',None),'SpecialWeapons':('SpecialWeapons',None),
                'Orbit':('Orbit','SpecialWeapons'),'WaterCollisionCandidate':('WaterCollisionCandidate','SpecialWeapons'),
                'Bridge':('Bridge','SpecialWeapons'),'EnsureWaterScale':('EnsureWaterScale','SpecialWeapons'),
                'SpecialDrawShots':('SpecialDrawShots',None),'SpecialDrawWaterShot':('SpecialDrawWaterShot',None),
                'WeaponEnemies':('WaterShieldEnemies',None)if revision=='CJ'else('Enemies','MegaManWeapons'),
                'WeaponBlocks':('Blocks','MegaManWeapons'),'AudioUpdate':('AudioUpdate',None)}
            hooks={n:im.hook(label,scope=scope)for n,(label,scope)in specs.items()}
            hooks.update(NMI=im.hook('NonMaskableInterrupt'),IRQ=im.hook('IrqScrollSplit'),
                NMI_END=im.hook('NonMaskableInterrupt',delta='last'),IRQ_END=im.hook('IrqScrollSplit',delta='last'))
            ret=im.hook('FarCallCommon',delta=im.ram['FarcallJmpTarget_SMC']+3-im.ram['FarCallCommon'])
            for char in (1,9):
                folder=O/f'{revision}-{mapper}-{char}';folder.mkdir()
                profile=dict(hooks=hooks,ram=im.ram,ram_return=ret,start_frame=550,stop_frame=1450,base_policy=noop.as_posix())
                text=template.FIXTURE
                for token,value in {'__CHARACTER_ID__':str(char),'__BOOTSTRAP_PATH__':a.lua((R/'tests/menu-bootstrap.lua').as_posix()),
                    '__PROFILE_CONFIG__':a.lua(profile),'__PROFILER_PATH__':a.lua(profiler.as_posix())}.items():
                    assert text.count(token)==1;text=text.replace(token,value)
                cfg=dict(out=(folder/'native').as_posix()+'/',character=char,observeSelected=7,
                    hooks={'FullSpecialWeapons':im.hook('SpecialWeapons'),'NMI':im.hook('NonMaskableInterrupt'),
                        'NMIEnd':im.hook('NonMaskableInterrupt',delta='last'),'IRQ':im.hook('IrqScrollSplit'),
                        'IRQEnd':im.hook('IrqScrollSplit',delta='last')})
                text=text.replace('ORDINARY_PROFILE=','CFG='+a.lua(cfg)+'\ndofile('+a.lua(observer.as_posix())+')\nORDINARY_PROFILE=')
                fixture=folder/'component.lua';fixture.write_text(text,encoding='utf-8')
                command=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder/'native'),str(fixture),str(rom),'--timeout','180']
                binding=dict(ROM=im.metadata(),revision=revision,character=char,profile=profile,
                    fixture_sha256=sha(fixture),profiler_sha256=sha(profiler),observer_sha256=sha(observer),command=command)
                (folder/'binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf-8')
                jobs.append((revision,mapper,char,folder,command))
    prep=dict(workspace_before=used,workspace_cap=100_000_000_000,phase_reservation=250_000_000,
        parent_checkpoint_sha256=sha(previous/'manifest.json'),script_sha256=sha(__file__),
        scope='Authored equipment at550 and explicit Hard-mode bootstrap at60, all writes journaled; original populated1-1 actors, terrain and player positions. Real input summons shield, walks until native eligible enemy and8 visible balls, expands withB. Not natural acquisition or route completion. Timings subtract attained ISR cycles; nested scopes are not additive.')
    (O/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
    def run(job):
        rev,mapper,char,folder,command=job
        with(folder/'host.log').open('wb')as log:proc=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
        records=[json.loads(z)for z in(folder/'native/ordinary-profile.jsonl').read_text().splitlines()]
        bins=collections.defaultdict(list)
        for z in records:
            assert z['exclusive_cycles']>=0
            key='/'.join((z['name'],'expand'if z['expand']else'orbit','populated'if z['enemies']else'empty','full8'if z['visible']==8 else'partial'))
            bins[key].append(z)
        scopes={k:dict(samples=len(v),mean=statistics.mean(z['exclusive_cycles']for z in v),
            median=statistics.median(z['exclusive_cycles']for z in v),maximum=max(z['exclusive_cycles']for z in v),
            native_elapsed_max=max(z['cycles']for z in v),attained_IRQ=sum(z['irq']for z in v),attained_NMI=sum(z['nmi']for z in v),
            lag_increments=sum(z['lag']for z in v),physical_frame_spills=sum(z['frame_delta']for z in v))for k,v in bins.items()}
        result=dict(revision=rev,mapper=mapper,character=char,exit=proc.returncode,scopes=scopes,
            coverage={phase:len(bins.get(f'SpecialWeapons/{phase}/populated/full8',[]))for phase in('orbit','expand')},
            raw_sha256=sha(folder/'native/ordinary-profile.jsonl'),binding_sha256=sha(folder/'binding.json'))
        (folder/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(rev,mapper,char,proc.returncode,result['coverage'],flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(run,jobs))
    report=dict(passed=all(z['exit']==0 and all(z['coverage'].values())for z in results),groups=results,goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert report['passed'],'Inspect native coverage and failures before admitting this change'

if __name__=='__main__':main()
