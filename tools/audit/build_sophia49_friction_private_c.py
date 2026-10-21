"""Build isolated guarded friction C on ratio B; no promotion."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'build/verification/root49o2-sophia-ratio-private-build-b'
PACKET=ROOT/'build/verification/agent49o2-sophia-friction-proposal-c'
OUT=ROOT/'build/verification/root49o2-sophia-friction-private-build-c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+80_000_000<50_000_000_000
    assert sha(PACKET/'frozen.json')=='049000ab5f83e1a4872c6d4ef84efeb8c64be2482934509e3673538e1963f659'
    f=json.loads((PACKET/'frozen.json').read_text())
    for n,r in f['files'].items():assert sha(PACKET/n)==r['sha256']
    templates={r['mapper']:r for r in json.loads((PACKET/'compiled-template.json').read_text())}
    assert sha(PARENT/'report.json')=='98302179e23d0fa8621e60f8bba9fceca67c9372b7c0fe758dced097e5178514'
    archive=PARENT/'source-ratio-b.zip';assert sha(archive)=='ea58307af53fc6597cc89a31621e3ba28077879a658e51753355cb531c4eec69'
    cat=json.loads((PARENT/'report.json').read_text())['source409_hashes'];assert len(cat)==409
    current=json.loads((ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n)==h for n,h in current.items())
    OUT.mkdir();source=OUT/'source';source.mkdir()
    with zipfile.ZipFile(archive)as z:
        assert json.loads(z.read('archived-file-hashes.json'))==cat
        assert set(z.namelist())==set(cat)|{'archived-file-hashes.json'}
        for n,h in cat.items():
            p=(source/n).resolve();assert p.is_relative_to(source.resolve())
            raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==h
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    target=source/'src/remaining_weapons.s';assert sha(target)==cat['src/remaining_weapons.s']
    target.write_bytes((PACKET/'private/remaining_weapons.s').read_bytes())
    assert sha(target)=='d21c507a6de1868506c8644649b8c4ac2b06e7203f4d64cbd94f868714dfc391'
    newcat=dict(cat);newcat['src/remaining_weapons.s']=sha(target)
    compiler=ROOT/'tools/Windows/cc65'
    compiler_pins={p.relative_to(compiler).as_posix():sha(p)for p in compiler.rglob('*')if p.is_file()}
    driver=(source/'tools/build.py').read_text()
    driver=driver.replace('ROOT = Path(__file__).resolve().parents[1]','ROOT = Path('+repr(str(source))+')')
    driver=driver.replace("bundled = ROOT / 'tools/Windows/cc65/bin/cl65.exe'",'bundled = Path('+repr(str(compiler/'bin/cl65.exe'))+')')
    marker="'-l', f'build/{name}.lst', '-m', f'build/{name}.map',"
    assert driver.count(marker)==1;driver=driver.replace(marker,"'-m', f'build/{name}.map',")
    driverpath=OUT/'compact-build-driver.py';driverpath.write_text(driver)
    report={'status':'building-private-friction-on-ratio-B','accepted_release':False,'goal_complete':False,
            'script_sha256':sha(Path(__file__)),'packet_freeze_sha256':sha(PACKET/'frozen.json'),
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
        old=(PARENT/'source/build'/(name+'.nes')).read_bytes();new=(source/'build'/(name+'.nes')).read_bytes()
        assert len(old)==len(new)
        diff=[i for i,(a,b)in enumerate(zip(old,new))if a!=b]
        t=templates[mapper];prefix=t['entry']['rom_offset'];cold=t['cold_rom_offset']
        allowed=set(range(prefix,prefix+58))|set(range(cold,cold+61))
        assert diff and set(diff)<=allowed
        assert new[prefix:prefix+58].hex()==t['expected_prefix58_hex']
        assert new[prefix+58:prefix+90].hex()==t['unchanged_tail32_hex']
        assert new[cold:cold+61].hex()==t['expected_cold61_hex']
        assert hashlib.sha256(new[16+6*8192:16+7*8192]).hexdigest()==t['expected_bank6_sha256']
        case.update(changed_bytes=len(diff),only_exact_prefix58_and_cold61=True,
                    independent_bank6_template_sha256=t['expected_bank6_sha256']);save()
    assert all(sha(source/n)==h for n,h in newcat.items())
    assert all(sha(compiler/n)==h for n,h in compiler_pins.items())
    assert all(sha(ROOT/n)==h for n,h in current.items())
    with zipfile.ZipFile(OUT/'source-friction-c.zip','x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(newcat):z.write(source/n,n)
        z.writestr('archived-file-hashes.json',json.dumps(newcat,indent=2)+'\n')
    report.update(status='PASS_PRIVATE_FRICTION_BUILD_AND_EXACT_BANK6_TEMPLATES_ONLY',
                  source_archive_sha256=sha(OUT/'source-friction-c.zip'),workspace_after=workspace_bytes(ROOT))
    save();print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json'),'builds':report['builds']},indent=2))


if __name__=='__main__':main()
