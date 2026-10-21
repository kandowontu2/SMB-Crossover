"""Publish only the verified advanced-projectile renderer ownership repair."""
from pathlib import Path
import datetime,gzip,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-bill-laser-render-a';B=V/'root49-easy-hard-user-baseline-a';C=R/'build/checkpoints/roster-audit-v49-bill-laser-u'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not C.exists()
    baseline=json.loads((B/'baseline.json').read_text());before=baseline['current_source_hashes']
    assert all(sha(R/n)==h for n,h in before.items())
    build=json.loads((H/'report.json').read_text());assert build['status']=='PASS_PRIVATE_LASER_RENDER_BUILD_ONLY'
    regress=H/'regressions-b/report.json';rg=json.loads(regress.read_text());assert rg['status']=='PASS_16_LASER_RENDER_REGRESSIONS' and len(rg['results'])==16 and all(q['exit']==0 for q in rg['results'])
    refs=[H/'report.json',regress]
    for tag,kind in [('control-m3-b','control'),('control-m5-d','control'),('candidate-m3-f','candidate'),('candidate-m5-g','candidate')]:
        folder=H/'native'/tag;data=json.loads((folder/'host-report.json').read_text());assert data['admitted'] and data['result']['cases']==60
        assert data['result']['foreign_cases']==(24 if kind=='control' else 0)
        assert sha(folder/'binding.json')==data['binding_sha256'] and sha(folder/'native-core.lua')==data['core_sha256']
        rows=[json.loads(line)for line in(folder/'events.jsonl').read_text().splitlines()];rows=[q for q in rows if q['event']=='case'];assert len(rows)==60
        if kind=='candidate':
            assert all(q['foreign']==0 and(q['emitted']>0 if q['weapon']in[2,3]else q['legacy']>0)for q in rows)
        refs.extend([folder/n for n in ['host-report.json','binding.json','native-core.lua','events.jsonl','native.log']])
    target='src/roster_weapons.s';old=(R/target).read_bytes();new=(H/'source'/target).read_bytes()
    assert sha(R/target)==build['before_source_sha256'] and hashlib.sha256(new).hexdigest()==build['after_source_sha256']
    original='  lda RgShotType,x\r\n  jeq Next\r\n  lda SelectedCharacter'.encode()
    replacement='''  lda RgShotType,x
  beq SkipForeign
  cmp #32
  bcc Legacy
SkipForeign:
  jmp Next                    ;RemainingDraw owns advanced weapons and CHR.
Legacy:
  lda SelectedCharacter'''.replace('\n','\r\n').encode()
    start=old.index(b'.proc RosterDrawShots');end=old.index(b'.endproc',start)
    part=old[start:end];assert part.count(original)==1
    assert old[:start]+part.replace(original,replacement)+old[end:]==new,'Exact single source hunk only'
    # Every other private source differs at most by admitted generator line endings.
    for n in before:
        if n==target:continue
        assert(H/'source'/n).read_bytes().replace(b'\r\n',b'\n')==(R/n).read_bytes().replace(b'\r\n',b'\n'),n
    C.mkdir(parents=True)
    manifest=dict(status='PUBLISHING_VERIFIED_LASER_SINGLE_RENDERER_U',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),publisher_sha256=sha(__file__),parent_user_baseline_sha256=sha(B/'baseline.json'),
        before_source_hashes=before,source_changes={target:dict(before=sha(R/target),after=hashlib.sha256(new).hexdigest())},builds=[],
        evidence=[dict(path=str(p.relative_to(R)),sha256=sha(p),bytes=p.stat().st_size)for p in refs],
        behavior='Advanced RgShotType32+ is drawn only by RemainingDraw; legacy projectile renderer no longer submits machine-bullet art for laser/flare or other advanced weapons.',
        user_labels_and_seven_generated_files_preserved=True,Easy_Hard_expansion_included=False,accepted_release=False,goal_complete=False)
    def save():(C/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    save();(R/target).write_bytes(new)
    for mapper in ['mmc3','mmc5']:
        candidate=H/('source/build/smb-crossover-'+mapper+'.nes');row=next(q for q in build['builds']if q['mapper']==mapper);assert sha(candidate)==row['ROM_sha256']
        artifacts={}
        for ext in ['nes','lbl','map','dbg']:
            src=candidate.with_suffix('.'+ext);dst=R/('build/smb-crossover-'+mapper+'.'+ext)
            shutil.copyfile(src,dst);assert sha(src)==sha(dst)
            artifacts[ext]=dict(path=str(dst.relative_to(R)),sha256=sha(dst),bytes=dst.stat().st_size)
            if ext!='dbg':shutil.copyfile(dst,C/dst.name)
            else:
                raw=gzip.compress(dst.read_bytes(),mtime=0);(C/(dst.name+'.gz')).write_bytes(raw)
                if dst.with_suffix('.dbg.gz').exists():dst.with_suffix('.dbg.gz').write_bytes(raw)
        manifest['builds'].append(dict(mapper=mapper,artifacts=artifacts,tested_candidate_byte_exact=True,RAM_CHR_DPCM_preserved=True));save()
    after={n:sha(R/n)for n in before};assert[n for n in after if after[n]!=before[n]]==[target]
    for n in baseline['source_changes_from_T']:assert after[n]==before[n],n
    archive=C/'source-v49-bill-laser-u.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(after):z.write(R/n,n)
    manifest.update(status='PASS_WORKING_BILL_LASER_RENDER_U_BOTH_MAPPERS',source_hashes=after,source_archive=dict(path=str(archive.relative_to(R)),sha256=sha(archive),bytes=archive.stat().st_size),
        native_scope='60 actual-controller cases/map: Bill/Lance, 5 weapons, stand/air/prone, both facings. Controls24wrong-render cases/map, candidates0; exactmappedlaser/flare art emitted.16existing regressions including4800Laser/Flare collisionequivalence cases.',
        visual_review='ActualM3 screenshots at ages10/14/18/22 inspected; source laser visible at18/22, incorrect machine bullets seen on originalcontrol. Ordinary NES sprite/CHR-window sharing remains; no universal no-flicker claim.')
    save();print(manifest['status'],sha(C/'manifest.json'),flush=True)
if __name__=='__main__':main()
