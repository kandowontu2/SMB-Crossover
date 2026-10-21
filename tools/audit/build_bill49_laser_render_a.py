"""Isolate the user's Contra laser double-render defect on the working baseline."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';B=V/'root49-easy-hard-user-baseline-a';H=V/'root49-bill-laser-render-a';S=H/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.dont_write_bytecode=True;assert not H.exists()
    b=json.loads((B/'baseline.json').read_text());assert all(sha(R/n)==v for n,v in b['current_source_hashes'].items())
    H.mkdir();S.mkdir()
    with zipfile.ZipFile(R/'build/checkpoints/roster-audit-v49-ryu-head-t/source-v49-ryu-head-t.zip')as z:
        assert all((S/n).resolve().is_relative_to(S.resolve())for n in z.namelist());z.extractall(S)
    with zipfile.ZipFile(B/'user-source-overlay.zip')as z:
        for n in b['source_changes_from_T']:(S/n).write_bytes(z.read(n))
    assert all(sha(S/n)==v for n,v in b['current_source_hashes'].items())
    p=S/'src/roster_weapons.s';text=p.read_text();start=text.index('.proc RosterDrawShots');end=text.index('.endproc',start)
    part=text[start:end];old='  lda RgShotType,x\n  jeq Next\n  lda SelectedCharacter';assert part.count(old)==1
    part=part.replace(old,'''  lda RgShotType,x
  beq SkipForeign
  cmp #32
  bcc Legacy
SkipForeign:
  jmp Next                    ;RemainingDraw owns advanced weapons and CHR.
Legacy:
  lda SelectedCharacter''')
    p.write_text(text[:start]+part+text[end:])
    report=dict(status='BUILDING_BILL_LASER_RENDER_FIX',script_sha256=sha(__file__),baseline_sha256=sha(B/'baseline.json'),before_source_sha256=b['current_source_hashes']['src/roster_weapons.s'],after_source_sha256=sha(p),builds=[],main_changed=False,accepted_release=False,goal_complete=False)
    def save():(H/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();driver=H/'build-driver.py';code=(V/'root49-easy-inventory-base-a/compact-build-driver.py').read_text();old='ROOT = Path('+repr(str(V/'root49-easy-inventory-base-a/source'))+')';assert code.count(old)==1;driver.write_text(code.replace(old,'ROOT = Path('+repr(str(S))+')'))
    spec=importlib.util.spec_from_file_location('laser_image',V/'agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build.log')
        with log.open('wb')as f:rc=subprocess.run([sys.executable,str(driver),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save();assert rc==0
        im=mod.Image(S/('build/smb-crossover-'+mapper+'.nes'));oldim=mod.Image(B/im.path.name)
        assert im.ram==oldim.ram;assert im.raw[16+64*8192:]==oldim.raw[16+64*8192:]
        d=next(v for v in im.segs.values()if v['name']=='BASS_DPCM');assert im.raw[d['ooffs']:d['ooffs']+d['size']]==oldim.raw[d['ooffs']:d['ooffs']+d['size']]
        row.update(ROM_sha256=sha(im.path),RAM_exact=True,CHR_exact=True,DPCM_exact=True,metasprite_segment=next(v for v in im.segs.values()if v['name']=='METASPRITE'));save()
    assert all(sha(R/n)==v for n,v in b['current_source_hashes'].items())
    report['status']='PASS_PRIVATE_LASER_RENDER_BUILD_ONLY';save();print(report['status'],sha(H/'report.json'),flush=True)
if __name__=='__main__':main()
