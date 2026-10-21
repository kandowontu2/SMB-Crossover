"""Fresh private current-P build with the exact two tested Sophia replacements."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-sophia-integrated-private-r'
SOURCE=OUT/'source'
PACKET=ROOT/'build/verification/agent49o2-sophia-promotion-current-p-q'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(PACKET/'frozen.json')=='56ce1cd46220e7d252e95b7fb03d63cc9ac41ea1853cd5afc83b26437ce2b29a'
    for n,pin in json.loads((PACKET/'frozen.json').read_text())['files'].items():
        assert sha(PACKET/n)==pin['sha256']and (PACKET/n).stat().st_size==pin['bytes']
    recipe=json.loads((PACKET/'recipe.json').read_text())
    for p in recipe['dependencies']:assert sha(Path(p['path']))==p['sha256']
    manifest=Path(recipe['base_manifest']['path']);assert sha(manifest)==recipe['base_manifest']['sha256']
    oldcat=json.loads(manifest.read_text())['source_hashes'];expected=recipe['expected_source_members']
    assert len(oldcat)==len(expected)==409 and all(sha(ROOT/n)==h for n,h in oldcat.items())
    compiler=ROOT/'tools/Windows/cc65'
    compiler_pins={str(p.relative_to(compiler)).replace('\\','/'):sha(p)for p in compiler.rglob('*')if p.is_file()}
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+100_000_000<50_000_000_000
    OUT.mkdir();SOURCE.mkdir()
    report=dict(status='RUNNING_PRIVATE_P_SOPHIA_BUILD',accepted_release=False,goal_complete=False,
                script_sha256=sha(Path(__file__)),packet_sha256=sha(PACKET/'frozen.json'),workspace_before=used,
                reserved_bytes=100_000_000,source409_hashes=expected,builds=[],compiler_hashes=compiler_pins)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    archive=Path(recipe['base_source_archive']['path']);assert sha(archive)==recipe['base_source_archive']['sha256']
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(oldcat)|{'archived-file-hashes.json'}
        assert json.loads(z.read('archived-file-hashes.json'))==oldcat
        for n in z.namelist():assert (SOURCE/n).resolve().is_relative_to(SOURCE.resolve())
        z.extractall(SOURCE)
    for n,h in oldcat.items():assert sha(SOURCE/n)==h
    for row in recipe['changes']:
        p=Path(row['private']['path']);assert sha(p)==row['private']['sha256']
        (SOURCE/row['member']).write_bytes(p.read_bytes())
    assert all(sha(SOURCE/n)==h for n,h in expected.items())
    code=(SOURCE/'tools/build.py').read_text()
    code=code.replace('ROOT = Path(__file__).resolve().parents[1]','ROOT = Path('+repr(str(SOURCE))+')')
    code=code.replace("bundled = ROOT / 'tools/Windows/cc65/bin/cl65.exe'",'bundled = Path('+repr(str(compiler/'bin/cl65.exe'))+')')
    token="'-l', f'build/{name}.lst', '-m', f'build/{name}.map',";assert code.count(token)==1
    code=code.replace(token,"'-m', f'build/{name}.map',")
    driver=OUT/'compact-build-driver.py';driver.write_text(code)
    report.update(private_driver_sha256=sha(driver),driver_differences=['Absolute private source ROOT','Absolute original compiler','Omit optional assembler listing; original build.py retained'])
    save()
    for mm,baseline in [('mmc3',False),('mmc5',False),('mmc3',True)]:
        name='smb-crossover-'+mm+('-baseline'if baseline else'')
        command=[sys.executable,str(driver),'--mapper',mm]+(['--baseline']if baseline else[])
        log=OUT/(name+'.log')
        with log.open('wb')as f:p=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        row=dict(mapper=mm,baseline=baseline,name=name,exit=p.returncode,log_sha256=sha(log),outputs={})
        report['builds'].append(row);save();assert p.returncode==0
        for ext in ('nes','dbg','lbl','map'):
            q=(SOURCE/'build'/name).with_suffix('.'+ext)
            row['outputs'][ext]=dict(path=str(q),sha256=sha(q),bytes=q.stat().st_size)
        expected_rom='0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'if baseline else recipe['per_mapper'][mm]['expected_whole_ROM_sha256']
        assert row['outputs']['nes']['sha256']==expected_rom
        assert not (SOURCE/'build'/name).with_suffix('.lst').exists()
        save()
    assert all(sha(SOURCE/n)==h for n,h in expected.items())and all(sha(ROOT/n)==h for n,h in oldcat.items())
    assert all(sha(compiler/n)==h for n,h in compiler_pins.items())
    newarchive=OUT/'source-current-p-sophia-r.zip'
    with zipfile.ZipFile(newarchive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(expected):z.write(SOURCE/n,n)
        z.writestr('archived-file-hashes.json',json.dumps(expected,indent=2)+'\n')
    report.update(status='PASS_PRIVATE_BUILD_EXACT_WHOLE_ROM_TEMPLATE_ONLY',source_archive_sha256=sha(newarchive),workspace_after=workspace_bytes(ROOT),
                  qualification='Private build only. Each ROM literal P with exact previously tested C2b banks6/36; baseline literal original. Full integrated native regressions/performance and root promotion decision remain pending.')
    assert report['workspace_after']<50_000_000_000
    save();print(report['status'],sha(OUT/'report.json'),flush=True)
    command=[sys.executable,str(PACKET/'bind_actual.py'),'--directory',str(SOURCE/'build'),
             '--build-report',str(OUT/'report.json'),'--build-report-sha256',sha(OUT/'report.json'),
             '--source-archive',str(newarchive),'--source-archive-sha256',sha(newarchive),'--out',str(OUT/'actual-integration-binding.json')]
    with (OUT/'binding.log').open('wb')as f:p=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    print('Host binding exit',p.returncode,flush=True);assert p.returncode==0

if __name__=='__main__':main()
