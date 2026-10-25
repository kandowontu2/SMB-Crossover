"""Retain completed NT component/route evidence outside the capped workspace."""
import datetime
import json
import os
from pathlib import Path
from archive_workspace_hz import ROOT, ARCHIVE, inventory, bounded, sha


def main():
    out=ROOT/'build/verification/meta-knight-source-nu/archive-nt-evidence'
    out.mkdir(parents=True,exist_ok=False)
    receipt=json.loads((ROOT/'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    assert ARCHIVE.drive.lower()==ROOT.drive.lower()
    checkpoint=ROOT/'build/checkpoints/little-mac-star-nt'
    manifest=json.loads((checkpoint/'manifest.json').read_text())
    assert sha(checkpoint/'candidate.nes')==manifest['rom_sha256']
    qa=ROOT/'build/verification/little-mac-star-nt'
    names=['entry-v2','baseline-v1','discover-mac-easy-v2','discover-mac-easy-v3',
           'discover-mac-hard-v2','replay-mac-hard-v2']
    names += [f'physical-{mode}-v{v}'for mode in('easy','hard')for v in(1,2,3)]
    moves=[]
    for name in names:
        source=bounded(qa/name,qa)
        relative=source.relative_to(ROOT)
        target=bounded(ARCHIVE/relative,ARCHIVE)
        assert source.is_dir()and not target.exists()
        files={p.relative_to(source).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(source)}
        item=dict(relative=relative.as_posix(),bytes=sum(v['bytes']for v in files.values()),files=len(files))
        moves.append((source,target,item,files))
    (out/'plan.json').write_text(json.dumps([dict(source=str(s),target=str(t),move=i,files=f)for s,t,i,f in moves],indent=2)+'\n')
    for source,target,item,files in moves:
        target.parent.mkdir(parents=True,exist_ok=True)
        os.rename(source,target)
        assert{p.relative_to(target).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(target)}==files
    items=[i for _,_,i,_ in moves]
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=str(ARCHIVE),moves=items,
                archived_bytes=sum(i['bytes']for i in items),all_files_sha256_verified=True,deleted_files=0,
                completed_and_failed_cases_both_retained=True,checkpoint_and_top_level_proof_remain_local=True)
    receipt['directories'].extend(items)
    receipt['archived_bytes']+=report['archived_bytes']
    receipt['archived_files']+=sum(i['files']for i in items)
    receipt.setdefault('additional_archives',[]).append(report)
    (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(archived_bytes=report['archived_bytes'],files=sum(i['files']for i in items),all_files_sha256_verified=True,deleted_files=0)))


if __name__=='__main__':main()
