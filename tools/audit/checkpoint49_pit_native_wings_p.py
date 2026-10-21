"""Checkpoint and verify the native Pit wing/body pointer correction."""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'build/checkpoints/roster-audit-v49-provisional-o2'
OUT=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
QA=ROOT/'build/verification/root49-pit-native-wings-p'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists() and not QA.exists()
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+100_000_000<50_000_000_000
    sys.path.insert(0,str(ROOT/'tools'));import run_mesen
    helper=ROOT/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('wing_image',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    before=json.loads((PARENT/'manifest.json').read_text())['source_hashes']
    after={n:sha(ROOT/n) for n in before}
    changed=[n for n in before if before[n]!=after[n]]
    assert set(changed)=={'src/pit_metasprites.inc','tools/reference/build_expanded_assets.py'},changed
    OUT.mkdir();QA.mkdir()
    compiled=[]
    poses={'FLAP1':(78,4),'FLAP2':(79,4),'FLAPSHOT1':(80,22),
           'FLAPSHOT2':(81,22),'FLAPUP1':(82,23),'FLAPUP2':(83,23)}
    for mapper in ('mmc3','mmc5'):
        name=f'smb-crossover-{mapper}'
        old=module.Image(PARENT/(name+'.nes'));new=module.Image(ROOT/'build'/(name+'.nes'))
        allowed=set();checks=[]
        for suffix in ('LeftLo','LeftHi','RightLo','RightHi','Banks'):
            s=new.sym('XgPIT'+suffix);seg=new.segs[s['seg']]
            off=seg['ooffs']+s['val']-seg['start']
            assert s['val']==old.sym('XgPIT'+suffix)['val']
            table=new.raw[off:off+252]
            for power in range(3):
                for pose,(dest,source) in poses.items():
                    i=power*84+dest;j=power*84+source
                    assert table[i]==table[j],(mapper,suffix,power,pose)
                    allowed.add(off+i)
                    checks.append({'table':suffix,'power':power,'pose':pose,'native_pose_index':source,
                                   'value':table[i],'ROM_offset':off+i})
        diff=[i for i,(a,b) in enumerate(zip(old.raw,new.raw))if a!=b]
        assert diff and set(diff)<=allowed
        assert old.ram==new.ram
        # Every other ROM byte, including CHR and all physics/code, is literal O2.
        for ext in ('nes','dbg','lbl','map','lst'):
            shutil.copyfile(ROOT/'build'/(name+'.'+ext),OUT/(name+'.'+ext))
        compiled.append({'mapper':mapper,'changed_ROM_bytes':len(diff),'allowed_table_cells':len(allowed),
                         'all_other_ROM_bytes_literal_O2':True,'all_RAM_symbols_exact':True,
                         'target':module.Image(OUT/(name+'.nes')).metadata(),'checks':checks})
    with zipfile.ZipFile(OUT/'source-v49-pit-wings-p.zip','x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(after):z.write(ROOT/n,n)
        z.writestr('archived-file-hashes.json',json.dumps(after,indent=2)+'\n')
    manifest={'status':'building-targeted-wing-validation','accepted_release':False,'goal_complete':False,
              'parent':'roster-audit-v49-provisional-o2','source_hashes':after,'compiler_source_files':409,
              'source_changes':changed,'source_archive_sha256':sha(OUT/'source-v49-pit-wings-p.zip'),
              'script_sha256':sha(Path(__file__)),'compiled':compiled,'tests':[]}
    def save():(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    save()
    names=('pit-flight','pit-attacks','pit-controls','pit-fresh-fire','pit-systems',
           'pit-lives-screen','pit-powerup-animation','pit-environment','pit-crouch-clearance',
           'player-outlines-render','character-select','guest-loading-vram','empty-metasprites')
    pinned={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in (ROOT/'tests').rglob('*')if p.is_file()}
    pinned['tools/run_mesen.py']=sha(ROOT/'tools/run_mesen.py')
    for mapper in ('mmc3','mmc5'):
        for name in names:
            folder=QA/(mapper+'-'+name);folder.mkdir()
            script=folder/('pit-wings-p-'+mapper+'-'+name+'.lua')
            s='OUTPUT='+module.lua(folder.as_posix()+'/')+'\nTEST_DIR='+module.lua((ROOT/'tests').as_posix()+'/')+'\n'
            if name!='character-select':s+='dofile(TEST_DIR.."menu-bootstrap.lua")\n'
            s+='dofile(TEST_DIR..'+module.lua(name+'.lua')+')\n'
            script.write_text(s)
            code=run_mesen.run(script,OUT/f'smb-crossover-{mapper}.nes',timeout=90,
                               emulator_options=['--nes.ramPowerOnState=AllZeros',
                                                 '--nes.randomizeCpuPpuAlignment=false',
                                                 '--nes.randomizeMapperPowerOnState=false'])
            log=ROOT/'build/verification'/f'smb-crossover-{mapper}-{script.stem}.log'
            manifest['tests'].append({'mapper':mapper,'test':name,'native_exit':code,
                                      'log_sha256':sha(log),'script_sha256':sha(script)})
            save();assert code==0,(mapper,name,log)
    assert all(sha(ROOT/n)==h for n,h in after.items())
    assert all(sha(ROOT/n)==h for n,h in pinned.items())
    for row in compiled:
        for key in ('rom','debug','labels','map'):
            r=row['target'][key];assert sha(Path(r['path']))==r['sha256']
    manifest.update(status='PASS_native_Pit_wings_tables_and_26_targeted_native_cases_full_goal_incomplete',
                    fixture_hashes=pinned,workspace_bytes=workspace_bytes(ROOT),
                    qualification='No new wing drawing. Both flight phases reuse the same original native wing/body pose; flight controls/fuel unchanged. Full roster/final video goal remains incomplete.')
    save()
    print(json.dumps({'status':manifest['status'],'manifest':str(OUT/'manifest.json'),
                      'sha256':sha(OUT/'manifest.json'),'tests':len(manifest['tests']),
                      'ROMs':{r['mapper']:r['target']['rom']['sha256'] for r in compiled}},indent=2))


if __name__=='__main__':main()
