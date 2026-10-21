"""Build the frozen, isolated O2 Sophia ratio proposal; no promotion."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'build/checkpoints/roster-audit-v49-provisional-o2'
PACKET=ROOT/'build/verification/agent49o2-sophia-ratio-optimization-b-final'
OUT=ROOT/'build/verification/root49o2-sophia-ratio-private-build-b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+80_000_000<50_000_000_000
    assert sha(PACKET/'freeze.json')=='829e5e867cfa3570ebdf03fd30b679edc58453189fe0295d8179febf14963fbe'
    f=json.loads((PACKET/'freeze.json').read_text())
    for n,r in f['files'].items():assert sha(PACKET/n)==r['sha256']
    contract=json.loads((PACKET/'contract.json').read_text())
    archive=PARENT/'source-v49.zip';assert sha(archive)=='8c9d8b841f6a4b4680ad4675afdc2336a6bb6801141e2cb6b45d50fe7209db53'
    cat=json.loads((PARENT/'manifest.json').read_text())['source_hashes'];assert len(cat)==409
    OUT.mkdir();source=OUT/'source';source.mkdir()
    with zipfile.ZipFile(archive)as z:
        assert json.loads(z.read('archived-file-hashes.json'))==cat
        assert set(z.namelist())==set(cat)|{'archived-file-hashes.json'}
        for n,h in cat.items():
            p=(source/n).resolve();assert p.is_relative_to(source.resolve())
            raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==h
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    target=source/'src/sophia_math.s';assert sha(target)==contract['source_before']['sha256']
    target.write_bytes((PACKET/'sophia_math.s').read_bytes())
    assert sha(target)==contract['source_after']['sha256']
    newcat=dict(cat);newcat['src/sophia_math.s']=sha(target)
    compiler=ROOT/'tools/Windows/cc65'
    compiler_pins={p.relative_to(compiler).as_posix():sha(p)for p in compiler.rglob('*')if p.is_file()}
    driver=(source/'tools/build.py').read_text()
    driver=driver.replace('ROOT = Path(__file__).resolve().parents[1]','ROOT = Path('+repr(str(source))+')')
    driver=driver.replace("bundled = ROOT / 'tools/Windows/cc65/bin/cl65.exe'",'bundled = Path('+repr(str(compiler/'bin/cl65.exe'))+')')
    marker="'-l', f'build/{name}.lst', '-m', f'build/{name}.map',"
    assert driver.count(marker)==1;driver=driver.replace(marker,"'-m', f'build/{name}.map',")
    driverpath=OUT/'compact-build-driver.py';driverpath.write_text(driver)
    report={'status':'building-private-ratio-only','accepted_release':False,'goal_complete':False,
            'script_sha256':sha(Path(__file__)),'packet_freeze_sha256':sha(PACKET/'freeze.json'),
            'parent_archive_sha256':sha(archive),'source409_hashes':newcat,'compiler_hashes':compiler_pins,
            'private_driver_sha256':sha(driverpath),'workspace_before':used,'builds':[]}
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for mapper in ('mmc3','mmc5'):
        with (OUT/(mapper+'.log')).open('wb')as log:
            r=subprocess.run([sys.executable,str(driverpath),'--mapper',mapper],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        case={'mapper':mapper,'compiler_exit':r.returncode};report['builds'].append(case);save()
        assert r.returncode==0,str(OUT/(mapper+'.log'))
        name='smb-crossover-'+mapper
        case['outputs']={ext:{'path':str((source/'build'/name).with_suffix('.'+ext)),
                              'sha256':sha((source/'build'/name).with_suffix('.'+ext))}
                         for ext in ('nes','dbg','lbl','map')}
        old=(PARENT/(name+'.nes')).read_bytes();new=(source/'build'/(name+'.nes')).read_bytes()
        assert len(old)==len(new)
        diff=[i for i,(a,b)in enumerate(zip(old,new))if a!=b]
        assert diff and all((i-16)//8192==36 for i in diff)
        case.update(changed_bytes=len(diff),only_bank36=True);save()
    assert all(sha(source/n)==h for n,h in newcat.items())
    assert all(sha(compiler/n)==h for n,h in compiler_pins.items())
    with zipfile.ZipFile(OUT/'source-ratio-b.zip','x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(newcat):z.write(source/n,n)
        z.writestr('archived-file-hashes.json',json.dumps(newcat,indent=2)+'\n')
    report.update(status='PASS_PRIVATE_RATIO_BUILD_ONLY_NOT_ABI_OR_PERFORMANCE_ACCEPTANCE',
                  source_archive_sha256=sha(OUT/'source-ratio-b.zip'),workspace_after=workspace_bytes(ROOT))
    save();print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json'),'builds':report['builds']},indent=2))


if __name__=='__main__':main()
