"""Resume A's source after rejecting its incorrectly rebound build-driver ROOT."""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, sys
R=Path(__file__).resolve().parents[2]
H=R/'build/verification/root49-easy-injury-private-a'; S=H/'source'
B=R/'build/verification/root49-easy-hard-user-baseline-a'
P=R/'build/verification/root49-easy-inventory-base-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.dont_write_bytecode=True
    out=H/'build-review-b.json';assert not out.exists()
    original=json.loads((H/'report.json').read_text())
    assert all(sha(S/n)==h for n,h in original['changes'].items())
    baseline=json.loads((B/'baseline.json').read_text())
    assert all(sha(R/n)==h for n,h in baseline['current_source_hashes'].items())
    driver=H/'corrected-build-driver-b.py'
    code=(P/'compact-build-driver.py').read_text()
    old='ROOT = Path('+repr(str(P/'source'))+')'
    assert code.count(old)==1
    driver.write_text(code.replace(old,'ROOT = Path('+repr(str(S))+')'))
    report=dict(status='BUILDING_PRIVATE_LEGACY_DAMAGE_B',script_sha256=sha(__file__),
        initial_host_negative_sha256=sha(H/'report.json'),cause='Initial driver retained parent ROOT; no injury ROM was produced. Rebound exact Python literal with assert.',
        source_changes=original['changes'],builds=[],main_changed=False,complete_Easy_behavior=False,accepted_release=False,goal_complete=False)
    def save():out.write_text(json.dumps(report,indent=2)+'\n')
    save()
    parser=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('injury_image_b',parser)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build-b.log')
        with log.open('wb')as f:
            rc=subprocess.run([sys.executable,str(driver),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save()
        assert rc==0,mapper
        rom=S/('build/smb-crossover-'+mapper+'.nes');im=mod.Image(rom);oldim=mod.Image(B/rom.name)
        assert all(im.ram[k]==v for k,v in oldim.ram.items())
        assert im.raw[16+64*8192:]==oldim.raw[16+64*8192:]
        d=next(v for v in im.segs.values()if v['name']=='BASS_DPCM')
        assert im.raw[d['ooffs']:d['ooffs']+d['size']]==oldim.raw[d['ooffs']:d['ooffs']+d['size']]
        row.update(ROM_sha256=sha(rom),old_RAM_exact=True,CHR_exact=True,DPCM_exact=True,
            segments={k:next(v for v in im.segs.values()if v['name']==k)for k in ['INVENTORY','SAMUS','FIXED','SRAM']})
        save()
    assert all(sha(R/n)==h for n,h in baseline['current_source_hashes'].items())
    report['status']='PASS_PRIVATE_LEGACY_DAMAGE_BUILD_ONLY'
    report['all_candidate_source_hashes']={n:sha(S/n)for n in baseline['current_source_hashes']}|{'src/guest_legacy_injury.s':sha(S/'src/guest_legacy_injury.s')}
    report['limits']='Build/layout only; lifecycle and native freeze/Hard regression execution pending. NES binary opacity approximates source alpha.'
    save();print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
