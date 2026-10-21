"""Build the requested menu/behavior over the immutable optimized R candidate."""
from pathlib import Path
import hashlib,importlib.util,json,re,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49-menu-options-private-s'
SOURCE=OUT/'source'
MENU=ROOT/'build/verification/menu-options-behavior-private-a'
BASE=ROOT/'build/verification/root49p-sophia-integrated-private-r'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(MENU/'implementation-freeze.json')=='23f12e93ddd16b0887189c3e86285e076fe9187c6b13e56cad8dbaf418d385f8'
    freeze=json.loads((MENU/'implementation-freeze.json').read_text())
    for n,p in freeze['files'].items():assert sha(MENU/n)==p['sha256']and (MENU/n).stat().st_size==p['bytes']
    contract=json.loads((MENU/'contract.json').read_text());parent=contract['parent_catalog']
    assert len(parent)==409 and all(sha(ROOT/n)==h for n,h in parent.items())
    for n,h in contract['candidate_catalog'].items():assert sha(MENU/'source'/n)==h
    built=json.loads((BASE/'report.json').read_text())
    assert sha(BASE/'report.json')=='51eb15b3a2a00bb050990cf8c7ceadd4538583e4311b2e97c29621bc9f574f63'
    oldcat=built['source409_hashes'];expected=dict(oldcat)
    for n,pin in contract['changed'].items():
        assert oldcat.get(n)==pin['before_sha256'],n
        expected[n]=pin['after_sha256']
    assert len(expected)==410
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+375_000_000<50_000_000_000
    OUT.mkdir();SOURCE.mkdir()
    report=dict(status='RUNNING_MENU_S_PRIVATE_BUILD',accepted_release=False,goal_complete=False,
        script_sha256=sha(Path(__file__)),menu_freeze_sha256=sha(MENU/'implementation-freeze.json'),
        base_build_sha256=sha(BASE/'report.json'),source410_hashes=expected,workspace_before=used,builds=[])
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();archive=BASE/'source-current-p-sophia-r.zip';assert sha(archive)==built['source_archive_sha256']
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(oldcat)|{'archived-file-hashes.json'}
        assert json.loads(z.read('archived-file-hashes.json'))==oldcat
        for n in z.namelist():assert (SOURCE/n).resolve().is_relative_to(SOURCE.resolve())
        z.extractall(SOURCE)
    for n in contract['changed']:(SOURCE/n).write_bytes((MENU/'source'/n).read_bytes())
    assert all(sha(SOURCE/n)==h for n,h in expected.items())
    compiler=ROOT/'tools/Windows/cc65/bin/cl65.exe'
    compiler_before=sha(compiler);code=(SOURCE/'tools/build.py').read_text()
    code=code.replace('ROOT = Path(__file__).resolve().parents[1]','ROOT = Path('+repr(str(SOURCE))+')')
    code=code.replace("bundled = ROOT / 'tools/Windows/cc65/bin/cl65.exe'",'bundled = Path('+repr(str(compiler))+')')
    old="'-l', f'build/{name}.lst', '-m', f'build/{name}.map',";assert code.count(old)==1
    code=code.replace(old,"'-m', f'build/{name}.map',")
    driver=OUT/'compact-build-driver.py';driver.write_text(code);report['private_driver_sha256']=sha(driver);save()
    lib=ROOT/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(lib)=='54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    sp=importlib.util.spec_from_file_location('menu_actual_image',lib);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
    for mm,baseline in [('mmc3',False),('mmc5',False),('mmc3',True)]:
        name='smb-crossover-'+mm+('-baseline'if baseline else'')
        command=[sys.executable,str(driver),'--mapper',mm]+(['--baseline']if baseline else[])
        log=OUT/(name+'.log')
        with log.open('wb')as f:p=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        row=dict(mapper=mm,baseline=baseline,name=name,exit=p.returncode,log_sha256=sha(log),outputs={})
        report['builds'].append(row);save();assert p.returncode==0
        for ext in ('nes','dbg','lbl','map'):
            q=(SOURCE/'build'/name).with_suffix('.'+ext);row['outputs'][ext]=dict(path=str(q),sha256=sha(q),bytes=q.stat().st_size)
        if baseline:assert row['outputs']['nes']['sha256']=='0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'
        else:
            before=mod.Image(BASE/'source/build'/f'smb-crossover-{mm}.nes');after=mod.Image(SOURCE/'build'/f'smb-crossover-{mm}.nes')
            assert all(after.ram.get(n)==v for n,v in before.ram.items())
            assert set(after.ram)-set(before.ram)=={'CrossoverBehaviorVersion'}
            assert after.ram['CrossoverBehaviorVersion']==0x7fe1
            def seg(im,n):return next(s for s in im.segs.values()if s['name']==n)
            for n in ('SAMUS','OBJECT','LOWCODE','BASS_DPCM'):
                assert (seg(before,n)['start'],seg(before,n)['size'])==(seg(after,n)['start'],seg(after,n)['size']),n
            assert seg(after,'FIXED')['size']==seg(before,'FIXED')['size']+9
            assert seg(after,'SRAM')['size']==seg(before,'SRAM')['size']+1
            assert seg(after,'CHAR_SELECT')['size']==contract['budgets'][mm]['new_char_select_static']
            for bank in (6,36):assert before.raw[16+bank*8192:16+(bank+1)*8192]==after.raw[16+bank*8192:16+(bank+1)*8192]
            assert before.raw[16+64*8192:]==after.raw[16+64*8192:]
            d=seg(after,'BASS_DPCM');assert before.raw[d['ooffs']:d['ooffs']+d['size']]==after.raw[d['ooffs']:d['ooffs']+d['size']]
            row['layout']=dict(old_RAM_addresses_exact=True,new_behavior_address=0x7fe1,Sophia_optimized_banks_exact=True,
                CHR_exact=True,DPCM_exact=True,FIXED_delta=9,SRAM_delta=1,CHAR_SELECT_size=seg(after,'CHAR_SELECT')['size'],
                menu_bank_free=8192-(seg(after,'CHAR_SELECT')['start']+seg(after,'CHAR_SELECT')['size']-0xa000))
        save()
    assert sha(compiler)==compiler_before
    assert all(sha(SOURCE/n)==h for n,h in expected.items())and all(sha(ROOT/n)==h for n,h in parent.items())
    newarchive=OUT/'source-menu-options-s.zip'
    with zipfile.ZipFile(newarchive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(expected):z.write(SOURCE/n,n)
        z.writestr('archived-file-hashes.json',json.dumps(expected,indent=2)+'\n')
    report.update(status='PASS_PRIVATE_MENU_S_BUILD_LAYOUT_ONLY',source_archive_sha256=sha(newarchive),workspace_after=workspace_bytes(ROOT),
        qualification='Requested UI/behavior compiled on both maps with original baseline exact. Old RAM addresses preserved; native menu/combat/source-mode regression and audible dispatch checks remain pending. Main source untouched.')
    save();print(report['status'],sha(OUT/'report.json'),flush=True)

if __name__=='__main__':main()
