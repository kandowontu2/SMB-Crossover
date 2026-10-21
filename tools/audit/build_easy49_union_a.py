"""Compose frozen private behavior layers; preserve user's working source."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
H=V/'root49-easy-union-a';S=H/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.dont_write_bytecode=True;assert not H.exists()
    base=json.loads((V/'root49-easy-hard-user-baseline-a/baseline.json').read_text())
    assert all(sha(R/n)==v for n,v in base['current_source_hashes'].items())
    root=V/'root49-easy-contact-private-d';rootdata=json.loads((root/'build-review-f.json').read_text())
    assert all(sha(root/'source'/n)==v for n,v in rootdata['all_source_hashes'].items())
    for tag in ['eligibility-m3-g','eligibility-m5-h']:
        data=json.loads((root/'native'/tag/'host-report.json').read_text());assert data['exit']==0 and data['result']['cases']==144
    H.mkdir();shutil.copytree(root/'source',S,ignore=shutil.ignore_patterns('build','__pycache__'))
    report=dict(status='COMPOSING_FROZEN_PRIVATE_LAYERS',script_sha256=sha(__file__),inputs=[],merges=[],builds=[],main_changed=False,complete_Easy_behavior=False,accepted_release=False,goal_complete=False)
    def save():(H/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();mm=V/'agent49-megaman-easy-hard-implementation-a';mmdat=json.loads((mm/'handoff.json').read_text())
    assert sha(mm/'freeze.json')=='3958919bc389a447ca8764d5115dea27e49d409d7d28a1ab3744e4615022bc36'
    assert sha(mm/'source-overlay.zip')==mmdat['source_overlay_sha256']
    with zipfile.ZipFile(mm/'source-overlay.zip')as z:
        for n,row in mmdat['changed'].items():
            raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==row['after'];(S/n).write_bytes(raw)
    report['inputs'].append(dict(owner='MegaMan',freeze_sha256=sha(mm/'freeze.json'),overlay_sha256=sha(mm/'source-overlay.zip')));save()
    sb=V/'agent49easy-samus-bill-runtime-a';sbdat=json.loads((sb/'tier-freeze.json').read_text())
    assert sha(sb/'tier-freeze.json')=='dc33410e138fd345961c8f60b3295fa5cfbeed4191e26ffe573fa99439fe523e'
    for n in ['samus.s','samus_weapons.s','remaining_weapons.s','roster_weapons.s']:
        p=sb/'overlay/src'/n;key=str(p.relative_to(R)).replace('\\','/');assert sha(p)==sbdat['files'][key];shutil.copyfile(p,S/'src'/n)
    report['inputs'].append(dict(owner='SamusBillTiers',freeze_sha256=sha(sb/'tier-freeze.json')));save()
    lsr=V/'agent-lsr-easy-hard-implementation-a';ldat=json.loads((lsr/'numeric-primary-freeze-h.json').read_text())
    assert sha(lsr/'numeric-primary-freeze-h.json')=='bbe53a635c5f44eacdb9adc391473e23f59a714f76126649679ad04d7eecb1bd'
    ls=lsr/'source-b';conflicts=[]
    # LSR's frozen physics explicitly incorporates the exact final MM physics
    # and adds only LinkGravity. Do not three-way duplicate that relocation.
    assert ldat['physics_union']['parent_MM_sha256']==mmdat['changed']['src/megaman_physics.s']['after']
    for n in ['src/megaman_physics.s','src/roster.s','src/source_weapons.s','src/easy_lsr.s']:
        assert sha(ls/n)==ldat['source_catalog'][n];shutil.copyfile(ls/n,S/n)
    ep=S/'src/entrypoint.s'
    assert '.include "easy_lsr.s"'not in ep.read_text()
    with ep.open('a')as f:f.write('\n.if ::ENABLE_CROSSOVER\n.include "easy_lsr.s"\n.endif\n')
    for n in ['src/megaman_weapons.s','src/remaining_weapons.s','src/roster_weapons.s']:
        assert sha(ls/n)==ldat['source_catalog'][n]
        folder=H/'merges'/Path(n).stem;folder.mkdir(parents=True)
        current=folder/'current.s';ancestor=folder/'base.s';incoming=folder/'incoming.s'
        current.write_text((S/n).read_text());ancestor.write_text((R/n).read_text());incoming.write_text((ls/n).read_text())
        proc=subprocess.run(['git','merge-file','--stdout',str(current),str(ancestor),str(incoming)],capture_output=True,cwd=R)
        result=folder/'merged.s';result.write_bytes(proc.stdout)
        report['merges'].append(dict(path=n,exit=proc.returncode,current_sha256=sha(current),base_sha256=sha(ancestor),incoming_sha256=sha(incoming),result_sha256=sha(result)))
        if proc.returncode:conflicts.append(n)
        else:shutil.copyfile(result,S/n)
        save()
    report['inputs'].append(dict(owner='LinkSimonNumericPrimary',freeze_sha256=sha(lsr/'numeric-primary-freeze-h.json')))
    report['conflicts']=conflicts;save();assert not conflicts,conflicts
    driver=H/'build-driver.py';text=(root/'build-driver.py').read_text();old='ROOT = Path('+repr(str(root/'source'))+')';assert text.count(old)==1;driver.write_text(text.replace(old,'ROOT = Path('+repr(str(S))+')'))
    parser=V/'agent49g-samus-crouch-fix-proposal-b/image.py';spec=importlib.util.spec_from_file_location('union_image',parser);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build.log')
        with log.open('wb')as f:rc=subprocess.run([sys.executable,str(driver),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save();assert rc==0
        im=mod.Image(S/('build/smb-crossover-'+mapper+'.nes'));before=mod.Image(root/('source/build/smb-crossover-'+mapper+'.nes'))
        assert im.ram==before.ram;assert im.raw[16+64*8192:]==before.raw[16+64*8192:]
        ds=next(v for v in im.segs.values()if v['name']=='BASS_DPCM');assert im.raw[ds['ooffs']:ds['ooffs']+ds['size']]==before.raw[ds['ooffs']:ds['ooffs']+ds['size']]
        row.update(ROM_sha256=sha(im.path),RAM_exact=True,CHR_exact=True,DPCM_exact=True,segments={n:next(v for v in im.segs.values()if v['name']==n)for n in ['TITLE','RENDER','GUEST','PLAYER','SAMUS','SPECIAL_EXTRA','SPECIAL_ROSTER','INVENTORY']});save()
    assert all(sha(R/n)==v for n,v in base['current_source_hashes'].items())
    report['status']='PASS_PRIVATE_EASY_NUMERIC_TIER_UNION_BUILD_ONLY';report['all_source_hashes']={n:sha(S/n)for n in rootdata['all_source_hashes']}|{'src/easy_lsr.s':sha(S/'src/easy_lsr.s')};save();print(report['status'],sha(H/'report.json'),flush=True)
if __name__=='__main__':main()
