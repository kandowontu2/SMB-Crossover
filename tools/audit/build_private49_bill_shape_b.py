"""Root-only private Bill shape build, with original compiler and no optional listings.

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
OUT = ROOT / 'build/verification/root49o2-bill-shape-private-b'
PACKET = ROOT / 'build/verification/agent49o2-bill-jump-shape-proposal-b'
PARENT = ROOT / 'build/checkpoints/roster-audit-v49-provisional-o2'
SOURCE = OUT / 'source'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def workspace_bytes():
    return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())


def run(command, log):
    with log.open('wb') as f:
        completed = subprocess.run(command, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    assert completed.returncode == 0, (completed.returncode, str(log))



def records(path, kind):
    out=[]
    for line in path.read_text().splitlines():
        if line.startswith(kind+'\t'):
            pairs=re.findall(r'(?:^|,)([a-zA-Z_][a-zA-Z0-9_]*)=("[^"]*"|[^,]*)',line.split('\t',1)[1])
            out.append({k:v.strip('"')for k,v in pairs})
    return out

def ram_symbols(path):
    segs={r['id']:r for r in records(path,'seg')}
    scopes={r['id']:r for r in records(path,'scope')}
    def scope(i):
        r=scopes[i];return (scope(r['parent'])+'::'if 'parent'in r else '')+r.get('name','')
    found={}
    for r in records(path,'sym'):
        if r.get('type')!='lab'or r.get('seg')not in segs:continue
        seg=segs[r['seg']];start=int(seg['start'],0)
        if not(0<=start<0x800 or 0x6000<=start<0x8000):continue
        key=(scope(r['scope']),r['name'],seg['name'])
        val=int(r['val'],0)
        if key in found:assert found[key]==val
        found[key]=val
    return found

def labels(path):
    out={}
    for a,n in re.findall(r'^al\s+([0-9a-fA-F]+)\s+\.(\S+)',path.read_text(),re.M):
        out[n]=int(a,16)
    return out

def verify_layout(results):
    checks={}
    for mapper in ('mmc3','mmc5'):
        name='smb-crossover-'+mapper
        before=PARENT/name;after=SOURCE/'build'/name
        oldmap=before.with_suffix('.map').read_text()
        old={m[0]:dict(start=int(m[1],16),end=int(m[2],16),size=int(m[3],16))for m in re.findall(r'^([A-Z_0-9]+)\s+([0-9A-F]{6})\s+([0-9A-F]{6})\s+([0-9A-F]{6})\s+[0-9A-F]+\s*$',oldmap,re.M)}
        new=results[name]['segments']
        for k,r in old.items():
            if 0<=r['start']<0x800 or 0x6000<=r['start']<0x8000:assert new[k]==r,('RAM segment changed',mapper,k)
        olds=ram_symbols(before.with_suffix('.dbg'));news=ram_symbols(after.with_suffix('.dbg'))
        assert olds==news,('All allocated RAM labels/addresses exact',mapper,[(k,olds.get(k),news.get(k))for k in olds.keys()|news.keys()if olds.get(k)!=news.get(k)][:20])
        assert new['LOWCODE']['size']==old['LOWCODE']['size']
        assert new['FIXED']['size']==old['FIXED']['size']+12
        assert new['OAMALIGNED']['size']==old['OAMALIGNED']['size']+16
        assert new['OAMALIGNED']['end']==0xE05D
        assert new['ROSTER']['size']<=old['ROSTER']['size']+399
        dpcm=new['BASS_DPCM']['start'];assert new['BASS_DPCM']==old['BASS_DPCM']
        a=before.with_suffix('.nes').read_bytes();b=after.with_suffix('.nes').read_bytes()
        first=16+63*8192+dpcm-0xE000;last=16+64*8192
        assert a[first:last]==b[first:last],('DPCM/post-DPCM/vectors exact',mapper)
        assert a[16+63*8192:16+63*8192+78]==b[16+63*8192:16+63*8192+78],('Old OAM aligned reader/bridge exact',mapper)
        assert a[16+64*8192:]==b[16+64*8192:],('All CHR exact',mapper)
        oldlbl=labels(before.with_suffix('.lbl'));newlbl=labels(after.with_suffix('.lbl'))
        for symbol,length in [('BoundBoxCtrlData',84),('BlockBuffer_X_Adder',86),('BlockBuffer_Y_Adder',86),('BlockBufferAdderData',11)]:
            def block(rom,symbols):
                v=symbols[symbol];assert 0xC000<=v<=0xFFFF,(symbol,v)
                at=16+(62 if v<0xE000 else 63)*8192+v%8192
                return rom[at:at+length]
            assert block(a,oldlbl)==block(b,newlbl),('Old table contents exact',mapper,symbol)
        checks[mapper]=dict(allocated_RAM_labels=len(olds),RAM_layout_exact=True,CHR_exact=True,DPCM_post_tail_vectors_exact=True,
                            LOWCODE_delta=0,FIXED_delta=12,OAMALIGNED_end=0xE05D,
                            ROSTER_growth=new['ROSTER']['size']-old['ROSTER']['size'],old_body_and_adder_rows_literal=True)
    return checks

def main():
    assert not OUT.exists(), 'Fresh private destination required'
    before = workspace_bytes()
    # Includes all new source/output/archive/logs, plus small host-only agent packets.
    reserve = 52_000_000
    assert before + reserve < 50_000_000_000, (before, reserve)
    freeze_path = PACKET / 'freeze.json'
    assert sha(freeze_path) == '83a9764604987066312dc7094b30c0446f6a5c991782f1b3ae1feb376b4141ad'
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
    run([sys.executable,str(PACKET/'verify.py')],OUT/'proposal-verify.log')
    materialize=[sys.executable,str(PACKET/'materialize.py'),'--source-copy',str(SOURCE),'--freeze-sha256',sha(freeze_path)]
    run(materialize,OUT/'materialize-preflight.log')
    run(materialize+['--apply'],OUT/'materialize-apply.log')
    source_catalog = {name:sha(SOURCE/name) for name in catalog}
    for name in ('src/bill_shape.s',):
        source_catalog[name] = sha(SOURCE/name)
    assert len(source_catalog) == 410
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
    run([sys.executable,str(PACKET/'check_build.py'),'--source-copy',str(SOURCE),'--freeze-sha256',sha(freeze_path)],OUT/'proposal-build-check.log')
    layout_checks = verify_layout(results)
    current=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json'
    for n,h in json.loads(current.read_text())['source_hashes'].items():assert sha(ROOT/n)==h
    for name,h in source_catalog.items():
        assert sha(SOURCE/name) == h, ('Post-build source changed',name)
    for name,h in compiler_catalog.items():
        assert sha(compiler_root/name) == h, ('Compiler changed',name)
    new_archive = OUT/'source-bill-shape-b.zip'
    with zipfile.ZipFile(new_archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(source_catalog):
            z.write(SOURCE/name,name)
    after = workspace_bytes()
    assert after < 50_000_000_000
    report = {'status':'PASS_PRIVATE_BUILD_ONLY_NOT_GAMEPLAY_OR_ABI_VALIDATION',
              'accepted_release':False,'goal_complete':False,
              'script_sha256':sha(Path(__file__)), 'frozen_overlay_sha256':sha(freeze_path),
              'parent_archive_sha256':sha(archive),'source410_hashes':source_catalog,
              'source_archive_sha256':sha(new_archive),'compiler_hashes':compiler_catalog,
              'catalog_build_driver_sha256':catalog['tools/build.py'],
              'private_driver_sha256':sha(driver_path),
              'driver_differences':['Private absolute source ROOT','Absolute original bundled compiler path',
                                    'Omit optional assembler -l listing argument; no existing metadata deletion'],
              'workspace_before':before,'workspace_after':after,'reserved_bytes':reserve,'layout_checks':layout_checks,'builds':results}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(OUT/'report.json'),
                      'workspace_after':after,'outputs':{n:r['outputs']['nes'] for n,r in results.items()}},indent=2))


if __name__ == '__main__':
    main()
