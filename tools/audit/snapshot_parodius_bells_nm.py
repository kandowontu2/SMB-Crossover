"""Freeze verified private Bell work and reproduce its ROM from saved sources."""
from pathlib import Path
import datetime,gzip,hashlib,importlib.util,json,shutil,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/parodius-bells-nm'
FINAL=ROOT/'build/checkpoints/parodius-bells-nm'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    assert not FINAL.exists(),'Preserve completed checkpoints'
    rom=QA/'smb-crossover-mmc5-pickups-v3.nes';digest=sha(rom)
    parent=read(ROOT/'build/checkpoints/parodius-integration-nl/manifest.json')
    public=read(ROOT/'build/checkpoints/mmc3-menu-nk/manifest.json')
    evidence={};prelude=(ROOT/'tests/parodius-integration.lua').read_text().split('local pulses=')[0]
    suites={'components':('final-components-v3','components.lua',(ROOT/'tests/parodius-integration.lua').read_text(),'proof.json'),
            'bells':('final-bells-v3','bells.lua',prelude+(ROOT/'tests/parodius-bells.lua').read_text(),'bell-proof.json'),
            'pickups':('physical-pickups-v6','pickups.lua',prelude+(ROOT/'tests/parodius-pickups.lua').read_text(),'pickup-proof.json')}
    validator=module('snapshot_pickup_validator',ROOT/'tools/audit/check_parodius_pickups.py')
    for key,(folder,script_name,body,proof_name)in suites.items():
        result=read(QA/folder/'results.json')
        assert result['ROM_sha256']==digest and set(result['results'])=={'1','2','3'}
        assert all(row['exit']==0 for row in result['results'].values())
        evidence[key]=dict(summary=result,details={})
        for variant in (1,2,3):
            path=QA/folder/str(variant);script=path/script_name;f=path/'build/verification'
            assert script.read_text()==f'PN_VARIANT={variant}\n'+body
            if key!='components':assert result['results'][str(variant)]['script_sha256']==sha(script)
            proof=read(f/proof_name)
            if key=='components':assert proof['passed']and proof['missingPoses']==0 and proof['rendererBudgetChecks']>100
            elif key=='bells':assert proof['passed']and proof['redShots']==3 and proof['paletteReads']>=64 and proof['missingPoses']==0
            else:
                assert proof['resetChecks']>0 and proof['hitCycles']==16
                assert validator.pixels(f,proof,variant)==15
            evidence[key]['details'][str(variant)]=dict(proof=proof,script_sha256=sha(script))
    evidence['pickup_validator_sha256']=sha(ROOT/'tools/audit/check_parodius_pickups.py')
    entries={}
    for group in range(1,4):
        subset=read(QA/f'final-entry-group{group}/results.json')
        assert subset['rom_sha256']==digest and len(subset['results'])==12
        assert not set(entries)&set(subset['results'])
        entries.update(subset['results'])
    assert len(entries)==36 and all(row['exit']==0 for row in entries.values())
    evidence['cold_entries']=entries;evidence['routes']={}
    for name in ('octopus','twinbee','pentarou'):
        route=QA/f'replay-{name}-v3';proof=read(route/'manifest.json')
        assert proof['ROM_sha256']==digest and proof['fixed_replay'] and proof['exit']==0
        assert proof['result']['cleared']and proof['result']['deaths']==0 and proof['result']['failure']is None
        assert proof['inputs_sha256']==sha(route/'inputs.csv')
        evidence['routes'][name]=proof
    oracle=read(QA/'final-differential/results.json')
    assert set(oracle['mappers'])=={'mmc3','mmc5'}
    for row in oracle['mappers'].values():assert row['passed']and len(row['cases'])==272 and row['instructions']==440792
    evidence['native_bell_oracle']=oracle
    art=read(QA/'packed-art-proof.json');assert art['native_pose_pixels_equal']and len(art['cases'])==664
    assert art['CHR_sha256']==sha(ROOT/'chr/characters/parodius.chr')
    evidence['packed_art']=art
    evidence['original_renderer']=read(ROOT/'build/verification/parodius-native-ni/art-oracle.json')
    assert evidence['original_renderer']['palette_cases']==1796
    names=set(parent['source_files'])
    for folder in ('src','chr','audio','inc','ports/mmc3-oversized','reference/parodius-nes'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/folder).rglob('*')
                     if p.is_file()and p.suffix not in('.o','.pyc','.pdf'))
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tools').rglob('*parodius*.py'))
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tests').glob('parodius*.lua'))
    names.update(['docs/qa/parodius-bells-2026-10-23.md','tools/reference/observe_parodius_pickups.lua'])
    hashes={name:sha(ROOT/name)for name in sorted(names)}
    sys.path.insert(0,str(ROOT/'tools'));from playthroughs.roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+3*sum((ROOT/name).stat().st_size for name in names)<30_000_000_000
    stage=QA/'snapshot-v3';assert not stage.exists();stage.mkdir()
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
        for name in sorted(names):archive.write(ROOT/name,name)
    source=stage/'source'
    with zipfile.ZipFile(stage/'source.zip')as archive:archive.extractall(source)
    output=stage/'roundtrip.nes'
    result=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),
                           '--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),
                           '--output',str(output)],cwd=source,capture_output=True,text=True)
    (stage/'roundtrip.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and sha(output)==digest,'Saved-source rebuild differs'
    assert all(sha(ROOT/name)==value for name,value in hashes.items()),'Source changed during snapshot'
    for mapper,value in public['ROMs'].items():assert sha(ROOT/'build'/('smb-crossover-'+mapper+'.nes'))==value
    FINAL.mkdir();shutil.copy2(stage/'source.zip',FINAL/'source.zip')
    for suffix in('.nes','.lbl','.map','.dbg'):
        original=rom.with_suffix(suffix)
        if suffix=='.dbg':(FINAL/'candidate.dbg.gz').write_bytes(gzip.compress(original.read_bytes(),mtime=0))
        else:shutil.copy2(original,FINAL/('candidate'+suffix))
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status='PRIVATE_PARODIUS_BELL_PICKUP_ART_AND_EASY_1_1_PROOF_NOT_RELEASED',
                identities=36,ROM_sha256=digest,source_zip_sha256=sha(FINAL/'source.zip'),source_files=hashes,
                source_bundle_rebuild_exact=True,evidence=evidence,
                limitations=['Source audio/music, native palette overrides, shield geometry, hero-change and exact Bell edge/disappearance remain open.',
                             'SMB drop policy and every-equipment physical acquisition need review.',
                             'Production MMC3 Parodius integration and Roll remain unfinished.',
                             'The three surface Easy routes and seeded arenas do not prove the full final character/powerup matrix.',
                             'Colors are explicitly quantized; pickup sprites fit the isolated scanline limit, while the full world still shares hardware sprite limits.',
                             'Published33-identity MMC3 and MMC5 ROMs are unchanged.'])
    (FINAL/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    assert workspace_bytes(ROOT)<30_000_000_000
    print(json.dumps(dict(checkpoint=str(FINAL),ROM_sha256=digest,source_bundle_rebuild_exact=True,published=False)))

if __name__=='__main__':main()
