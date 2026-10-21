"""Merge independently frozen mode layers and the published laser hotfix."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';A=V/'root49-easy-union-a';H=V/'root49-easy-union-b';S=H/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def expect(v):return v['sha256']if isinstance(v,dict)else v
def main():
    sys.dont_write_bytecode=True;assert not H.exists()
    cp=R/'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json';u=json.loads(cp.read_text());assert sha(cp)=='4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    assert all(sha(R/n)==v for n,v in u['source_hashes'].items())
    root=V/'root49-easy-contact-private-d';rdata=json.loads((root/'build-review-f.json').read_text());expected=dict(rdata['all_source_hashes'])
    mm=V/'agent49-megaman-easy-hard-implementation-a';md=json.loads((mm/'handoff.json').read_text())
    for n,d in md['changed'].items():expected[n]=d['after']
    sb=V/'agent49easy-samus-bill-runtime-a';sd=json.loads((sb/'tier-freeze.json').read_text())
    for n in ['samus.s','samus_weapons.s','remaining_weapons.s','roster_weapons.s']:
        p=sb/'overlay/src'/n;expected['src/'+n]=expect(sd['files'][p.relative_to(R).as_posix()])
    lsr=V/'agent-lsr-easy-hard-implementation-a';ld=json.loads((lsr/'numeric-primary-freeze-h.json').read_text())
    for n in ['src/megaman_physics.s','src/roster.s','src/source_weapons.s','src/easy_lsr.s']:expected[n]=ld['source_catalog'][n]
    ad=json.loads((A/'report.json').read_text());assert ad['conflicts']==[] and ad['builds'][0]['exit']!=0
    for m in ad['merges']:expected[m['path']]=m['result_sha256']
    original=(root/'source/src/entrypoint.s').read_text();actual=(A/'source/src/entrypoint.s').read_text()
    assert actual==original+'\n.if ::ENABLE_CROSSOVER\n.include "easy_lsr.s"\n.endif\n'
    expected['src/entrypoint.s']=sha(A/'source/src/entrypoint.s')
    assert all(sha(A/'source'/n)==v for n,v in expected.items()),'All previous union inputs are bound'
    H.mkdir();shutil.copytree(A/'source',S,ignore=shutil.ignore_patterns('build','__pycache__'))
    report=dict(status='MERGING_FROZEN_EASY_LINK_AND_SAMUS_EFFECTS',script_sha256=sha(__file__),parent_negative_sha256=sha(A/'report.json'),
        parent_source_hashes=expected,inputs=[],merges=[],builds=[],main_changed=False,complete_Easy_behavior=False,accepted_release=False,goal_complete=False)
    def save():(H/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();conflicts=[]
    def merge(owner,n,ancestor,incoming):
        folder=H/'merges'/owner/Path(n).stem;folder.mkdir(parents=True)
        cur=folder/'current.s';base=folder/'base.s';other=folder/'incoming.s'
        cur.write_text((S/n).read_text());base.write_text(ancestor.read_text());other.write_text(incoming.read_text())
        p=subprocess.run(['git','merge-file','--stdout',str(cur),str(base),str(other)],cwd=R,capture_output=True)
        result=folder/'merged.s';result.write_bytes(p.stdout)
        report['merges'].append(dict(owner=owner,path=n,exit=p.returncode,current_sha256=sha(cur),base_sha256=sha(base),incoming_sha256=sha(other),result_sha256=sha(result)))
        if p.returncode:conflicts.append(owner+':'+n)
        else:shutil.copyfile(result,S/n)
        save()
    order=V/'agent-lsr-easy-link-order-a';od=json.loads((order/'implementation-freeze-j.json').read_text())
    assert sha(order/'implementation-freeze-j.json')=='4f424f4dae94253fafa2b889902d063138b1acc73cf97c8cf37a68e8a2011bec'
    for n,d in od['changed'].items():
        incoming=order/'after'/n;assert sha(incoming)==d['after_sha256']
        if d['before_sha256']is None:assert not(S/n).exists();shutil.copyfile(incoming,S/n)
        else:
            ancestor=lsr/'source-b'/n;assert sha(ancestor)==d['before_sha256'];merge('LinkOrder',n,ancestor,incoming)
    report['inputs'].append(dict(owner='LinkOrderJ',freeze_sha256=sha(order/'implementation-freeze-j.json')))
    stop=V/'agent49easy-samus-stop-b';sf=json.loads((stop/'freeze.json').read_text());assert sha(stop/'freeze.json')=='ce889bde24f6f2b8bbb59871b4f74a0fdea93a9d4ad860194cc840baf5dc1bfd'
    for incoming in sorted((stop/'overlay/src').glob('*.s')):
        n='src/'+incoming.name;key=incoming.relative_to(R).as_posix();assert sha(incoming)==expect(sf['files'][key]);ancestor=sb/'source'/n
        merge('SamusEasySTOP',n,ancestor,incoming)
    report['inputs'].append(dict(owner='SamusEasySTOP',freeze_sha256=sha(stop/'freeze.json')))
    hard=V/'agent49hard-samus-effects-c';hf=json.loads((hard/'freeze.json').read_text());assert sha(hard/'freeze.json')=='51fd87465bc0a17b0874bdc9df05d3a4acef42137c867d6f5b187c241058435a'
    for incoming in sorted((hard/'overlay/src').glob('*.s')):
        n='src/'+incoming.name;key=incoming.relative_to(R).as_posix();assert sha(incoming)==expect(hf['files'][key]);ancestor=stop/'source'/n
        merge('SamusHardINVUL',n,ancestor,incoming)
    report['inputs'].append(dict(owner='SamusHardINVUL',freeze_sha256=sha(hard/'freeze.json')))
    # Preserve U's exact already-tested rendering repair. Its ancestor is the
    # frozen user baseline, not today's modified working roster file.
    ancestor=H/'laser-base.s';ancestor.write_bytes((V/'root49-bill-laser-render-a/source/src/roster_weapons.s').read_bytes())
    text=ancestor.read_text();a0=text.index('.proc RosterDrawShots');a1=text.index('.endproc',a0)
    fixed='''  lda RgShotType,x
  beq SkipForeign
  cmp #32
  bcc Legacy
SkipForeign:
  jmp Next                    ;RemainingDraw owns advanced weapons and CHR.
Legacy:
  lda SelectedCharacter'''
    part=text[a0:a1];assert part.count(fixed)==1;ancestor.write_text(text[:a0]+part.replace(fixed,'  lda RgShotType,x\n  jeq Next\n  lda SelectedCharacter')+text[a1:])
    merge('PublishedLaserU','src/roster_weapons.s',ancestor,R/'src/roster_weapons.s')
    report['conflicts']=conflicts;save();assert not conflicts,conflicts
    driver=H/'build-driver.py';text=(A/'build-driver.py').read_text();old='ROOT = Path('+repr(str(A/'source'))+')';assert text.count(old)==1;driver.write_text(text.replace(old,'ROOT = Path('+repr(str(S))+')'))
    spec=importlib.util.spec_from_file_location('union_b_image',V/'agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build.log')
        with log.open('wb')as f:rc=subprocess.run([sys.executable,str(driver),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save();assert rc==0
        im=mod.Image(S/('build/smb-crossover-'+mapper+'.nes'));before=mod.Image(root/('source/build/smb-crossover-'+mapper+'.nes'))
        assert im.ram==before.ram;assert im.raw[16+64*8192:]==before.raw[16+64*8192:]
        ds=next(v for v in im.segs.values()if v['name']=='BASS_DPCM');assert im.raw[ds['ooffs']:ds['ooffs']+ds['size']]==before.raw[ds['ooffs']:ds['ooffs']+ds['size']]
        row.update(ROM_sha256=sha(im.path),RAM_exact=True,CHR_exact=True,DPCM_exact=True,segments={n:next(v for v in im.segs.values()if v['name']==n)for n in ['TITLE','RENDER','GUEST','PLAYER','SAMUS','SPECIAL_EXTRA','SPECIAL_ROSTER','INVENTORY','OBJECT','METASPRITE']});save()
    assert all(sha(R/n)==v for n,v in u['source_hashes'].items())
    names=set(expected)|set(od['changed']);report['all_source_hashes']={n:sha(S/n)for n in names};report['status']='PASS_PRIVATE_LINK_AND_SAMUS_EFFECTS_UNION_BUILD_ONLY';save();print(report['status'],sha(H/'report.json'),flush=True)
if __name__=='__main__':main()
