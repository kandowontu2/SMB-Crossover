"""Resolve union B's bank capacity with an existing bank-called closure."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';P=V/'root49-easy-union-b';H=V/'root49-easy-union-c';S=H/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.dont_write_bytecode=True;assert not H.exists()
    previous=json.loads((P/'report.json').read_text());assert previous['conflicts']==[] and previous['builds'][0]['exit']!=0
    expected=dict(previous['parent_source_hashes'])
    od=json.loads((V/'agent-lsr-easy-link-order-a/implementation-freeze-j.json').read_text())
    for n,d in od['changed'].items():
        if d['before_sha256']is None:expected[n]=d['after_sha256']
    for row in previous['merges']:expected[row['path']]=row['result_sha256']
    assert all(sha(P/'source'/n)==v for n,v in expected.items())
    u=json.loads((R/'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json').read_text());assert all(sha(R/n)==v for n,v in u['source_hashes'].items())
    H.mkdir();shutil.copytree(P/'source',S,ignore=shutil.ignore_patterns('build','__pycache__'))
    refs=[]
    for p in (S/'src').glob('*'):
        if p.suffix not in ['.s','.inc']:continue
        for line in p.read_text().splitlines():
            if'MegaManPaletteState'in line:refs.append((p.relative_to(S).as_posix(),line.strip()))
    assert refs==[('src/characters.s','farcall MegaManPaletteState'),('src/megaman_palette.s','.proc MegaManPaletteState')],refs
    palette=S/'src/megaman_palette.s';text=palette.read_text();assert text.count('.segment "GUEST"')==1;palette.write_text(text.replace('.segment "GUEST"','.segment "INVENTORY"'))
    expected['src/megaman_palette.s']=sha(palette)
    driver=H/'build-driver.py';text=(P/'build-driver.py').read_text();old='ROOT = Path('+repr(str(P/'source'))+')';assert text.count(old)==1;driver.write_text(text.replace(old,'ROOT = Path('+repr(str(S))+')'))
    report=dict(status='BUILDING_PRIVATE_UNION_C',script_sha256=sha(__file__),parent_bank_capacity_negative_sha256=sha(P/'report.json'),
        source_hashes=expected,relocation=dict(closure='MegaManPaletteState withColors',old_segment='GUEST',new_segment='INVENTORY',references=refs,new_bank_crossings=0,new_RAM=0),builds=[],main_changed=False,complete_Easy_behavior=False,accepted_release=False,goal_complete=False)
    def save():(H/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();spec=importlib.util.spec_from_file_location('union_c_image',V/'agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build.log')
        with log.open('wb')as f:rc=subprocess.run([sys.executable,str(driver),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save();assert rc==0
        im=mod.Image(S/('build/smb-crossover-'+mapper+'.nes'));before=mod.Image(V/('root49-easy-contact-private-d/source/build/smb-crossover-'+mapper+'.nes'))
        assert im.ram==before.ram;assert im.raw[16+64*8192:]==before.raw[16+64*8192:]
        ds=next(v for v in im.segs.values()if v['name']=='BASS_DPCM');assert im.raw[ds['ooffs']:ds['ooffs']+ds['size']]==before.raw[ds['ooffs']:ds['ooffs']+ds['size']]
        row.update(ROM_sha256=sha(im.path),RAM_exact=True,CHR_exact=True,DPCM_exact=True,segments={n:next(v for v in im.segs.values()if v['name']==n)for n in ['TITLE','RENDER','GUEST','PLAYER','SAMUS','SPECIAL_EXTRA','SPECIAL_ROSTER','INVENTORY','OBJECT','METASPRITE']});save()
    assert all(sha(S/n)==v for n,v in expected.items());assert all(sha(R/n)==v for n,v in u['source_hashes'].items())
    report['status']='PASS_PRIVATE_MODE_UNION_C_BUILD_ONLY';save();print(report['status'],sha(H/'report.json'),flush=True)
if __name__=='__main__':main()
