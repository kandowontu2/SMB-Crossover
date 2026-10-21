"""Preserve the user's current Easy/Hard edit and rebuilt artifacts verbatim."""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
H=R/'build/verification/root49-easy-hard-user-baseline-a'
T=R/'build/checkpoints/roster-audit-v49-ryu-head-t'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def spans(a,b):
    assert len(a)==len(b)
    result=[]
    for i,(x,y) in enumerate(zip(a,b)):
        if x!=y:
            if result and result[-1][1]==i:result[-1][1]=i+1
            else:result.append([i,i+1])
    return result


def main():
    assert not (H/'baseline.json').exists()
    base=json.loads((T/'manifest.json').read_text())
    assert sha(T/'manifest.json')=='0e9988755d097d0d37eabde2c96f9827ab819b7718214c2f27bab2e72f2893f4'
    cat=base['source_hashes']
    assert len(cat)==412
    current={n:sha(R/n) for n in cat}
    changed={n:dict(before=cat[n],after=current[n])for n in cat if cat[n]!=current[n]}
    text=(R/'src/character_select.s').read_text()
    assert '"MODE             EASY "' in text and '"MODE             HARD "' in text
    H.mkdir(exist_ok=True)
    for n in changed:
        q=H/'source-overlay'/n
        q.parent.mkdir(parents=True,exist_ok=True)
        if q.exists():assert sha(q)==current[n], 'Retain the initial user overlay'
        else:shutil.copyfile(R/n,q)
    overlay=H/'user-source-overlay.zip'
    if overlay.exists():
        with zipfile.ZipFile(overlay)as z:
            assert json.loads(z.read('current-source-hashes.json'))==current
            for n in changed:assert hashlib.sha256(z.read(n)).hexdigest()==current[n]
    else:
        with zipfile.ZipFile(overlay,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
            for n in sorted(changed):z.write(R/n,n)
            z.writestr('current-source-hashes.json',json.dumps(current,indent=2)+'\n')
    sys.path.insert(0,str(R/'build/verification/agent49g-samus-crouch-fix-proposal-b'))
    from image import Image
    artifacts=[]
    for mapper in ['mmc3','mmc5']:
        rom=R/('build/smb-crossover-'+mapper+'.nes')
        old=T/rom.name
        im=Image(rom)
        strings=im.hook('Text','QueueOptionLine')['rom_offset']
        differences=spans(old.read_bytes(),rom.read_bytes())
        strings_only=all(strings<=start<end<=strings+88 for start,end in differences)
        files={}
        for ext in ['nes','lbl','map']:
            p=rom.with_suffix('.'+ext);q=H/p.name
            shutil.copyfile(p,q)
            files[ext]=dict(path=str(q.relative_to(R)),sha256=sha(q),bytes=q.stat().st_size)
        dbg=rom.with_suffix('.dbg');out=H/(rom.stem+'.dbg.gz')
        out.write_bytes(gzip.compress(dbg.read_bytes(),compresslevel=9,mtime=0))
        files['dbg.gz']=dict(path=str(out.relative_to(R)),sha256=sha(out),uncompressed_sha256=sha(dbg))
        artifacts.append(dict(mapper=mapper,files=files,prior_T_ROM_sha256=sha(old),
            differing_ROM_bytes=sum(end-start for start,end in differences),ROM_difference_spans=differences,
            options_text_ROM_offset=strings,ROM_differences_only_in_options_text=strings_only,
            labels_equal_T=rom.with_suffix('.lbl').read_bytes()==old.with_suffix('.lbl').read_bytes()))
    source_archive=T/'source-v49-ryu-head-t.zip'
    report=dict(status='FROZEN_USER_EASY_HARD_LABEL_BASELINE_NO_BEHAVIOR_IMPLEMENTATION_CLAIM',
        script_sha256=sha(__file__),parent_T_manifest_sha256=sha(T/'manifest.json'),
        parent_T_source_archive_sha256=sha(source_archive),source_changes_from_T=changed,
        current_source_hashes=current,source_overlay_sha256=sha(overlay),builds=artifacts,
        user_changes_preserved=True,main_modified_by_this_tool=False,
        host_preparation_correction='Initial metadata lookup used QueueOptions/Text; actual data belongs to QueueOptionLine/Text. Existing identical user overlay retained and verified before resuming. No ROM/native execution occurred in that failed preparation.',
        requested_behavior_work='Verified old-source character differences underEasy; Hard remains2.02. Later-only characters have no invented1.0 counterpart.',
        accepted_release=False,goal_complete=False)
    (H/'baseline.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],changed_files=list(changed),
        strings_only=[a['ROM_differences_only_in_options_text']for a in artifacts],
        sha256=sha(H/'baseline.json'))),flush=True)


if __name__=='__main__':main()
