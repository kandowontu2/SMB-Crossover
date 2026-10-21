"""Root-only private head build, with original compiler and no optional listings.

Leaves the catalog's normal build.py and all shared runtime files unchanged.
All existing evidence is retained. This is build evidence, not gameplay proof.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root49o2-head-private-build-e'
PACKET = ROOT / 'build/verification/ryu49o2-head-implementation-e'
PARENT = ROOT / 'build/checkpoints/roster-audit-v49-provisional-o2'
SOURCE = OUT / 'source'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def workspace_bytes():
    return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())


def run(command, log):
    with log.open('wb') as f:
        completed = subprocess.run(command, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    assert completed.returncode == 0, (completed.returncode, str(log))


def main():
    assert not OUT.exists(), 'Fresh private destination required'
    before = workspace_bytes()
    # Includes all new source/output/archive/logs, plus small host-only agent packets.
    reserve = 52_000_000
    assert before + reserve < 50_000_000_000, (before, reserve)
    freeze_path = PACKET / 'freeze.json'
    assert sha(freeze_path) == 'd3c9008771b08073e10a700f62dc12b1bacfb565e37571a74dd8ce45e15cc735'
    freeze = json.loads(freeze_path.read_text())
    for name, info in freeze['files'].items():
        assert sha(PACKET/name) == info['sha256'], name
        assert (PACKET/name).stat().st_size == info['bytes'], name
    archive = PARENT/'source-v49.zip'
    assert sha(archive) == '8c9d8b841f6a4b4680ad4675afdc2336a6bb6801141e2cb6b45d50fe7209db53'
    manifest = json.loads((PARENT/'manifest.json').read_text())
    catalog = manifest['source_hashes']
    assert len(catalog) == 409
    compiler_root = ROOT/'tools/Windows/cc65'
    compiler_catalog = {str(p.relative_to(compiler_root)).replace('\\','/'):sha(p)
                        for p in compiler_root.rglob('*') if p.is_file()}
    OUT.mkdir()
    SOURCE.mkdir()
    with zipfile.ZipFile(archive) as z:
        assert {i.filename for i in z.infolist() if not i.is_dir()} == set(catalog) | {'archived-file-hashes.json'}
        assert json.loads(z.read('archived-file-hashes.json')) == catalog
        for i in z.infolist():
            assert (SOURCE/i.filename).resolve().is_relative_to(SOURCE.resolve())
        z.extractall(SOURCE)
    for name,h in catalog.items():
        assert sha(SOURCE/name) == h, name
    run([sys.executable,str(PACKET/'materialize.py'),'--destination',str(SOURCE)],OUT/'materialize.log')
    source_catalog = {name:sha(SOURCE/name) for name in catalog}
    for name in ('src/guest_foot_side.s','src/ryu_source_head.s'):
        source_catalog[name] = sha(SOURCE/name)
    assert len(source_catalog) == 411
    original_driver = (SOURCE/'tools/build.py').read_text()
    assert sha(SOURCE/'tools/build.py') == catalog['tools/build.py']
    driver = original_driver.replace('ROOT = Path(__file__).resolve().parents[1]',
                                    'ROOT = Path('+repr(str(SOURCE))+')')
    driver = driver.replace("bundled = ROOT / 'tools/Windows/cc65/bin/cl65.exe'",
                            'bundled = Path('+repr(str(compiler_root/'bin/cl65.exe'))+')')
    old_listing = "'-l', f'build/{name}.lst', '-m', f'build/{name}.map',"
    assert driver.count(old_listing) == 1
    driver = driver.replace(old_listing,"'-m', f'build/{name}.map',")
    driver_path = OUT/'compact-build-driver.py'
    driver_path.write_text(driver,encoding='utf8')
    results = {}
    for mapper,baseline in [('mmc3',False),('mmc5',False),('mmc3',True)]:
        name = 'smb-crossover-'+mapper+('-baseline' if baseline else '')
        command = [sys.executable,str(driver_path),'--mapper',mapper]+(['--baseline'] if baseline else [])
        run(command,OUT/(name+'.log'))
        outputs = {ext:{'path':str((SOURCE/'build'/name).with_suffix('.'+ext).relative_to(ROOT)).replace('\\','/'),
                        'sha256':sha((SOURCE/'build'/name).with_suffix('.'+ext)),
                        'bytes':(SOURCE/'build'/name).with_suffix('.'+ext).stat().st_size}
                   for ext in ('nes','dbg','lbl','map')}
        assert not (SOURCE/'build'/name).with_suffix('.lst').exists()
        if baseline:
            assert outputs['nes']['sha256'] == '0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'
        text = (SOURCE/'build'/name).with_suffix('.map').read_text()
        segments = {m[0]:{'start':int(m[1],16),'end':int(m[2],16),'size':int(m[3],16)}
                    for m in re.findall(r'^([A-Z_0-9]+)\s+([0-9A-F]{6})\s+([0-9A-F]{6})\s+([0-9A-F]{6})\s+[0-9A-F]+\s*$',text,re.M)}
        results[name] = {'outputs':outputs,'segments':segments}
    for name,h in source_catalog.items():
        assert sha(SOURCE/name) == h, ('Post-build source changed',name)
    for name,h in compiler_catalog.items():
        assert sha(compiler_root/name) == h, ('Compiler changed',name)
    new_archive = OUT/'source-head-e.zip'
    with zipfile.ZipFile(new_archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(source_catalog):
            z.write(SOURCE/name,name)
    after = workspace_bytes()
    assert after < 50_000_000_000
    report = {'status':'PASS_PRIVATE_BUILD_ONLY_NOT_GAMEPLAY_OR_ABI_VALIDATION',
              'accepted_release':False,'goal_complete':False,
              'script_sha256':sha(Path(__file__)), 'frozen_overlay_sha256':sha(freeze_path),
              'parent_archive_sha256':sha(archive),'source411_hashes':source_catalog,
              'source_archive_sha256':sha(new_archive),'compiler_hashes':compiler_catalog,
              'catalog_build_driver_sha256':catalog['tools/build.py'],
              'private_driver_sha256':sha(driver_path),
              'driver_differences':['Private absolute source ROOT','Absolute original bundled compiler path',
                                    'Omit optional assembler -l listing argument; no existing metadata deletion'],
              'workspace_before':before,'workspace_after':after,'reserved_bytes':reserve,'builds':results}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(OUT/'report.json'),
                      'workspace_after':after,'outputs':{n:r['outputs']['nes'] for n,r in results.items()}},indent=2))


if __name__ == '__main__':
    main()
